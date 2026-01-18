"""Hashing utilities for cache keys and IR fingerprinting."""

import hashlib
import json
from typing import Any, Dict


def hash_ir(ir_data: Dict[str, Any]) -> str:
    """Generate deterministic hash for IR data."""
    # Normalize by removing volatile fields
    normalized = {
        "meta": {
            "intent": ir_data.get("meta", {}).get("intent"),
            "schema_version": ir_data.get("meta", {}).get("schema_version"),
        },
        "task": ir_data.get("task", {}),
        "context": ir_data.get("context", {}),
        "constraints": ir_data.get("constraints", {}),
        "output_contract": ir_data.get("output_contract", {}),
    }
    json_str = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(json_str.encode()).hexdigest()[:16]


def generate_cache_key(
    ir_hash: str,
    schema_version: str,
    compiler_version: str,
    target_model: str,
) -> str:
    """Generate cache key from IR hash, schema version, compiler version, and target model."""
    components = [ir_hash, schema_version, compiler_version, target_model]
    key_str = "|".join(components)
    return hashlib.sha256(key_str.encode()).hexdigest()


def hash_string(data: str) -> str:
    """Hash a string."""
    return hashlib.sha256(data.encode()).hexdigest()[:16]
