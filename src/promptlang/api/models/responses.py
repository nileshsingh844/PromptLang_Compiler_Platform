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
    knowledge_sources_used: List[str] = Field(
        default_factory=list,
        description="Source URLs used for RAG context injection",
    )
    knowledge_top_k: int = Field(0, description="Configured top_k used for retrieval")
    rag_enabled: bool = Field(False, description="Whether RAG retrieval/injection was enabled")


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


class PromptTemplatesResponse(BaseModel):
    """Response model for /api/v1/templates endpoint."""

    templates: List[str]


class PromptPreviewResponse(BaseModel):
    """Response model for /api/v1/preview endpoint."""

    template_name: str
    prompt: str


class PromptJobResponse(BaseModel):
    """Response model for /api/v1/prompt/{job_id} endpoint."""

    job_id: str
    template_name: str
    prompt: str
    ir: Dict[str, Any]
    knowledge_card: Dict[str, Any]
    enriched_context: Dict[str, Any]
    sources: Dict[str, Any]
    provenance: Dict[str, Any]


class PromptGenerateResponse(PromptJobResponse):
    """Response model emitted as an SSE 'result' event payload."""
    pass
