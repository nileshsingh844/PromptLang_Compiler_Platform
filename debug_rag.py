#!/usr/bin/env python3
"""
Debug script to check RAG filtering effectiveness.
"""

import sys
sys.path.insert(0, "/home/nilesh/Desktop/GROQ/promptlang_migration/PromptLang_Compiler_Platform/src")

from promptlang.core.knowledge.retriever import KnowledgeRetriever

def test_filtering():
    """Test the filtering logic directly."""
    retriever = KnowledgeRetriever()
    
    query = "Create a FastAPI REST API with user authentication using JWT tokens"
    print(f"Query: {query}")
    print()
    
    # Test search
    results = retriever.search(query, top_k=10)
    print(f"Found {len(results)} results")
    print()
    
    # Check each result
    for i, result in enumerate(results[:5]):
        title = result.get("title", "No title")
        url = result.get("url", "No URL")
        score = result.get("score", 0)
        text_preview = result.get("text", "")[:100] + "..."
        
        # Test filtering
        should_filter = retriever._should_filter_chunk(result, query)
        
        print(f"Result {i+1}:")
        print(f"  Title: {title}")
        print(f"  URL: {url}")
        print(f"  Score: {score:.3f}")
        print(f"  Should filter: {should_filter}")
        print(f"  Preview: {text_preview}")
        print()

if __name__ == "__main__":
    test_filtering()
