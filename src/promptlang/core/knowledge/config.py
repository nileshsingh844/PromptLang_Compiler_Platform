"""Configuration for knowledge retriever."""

from pathlib import Path


class KnowledgeConfig:
    """Configuration for knowledge retrieval system."""
    
    def __init__(self):
        # Retrieval settings
        self.top_k = 6
        self.max_chunk_chars = 900
        
        # Embedding settings
        self.embedding_model = "all-MiniLM-L6-v2"
        
        # File paths (repo-root relative)
        self.index_path = Path("knowledge/index/faiss.index")
        self.meta_path = Path("knowledge/index/meta.json")
        self.chunks_path = Path("knowledge/chunks/chunks.jsonl")
        
        # Retrieval settings
        self.min_score_threshold = 0.0  # Include all results by default
        self.enable_deduplication = True
