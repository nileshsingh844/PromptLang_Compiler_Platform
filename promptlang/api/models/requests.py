"""Request models for API endpoints."""

from typing import List, Optional

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Request model for /api/generate endpoint."""

    input: str = Field(..., description="Human input text")
    intent: Optional[str] = Field(None, description="Explicit intent (scaffold/debug/refactor/explain/devops)")
    target_model: Optional[str] = Field("oss", description="Target model")
    token_budget: Optional[int] = Field(4000, ge=100, le=100000, description="Token budget")
    scaffold_mode: Optional[str] = Field("full", pattern="^(quick|full)$", description="Scaffold mode")
    security_level: Optional[str] = Field("high", pattern="^(low|high)$", description="Security level")
    validation_mode: Optional[str] = Field("strict", pattern="^(strict|progressive)$", description="Validation mode")


class ValidateRequest(BaseModel):
    """Request model for /api/validate endpoint."""

    ir_json: dict = Field(..., description="IR JSON to validate")


class OptimizeRequest(BaseModel):
    """Request model for /api/optimize endpoint."""

    ir_json: dict = Field(..., description="IR JSON to optimize")
    token_budget: Optional[int] = Field(4000, ge=100, le=100000, description="Token budget")
    intent: Optional[str] = Field("scaffold", description="Intent for adaptive budgeting")
