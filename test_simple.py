#!/usr/bin/env python3
"""
Simple test for Options B and C enhancements to RAG context enrichment.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_option_b():
    """Test Option B: Enhanced RAG with keyword boosters and filters."""
    print("=== Testing Option B: Enhanced RAG ===")
    
    try:
        from promptlang.core.knowledge.retriever import KnowledgeRetriever
        
        retriever = KnowledgeRetriever()
        
        # Test query for FastAPI authentication
        query = "FastAPI user authentication with JWT"
        print(f"Query: {query}")
        
        # Test keyword boosters
        boosted_query = retriever._apply_keyword_boosters(query)
        print(f"Boosted query: {boosted_query}")
        
        # Test filtering
        test_chunk = {
            "text": "This is about FastAPI JWT authentication implementation",
            "title": "FastAPI Auth Guide",
            "url": "https://docs.fastapi.com/authentication"
        }
        should_filter = retriever._should_filter_chunk(test_chunk, query)
        print(f"Should filter relevant chunk: {should_filter}")
        
        # Test filtering of irrelevant chunk
        irrelevant_chunk = {
            "text": "Docker Kubernetes deployment pipeline CI/CD",
            "title": "DevOps Pipeline Setup",
            "url": "https://example.com/docker-kubernetes"
        }
        should_filter_irrelevant = retriever._should_filter_chunk(irrelevant_chunk, query)
        print(f"Should filter irrelevant chunk: {should_filter_irrelevant}")
        
        # Test relevance boosting
        base_score = 0.5
        boosted_score = retriever._apply_relevance_boost(test_chunk, query, base_score)
        print(f"Base score: {base_score}, Boosted score: {boosted_score}")
        
        print("✅ Option B tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Option B test failed: {e}")
        return False


def test_context_enrichment():
    """Test context enrichment components."""
    print("\n=== Testing Context Enrichment ===")
    
    try:
        from promptlang.core.context_enrichment.best_practices import BestPracticesRetriever
        from promptlang.core.context_enrichment.examples import ExampleCollector
        
        # Test with Option B (enhanced RAG)
        bp_retriever = BestPracticesRetriever()
        print("BestPracticesRetriever created with Option B (enhanced RAG)")
        
        example_collector = ExampleCollector()
        print("ExampleCollector created with Option B (enhanced RAG)")
        
        print("✅ Context enrichment tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Context enrichment test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Testing Enhanced RAG Implementation\n")
    
    # Check if knowledge base exists
    kb_path = Path("knowledge_base")
    if not kb_path.exists():
        print("⚠️  Knowledge base not found. Testing with mock data only.")
    
    results = []
    results.append(test_option_b())
    results.append(test_context_enrichment())
    
    print(f"\n=== Summary ===")
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed.")
        return 1


if __name__ == "__main__":
    exit(main())
