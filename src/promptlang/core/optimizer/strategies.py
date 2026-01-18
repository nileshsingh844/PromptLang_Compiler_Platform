"""Token optimization strategies."""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class OptimizationStrategy:
    """Base class for optimization strategies."""

    def optimize(self, ir: Dict[str, Any], target_budget: int) -> Dict[str, Any]:
        """Optimize IR to fit within token budget."""
        raise NotImplementedError


class SemanticChunkingStrategy(OptimizationStrategy):
    """Chunk IR into semantic sections for compression."""

    def optimize(self, ir: Dict[str, Any], target_budget: int) -> Dict[str, Any]:
        """Chunk IR into semantic sections."""
        # This is a placeholder - in production would estimate tokens and chunk
        optimized = ir.copy()
        optimized.setdefault("optimization", {})["semantic_chunks"] = [
            "task",
            "constraints",
            "contract",
            "examples",
            "verification",
        ]
        return optimized


class DeduplicationStrategy(OptimizationStrategy):
    """Remove duplicate entities and repeated mentions."""

    def optimize(self, ir: Dict[str, Any], target_budget: int) -> Dict[str, Any]:
        """Remove duplicates from IR."""
        optimized = ir.copy()

        # Deduplicate stack mentions in context
        context = optimized.get("context", {})
        stack = context.get("stack", {})
        if stack:
            # Ensure no duplicate entries
            for key in stack:
                if isinstance(stack[key], list):
                    stack[key] = list(dict.fromkeys(stack[key]))  # Preserve order

        return optimized


class PriorityCompressionStrategy(OptimizationStrategy):
    """Compress based on priority - never compress critical fields."""

    NEVER_COMPRESS = [
        "output_contract",
        "must_avoid",
        "security_preserve",
        "required_sections",
        "required_files",
    ]

    def optimize(self, ir: Dict[str, Any], target_budget: int) -> Dict[str, Any]:
        """Compress IR prioritizing non-critical fields."""
        optimized = ir.copy()

        # Reduce examples/narrative if present
        task = optimized.get("task", {})
        description = task.get("description", "")

        # If description is very long, we could truncate (but be careful)
        # For MVP, we'll just mark it as compressible
        optimized.setdefault("optimization", {})["compressed_fields"] = [
            "task.description",
            "context.stack",
        ]

        return optimized
