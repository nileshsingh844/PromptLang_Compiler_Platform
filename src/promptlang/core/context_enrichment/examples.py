from __future__ import annotations

from typing import Any, Dict, List, Optional

from promptlang.core.knowledge import KnowledgeRetriever


class ExampleCollector:
    def __init__(self, retriever: Optional[KnowledgeRetriever] = None, top_k: int = 6,
                 use_llm_refinement: bool = False, llm_client: Optional[Any] = None):
        self.retriever = retriever or KnowledgeRetriever()
        self.top_k = top_k
        self.use_llm_refinement = use_llm_refinement
        self.llm_client = llm_client

    def collect(self, ir: Dict[str, Any]) -> List[Dict[str, Any]]:
        meta = ir.get("meta", {})
        task = ir.get("task", {})
        context = ir.get("context", {})
        stack = context.get("stack", {}) or {}

        intent = meta.get("intent") or ""
        desc = task.get("description") or ""
        lang = stack.get("language") or ""
        framework = stack.get("framework") or ""

        bits = ["Examples", intent, str(lang), str(framework), str(desc)]
        query = " ".join([b for b in bits if b]).strip()
        query = query[:500]
        
        # Use Option C (hybrid RAG + LLM refinement) if enabled and LLM client available
        if self.use_llm_refinement and self.llm_client:
            return self.retriever.search_with_llm_refinement(
                query, 
                top_k=self.top_k, 
                llm_client=self.llm_client,
                refine_top_n=min(self.top_k, 5)
            )
        else:
            # Use Option B (enhanced RAG with keyword boosters and filters)
            return self.retriever.search(query, top_k=self.top_k)
