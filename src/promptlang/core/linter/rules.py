"""IR linter with deterministic rules."""

import logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


class IRLinter:
    """Deterministic IR linter for stage 4."""

    def __init__(self):
        """Initialize linter."""
        self.rules = self._load_rules()

    def _load_rules(self) -> List[Callable[[Dict[str, Any]], List[Dict[str, str]]]]:
        """Load linting rules."""
        return [
            self._check_required_fields,
            self._check_constraints_validity,
            self._check_output_contract_completeness,
            self._check_token_budget_reasonableness,
        ]

    def lint(self, ir_data: Dict[str, Any]) -> tuple[bool, List[Dict[str, str]]]:
        """Lint IR and return findings.

        Returns:
            Tuple of (is_valid, findings_list)
        """
        findings: List[Dict[str, str]] = []

        for rule in self.rules:
            try:
                rule_findings = rule(ir_data)
                findings.extend(rule_findings)
            except Exception as e:
                logger.warning(f"Lint rule failed: {e}")
                findings.append({
                    "severity": "warning",
                    "rule": rule.__name__,
                    "message": f"Rule check failed: {e}",
                })

        is_valid = all(f.get("severity") != "error" for f in findings)
        return is_valid, findings

    def _check_required_fields(self, ir: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check required fields are present."""
        findings = []
        required = ["meta", "task", "context", "constraints", "output_contract", "quality_checks"]

        for field in required:
            if field not in ir:
                findings.append({
                    "severity": "error",
                    "rule": "required_fields",
                    "message": f"Missing required field: {field}",
                })

        return findings

    def _check_constraints_validity(self, ir: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check constraints are valid."""
        findings = []
        constraints = ir.get("constraints", {})

        if "must_avoid" not in constraints:
            findings.append({
                "severity": "error",
                "rule": "constraints_validity",
                "message": "constraints.must_avoid is required",
            })

        token_budget = constraints.get("token_budget")
        if token_budget is not None:
            if not isinstance(token_budget, int) or token_budget < 100:
                findings.append({
                    "severity": "error",
                    "rule": "constraints_validity",
                    "message": "token_budget must be integer >= 100",
                })

        return findings

    def _check_output_contract_completeness(self, ir: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check output contract is complete."""
        findings = []
        contract = ir.get("output_contract", {})

        if "required_sections" not in contract:
            findings.append({
                "severity": "error",
                "rule": "output_contract_completeness",
                "message": "output_contract.required_sections is required",
            })

        if "file_block_format" not in contract:
            findings.append({
                "severity": "error",
                "rule": "output_contract_completeness",
                "message": "output_contract.file_block_format is required",
            })

        return findings

    def _check_token_budget_reasonableness(self, ir: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check token budget is reasonable."""
        findings = []
        constraints = ir.get("constraints", {})
        token_budget = constraints.get("token_budget")

        if token_budget is not None:
            if token_budget > 100000:
                findings.append({
                    "severity": "warning",
                    "rule": "token_budget_reasonableness",
                    "message": f"token_budget {token_budget} is very large",
                })

        return findings
