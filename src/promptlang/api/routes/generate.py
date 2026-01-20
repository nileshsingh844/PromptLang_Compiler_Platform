"""Generate endpoint route."""

import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse

from promptlang.api.models.requests import GenerateRequest
from promptlang.api.models.responses import GenerateResponse, ValidationReportModel, ProvenanceModel
from promptlang.core.cache.manager import CacheManager
from promptlang.core.pipeline.orchestrator import PipelineOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["generate"])

# Global orchestrator (initialized on app startup)
orchestrator: Optional[PipelineOrchestrator] = None
cache_manager: Optional[CacheManager] = None


def init_orchestrator(cm: Optional[CacheManager] = None):
    """Initialize orchestrator (called from main)."""
    global orchestrator, cache_manager
    cache_manager = cm or CacheManager()
    orchestrator = PipelineOrchestrator(cache_manager=cache_manager)


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    """Generate prompt and scaffold from human input."""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")

    try:
        # Execute pipeline
        result = await orchestrator.execute(
            input_text=request.input,
            intent=request.intent,
            target_model=request.target_model or "oss",
            token_budget=request.token_budget or 4000,
            scaffold_mode=request.scaffold_mode or "full",
            security_level=request.security_level or "high",
            validation_mode=request.validation_mode or "strict",
        )

        # Check if result was cached (simplified check)
        cache_hit = False
        if idempotency_key:
            # Could use idempotency key for cache lookup
            pass

        # Convert validation report
        validation_report = result["validation_report"]
        validation_report_model = ValidationReportModel(**validation_report)

        # Convert provenance
        provenance = result["provenance"]
        provenance_model = ProvenanceModel(**provenance)

        response = GenerateResponse(
            status=result["status"],
            ir_json=result["ir_json"],
            optimized_ir=result["optimized_ir"],
            compiled_prompt=result["compiled_prompt"],
            output=result["output"],
            validation_report=validation_report_model,
            warnings=result.get("warnings", []),
            provenance=provenance_model,
            cache_hit=cache_hit,
            knowledge_sources_used=result.get("knowledge_sources_used", []),
            knowledge_top_k=result.get("knowledge_top_k", 0),
            rag_enabled=result.get("rag_enabled", False),
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Generate endpoint error")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
