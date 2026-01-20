#!/usr/bin/env python3
"""
Test synthetic fallback directly.
"""

import sys
sys.path.insert(0, "/home/nilesh/Desktop/GROQ/promptlang_migration/PromptLang_Compiler_Platform/src")

from promptlang.core.context_enrichment.best_practices import BestPracticesRetriever

def test_synthetic_fallback():
    """Test synthetic fallback directly."""
    retriever = BestPracticesRetriever()
    
    # Create a mock IR for FastAPI authentication
    ir = {
        "meta": {"intent": "prompt_generation"},
        "task": {"description": "Create a FastAPI REST API with user authentication using JWT tokens"},
        "context": {
            "stack": {"language": "python", "framework": "fastapi"}
        }
    }
    
    print("Testing synthetic fallback...")
    results = retriever.retrieve(ir)
    
    print(f"Got {len(results)} results:")
    for i, result in enumerate(results[:3]):
        print(f"  {i+1}. {result.get('title', 'No title')}")
        print(f"     URL: {result.get('url', 'No URL')}")
        print(f"     Score: {result.get('score', 0):.3f}")

if __name__ == "__main__":
    test_synthetic_fallback()
