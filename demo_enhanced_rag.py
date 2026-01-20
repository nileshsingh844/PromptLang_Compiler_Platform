#!/usr/bin/env python3
"""
Demo script showing Options B & C improvements for FastAPI authentication query.
"""

import requests
import json
import time

def test_enhanced_rag_demo():
    """Test the enhanced RAG with a FastAPI authentication example."""
    
    print("🚀 Testing Enhanced RAG Options B & C")
    print("=" * 50)
    
    # Test query
    query = "Create a FastAPI REST API with user authentication using JWT tokens"
    print(f"Query: {query}")
    print()
    
    # Generate prompt using enhanced RAG
    payload = {
        "input": query,
        "template_name": "universal_cursor_prompt",
        "repo_url": "",
        "urls": [],
        "token_budget": 4000
    }
    
    print("📡 Sending request to enhanced RAG pipeline...")
    response = requests.post(
        "http://localhost:8000/api/v1/generate",
        headers={
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        },
        json=payload,
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        return
    
    # Parse SSE response
    lines = response.text.split('\n')
    job_id = None
    context_enrichment_data = None
    
    for line in lines:
        if line.startswith('data: '):
            try:
                data = json.loads(line[6:])
                if 'job_id' in data:
                    job_id = data['job_id']
                if 'enriched_context' in data:
                    context_enrichment_data = data
                    break
            except:
                continue
    
    if not job_id:
        print("❌ No job ID found in response")
        return
    
    print(f"✅ Job generated: {job_id[:8]}...")
    
    # Get the full result
    result_response = requests.get(f"http://localhost:8000/api/v1/prompt/{job_id}")
    if result_response.status_code != 200:
        print(f"❌ Failed to get result: {result_response.status_code}")
        return
    
    result = result_response.json()
    
    # Analyze the enriched context
    enriched_context = result.get('enriched_context', {})
    meta = enriched_context.get('meta', {})
    
    print("\n📊 Context Enrichment Results:")
    print(f"  • Best practices: {meta.get('best_practices_count', 0)} items")
    print(f"  • Examples: {meta.get('examples_count', 0)} items")
    print(f"  • Domain knowledge: {meta.get('domain_knowledge_count', 0)} items")
    print(f"  • Method: {meta.get('best_practices_method', 'enhanced_rag')}")
    print(f"  • Enabled: {meta.get('enabled', False)}")
    
    # Show best practices (if any)
    best_practices = enriched_context.get('best_practices', [])
    if best_practices:
        print(f"\n🎯 Top Best Practices ({len(best_practices)}):")
        for i, bp in enumerate(best_practices[:3], 1):
            title = bp.get('title', 'No title')
            url = bp.get('url', '')
            score = bp.get('score', 0)
            print(f"  {i}. {title}")
            print(f"     Score: {score:.3f}")
            if url:
                print(f"     Source: {url}")
            print()
    
    # Check for relevance improvements
    print("🔍 Relevance Analysis:")
    
    # Check if Docker/K8s content was filtered out (good sign)
    docker_keywords = ['docker', 'kubernetes', 'k8s', 'container']
    filtered_count = 0
    
    for bp in best_practices:
        text = (bp.get('text', '') + ' ' + bp.get('title', '')).lower()
        if any(keyword in text for keyword in docker_keywords):
            filtered_count += 1
    
    if filtered_count == 0:
        print("  ✅ Docker/K8s content successfully filtered out")
    else:
        print(f"  ⚠️  Found {filtered_count} Docker/K8s items (should be filtered)")
    
    # Check for FastAPI/auth content (good sign)
    fastapi_keywords = ['fastapi', 'jwt', 'auth', 'authentication', 'oauth']
    relevant_count = 0
    
    for bp in best_practices:
        text = (bp.get('text', '') + ' ' + bp.get('title', '')).lower()
        if any(keyword in text for keyword in fastapi_keywords):
            relevant_count += 1
    
    if relevant_count > 0:
        print(f"  ✅ Found {relevant_count} FastAPI/auth relevant items")
    else:
        print("  ⚠️  No FastAPI/auth items found")
    
    # Show timing
    provenance = result.get('provenance', {})
    timings = provenance.get('stage_timings_ms', {})
    context_time = timings.get('stage_5_context_enrichment', 0)
    
    print(f"\n⏱️  Context enrichment took {context_time:.0f}ms")
    
    print("\n🎉 Enhanced RAG Options B & C demo completed!")
    print("   • Option B: Keyword boosters + domain filters ✓")
    print("   • Option C: Ready for LLM refinement (when configured)")

if __name__ == "__main__":
    test_enhanced_rag_demo()
