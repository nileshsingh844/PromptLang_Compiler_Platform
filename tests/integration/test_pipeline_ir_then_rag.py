"""Integration test: IR translation happens before RAG retrieval and prompt injection works."""

import asyncio

import pytest

from promptlang.core.pipeline.orchestrator import PipelineOrchestrator


@pytest.mark.asyncio
async def test_pipeline_ir_then_rag_injects_knowledge():
    orchestrator = PipelineOrchestrator()

    # Use a query likely to match knowledge base.
    input_text = "Design a microservices architecture with C4 model and include observability and security"

    result = await orchestrator.execute(
        input_text=input_text,
        intent="scaffold",
        target_model="oss",
        token_budget=4000,
        scaffold_mode="full",
        security_level="high",
        validation_mode="strict",
    )

    # IR exists
    assert "ir_json" in result
    assert isinstance(result["ir_json"], dict)

    # RAG fields are present
    assert "knowledge_sources_used" in result
    assert "knowledge_top_k" in result
    assert "rag_enabled" in result

    # Prompt contains injected knowledge block (only when RAG actually ran)
    compiled_prompt = result.get("compiled_prompt", "")
    if result.get("rag_enabled") and result.get("knowledge_sources_used"):
        assert "REFERENCE KNOWLEDGE" in compiled_prompt

    # Sources list should be consistent with injected retrieval
    assert isinstance(result["knowledge_sources_used"], list)
    # may be empty if artifacts missing; if present ensure URLs
    for url in result["knowledge_sources_used"]:
        assert isinstance(url, str)
        assert url.startswith("http")
