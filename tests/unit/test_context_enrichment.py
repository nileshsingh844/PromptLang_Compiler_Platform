import pytest

from promptlang.core.context_enrichment.best_practices import BestPracticesRetriever
from promptlang.core.context_enrichment.examples import ExampleCollector
from promptlang.core.context_enrichment.domain_knowledge import DomainKnowledgeInjector
from promptlang.core.context_enrichment.enricher import ContextEnricher


class FakeRetriever:
    def __init__(self):
        self.queries = []

    def search(self, query: str, top_k: int = 6):
        self.queries.append((query, top_k))
        return [{"text": "x", "url": "http://example.com", "title": "t", "score": 1.0}]


def test_best_practices_retriever_builds_query():
    r = FakeRetriever()
    bp = BestPracticesRetriever(retriever=r, top_k=3)
    ir = {"meta": {"intent": "scaffold"}, "task": {"description": "Build an API"}, "context": {"stack": {}}}

    out = bp.retrieve(ir)
    assert out
    assert r.queries
    assert r.queries[0][1] == 3
    assert "Best practices" in r.queries[0][0]


def test_example_collector_builds_query():
    r = FakeRetriever()
    ex = ExampleCollector(retriever=r, top_k=2)
    ir = {
        "meta": {"intent": "scaffold"},
        "task": {"description": "Build a CLI"},
        "context": {"stack": {"language": "Go", "framework": "cobra"}},
    }

    out = ex.collect(ir)
    assert out
    assert r.queries[0][1] == 2
    q = r.queries[0][0]
    assert "Examples" in q
    assert "Go" in q


def test_domain_knowledge_injector_uses_knowledge_card_domain():
    r = FakeRetriever()
    dk = DomainKnowledgeInjector(retriever=r, top_k=4)
    ir = {"task": {"description": "Build a payments system"}, "context": {}}

    out = dk.inject(ir, knowledge_card={"domain": "fintech"})
    assert out
    assert r.queries[0][1] == 4
    assert "fintech" in r.queries[0][0]


def test_context_enricher_aggregates_results():
    r = FakeRetriever()
    enricher = ContextEnricher(
        best_practices=BestPracticesRetriever(retriever=r),
        examples=ExampleCollector(retriever=r),
        domain_knowledge=DomainKnowledgeInjector(retriever=r),
    )

    ir = {"meta": {"intent": "scaffold"}, "task": {"description": "Build"}, "context": {"stack": {}}}
    enriched = enricher.enrich(ir, knowledge_card={"domain": "general"})

    assert enriched.meta["enabled"] is True
    assert enriched.best_practices
    assert enriched.examples
    assert enriched.domain_knowledge
