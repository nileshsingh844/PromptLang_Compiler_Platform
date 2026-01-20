from __future__ import annotations

from typing import Any, Dict, List, Optional

from promptlang.core.knowledge import KnowledgeRetriever


class DomainKnowledgeInjector:
    def __init__(self, retriever: Optional[KnowledgeRetriever] = None, top_k: int = 6):
        self.retriever = retriever or KnowledgeRetriever()
        self.top_k = top_k

    def inject(self, ir: Dict[str, Any], knowledge_card: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        domain = ""
        if isinstance(knowledge_card, dict):
            domain = str(knowledge_card.get("domain") or "")
        if not domain:
            context = ir.get("context", {})
            domain = str(context.get("domain") or "")

        task = ir.get("task", {})
        desc = str(task.get("description") or "")

        if domain:
            query = f"Domain knowledge. {domain}. {desc}"[:500]
        else:
            query = f"Domain knowledge. {desc}"[:500]

        return self.retriever.search(query, top_k=self.top_k)
