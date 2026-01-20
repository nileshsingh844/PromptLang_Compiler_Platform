from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional


class PromptTemplateEngine:
    def __init__(self, templates_dir: Optional[Path] = None):
        self._templates_dir = templates_dir or (Path(__file__).parent / "templates")
        self._env = None

    def list_templates(self) -> List[str]:
        if not self._templates_dir.exists():
            return []
        names: List[str] = []
        for p in sorted(self._templates_dir.glob("*.j2")):
            names.append(p.stem)
        return names

    def render(
        self,
        template_name: str,
        *,
        ir: Optional[Dict[str, Any]] = None,
        knowledge_card: Optional[Dict[str, Any]] = None,
        enriched_context: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        env = self._get_env()
        template_file = f"{template_name}.j2"
        template = env.get_template(template_file)

        payload: Dict[str, Any] = {
            "ir": ir or {},
            "knowledge_card": knowledge_card or {},
            "enriched_context": enriched_context or {},
        }
        if extra:
            payload.update(extra)

        return template.render(**payload)

    def _get_env(self):
        if self._env is not None:
            return self._env

        try:
            from jinja2 import Environment, FileSystemLoader, select_autoescape  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "jinja2 is required for prompt compilation. Install 'jinja2' to enable PromptTemplateEngine."
            ) from e

        self._env = Environment(
            loader=FileSystemLoader(str(self._templates_dir)),
            autoescape=select_autoescape(enabled_extensions=()),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        return self._env
