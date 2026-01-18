"""IR validator with retry and repair logic."""

import logging
from typing import Any, Dict, Optional

from promptlang.core.ir.schema_loader import validate_ir

logger = logging.getLogger(__name__)


class IRValidator:
    """IR schema validator with retry and basic repair."""

    def __init__(self, schema_version: str = "2.1", max_retries: int = 3):
        """Initialize validator.

        Args:
            schema_version: Schema version to validate against
            max_retries: Maximum retry attempts
        """
        self.schema_version = schema_version
        self.max_retries = max_retries

    def validate(
        self, ir_data: Dict[str, Any], attempt: int = 0
    ) -> tuple[bool, Optional[list[str]], Dict[str, Any]]:
        """Validate IR with retry and basic repair.

        Returns:
            Tuple of (is_valid, errors, repaired_ir)
        """
        is_valid, errors = validate_ir(ir_data, version=self.schema_version)

        if is_valid:
            return True, None, ir_data

        if attempt >= self.max_retries:
            logger.error(f"IR validation failed after {self.max_retries} attempts")
            return False, errors, ir_data

        # Attempt basic repair
        repaired = self._attempt_repair(ir_data, errors)
        logger.info(f"Retrying validation (attempt {attempt + 1}/{self.max_retries})")
        return self.validate(repaired, attempt=attempt + 1)

    def _attempt_repair(self, ir_data: Dict[str, Any], errors: list[str]) -> Dict[str, Any]:
        """Attempt basic repair of IR based on validation errors."""
        repaired = ir_data.copy()

        # Ensure required top-level fields exist
        if "meta" not in repaired:
            repaired["meta"] = {}
        if "task" not in repaired:
            repaired["task"] = {}
        if "constraints" not in repaired:
            repaired["constraints"] = {}

        # Ensure required meta fields
        meta = repaired.setdefault("meta", {})
        if "intent" not in meta:
            meta["intent"] = "scaffold"  # Default
        if "schema_version" not in meta:
            meta["schema_version"] = "2.1.0"
        if "compiler_version" not in meta:
            meta["compiler_version"] = "0.1.0"

        # Ensure required task fields
        task = repaired.setdefault("task", {})
        if "description" not in task:
            task["description"] = ""

        # Ensure required constraints
        constraints = repaired.setdefault("constraints", {})
        if "must_avoid" not in constraints:
            constraints["must_avoid"] = []

        # Ensure output_contract
        if "output_contract" not in repaired:
            repaired["output_contract"] = {
                "required_sections": [],
                "file_block_format": "strict",
            }

        # Ensure quality_checks
        if "quality_checks" not in repaired:
            repaired["quality_checks"] = {}

        return repaired
