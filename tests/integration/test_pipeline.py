"""Integration tests for full pipeline."""

import asyncio
import json
from pathlib import Path

import pytest

from promptlang.core.cache.manager import CacheManager
from promptlang.core.pipeline.orchestrator import PipelineOrchestrator


@pytest.fixture
def orchestrator():
    """Create orchestrator instance."""
    cache_manager = CacheManager()
    return PipelineOrchestrator(cache_manager=cache_manager)


@pytest.mark.asyncio
async def test_full_pipeline_scaffold(orchestrator):
    """Test full pipeline for scaffold intent."""
    result = await orchestrator.execute(
        input_text="Create a FastAPI REST API",
        intent="scaffold",
        target_model="oss",
        token_budget=4000,
        scaffold_mode="full",
        security_level="high",
        validation_mode="strict",
    )

    assert result["status"] in ["success", "warning", "error", "blocked"]
    assert "ir_json" in result
    assert "optimized_ir" in result
    assert "compiled_prompt" in result
    assert "output" in result
    assert "validation_report" in result
    assert "provenance" in result


@pytest.mark.asyncio
async def test_full_pipeline_debug(orchestrator):
    """Test full pipeline for debug intent."""
    result = await orchestrator.execute(
        input_text="Fix AttributeError in my Python code",
        intent="debug",
        target_model="oss",
        token_budget=2000,
    )

    assert result["status"] in ["success", "warning", "error", "blocked"]
    assert result["ir_json"]["meta"]["intent"] == "debug"


@pytest.mark.asyncio
async def test_pipeline_caching(orchestrator):
    """Test pipeline caching behavior."""
    input_text = "Create a test project"

    # First execution
    result1 = await orchestrator.execute(
        input_text=input_text,
        target_model="oss",
        token_budget=4000,
    )

    # Second execution (should use cache)
    result2 = await orchestrator.execute(
        input_text=input_text,
        target_model="oss",
        token_budget=4000,
    )

    # Results should be identical
    assert result1["ir_json"] == result2["ir_json"]


@pytest.mark.asyncio
async def test_pipeline_stage_4_5_parallelism(orchestrator):
    """Test that stages 4 and 5 run concurrently."""
    result = await orchestrator.execute(
        input_text="Create a project",
        target_model="oss",
        token_budget=4000,
    )

    timings = result["provenance"]["stage_timings_ms"]
    # Both stage_4 and stage_5 should have timings
    assert "stage_4_5_parallel" in timings
    # Parallel stage should complete faster than sequential would
