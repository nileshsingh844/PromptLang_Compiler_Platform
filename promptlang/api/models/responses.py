"""Response models for API endpoints."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProvenanceModel(BaseModel):
    """Provenance information."""

    request_id: str
    build_hash: str
    stage_timings_ms: Dict[str, float]
    token_usage: Dict[str, Any]
    cost_metadata: Dict[str, Any]
    transformation_chain: List[str]


class ValidationReportModel(BaseModel):
    """Validation report model."""

    status: str
    parallel: bool
    stage_timings_ms: Dict[str, float]
    findings: List[Dict[str, Any]]
    contract_compliance: Dict[str, Any]
    summary: Dict[str, Any]


class GenerateResponse(BaseModel):
    """Response model for /api/generate endpoint."""

    status: str
    ir_json: Dict[str, Any]
    optimized_ir: Dict[str, Any]
    compiled_prompt: str
    output: str
    validation_report: ValidationReportModel
    warnings: List[str]
    provenance: ProvenanceModel
    cache_hit: bool = Field(False, description="Whether result came from cache")


class ValidateResponse(BaseModel):
    """Response model for /api/validate endpoint."""

    valid: bool
    errors: Optional[List[str]] = None
    repaired_ir: Optional[Dict[str, Any]] = None


class OptimizeResponse(BaseModel):
    """Response model for /api/optimize endpoint."""

    optimized_ir: Dict[str, Any]
    warnings: List[str]
    estimated_tokens: int
