"""Pipeline orchestrator coordinating stages 0-8 with parallelism."""

import asyncio
import hashlib
import logging
import os
import uuid
from typing import Any, Dict, List, Optional

import structlog

from promptlang.core.cache.manager import CacheManager
from promptlang.core.clarification.engine import ClarificationEngine
from promptlang.core.compiler.dialect_compiler import DialectCompiler
from promptlang.core.generator.scaffold import ScaffoldGenerator
from promptlang.core.intent.router import IntentRouter
from promptlang.core.ir.validator import IRValidator
from promptlang.core.linter.rules import IRLinter
from promptlang.core.optimizer.token_optimizer import TokenOptimizer
from promptlang.core.translator.ir_builder import IRBuilder
from promptlang.core.utils.hashing import generate_cache_key, hash_ir
from promptlang.core.utils.timing import TimingContext
from promptlang.core.validator.output_validator import OutputValidator

logger = structlog.get_logger()


class PipelineOrchestrator:
    """Orchestrates the complete pipeline stages 0-8."""

    def __init__(
        self,
        cache_manager: Optional[CacheManager] = None,
        llm_provider: Optional[str] = None,
    ):
        """Initialize orchestrator.

        Args:
            cache_manager: Cache manager instance
            llm_provider: LLM provider name (default: mock)
        """
        self.cache_manager = cache_manager or CacheManager()
        self.llm_provider_name = llm_provider or os.getenv("LLM_PROVIDER", "mock")

        # Initialize stage components
        self.intent_router = IntentRouter()
        self.clarification_engine = ClarificationEngine()
        self.ir_builder = IRBuilder()
        self.ir_validator = IRValidator()
        self.linter = IRLinter()
        self.token_optimizer = TokenOptimizer()
        self.dialect_compiler = DialectCompiler()
        self.scaffold_generator = ScaffoldGenerator()
        self.output_validator = OutputValidator()

    async def execute(
        self,
        input_text: str,
        intent: Optional[str] = None,
        target_model: str = "oss",
        token_budget: int = 4000,
        scaffold_mode: str = "full",
        security_level: str = "high",
        validation_mode: str = "strict",
    ) -> Dict[str, Any]:
        """Execute full pipeline stages 0-8.

        Args:
            input_text: Human input
            intent: Explicit intent (optional)
            target_model: Target model
            token_budget: Token budget
            scaffold_mode: Scaffold mode (quick/full)
            security_level: Security level (low/high)
            validation_mode: Validation mode (strict/progressive)

        Returns:
            Complete pipeline result
        """
        request_id = str(uuid.uuid4())
        timing = TimingContext()

        # Generate build hash
        build_hash = hashlib.sha256(
            f"{os.getenv('BUILD_HASH', 'dev')}".encode()
        ).hexdigest()[:8]

        logger.info("Pipeline execution started", request_id=request_id)

        # Stage 0: Input normalization (DTO creation)
        with timing.stage("stage_0_input"):
            normalized_input = {
                "input": input_text,
                "intent": intent,
                "target_model": target_model,
                "token_budget": token_budget,
                "scaffold_mode": scaffold_mode,
                "security_level": security_level,
                "validation_mode": validation_mode,
            }

        # Generate cache key
        # First we need IR to generate cache key, so we'll generate it after stage 2

        # Stage 1: Intent routing
        with timing.stage("stage_1_intent"):
            detected_intent = self.intent_router.route(input_text, explicit_intent=intent)

        # Stage 1.5: Clarification
        with timing.stage("stage_1_5_clarification"):
            questions, assumptions = self.clarification_engine.clarify(
                input_text, detected_intent
            )
            context = assumptions

        # Stage 2: IR Translation
        with timing.stage("stage_2_translate"):
            ir = await self.ir_builder.build(
                input_text, explicit_intent=detected_intent, context=context
            )

        # Generate cache key now that we have IR
        ir_hash = hash_ir(ir)
        schema_version = ir.get("meta", {}).get("schema_version", "2.1.0")
        compiler_version = "0.1.0"
        cache_key = generate_cache_key(ir_hash, schema_version, compiler_version, target_model)

        # Check cache
        cached_result = self.cache_manager.get(cache_key)
        if cached_result:
            logger.info("Cache hit", request_id=request_id, cache_key=cache_key[:16])
            return cached_result

        # Stage 3: Schema Validation
        with timing.stage("stage_3_validate"):
            is_valid, errors, ir = self.ir_validator.validate(ir)
            if not is_valid:
                raise ValueError(f"IR validation failed: {errors}")

        # Stage 4 & 5: Parallel execution (Linter + Optimizer)
        with timing.stage("stage_4_5_parallel"):
            linter_task = asyncio.create_task(self._run_linter(ir))
            optimizer_task = asyncio.create_task(self._run_optimizer(ir, token_budget, detected_intent))

            # Wait for both
            linter_valid, linter_findings = await linter_task
            optimized_ir, optimization_warnings = await optimizer_task

            if not linter_valid:
                logger.warning("Linter found issues", findings=linter_findings)

        # Stage 6: Dialect Compilation
        with timing.stage("stage_6_compile"):
            compiled_prompt = self.dialect_compiler.compile(optimized_ir, target_model=target_model)

        # Stage 7: Scaffold Generation
        with timing.stage("stage_7_generate"):
            output = await self.scaffold_generator.generate(
                compiled_prompt, optimized_ir, scaffold_mode=scaffold_mode
            )

        # Stage 8: Output Validation (concurrent checks)
        with timing.stage("stage_8_validate"):
            validation_report = await self.output_validator.validate(output, optimized_ir)

        # Build provenance
        provenance = {
            "request_id": request_id,
            "build_hash": build_hash,
            "stage_timings_ms": timing.get_timings(),
            "token_usage": {
                "estimated": self._estimate_tokens(optimized_ir),
                "budget": token_budget,
            },
            "cost_metadata": {},
            "transformation_chain": [
                "input_normalization",
                "intent_routing",
                "clarification",
                "ir_translation",
                "schema_validation",
                "ir_linting",
                "token_optimization",
                "dialect_compilation",
                "scaffold_generation",
                "output_validation",
            ],
        }

        # Build result
        result = {
            "status": validation_report.get("status", "success"),
            "ir_json": ir,
            "optimized_ir": optimized_ir,
            "compiled_prompt": compiled_prompt,
            "output": output,
            "validation_report": validation_report,
            "warnings": optimization_warnings + linter_findings,
            "provenance": provenance,
        }

        # Cache result
        self.cache_manager.set(cache_key, result)

        logger.info("Pipeline execution complete", request_id=request_id, status=result["status"])
        return result

    async def _run_linter(self, ir: Dict[str, Any]) -> tuple[bool, List[Dict[str, str]]]:
        """Run linter asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.linter.lint, ir)

    async def _run_optimizer(
        self, ir: Dict[str, Any], token_budget: int, intent: str
    ) -> tuple[Dict[str, Any], List[str]]:
        """Run token optimizer asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.token_optimizer.optimize, ir, token_budget, intent
        )

    def _estimate_tokens(self, ir: Dict[str, Any]) -> int:
        """Estimate token count."""
        import json
        json_str = json.dumps(ir, separators=(",", ":"))
        return len(json_str) // 4
