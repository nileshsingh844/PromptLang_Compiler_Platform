"""Dialect compiler for stage 6 - compiles optimized IR to model-specific format."""

import json
import logging
from typing import Any, Dict, List, Optional

from promptlang.core.compiler.dialects.claude import ClaudeDialectCompiler
from promptlang.core.compiler.dialects.gpt import GPTDialectCompiler
from promptlang.core.compiler.dialects.oss import OSSDialectCompiler

logger = logging.getLogger(__name__)


class DialectCompiler:
    """Compiles optimized IR to target model dialect."""

    def __init__(self):
        """Initialize dialect compiler."""
        self.compilers = {
            "claude": ClaudeDialectCompiler(),
            "gpt": GPTDialectCompiler(),
            "oss": OSSDialectCompiler(),
        }

    def compile(
        self,
        ir: Dict[str, Any],
        target_model: str = "oss",
        retrieved_knowledge: Optional[List[Dict[str, Any]]] = None,
        token_budget: Optional[int] = None,
    ) -> str:
        """Compile IR to target dialect.

        Args:
            ir: Optimized IR
            target_model: Target model (claude/gpt/oss)

        Returns:
            Compiled prompt string
        """
        # Normalize target_model
        target_lower = target_model.lower()

        if target_lower.startswith("claude"):
            dialect = "claude"
        elif target_lower.startswith("gpt") or target_lower.startswith("openai"):
            dialect = "gpt"
        else:
            dialect = "oss"  # Default

        compiler = self.compilers.get(dialect, self.compilers["oss"])

        logger.info(f"Compiling to {dialect} dialect for model {target_model}")

        compiled_prompt = compiler.compile(ir)

        if not retrieved_knowledge:
            return compiled_prompt

        injected = self._inject_reference_knowledge(
            compiled_prompt=compiled_prompt,
            dialect=dialect,
            retrieved_knowledge=retrieved_knowledge,
            token_budget=token_budget,
        )
        return injected

    def _inject_reference_knowledge(
        self,
        compiled_prompt: str,
        dialect: str,
        retrieved_knowledge: List[Dict[str, Any]],
        token_budget: Optional[int],
    ) -> str:
        # Normalize, dedupe by URL, keep best scored
        by_url: Dict[str, Dict[str, Any]] = {}
        for item in retrieved_knowledge:
            url = (item.get("url") or "").strip()
            if not url:
                continue
            prev = by_url.get(url)
            if prev is None or float(item.get("score", 0.0)) > float(prev.get("score", 0.0)):
                by_url[url] = item

        items = list(by_url.values())
        items.sort(key=lambda x: float(x.get("score", 0.0)), reverse=True)
        items = items[:6]

        def make_block(chunks: List[Dict[str, Any]]) -> str:
            lines = ["REFERENCE KNOWLEDGE (retrieved from engineering docs):"]
            for c in chunks:
                text = (c.get("text") or "").strip()
                if len(text) > 900:
                    text = text[:900].rstrip() + "..."
                lines.append(f"- {text}")
                lines.append(f"Source: {c.get('url')}")
            return "\n".join(lines).strip() + "\n"

        # If token budget is exceeded, drop lowest scored chunks first.
        if token_budget is not None and token_budget > 0:
            # crude token estimate: chars/4
            while items:
                candidate = self._apply_injection(compiled_prompt, dialect, make_block(items))
                if (len(candidate) // 4) <= token_budget:
                    return candidate
                items.pop()  # remove lowest score (end)
            return compiled_prompt

        return self._apply_injection(compiled_prompt, dialect, make_block(items))

    def _apply_injection(self, compiled_prompt: str, dialect: str, knowledge_block: str) -> str:
        if dialect == "gpt":
            try:
                data = json.loads(compiled_prompt)
                messages = data.get("messages", [])
                # Insert after the first system message if present; else prepend.
                insert_at = 1 if messages and messages[0].get("role") == "system" else 0
                messages.insert(
                    insert_at,
                    {"role": "system", "content": knowledge_block},
                )
                data["messages"] = messages
                return json.dumps(data, indent=2)
            except Exception:
                # Fallback: prepend plain text
                return knowledge_block + "\n" + compiled_prompt

        # OSS / Claude are plain string prompts
        return knowledge_block + "\n" + compiled_prompt
