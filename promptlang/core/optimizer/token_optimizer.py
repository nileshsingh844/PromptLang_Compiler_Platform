"""Token optimizer for stage 5."""

import hashlib
import logging
from typing import Any, Dict, List

from promptlang.core.optimizer.strategies import (
    SemanticChunkingStrategy,
    DeduplicationStrategy,
    PriorityCompressionStrategy,
)

logger = logging.getLogger(__name__)


class TokenOptimizer:
    """Token optimizer implementing semantic chunking, deduplication, and priority compression."""

    def __init__(self):
        """Initialize token optimizer."""
        self.strategies = [
            SemanticChunkingStrategy(),
            DeduplicationStrategy(),
            PriorityCompressionStrategy(),
        ]

    def optimize(
        self,
        ir_data: Dict[str, Any],
        token_budget: int,
        intent: str = "scaffold",
    ) -> tuple[Dict[str, Any], List[str]]:
        """Optimize IR to fit token budget.

        Args:
            ir_data: Input IR
            token_budget: Target token budget
            intent: Intent for adaptive budgeting

        Returns:
            Tuple of (optimized_ir, warnings_list)
        """
        warnings: List[str] = []

        # Get adaptive budget by intent
        adaptive_budget = self._get_adaptive_budget(token_budget, intent)

        optimized = ir_data.copy()

        # Apply optimization strategies
        for strategy in self.strategies:
            try:
                optimized = strategy.optimize(optimized, adaptive_budget)
            except Exception as e:
                logger.warning(f"Optimization strategy failed: {e}")
                warnings.append(f"Strategy {strategy.__class__.__name__} failed: {e}")

        # Generate semantic fingerprint
        fingerprint = self._generate_semantic_fingerprint(optimized)

        # Store optimization metadata
        optimization_meta = optimized.setdefault("optimization", {})
        optimization_meta["semantic_fingerprint"] = fingerprint
        optimization_meta["priority_weights"] = self._get_priority_weights(intent)

        # Estimate token count (rough approximation)
        estimated_tokens = self._estimate_tokens(optimized)

        if estimated_tokens > adaptive_budget:
            warnings.append(f"Estimated tokens ({estimated_tokens}) exceed budget ({adaptive_budget})")
            if estimated_tokens > adaptive_budget * 1.5:
                raise ValueError("Scope too large, split into sub-tasks")

        logger.info(f"IR optimized: estimated {estimated_tokens} tokens (budget: {adaptive_budget})")
        return optimized, warnings

    def _get_adaptive_budget(self, base_budget: int, intent: str) -> int:
        """Get adaptive budget based on intent."""
        # Intent-based budget multipliers
        multipliers = {
            "scaffold": 1.2,  # Highest
            "devops": 1.1,  # High
            "debug": 1.0,
            "refactor": 1.0,
            "explain": 0.9,  # Lowest
        }
        multiplier = multipliers.get(intent, 1.0)
        return int(base_budget * multiplier)

    def _generate_semantic_fingerprint(self, ir: Dict[str, Any]) -> str:
        """Generate semantic fingerprint for IR."""
        # Use key semantic fields
        key_fields = {
            "intent": ir.get("meta", {}).get("intent"),
            "task_scope": ir.get("task", {}).get("scope"),
            "required_sections": ir.get("output_contract", {}).get("required_sections", []),
        }
        import json
        key_str = json.dumps(key_fields, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]

    def _get_priority_weights(self, intent: str) -> Dict[str, float]:
        """Get priority weights for compression by intent."""
        base_weights = {
            "output_contract": 1.0,  # Never compress
            "must_avoid": 1.0,  # Never compress
            "security_constraints": 1.0,  # Never compress
            "task_description": 0.8,
            "context": 0.6,
            "examples": 0.4,
        }
        return base_weights

    def _estimate_tokens(self, ir: Dict[str, Any]) -> int:
        """Rough token estimation (characters / 4 approximation)."""
        import json
        json_str = json.dumps(ir, separators=(",", ":"))
        return len(json_str) // 4  # Rough approximation
