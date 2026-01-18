"""Unit tests for IR validator."""

import json
from pathlib import Path

import pytest

from promptlang.core.ir.validator import IRValidator


@pytest.fixture
def valid_ir():
    """Load valid IR fixture."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "scaffold_fastapi.json"
    with open(fixture_path) as f:
        return json.load(f)


def test_validate_valid_ir(valid_ir):
    """Test validation of valid IR."""
    validator = IRValidator()
    is_valid, errors, repaired = validator.validate(valid_ir)
    assert is_valid
    assert errors is None


def test_validate_missing_required_fields():
    """Test validation of IR with missing required fields."""
    invalid_ir = {"meta": {"intent": "scaffold"}}
    validator = IRValidator()
    is_valid, errors, repaired = validator.validate(invalid_ir)
    assert not is_valid
    assert errors is not None


def test_validate_repair():
    """Test validation with repair."""
    invalid_ir = {"meta": {"intent": "scaffold"}}
    validator = IRValidator(max_retries=1)
    is_valid, errors, repaired = validator.validate(invalid_ir)
    # Should attempt repair
    assert "task" in repaired
