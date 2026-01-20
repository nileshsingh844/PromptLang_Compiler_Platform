from __future__ import annotations

from typing import Any, Dict, Optional

from .models import EnrichedContext
from .best_practices import BestPracticesRetriever
from .examples import ExampleCollector
from .domain_knowledge import DomainKnowledgeInjector


class ContextEnricher:
    def __init__(
        self,
        best_practices: Optional[BestPracticesRetriever] = None,
        examples: Optional[ExampleCollector] = None,
        domain_knowledge: Optional[DomainKnowledgeInjector] = None,
        use_llm_refinement: bool = False,
        llm_client: Optional[Any] = None,
    ):
        # Initialize retrievers with LLM refinement options
        self.best_practices = best_practices or BestPracticesRetriever(
            use_llm_refinement=use_llm_refinement, 
            llm_client=llm_client
        )
        self.examples = examples or ExampleCollector(
            use_llm_refinement=use_llm_refinement, 
            llm_client=llm_client
        )
        self.domain_knowledge = domain_knowledge or DomainKnowledgeInjector()

    def enrich(self, ir: Dict[str, Any], knowledge_card: Optional[Dict[str, Any]] = None) -> EnrichedContext:
        bp = []
        ex = []
        dk = []
        meta: Dict[str, Any] = {"enabled": True}

        try:
            bp = self.best_practices.retrieve(ir)
            meta["best_practices_count"] = len(bp)
            meta["best_practices_method"] = "llm_refined" if self.best_practices.use_llm_refinement else "enhanced_rag"
        except Exception as e:
            meta["best_practices_error"] = str(e)

        try:
            ex = self.examples.collect(ir)
            meta["examples_count"] = len(ex)
            meta["examples_method"] = "llm_refined" if self.examples.use_llm_refinement else "enhanced_rag"
        except Exception as e:
            meta["examples_error"] = str(e)

        try:
            dk = self.domain_knowledge.inject(ir, knowledge_card=knowledge_card)
            meta["domain_knowledge_count"] = len(dk)
        except Exception as e:
            meta["domain_knowledge_error"] = str(e)

        if any(k.endswith("_error") for k in meta.keys()):
            meta["enabled"] = False

        return EnrichedContext(
            best_practices=bp,
            examples=ex,
            domain_knowledge=dk,
            meta=meta,
        )
