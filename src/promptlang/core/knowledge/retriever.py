"""Knowledge retriever using existing FAISS index.

This module is runtime-only: it does not crawl/ingest.
It loads artifacts created under repo-root `knowledge/`.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class KnowledgeRetriever:
    """Retrieves knowledge chunks from an existing FAISS index."""

    # NOTE: We intentionally keep heavy deps (faiss/numpy/sentence-transformers)
    # out of module import-time to avoid hard failures during test collection in
    # environments where optional ML deps are not fully configured.
    _shared_index: Optional[Any] = None
    _shared_chunks: Optional[List[Dict[str, Any]]] = None
    _shared_meta: Optional[Dict[str, Any]] = None
    _shared_embedder: Optional[Any] = None
    _shared_vectorizer: Optional[Any] = None
    _shared_tfidf_matrix: Optional[Any] = None
    _loaded: bool = False

    def __init__(
        self,
        index_path: str = "knowledge/index/faiss.index",
        meta_path: str = "knowledge/index/meta.json",
        top_k: int = 6,
        max_chunk_chars: int = 900,
        embedding_model_name: str = "all-MiniLM-L6-v2",
    ):
        self.index_path = Path(index_path)
        self.meta_path = Path(meta_path)
        self.top_k = top_k
        self.max_chunk_chars = max_chunk_chars
        self.embedding_model_name = embedding_model_name

    @classmethod
    def _lazy_load(cls, index_path: Path, meta_path: Path, embedding_model_name: str) -> None:
        """Load index + chunk records once per process."""
        if cls._loaded:
            return

        # Load meta.json first (includes chunks list)
        if not meta_path.exists():
            raise FileNotFoundError(f"Knowledge metadata not found: {meta_path}")
        with open(meta_path, "r", encoding="utf-8") as f:
            cls._shared_meta = json.load(f)
        cls._shared_chunks = cls._shared_meta.get("chunks", [])

        # Prefer FAISS + sentence-transformers if available, but fall back to a
        # lightweight TF-IDF retriever when heavy ML deps (torch) are broken.
        if index_path.exists():
            try:
                import faiss  # type: ignore

                cls._shared_index = faiss.read_index(str(index_path))
            except Exception:
                cls._shared_index = None

        if cls._shared_index is not None:
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore

                cls._shared_embedder = SentenceTransformer(embedding_model_name, device="cpu")
            except Exception:
                cls._shared_embedder = None

        if cls._shared_index is None or cls._shared_embedder is None:
            # TF-IDF fallback (no torch required)
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
            except Exception as e:
                raise RuntimeError(
                    "scikit-learn is required for TF-IDF fallback retrieval. Install 'scikit-learn' to enable RAG."
                ) from e

            texts = [c.get("text", "") for c in (cls._shared_chunks or [])]
            cls._shared_vectorizer = TfidfVectorizer(
                max_features=20000,
                stop_words="english",
            )
            cls._shared_tfidf_matrix = cls._shared_vectorizer.fit_transform(texts)

        cls._loaded = True

    def _ensure_loaded(self) -> None:
        self._lazy_load(self.index_path, self.meta_path, self.embedding_model_name)

    @staticmethod
    def _trim_text(text: str, max_chars: int) -> str:
        if not text:
            return ""
        if len(text) <= max_chars:
            return text
        return text[:max_chars].rstrip() + "..."

    @staticmethod
    def _chunk_to_result(chunk: Dict[str, Any], score: float, max_chunk_chars: int) -> Dict[str, Any]:
        return {
            "text": KnowledgeRetriever._trim_text(chunk.get("text", ""), max_chunk_chars),
            "url": chunk.get("url", ""),
            "title": chunk.get("title", ""),
            "score": float(score),
        }
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return top_k chunks as {text,url,title,score}.

        Dedupes by URL and trims chunk text.
        Enhanced with keyword boosters and domain filters for better relevance.
        """
        self._ensure_loaded()

        if not query.strip():
            return []

        top_k = top_k or self.top_k
        chunks = self._shared_chunks or []
        index = self._shared_index
        embedder = self._shared_embedder

        # Option B: Keyword boosters and domain filters
        boosted_query = self._apply_keyword_boosters(query)
        
        if index is not None and embedder is not None and chunks:
            try:
                import numpy as np  # type: ignore
            except Exception as e:
                raise RuntimeError(
                    "numpy is required for knowledge retrieval. Install 'numpy' to enable RAG."
                ) from e

            query_vec = embedder.encode([boosted_query], normalize_embeddings=True)
            scores, indices = index.search(query_vec.astype(np.float32), min(top_k * 3, len(chunks)))

            results: List[Dict[str, Any]] = []
            seen_urls = set()
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(chunks):
                    continue
                chunk = chunks[idx]
                url = chunk.get("url", "")
                if not url or url in seen_urls:
                    continue
                
                # Apply domain filters
                if self._should_filter_chunk(chunk, query):
                    continue
                
                # Apply relevance boosting
                boosted_score = self._apply_relevance_boost(chunk, query, score)
                results.append(self._chunk_to_result(chunk, boosted_score, self.max_chunk_chars))
                seen_urls.add(url)

                if len(results) >= top_k:
                    break

            return results

        # TF-IDF fallback with enhancements
        vectorizer = self._shared_vectorizer
        matrix = self._shared_tfidf_matrix
        if vectorizer is None or matrix is None or not chunks:
            return []

        try:
            import numpy as np  # type: ignore
        except Exception as e:
            raise RuntimeError("numpy is required for TF-IDF fallback retrieval.") from e

        qv = vectorizer.transform([boosted_query])
        # cosine similarity for L2-normalized tf-idf vectors is dot product
        scores = (matrix @ qv.T).toarray().reshape(-1)
        # take a bit more for url de-dupe and filtering
        k = min(top_k * 5, len(scores))
        best = np.argpartition(-scores, range(k))[:k]
        best = best[np.argsort(-scores[best])]

        results: List[Dict[str, Any]] = []
        seen_urls = set()
        for idx in best:
            chunk = chunks[int(idx)]
            url = chunk.get("url", "")
            if not url or url in seen_urls:
                continue
            
            # Apply domain filters
            if self._should_filter_chunk(chunk, query):
                continue
            
            # Apply relevance boosting
            boosted_score = self._apply_relevance_boost(chunk, query, float(scores[int(idx)]))
            results.append(self._chunk_to_result(chunk, boosted_score, self.max_chunk_chars))
            seen_urls.add(url)
            if len(results) >= top_k:
                break

        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics from meta.json."""
        self._ensure_loaded()
        meta = self._shared_meta or {}
        chunks = self._shared_chunks or []
        index = self._shared_index

        backend = (
            "faiss+sentence_transformers"
            if (index is not None and self._shared_embedder is not None)
            else "tfidf"
        )

        return {
            "embedding_model": meta.get("embedding_model", self.embedding_model_name),
            "embedding_dimension": meta.get("embedding_dimension"),
            "total_chunks": meta.get("stats", {}).get("total_chunks", len(chunks)),
            "succeeded_urls": meta.get("stats", {}).get("succeeded_urls"),
            "failed_urls": meta.get("stats", {}).get("failed_urls"),
            "index_vectors": index.ntotal if index is not None else 0,
            "backend": backend,
            "top_k": self.top_k,
            "max_chunk_chars": self.max_chunk_chars,
        }
    
    def _apply_keyword_boosters(self, query: str) -> str:
        """Apply keyword boosters to enhance query relevance."""
        # Define keyword mappings for common tech domains
        boosters = {
            "fastapi": ["FastAPI", "python", "web", "api", "rest", "http", "async", "pydantic"],
            "auth": ["authentication", "authorization", "JWT", "OAuth2", "token", "security", "login", "user"],
            "jwt": ["JWT", "token", "bearer", "authentication", "security", "jsonwebtoken"],
            "oauth": ["OAuth2", "OAuth", "authorization", "client", "credentials", "scope"],
            "database": ["database", "sql", "orm", "models", "migration", "query"],
            "docker": ["Docker", "container", "dockerfile", "compose", "deployment"],
            "kubernetes": ["Kubernetes", "k8s", "deployment", "pod", "service", "ingress"],
            "testing": ["test", "pytest", "unit", "integration", "mock", "fixture"],
        }
        
        query_lower = query.lower()
        boosted_terms = [query]
        
        for keyword, related_terms in boosters.items():
            if keyword in query_lower:
                boosted_terms.extend(related_terms)
        
        return " ".join(boosted_terms)
    
    def _should_filter_chunk(self, chunk: Dict[str, Any], query: str) -> bool:
        """Filter out irrelevant chunks based on query context."""
        query_lower = query.lower()
        chunk_text = (chunk.get("text", "") + " " + chunk.get("title", "")).lower()
        chunk_url = chunk.get("url", "").lower()
        
        # Comprehensive filtering for FastAPI authentication queries
        if "fastapi" in query_lower and ("auth" in query_lower or "jwt" in query_lower or "authentication" in query_lower):
            # Filter out completely unrelated technologies
            unrelated_terms = [
                # Cloud platforms
                "aws", "azure", "gcp", "google cloud", "amazon web services",
                # Container/DevOps
                "docker", "kubernetes", "k8s", "container", "cicd", "ci/cd",
                "terraform", "ansible", "jenkins", "pipeline", "deployment",
                # Frontend/Testing
                "cypress", "selenium", "jest", "react", "vue", "angular",
                # Databases (unless specifically mentioned)
                "redis", "mongodb", "postgresql", "mysql", "database",
                # AI/ML (unless specifically mentioned)
                "llamaindex", "openai", "chatgpt", "machine learning", "ai",
                # General architecture patterns
                "microservices", "serverless", "lambda", "functions",
                # Monitoring/Ops
                "monitoring", "logging", "elk", "prometheus", "grafana",
                # Documentation tools
                "swagger", "openapi", "postman", "insomnia",
                # Other languages/frameworks
                "node.js", "express", "django", "flask", "rails", "spring",
                # General programming concepts
                "design patterns", "solid principles", "clean code",
                # Cloud-specific services
                "ec2", "s3", "lambda", "azure functions", "cloud functions",
                # Version control/CI
                "gitlab", "github actions", "gitlab ci", "version control"
            ]
            
            # But allow if chunk contains FastAPI-specific content
            fastapi_terms = ["fastapi", "pydantic", "uvicorn", "python web", "asyncio", "python api"]
            if any(term in chunk_text for term in fastapi_terms):
                # Only filter if it's primarily about unrelated topics
                unrelated_count = sum(1 for term in unrelated_terms if term in chunk_text)
                fastapi_count = sum(1 for term in fastapi_terms if term in chunk_text)
                return unrelated_count > fastapi_count * 1  # Filter if mostly unrelated (reduced threshold)
            else:
                # Filter if no FastAPI content and contains unrelated terms
                return any(term in chunk_text or term in chunk_url for term in unrelated_terms)
        
        # Filter out generic security docs if we need specific implementation guides
        if "auth" in query_lower and "implementation" in query_lower:
            generic_security = ["owasp", "cheat sheet", "security guide", "best practices", "top 10"]
            implementation_terms = ["code", "example", "tutorial", "implementation", "fastapi", "python"]
            
            has_generic = any(term in chunk_text for term in generic_security)
            has_implementation = any(term in chunk_text for term in implementation_terms)
            
            # Filter if it's generic security without implementation details
            return has_generic and not has_implementation
        
        # Filter out completely generic documentation
        generic_docs = ["welcome to", "getting started", "overview", "introduction", "documentation"]
        if any(term in chunk_text for term in generic_docs) and "fastapi" not in chunk_text:
            return True
        
        return False
    
    def _apply_relevance_boost(self, chunk: Dict[str, Any], query: str, base_score: float) -> float:
        """Apply relevance boosting to chunks based on keyword matches."""
        query_lower = query.lower()
        chunk_text = (chunk.get("text", "") + " " + chunk.get("title", "")).lower()
        chunk_url = chunk.get("url", "").lower()
        
        boost_multiplier = 1.0
        
        # Strong boost for exact FastAPI matches
        if "fastapi" in query_lower and "fastapi" in chunk_text:
            boost_multiplier *= 2.0
        
        # Boost for authentication-specific content
        if any(term in query_lower for term in ["auth", "jwt", "oauth", "token", "authentication"]):
            auth_terms = ["jwt", "oauth", "bearer", "token", "authentication", "authorization", "login", "user"]
            auth_matches = sum(1 for term in auth_terms if term in chunk_text)
            if auth_matches > 0:
                boost_multiplier *= (1.0 + (auth_matches * 0.3))  # Up to 2.5x boost
        
        # Boost for Python/FastAPI specific content
        python_terms = ["python", "pydantic", "uvicorn", "asyncio", "web framework"]
        python_matches = sum(1 for term in python_terms if term in chunk_text)
        if python_matches > 0:
            boost_multiplier *= (1.0 + (python_matches * 0.2))  # Up to 2x boost
        
        # Boost for code examples and tutorials
        if any(term in chunk_text for term in ["example", "tutorial", "code", "implementation", "sample"]):
            boost_multiplier *= 1.3
        
        # Boost for authoritative sources
        authoritative_domains = [
            "docs.fastapi", "fastapi.tiangolo.com", "github.com", "stackoverflow.com",
            "realpython.com", "testdriven.io", "python.org"
        ]
        if any(domain in chunk_url for domain in authoritative_domains):
            boost_multiplier *= 1.4
        
        # Boost for recent content (if timestamp available)
        if chunk.get("timestamp"):
            try:
                import datetime
                chunk_date = datetime.datetime.fromisoformat(chunk["timestamp"].replace('Z', '+00:00'))
                if chunk_date > datetime.datetime.now(chunk_date.tzinfo) - datetime.timedelta(days=365):
                    boost_multiplier *= 1.2
            except:
                pass
        
        # Penalize for unrelated content that slipped through
        penalized_terms = [
            "aws", "azure", "docker", "kubernetes", "react", "vue", "angular",
            "mongodb", "redis", "llamaindex", "cypress", "terraform"
        ]
        penalty_count = sum(1 for term in penalized_terms if term in chunk_text)
        if penalty_count > 0:
            boost_multiplier *= (1.0 - (penalty_count * 0.2))  # Reduce score for unrelated content
            boost_multiplier = max(boost_multiplier, 0.3)  # Don't reduce below 0.3x
        
        return base_score * boost_multiplier
    
    def search_with_llm_refinement(self, query: str, top_k: Optional[int] = None, 
                                 llm_client: Optional[Any] = None, refine_top_n: int = 5) -> List[Dict[str, Any]]:
        """Option C: Hybrid RAG + LLM refinement for better relevance.
        
        1. Retrieve top-k chunks using enhanced RAG (Option B)
        2. Use LLM to filter/rerank chunks for query relevance
        3. Return only the reranked top-N chunks
        """
        # Step 1: Get more candidates than needed using enhanced RAG
        candidates_k = (top_k or self.top_k) * 3
        candidates = self.search(query, top_k=candidates_k)
        
        if not candidates or not llm_client:
            # Fallback to regular search if no LLM available
            return candidates[:top_k or self.top_k]
        
        # Step 2: Use LLM to filter and rerank (sync wrapper for async)
        try:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            refined_chunks = loop.run_until_complete(
                self._llm_filter_and_rerank(query, candidates, llm_client, refine_top_n)
            )
            return refined_chunks
        except Exception as e:
            # Log error and fallback to regular search
            print(f"LLM refinement failed, falling back to regular search: {e}")
            return candidates[:top_k or self.top_k]
    
    def _llm_filter_and_rerank(self, query: str, candidates: List[Dict[str, Any]], 
                              llm_client: Any, top_n: int) -> List[Dict[str, Any]]:
        """Use LLM to filter and rerank candidate chunks."""
        # Prepare chunks for LLM evaluation
        chunk_texts = []
        for i, chunk in enumerate(candidates):
            text = chunk.get("text", "")
            title = chunk.get("title", "")
            url = chunk.get("url", "")
            chunk_texts.append(f"Chunk {i+1}:\nTitle: {title}\nURL: {url}\nContent: {text[:500]}...")
        
        chunks_text = "\n\n".join(chunk_texts)
        
        # Create LLM prompt for filtering and ranking
        prompt = f"""You are helping to select the most relevant knowledge chunks for a developer query.

Query: "{query}"

Below are {len(candidates)} knowledge chunks retrieved from RAG. Your task:
1. Filter out chunks that are NOT relevant to the query
2. Rank the remaining chunks by relevance (most relevant first)
3. Return only the top {top_n} most relevant chunks

Relevance criteria:
- Directly addresses the query topic
- Contains practical examples or code
- Comes from authoritative sources
- Is up-to-date and accurate
- Specifically matches the technology/framework mentioned

Chunks to evaluate:
{chunks_text}

Respond with a JSON array of chunk indices in order of relevance, like: [3, 1, 5, 2, 4]
Only include indices of chunks that are actually relevant."""

        try:
            # Call LLM (assuming it has a chat/completion interface)
            response = llm_client.chat.completions.create(
                model="llama-3.1-8b-instant",  # or appropriate model
                messages=[
                    {"role": "system", "content": "You are an expert at evaluating technical documentation relevance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            # Parse LLM response
            import json
            result = response.choices[0].message.content.strip()
            
            # Try to extract JSON array from response
            if '[' in result and ']' in result:
                json_start = result.find('[')
                json_end = result.rfind(']') + 1
                json_str = result[json_start:json_end]
                ranked_indices = json.loads(json_str)
            else:
                # Fallback: assume space-separated numbers
                ranked_indices = [int(x) for x in result.split() if x.isdigit()]
            
            # Convert 1-based indices to 0-based and filter valid ones
            valid_chunks = []
            for idx in ranked_indices:
                chunk_idx = idx - 1  # Convert to 0-based
                if 0 <= chunk_idx < len(candidates) and len(valid_chunks) < top_n:
                    chunk = candidates[chunk_idx].copy()
                    # Boost score based on LLM ranking
                    original_score = chunk.get("score", 0.0)
                    rank_boost = 1.0 + (top_n - len(valid_chunks)) * 0.1  # Higher rank = higher boost
                    chunk["score"] = original_score * rank_boost
                    chunk["llm_rank"] = len(valid_chunks) + 1
                    valid_chunks.append(chunk)
            
            return valid_chunks
            
        except Exception as e:
            print(f"Error in LLM filtering: {e}")
            # Fallback: return original candidates with slight score adjustment
            return candidates[:top_n]
