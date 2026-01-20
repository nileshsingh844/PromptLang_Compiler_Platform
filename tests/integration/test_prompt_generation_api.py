import asyncio
import json
from typing import Any, AsyncGenerator, Dict, Optional

import pytest
from httpx import ASGITransport, AsyncClient

from promptlang.api.main import app
from promptlang.api.routes import generate as generate_module
from promptlang.api.routes import prompt_generation as prompt_generation_module


class _FakeCacheManager:
    def __init__(self):
        self._store: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        return self._store.get(key)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value


class _FakePromptTemplateEngine:
    def list_templates(self):
        return ["universal_cursor_prompt", "other"]


class _FakeOrchestrator:
    def __init__(self):
        self.prompt_template_engine = _FakePromptTemplateEngine()

    async def execute_prompt_generation(
        self,
        input_text: str,
        template_name: str,
        repo_url=None,
        urls=None,
        token_budget: int = 4000,
        progress_callback=None,
    ):
        if progress_callback:
            progress_callback("stage_1", {"message": "started"})
            progress_callback("stage_2", {"message": "working"})

        # Yield back to the event loop so SSE queueing behaves as expected.
        await asyncio.sleep(0)

        return {
            "job_id": "job_test_123",
            "template_name": template_name,
            "prompt": f"# Prompt\n\nInput: {input_text}\n",
            "ir": {"meta": {"intent": "prompt_generation"}},
            "knowledge_card": {"summary": "fake"},
            "enriched_context": {"best_practices": [], "examples": [], "domain_knowledge": []},
            "sources": {"repo": repo_url, "urls": urls or []},
            "provenance": {"mock": True},
        }


async def _iter_sse_events(resp) -> AsyncGenerator[Dict[str, Any], None]:
    """Parse SSE messages emitted by /api/v1/generate.

    We parse lines of the form:
    event: <name>\n
    data: <json>\n\n
    """

    event: Optional[str] = None
    data: Optional[str] = None

    async for line in resp.aiter_lines():
        if not line:
            if event and data is not None:
                payload: Any
                try:
                    payload = json.loads(data)
                except Exception:
                    payload = data
                yield {"event": event, "data": payload}
            event = None
            data = None
            continue

        if line.startswith("event:"):
            event = line[len("event:") :].strip()
        elif line.startswith("data:"):
            part = line[len("data:") :].strip()
            data = (data or "") + part


@pytest.mark.asyncio
async def test_prompt_generation_templates_and_sse_and_job_retrieval(monkeypatch):
    # Patch global orchestrator + cache manager used by prompt_generation router.
    fake_cache = _FakeCacheManager()
    fake_orchestrator = _FakeOrchestrator()
    monkeypatch.setattr(generate_module, "cache_manager", fake_cache, raising=True)
    monkeypatch.setattr(generate_module, "orchestrator", fake_orchestrator, raising=True)
    # prompt_generation.py imported these symbols by value, so patch there too.
    monkeypatch.setattr(prompt_generation_module, "cache_manager", fake_cache, raising=True)
    monkeypatch.setattr(prompt_generation_module, "orchestrator", fake_orchestrator, raising=True)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Templates
        r = await client.get("/api/v1/templates")
        assert r.status_code == 200
        assert r.json()["templates"] == ["universal_cursor_prompt", "other"]

        # SSE generate
        req = {
            "input": "Create a FastAPI REST API",
            "template_name": "universal_cursor_prompt",
            "repo_url": None,
            "urls": [],
            "token_budget": 4000,
        }

        resp = await client.post(
            "/api/v1/generate",
            json=req,
            headers={"Accept": "text/event-stream"},
        )
        assert resp.status_code == 200
        assert resp.headers.get("content-type", "").startswith("text/event-stream")

        events = []
        async for ev in _iter_sse_events(resp):
            events.append(ev)
            if ev["event"] == "result":
                break

        assert any(e["event"] == "stage_1" for e in events)
        assert any(e["event"] == "stage_2" for e in events)

        result_events = [e for e in events if e["event"] == "result"]
        assert len(result_events) == 1
        job = result_events[0]["data"]
        assert job["job_id"] == "job_test_123"
        assert "prompt" in job

        # Retrieve stored job
        r2 = await client.get(f"/api/v1/prompt/{job['job_id']}")
        assert r2.status_code == 200
        assert r2.json()["job_id"] == "job_test_123"
