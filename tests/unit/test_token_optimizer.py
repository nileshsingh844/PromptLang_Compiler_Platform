"""Unit tests for token optimizer."""

import json
from pathlib import Path

import pytest

from promptlang.core.optimizer.token_optimizer import TokenOptimizer


@pytest.fixture
def sample_ir():
    """Load sample IR fixture."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "scaffold_fastapi.json"
    with open(fixture_path) as f:
        return json.load(f)


def test_optimize(sample_ir):
    """Test token optimization."""
    optimizer = TokenOptimizer()
    optimized, warnings = optimizer.optimize(sample_ir, token_budget=4000, intent="scaffold")
    assert "optimization" in optimized
    assert "semantic_fingerprint" in optimized["optimization"]


def test_optimize_adaptive_budget():
    """Test adaptive budget by intent."""
    optimizer = TokenOptimizer()
    scaffold_budget = optimizer._get_adaptive_budget(4000, "scaffold")
    explain_budget = optimizer._get_adaptive_budget(4000, "explain")
    assert scaffold_budget > explain_budget


def test_optimize_large_scope():
    """Test optimization with very large scope."""
    large_ir = {
        "meta": {"intent": "scaffold", "schema_version": "2.1.0"},
        "task": {"description": "x" * 100000},  # Very large description
        "context": {},
        "constraints": {"must_avoid": []},
        "output_contract": {"required_sections": [], "file_block_format": "strict"},
        "quality_checks": {},
    }
    optimizer = TokenOptimizer()
    with pytest.raises(ValueError, match="Scope too large"):
        optimizer.optimize(large_ir, token_budget=1000, intent="scaffold")
