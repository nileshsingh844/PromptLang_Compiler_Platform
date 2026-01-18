"""Dialect compiler for stage 6 - compiles optimized IR to model-specific format."""

import logging
from typing import Any, Dict

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
        return compiler.compile(ir)
