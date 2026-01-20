import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

from promptlang.api.models.requests import PromptGenerateRequest, PromptPreviewRequest
from promptlang.api.models.responses import (
    PromptGenerateResponse,
    PromptJobResponse,
    PromptPreviewResponse,
    PromptTemplatesResponse,
)
from promptlang.api.routes import generate as generate_routes

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["prompt_generation"])


def _sse(event: str, data: Dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.get("/templates", response_model=PromptTemplatesResponse)
async def list_templates():
    if not generate_routes.orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    return PromptTemplatesResponse(
        templates=generate_routes.orchestrator.prompt_template_engine.list_templates()
    )


@router.get("/prompt/{job_id}", response_model=PromptJobResponse)
async def get_prompt(job_id: str):
    if not generate_routes.cache_manager:
        raise HTTPException(status_code=500, detail="Cache manager not initialized")
    item = generate_routes.cache_manager.get(f"prompt_job:{job_id}")
    if not item:
        raise HTTPException(status_code=404, detail="Prompt job not found")
    return PromptJobResponse(**item)


@router.get("/download/{job_id}")
async def download_prompt(job_id: str):
    if not generate_routes.cache_manager:
        raise HTTPException(status_code=500, detail="Cache manager not initialized")
    item = generate_routes.cache_manager.get(f"prompt_job:{job_id}")
    if not item:
        raise HTTPException(status_code=404, detail="Prompt job not found")

    prompt = item.get("prompt", "")
    headers = {"Content-Disposition": f"attachment; filename=prompt_{job_id}.md"}
    return StreamingResponse(iter([prompt]), media_type="text/markdown", headers=headers)


@router.post("/preview", response_model=PromptPreviewResponse)
async def preview(request: PromptPreviewRequest):
    if not generate_routes.orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")

    result = await generate_routes.orchestrator.execute_prompt_generation(
        input_text=request.input,
        template_name=request.template_name or "universal_cursor_prompt",
        repo_url=request.repo_url,
        urls=request.urls,
        token_budget=request.token_budget or 4000,
    )
    return PromptPreviewResponse(
        template_name=result.get("template_name", request.template_name or "universal_cursor_prompt"),
        prompt=result.get("prompt", ""),
    )


@router.post("/generate")
async def generate_sse(request: PromptGenerateRequest):
    if not generate_routes.orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    if not generate_routes.cache_manager:
        raise HTTPException(status_code=500, detail="Cache manager not initialized")

    q: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
    done = asyncio.Event()

    def progress(stage: str, data: Dict[str, Any]) -> None:
        try:
            q.put_nowait({"stage": stage, "data": data})
        except Exception:
            return

    async def run_job() -> None:
        try:
            result = await generate_routes.orchestrator.execute_prompt_generation(
                input_text=request.input,
                template_name=request.template_name or "universal_cursor_prompt",
                repo_url=request.repo_url,
                urls=request.urls,
                token_budget=request.token_budget or 4000,
                progress_callback=progress,
            )
            generate_routes.cache_manager.set(f"prompt_job:{result['job_id']}", result)
            q.put_nowait({"stage": "result", "data": PromptGenerateResponse(**result).dict()})
        except Exception as e:
            q.put_nowait({"stage": "error", "data": {"message": str(e)}})
        finally:
            done.set()

    async def stream() -> AsyncGenerator[str, None]:
        task = asyncio.create_task(run_job())
        try:
            while True:
                if done.is_set() and q.empty():
                    break
                try:
                    msg = await asyncio.wait_for(q.get(), timeout=0.25)
                except asyncio.TimeoutError:
                    continue
                yield _sse(msg["stage"], msg["data"])
        finally:
            if not task.done():
                task.cancel()

    return StreamingResponse(stream(), media_type="text/event-stream")
