"""IR schema loader and validation."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import jsonschema
from jsonschema import Draft7Validator


def load_schema(version: str = "2.1") -> Dict[str, Any]:
    """Load IR schema from schemas directory."""
    schema_path = Path(__file__).parent.parent.parent.parent / "schemas" / f"ir_v{version}.json"
    
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, "r") as f:
        return json.load(f)


def get_validator(version: str = "2.1") -> Draft7Validator:
    """Get JSON Schema validator for IR."""
    schema = load_schema(version)
    return Draft7Validator(schema)


def validate_ir(
    ir_data: Dict[str, Any],
    version: str = "2.1",
    max_retries: int = 3,
) -> tuple[bool, Optional[list[str]]]:
    """Validate IR against schema with retry logic.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    validator = get_validator(version)
    errors = list(validator.iter_errors(ir_data))

    if not errors:
        return True, None

    error_messages = [str(error) for error in errors]
    return False, error_messages
