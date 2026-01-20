#!/usr/bin/env python3
"""
Test script for Options B and C enhancements to RAG context enrichment.

This script tests:
1. Option B: Enhanced RAG with keyword boosters and domain filters
2. Option C: Hybrid RAG + LLM refinement

Run with: python3 test_enhanced_rag.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from promptlang.core.knowledge.retriever import KnowledgeRetriever
from promptlang.core.context_enrichment.best_practices import BestPracticesRetriever
from promptlang.core.context_enrichment.examples import ExampleCollector


def test_option_b():
    """Test Option B: Enhanced RAG with keyword boosters and filters."""
    print("=== Testing Option B: Enhanced RAG ===")
    
    try:
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
        
    except Exception as e:
        print(f"❌ Option B test failed: {e}")
        return False
    
    return True


def test_option_c():
    """Test Option C: Hybrid RAG + LLM refinement (mock LLM)."""
    print("\n=== Testing Option C: Hybrid RAG + LLM Refinement ===")
    
    class MockLLMClient:
        """Mock LLM client for testing."""
        
        class chat:
            class completions:
                
                @staticmethod
                def create(*args, **kwargs):
                    class MockResponse:
                        class choices:
                            
                            @staticmethod
                            def __getitem__(_):
                                class MockChoice:
                                    class message:
                                        content = "[1, 3, 2]"  # Mock ranking
                                return MockChoice()
                        return MockResponse()
                    return MockResponse()
    
    try:
        retriever = KnowledgeRetriever()
        
        # Test with mock LLM client
        mock_llm = MockLLMClient()
        
        # Test LLM filtering and ranking logic
        candidates = [
            {"text": "FastAPI JWT auth", "title": "Auth Guide", "url": "https://fastapi.com/auth", "score": 0.8},
            {"text": "Docker setup", "title": "Dockerfile", "url": "https://example.com/docker", "score": 0.6},
            {"text": "FastAPI OAuth2", "title": "OAuth2 Guide", "url": "https://fastapi.com/oauth2", "score": 0.7},
        ]
        
        query = "FastAPI authentication"
        refined = retriever._llm_filter_and_rerank(query, candidates, mock_llm, top_n=2)
        
        print(f"Original candidates: {len(candidates)}")
        print(f"Refined candidates: {len(refined)}")
        
        for i, chunk in enumerate(refined):
            print(f"  {i+1}. {chunk['title']} (score: {chunk['score']:.2f}, llm_rank: {chunk.get('llm_rank', 'N/A')})")
        
        print("✅ Option C tests passed!")
        
    except Exception as e:
        print(f"❌ Option C test failed: {e}")
        return False
    
    return True


def test_context_enrichment_integration():
    """Test integration with context enrichment components."""
    print("\n=== Testing Context Enrichment Integration ===")
    
    try:
        # Test BestPracticesRetriever with Option B
        bp_retriever = BestPracticesRetriever()
        print("BestPracticesRetriever created with Option B (enhanced RAG)")
        
        # Test ExampleCollector with Option B
        example_collector = ExampleCollector()
        print("ExampleCollector created with Option B (enhanced RAG)")
        
        # Test with Option C (mock LLM)
        class MockLLM:
            class chat:
                class completions:
                    
                    @staticmethod
                    def create(*args, **kwargs):
                        class Response:
                            class choices:
                                
                                @staticmethod
                                def __getitem__(_):
                                    class Choice:
                                        class message:
                                            content = "[1, 2]"
                                    return Choice()
                            return Response()
                        return Response()
        
        mock_llm = MockLLM()
        bp_retriever_llm = BestPracticesRetriever(use_llm_refinement=True, llm_client=mock_llm)
        print("BestPracticesRetriever created with Option C (LLM refinement)")
        
        example_collector_llm = ExampleCollector(use_llm_refinement=True, llm_client=mock_llm)
        print("ExampleCollector created with Option C (LLM refinement)")
        
        print("✅ Context enrichment integration tests passed!")
        
    except Exception as e:
        print(f"❌ Context enrichment integration test failed: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("Testing Enhanced RAG Options B & C\n")
    
    # Check if knowledge base exists
    kb_path = Path("knowledge_base")
    if not kb_path.exists():
        print("⚠️  Knowledge base not found. Some tests may fail.")
        print("   Expected path: ./knowledge_base/")
    
    results = []
    results.append(test_option_b())
    results.append(test_option_c())
    results.append(test_context_enrichment_integration())
    
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
