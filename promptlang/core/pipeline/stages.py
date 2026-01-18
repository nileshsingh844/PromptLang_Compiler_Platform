"""Pipeline stage definitions and DTOs."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class StageInput:
    """Input DTO for pipeline stage."""

    ir: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


@dataclass
class StageOutput:
    """Output DTO for pipeline stage."""

    ir: Dict[str, Any]
    warnings: List[str]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PipelineContext:
    """Context shared across pipeline stages."""

    request_id: str
    intent: str
    target_model: str
    token_budget: int
    scaffold_mode: str
    security_level: str
    validation_mode: str
    cache_key: Optional[str] = None
