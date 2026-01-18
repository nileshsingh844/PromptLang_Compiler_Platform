"""Validate endpoint route."""

import logging

from fastapi import APIRouter, HTTPException

from promptlang.api.models.requests import ValidateRequest
from promptlang.api.models.responses import ValidateResponse
from promptlang.core.ir.validator import IRValidator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["validate"])


@router.post("/validate", response_model=ValidateResponse)
async def validate(request: ValidateRequest):
    """Validate IR JSON schema."""
    try:
        validator = IRValidator()
        is_valid, errors, repaired_ir = validator.validate(request.ir_json)

        return ValidateResponse(
            valid=is_valid,
            errors=errors,
            repaired_ir=repaired_ir if not is_valid else None,
        )
    except Exception as e:
        logger.exception("Validate endpoint error")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
