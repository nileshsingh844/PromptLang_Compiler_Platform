"""Output validator for stage 8 with concurrent validation checks."""

import asyncio
import logging
from typing import Any, Dict, List

from promptlang.core.utils.timing import TimingContext
from promptlang.core.validator.parsers import OutputParser
from promptlang.core.validator.syntax import SyntaxValidator
from promptlang.core.validator.security import SecurityScanner
from promptlang.core.validator.quality import QualityChecker
from promptlang.core.validator.contract import ContractVerifier

logger = logging.getLogger(__name__)


class OutputValidator:
    """Validates output with concurrent checks (stage 8)."""

    def __init__(self):
        """Initialize output validator."""
        self.parser = OutputParser()
        self.syntax_validator = SyntaxValidator()
        self.security_scanner = SecurityScanner()
        self.quality_checker = QualityChecker()
        self.contract_verifier = ContractVerifier()

    async def validate(
        self,
        output: str,
        ir: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Validate output with concurrent checks.

        Args:
            output: Generated output
            ir: IR with contract

        Returns:
            Validation report
        """
        timing = TimingContext()

        # Parse output first
        with timing.stage("parser"):
            parsed_output = self.parser.parse(output)

        file_blocks = parsed_output.get("file_blocks", [])

        # Run validators concurrently
        with timing.stage("concurrent_validation"):
            syntax_task = asyncio.create_task(
                self._run_syntax_validation(file_blocks)
            )
            security_task = asyncio.create_task(
                self._run_security_scan(file_blocks)
            )
            quality_task = asyncio.create_task(
                self._run_quality_check(file_blocks)
            )

            # Wait for all concurrent tasks
            syntax_valid, syntax_findings = await syntax_task
            security_findings = await security_task
            quality_findings = await quality_task

        # Contract verification (depends on parsed output)
        with timing.stage("contract_verification"):
            contract_compliant, compliance_summary = self.contract_verifier.verify(
                parsed_output, ir
            )

        # Merge findings
        all_findings = syntax_findings + security_findings + quality_findings

        # Determine overall status
        has_errors = any(f.get("severity") == "error" for f in all_findings)
        has_security_errors = any(
            f.get("type") == "security" and f.get("severity") == "error"
            for f in all_findings
        )

        # High security + strict mode → contract violations => BLOCKED
        security_level = ir.get("quality_checks", {}).get("security_level", "low")
        validation_level = ir.get("quality_checks", {}).get("validation_level", "progressive")

        if has_security_errors and security_level == "high":
            status = "blocked"
        elif not contract_compliant and validation_level == "strict":
            status = "blocked"
        elif has_errors:
            status = "error"
        elif all_findings:
            status = "warning"
        else:
            status = "success"

        # Build validation report
        report = {
            "status": status,
            "parallel": True,
            "stage_timings_ms": timing.get_timings(),
            "findings": all_findings,
            "contract_compliance": compliance_summary,
            "summary": {
                "total_findings": len(all_findings),
                "errors": len([f for f in all_findings if f.get("severity") == "error"]),
                "warnings": len([f for f in all_findings if f.get("severity") == "warning"]),
                "syntax_valid": syntax_valid,
                "contract_compliant": contract_compliant,
            },
        }

        logger.info(f"Output validation complete: status={status}, findings={len(all_findings)}")
        return report

    async def _run_syntax_validation(
        self, file_blocks: List[Dict[str, str]]
    ) -> tuple[bool, List[Dict[str, Any]]]:
        """Run syntax validation asynchronously."""
        # Run in thread pool since it's CPU-bound
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.syntax_validator.validate, file_blocks
        )

    async def _run_security_scan(
        self, file_blocks: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """Run security scan asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.security_scanner.scan, file_blocks
        )

    async def _run_quality_check(
        self, file_blocks: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """Run quality check asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.quality_checker.check, file_blocks
        )
