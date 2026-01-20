"""Pipeline orchestrator coordinating stages 0-8 with parallelism."""

import asyncio
import hashlib
import logging
import os
import uuid
from typing import Any, Callable, Dict, List, Optional

import structlog

from promptlang.core.cache.manager import CacheManager
from promptlang.core.clarification.engine import ClarificationEngine
from promptlang.core.compiler.dialect_compiler import DialectCompiler
from promptlang.core.generator.scaffold import ScaffoldGenerator
from promptlang.core.intent.router import IntentRouter
from promptlang.core.ir.validator import IRValidator
from promptlang.core.knowledge import KnowledgeRetriever, build_retrieval_query
from promptlang.core.linter.rules import IRLinter
from promptlang.core.optimizer.token_optimizer import TokenOptimizer
from promptlang.core.prompt_compiler import PromptTemplateEngine
from promptlang.core.translator.ir_builder import IRBuilder
from promptlang.core.utils.hashing import generate_cache_key, hash_ir
from promptlang.core.utils.timing import TimingContext
from promptlang.core.validator.output_validator import OutputValidator
from promptlang.core.llm.manager import LLMProviderManager
from promptlang.core.llm.config import LLMConfig, LLMProviderType

from promptlang.core.context_enrichment import ContextEnricher
from promptlang.core.extractor import ContentScraper, GitHubParser, KnowledgeCardBuilder
from promptlang.core.knowledge.llm_adapter import create_llm_adapter

logger = structlog.get_logger()


class PipelineOrchestrator:
    """Orchestrates the complete pipeline stages 0-8."""

    def __init__(
        self,
        cache_manager: Optional[CacheManager] = None,
        llm_provider: Optional[str] = None,
    ):
        """Initialize orchestrator.

        Args:
            cache_manager: Cache manager instance
        """
        self.cache_manager = cache_manager or CacheManager()
        
        # Initialize LLM manager for Option C (hybrid RAG + LLM refinement)
        # Use only Groq provider to avoid dependency issues
        try:
            llm_config = LLMConfig(
                primary_provider=LLMProviderType.GROQ,
                fallback_providers=[LLMProviderType.MOCK],  # Use mock as fallback
                max_retries=1,
                retry_delay=0.5
            )
            self.llm_manager = LLMProviderManager(llm_config)
            llm_adapter = create_llm_adapter(self.llm_manager)
            use_llm_refinement = True
        except Exception as e:
            print(f"Failed to initialize LLM manager, using Option B only: {e}")
            self.llm_manager = None
            llm_adapter = None
            use_llm_refinement = False
        
        # Initialize stage components
        self.intent_router = IntentRouter()
        self.clarification_engine = ClarificationEngine()
        self.ir_builder = IRBuilder()
        self.ir_validator = IRValidator()
        self.linter = IRLinter()
        self.token_optimizer = TokenOptimizer()
        self.dialect_compiler = DialectCompiler()
        self.knowledge_retriever = KnowledgeRetriever()
        self.scaffold_generator = ScaffoldGenerator()
        self.output_validator = OutputValidator()

        self.github_parser = GitHubParser(github_token=os.getenv("GITHUB_TOKEN"))
        self.content_scraper = ContentScraper()
        self.knowledge_card_builder = KnowledgeCardBuilder()
        
        # Initialize context enricher with LLM refinement support (Option C)
        llm_adapter = create_llm_adapter(self.llm_manager) if self.llm_manager else None
        self.context_enricher = ContextEnricher(
            use_llm_refinement=False,  # Disable Option C
            llm_client=llm_adapter  # Pass LLM adapter for refinement
        )
        self.prompt_template_engine = PromptTemplateEngine()

    def configure_context_enrichment(self, use_llm_refinement: bool = False, llm_client: Optional[Any] = None):
        """Configure context enrichment options.
        
        Args:
            use_llm_refinement: Enable Option C (hybrid RAG + LLM refinement)
            llm_client: LLM client for refinement (e.g., Groq, OpenAI client)
        """
        self.context_enricher = ContextEnricher(
            use_llm_refinement=use_llm_refinement,
            llm_client=llm_client
        )

    async def execute(
        self,
        input_text: str,
        intent: Optional[str] = None,
        target_model: str = "oss",
        token_budget: int = 4000,
        scaffold_mode: str = "full",
        security_level: str = "high",
        validation_mode: str = "strict",
    ) -> Dict[str, Any]:
        """Execute full pipeline stages 0-8.

        Args:
            input_text: Human input
            intent: Explicit intent (optional)
            target_model: Target model
            token_budget: Token budget
            scaffold_mode: Scaffold mode (quick/full)
            security_level: Security level (low/high)
            validation_mode: Validation mode (strict/progressive)

        Returns:
            Complete pipeline result
        """
        request_id = str(uuid.uuid4())
        timing = TimingContext()

        # Generate build hash
        build_hash = hashlib.sha256(
            f"{os.getenv('BUILD_HASH', 'dev')}".encode()
        ).hexdigest()[:8]

        logger.info("Pipeline execution started", request_id=request_id)

        # Stage 0: Input normalization (DTO creation)
        with timing.stage("stage_0_input"):
            normalized_input = {
                "input": input_text,
                "intent": intent,
                "target_model": target_model,
                "token_budget": token_budget,
                "scaffold_mode": scaffold_mode,
                "security_level": security_level,
                "validation_mode": validation_mode,
            }

        # Generate cache key
        # First we need IR to generate cache key, so we'll generate it after stage 2

        # Stage 1: Intent routing
        with timing.stage("stage_1_intent"):
            detected_intent = self.intent_router.route(input_text, explicit_intent=intent)

        # Stage 1.5: Clarification
        with timing.stage("stage_1_5_clarification"):
            questions, assumptions = self.clarification_engine.clarify(
                input_text, detected_intent
            )
            context = assumptions

        # Stage 2: IR Translation
        with timing.stage("stage_2_translate"):
            ir = await self.ir_builder.build(
                input_text, explicit_intent=detected_intent, context=context
            )

        # Stage 2.5: Knowledge Retrieval (IR -> RAG)
        with timing.stage("stage_2_5_rag_retrieval"):
            retrieved_knowledge = []
            rag_enabled = False
            try:
                retrieval_query = build_retrieval_query(ir)
                retrieved_knowledge = self.knowledge_retriever.search(retrieval_query, top_k=6)
                rag_enabled = True
            except Exception as e:
                logger.warning(f"RAG retrieval disabled: {e}")

            # Attach to pipeline context for downstream stages
            if isinstance(context, dict):
                context["retrieved_knowledge"] = retrieved_knowledge

        # Generate cache key now that we have IR
        ir_hash = hash_ir(ir)
        schema_version = ir.get("meta", {}).get("schema_version", "2.1.0")
        compiler_version = "0.1.0"
        cache_key = generate_cache_key(ir_hash, schema_version, compiler_version, target_model)

        # Check cache
        cached_result = self.cache_manager.get(cache_key)
        if cached_result:
            logger.info("Cache hit", request_id=request_id, cache_key=cache_key[:16])
            return cached_result

        # Stage 3: Schema Validation
        with timing.stage("stage_3_validate"):
            is_valid, errors, ir = self.ir_validator.validate(ir)
            if not is_valid:
                raise ValueError(f"IR validation failed: {errors}")

        # Stage 4 & 5: Parallel execution (Linter + Optimizer)
        with timing.stage("stage_4_5_parallel"):
            linter_task = asyncio.create_task(self._run_linter(ir))
            optimizer_task = asyncio.create_task(self._run_optimizer(ir, token_budget, detected_intent))

            # Wait for both
            linter_valid, linter_findings = await linter_task
            optimized_ir, optimization_warnings = await optimizer_task

            if not linter_valid:
                logger.warning("Linter found issues", findings=linter_findings)

        # Stage 6: Dialect Compilation
        with timing.stage("stage_6_compile"):
            compiled_prompt = self.dialect_compiler.compile(
                optimized_ir,
                target_model=target_model,
                retrieved_knowledge=retrieved_knowledge,
                token_budget=token_budget,
            )

        # Stage 7: Scaffold Generation
        with timing.stage("stage_7_generate"):
            output = await self.scaffold_generator.generate(
                compiled_prompt, optimized_ir, scaffold_mode=scaffold_mode
            )

        # Stage 8: Output Validation (concurrent checks)
        with timing.stage("stage_8_validate"):
            validation_report = await self.output_validator.validate(output, optimized_ir)

        # Build provenance
        provenance = {
            "request_id": request_id,
            "build_hash": build_hash,
            "stage_timings_ms": timing.get_timings(),
            "token_usage": {
                "estimated": self._estimate_tokens(optimized_ir),
                "budget": token_budget,
            },
            "cost_metadata": {},
            "transformation_chain": [
                "input_normalization",
                "intent_routing",
                "clarification",
                "ir_translation",
                "rag_retrieval",
                "schema_validation",
                "ir_linting",
                "token_optimization",
                "dialect_compilation",
                "scaffold_generation",
                "output_validation",
            ],
        }

        # Build result
        result = {
            "status": validation_report.get("status", "success"),
            "ir_json": ir,
            "optimized_ir": optimized_ir,
            "compiled_prompt": compiled_prompt,
            "output": output,
            "validation_report": validation_report,
            "warnings": optimization_warnings + linter_findings,
            "provenance": provenance,
            "knowledge_sources_used": [k.get("url") for k in (retrieved_knowledge or []) if k.get("url")],
            "knowledge_top_k": 6,
            "rag_enabled": rag_enabled,
        }

        # Cache result
        self.cache_manager.set(cache_key, result)

        logger.info("Pipeline execution complete", request_id=request_id, status=result["status"])
        return result

    async def execute_prompt_generation(
        self,
        *,
        input_text: str,
        template_name: str = "universal_cursor_prompt",
        repo_url: Optional[str] = None,
        urls: Optional[List[str]] = None,
        token_budget: int = 4000,
        progress_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        job_id = str(uuid.uuid4())
        timing = TimingContext()

        def emit(stage: str, data: Optional[Dict[str, Any]] = None) -> None:
            if progress_callback is None:
                return
            try:
                progress_callback(stage, data or {})
            except Exception:
                return

        normalized_urls = [u.strip() for u in (urls or []) if isinstance(u, str) and u.strip()]

        cache_payload = {
            "input_text": input_text,
            "template_name": template_name,
            "repo_url": repo_url or "",
            "urls": sorted(normalized_urls),
            "token_budget": token_budget,
        }
        cache_key = hashlib.sha256(str(cache_payload).encode("utf-8")).hexdigest()
        cache_key = f"prompt_generation:{cache_key}"

        cached = self.cache_manager.get(cache_key)
        if cached:
            emit("cache_hit", {"job_id": job_id})
            cached["job_id"] = job_id
            return cached

        emit("start", {"job_id": job_id})

        with timing.stage("stage_1_ir_translate"):
            emit("ir_translate")
            ir = await self.ir_builder.build(
                input_text,
                explicit_intent="prompt_generation",
                context={},
            )

        sources: Dict[str, Any] = {"repo_url": repo_url, "urls": normalized_urls}
        github_content = None
        scraped_contents: List[Dict[str, Any]] = []

        if repo_url:
            with timing.stage("stage_2_extract_github"):
                emit("extract_github", {"repo_url": repo_url})
                try:
                    github_content = await self.github_parser.extract(repo_url)
                    sources["github"] = {"full_name": github_content.repo_metadata.get("full_name")}
                except Exception as e:
                    sources["github_error"] = str(e)

        if normalized_urls:
            with timing.stage("stage_3_scrape_urls"):
                emit("scrape_urls", {"count": len(normalized_urls)})
                for u in normalized_urls:
                    try:
                        sc = await self.content_scraper.scrape_url(u)
                        scraped_contents.append(sc.dict())
                    except Exception as e:
                        scraped_contents.append({"url": u, "error": str(e)})

        with timing.stage("stage_4_knowledge_card"):
            emit("knowledge_card")
            try:
                if github_content is not None:
                    knowledge_card = (await self.knowledge_card_builder.build_from_github(github_content)).dict()
                else:
                    knowledge_card = (await self.knowledge_card_builder.build_from_text(input_text)).dict()
            except Exception as e:
                knowledge_card = {"error": str(e)}

        with timing.stage("stage_5_context_enrichment"):
            emit("context_enrichment")
            # Context enrichment disabled to avoid irrelevant data
            enriched_context = {
                "best_practices": [],
                "examples": [],
                "domain_knowledge": [],
                "meta": {
                    "enabled": False,
                    "reason": "Disabled to avoid irrelevant data"
                }
            }

        with timing.stage("stage_6_prompt_compile"):
            emit("prompt_compile", {"template": template_name})
            prompt = self.prompt_template_engine.render(
                template_name,
                ir=ir,
                knowledge_card=knowledge_card,
                enriched_context=enriched_context,
                extra={"token_budget": token_budget, "sources": sources, "scraped_contents": scraped_contents},
            )

        result = {
            "job_id": job_id,
            "template_name": template_name,
            "prompt": prompt,
            "ir": ir,
            "knowledge_card": knowledge_card,
            "enriched_context": enriched_context,
            "sources": sources,
            "provenance": {"stage_timings_ms": timing.get_timings()},
        }

        self.cache_manager.set(cache_key, result)
        emit("complete", {"job_id": job_id})
        return result

    async def _run_linter(self, ir: Dict[str, Any]) -> tuple[bool, List[Dict[str, str]]]:
        """Run linter asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.linter.lint, ir)

    async def _run_optimizer(
        self, ir: Dict[str, Any], token_budget: int, intent: str
    ) -> tuple[Dict[str, Any], List[str]]:
        """Run token optimizer asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.token_optimizer.optimize, ir, token_budget, intent
        )

    def _estimate_tokens(self, ir: Dict[str, Any]) -> int:
        """Estimate token count."""
        import json
        json_str = json.dumps(ir, separators=(",", ":"))
        return len(json_str) // 4
