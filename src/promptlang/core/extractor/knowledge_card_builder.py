from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from .github_parser import GitHubContent
from .content_scraper import ScrapedContent


class KnowledgeCard(BaseModel):
    # Core Information
    project_name: str
    project_type: str
    problem: str
    solution: str

    # Technical Details
    features: List[str]
    tech_stack: Dict[str, str]
    architecture_style: str

    # Context
    domain: str
    target_users: str
    use_cases: List[str]

    # Additional Context
    constraints: List[str]
    integrations: List[str]
    deployment_target: str


class KnowledgeCardBuilder:
    def __init__(self, llm_manager: Any = None):
        # llm_manager is expected to provide an async method `generate_with_fallback(...)`
        # We keep it optional so unit tests and offline runs can still function.
        self.llm = llm_manager

    async def build_from_github(self, github_content: GitHubContent) -> KnowledgeCard:
        cache_path = self._card_cache_path(github_content.repo_metadata.get("html_url", ""))
        cached = self._read_cache(cache_path)
        if cached is not None:
            return KnowledgeCard.model_validate(cached)

        if self.llm is None:
            card = self._heuristic_from_github(github_content)
            self._write_cache(cache_path, card.dict())
            return card

        prompt = (
            "Analyze this GitHub repository and create a structured knowledge card.\n\n"
            "README Content:\n"
            f"{github_content.readme}\n\n"
            f"Repo Description: {github_content.repo_metadata.get('description','')}\n"
            f"Repo Topics: {github_content.repo_metadata.get('topics', [])}\n"
            f"File Structure: {json.dumps(github_content.file_structure)[:4000]}\n"
            f"Docs Files: {list(github_content.docs.keys())[:20]}\n\n"
            "Return as JSON matching this schema keys:\n"
            "project_name, project_type, problem, solution, features, tech_stack, architecture_style, "
            "domain, target_users, use_cases, constraints, integrations, deployment_target.\n"
        )

        resp = await self.llm.generate_with_fallback(
            prompt=prompt,
            system_prompt="You are a software architect. Return only JSON.",
            temperature=0.2,
            max_tokens=500,
        )

        payload = self._safe_json(resp.content)
        card = self._fill_defaults(payload)
        self._write_cache(cache_path, card.dict())
        return card

    async def build_from_text(self, user_input: str) -> KnowledgeCard:
        cache_path = self._card_cache_path(user_input)
        cached = self._read_cache(cache_path)
        if cached is not None:
            return KnowledgeCard.model_validate(cached)

        if self.llm is None:
            card = self._heuristic_from_text(user_input)
            self._write_cache(cache_path, card.dict())
            return card

        prompt = (
            "Build a structured knowledge card from this project description.\n\n"
            f"User input:\n{user_input}\n\n"
            "Return only JSON matching keys:\n"
            "project_name, project_type, problem, solution, features, tech_stack, architecture_style, "
            "domain, target_users, use_cases, constraints, integrations, deployment_target.\n"
        )

        resp = await self.llm.generate_with_fallback(
            prompt=prompt,
            system_prompt="You are a software architect. Return only JSON.",
            temperature=0.2,
            max_tokens=500,
        )

        payload = self._safe_json(resp.content)
        card = self._fill_defaults(payload)
        self._write_cache(cache_path, card.dict())
        return card

    async def build_from_url(self, scraped_content: ScrapedContent) -> KnowledgeCard:
        cache_path = self._card_cache_path(scraped_content.metadata.get("url", ""))
        cached = self._read_cache(cache_path)
        if cached is not None:
            return KnowledgeCard.model_validate(cached)

        if self.llm is None:
            card = self._heuristic_from_text(scraped_content.main_content[:2000])
            self._write_cache(cache_path, card.dict())
            return card

        prompt = (
            "Analyze this web content and create a structured knowledge card.\n\n"
            f"Title: {scraped_content.title}\n"
            f"Content type: {scraped_content.content_type}\n\n"
            f"Main content:\n{scraped_content.main_content[:6000]}\n\n"
            "Return only JSON matching keys:\n"
            "project_name, project_type, problem, solution, features, tech_stack, architecture_style, "
            "domain, target_users, use_cases, constraints, integrations, deployment_target.\n"
        )

        resp = await self.llm.generate_with_fallback(
            prompt=prompt,
            system_prompt="You are a software architect. Return only JSON.",
            temperature=0.2,
            max_tokens=500,
        )

        payload = self._safe_json(resp.content)
        card = self._fill_defaults(payload)
        self._write_cache(cache_path, card.dict())
        return card

    def _fill_defaults(self, partial_card: dict) -> KnowledgeCard:
        d = partial_card or {}

        def as_list(v: Any) -> List[str]:
            if v is None:
                return []
            if isinstance(v, list):
                return [str(x) for x in v if str(x).strip()]
            return [str(v)]

        def as_dict(v: Any) -> Dict[str, str]:
            if isinstance(v, dict):
                return {str(k): str(val) for k, val in v.items()}
            return {}

        card = {
            "project_name": str(d.get("project_name") or "project"),
            "project_type": str(d.get("project_type") or "web_app"),
            "problem": str(d.get("problem") or "Define the user problem and goals."),
            "solution": str(d.get("solution") or "Provide a high-level solution approach."),
            "features": as_list(d.get("features")) or ["Core functionality"],
            "tech_stack": as_dict(d.get("tech_stack")) or {"language": "determine", "framework": "determine"},
            "architecture_style": str(d.get("architecture_style") or "monolith"),
            "domain": str(d.get("domain") or "general"),
            "target_users": str(d.get("target_users") or "end users"),
            "use_cases": as_list(d.get("use_cases")) or ["Primary workflow"],
            "constraints": as_list(d.get("constraints")),
            "integrations": as_list(d.get("integrations")),
            "deployment_target": str(d.get("deployment_target") or "cloud"),
        }

        return KnowledgeCard(**card)

    def _heuristic_from_text(self, text: str) -> KnowledgeCard:
        # Minimal heuristic for offline mode.
        name = "project"
        lowered = (text or "").lower()
        if "api" in lowered:
            ptype = "api"
        elif "cli" in lowered:
            ptype = "cli_tool"
        elif "library" in lowered or "sdk" in lowered:
            ptype = "library"
        else:
            ptype = "web_app"

        return KnowledgeCard(
            project_name=name,
            project_type=ptype,
            problem=text.strip()[:400] or "Define the problem.",
            solution="Build a production-ready system with best practices.",
            features=["Core feature set"],
            tech_stack={"language": "determine", "framework": "determine"},
            architecture_style="monolith",
            domain="general",
            target_users="end users",
            use_cases=["Primary workflow"],
            constraints=[],
            integrations=[],
            deployment_target="cloud",
        )

    def _heuristic_from_github(self, content: GitHubContent) -> KnowledgeCard:
        desc = content.repo_metadata.get("description") or ""
        text = (desc + "\n\n" + (content.readme or "")).strip()
        card = self._heuristic_from_text(text)
        # Improve project name if available
        full_name = content.repo_metadata.get("full_name")
        if full_name:
            card.project_name = str(full_name).split("/")[-1]
        return card

    def _card_cache_path(self, key: str) -> Path:
        h = hashlib.sha256((key or "").encode("utf-8")).hexdigest()[:16]
        base = Path("knowledge/extracted/cards")
        base.mkdir(parents=True, exist_ok=True)
        return base / f"card_{h}.json"

    def _read_cache(self, path: Path) -> Optional[dict]:
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _write_cache(self, path: Path, payload: dict) -> None:
        try:
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            return

    def _safe_json(self, text: str) -> dict:
        t = (text or "").strip()
        # Strip markdown fences
        if "```" in t:
            start = t.find("{")
            end = t.rfind("}")
            if start != -1 and end != -1 and end > start:
                t = t[start : end + 1]
        try:
            return json.loads(t)
        except Exception:
            return {}
