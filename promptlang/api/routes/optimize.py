"""Optimize endpoint route."""

import logging

from fastapi import APIRouter, HTTPException

from promptlang.api.models.requests import OptimizeRequest
from promptlang.api.models.responses import OptimizeResponse
from promptlang.core.optimizer.token_optimizer import TokenOptimizer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["optimize"])


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize(request: OptimizeRequest):
    """Optimize IR JSON for token budget."""
    try:
        optimizer = TokenOptimizer()
        optimized_ir, warnings = optimizer.optimize(
            request.ir_json,
            token_budget=request.token_budget or 4000,
            intent=request.intent or "scaffold",
        )

        # Estimate tokens
        import json
        estimated_tokens = len(json.dumps(optimized_ir, separators=(",", ":"))) // 4

        return OptimizeResponse(
            optimized_ir=optimized_ir,
            warnings=warnings,
            estimated_tokens=estimated_tokens,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Optimize endpoint error")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
