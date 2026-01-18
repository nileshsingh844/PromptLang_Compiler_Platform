"""Contract verifier for output contract compliance."""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ContractVerifier:
    """Verifies output contract compliance."""

    def verify(
        self,
        parsed_output: Dict[str, Any],
        ir: Dict[str, Any],
    ) -> tuple[bool, Dict[str, Any]]:
        """Verify output contract compliance.

        Returns:
            Tuple of (is_compliant, compliance_summary)
        """
        output_contract = ir.get("output_contract", {})
        required_sections = output_contract.get("required_sections", [])
        required_files = output_contract.get("required_files", [])
        file_block_format = output_contract.get("file_block_format", "strict")

        sections = parsed_output.get("sections", [])
        file_blocks = parsed_output.get("file_blocks", [])

        compliance_summary: Dict[str, Any] = {
            "required_sections_present": [],
            "required_sections_missing": [],
            "required_files_present": [],
            "required_files_missing": [],
            "file_block_format_correct": True,
            "compliant": True,
        }

        # Check required sections
        section_names = [s["name"] for s in sections]
        for section in required_sections:
            if section in section_names:
                compliance_summary["required_sections_present"].append(section)
            else:
                compliance_summary["required_sections_missing"].append(section)
                compliance_summary["compliant"] = False

        # Check required files
        file_paths = [fb["path"] for fb in file_blocks]
        for file_path in required_files:
            if file_path in file_paths:
                compliance_summary["required_files_present"].append(file_path)
            else:
                compliance_summary["required_files_missing"].append(file_path)
                compliance_summary["compliant"] = False

        # Check file block format
        if file_block_format == "strict":
            for file_block in file_blocks:
                if not file_block.get("language"):
                    compliance_summary["file_block_format_correct"] = False
                    compliance_summary["compliant"] = False

        return compliance_summary["compliant"], compliance_summary
