"""OSS (Open Source) dialect compiler using plain markdown with contract-first placement."""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class OSSDialectCompiler:
    """Compiles IR to OSS-optimized prompt format (plain deterministic markdown)."""

    def compile(self, ir: Dict[str, Any]) -> str:
        """Compile IR to OSS format with plain markdown.

        Format:
        - Output contract injected first
        - Plain markdown structure
        - Deterministic section ordering
        """
        parts = []

        # Contract first (CRITICAL)
        output_contract = ir.get("output_contract", {})
        parts.append("## OUTPUT CONTRACT (MANDATORY)")
        parts.append(self._format_contract(output_contract))
        parts.append("")

        # Task
        task = ir.get("task", {})
        parts.append("## Task")
        parts.append(task.get("description", ""))
        if task.get("scope"):
            parts.append(f"\n**Scope:** {task['scope']}")
        parts.append("")

        # Constraints
        constraints = ir.get("constraints", {})
        parts.append("## Constraints")
        if constraints.get("must_have"):
            parts.append(f"**Must have:** {', '.join(constraints['must_have'])}")
        if constraints.get("must_avoid"):
            parts.append(f"**Must avoid:** {', '.join(constraints['must_avoid'])}")
        if constraints.get("security_preserve"):
            parts.append("**Security preservation:** required")
        parts.append("")

        # Context
        context = ir.get("context", {})
        if context.get("stack"):
            stack = context["stack"]
            parts.append("## Context")
            parts.append(f"**Stack:** language={stack.get('language', '')}, framework={stack.get('framework', '')}")
            parts.append("")

        # Quality requirements
        quality = ir.get("quality_checks", {})
        if quality:
            parts.append("## Quality Requirements")
            if quality.get("validation_level"):
                parts.append(f"**Validation level:** {quality['validation_level']}")
            if quality.get("security_level"):
                parts.append(f"**Security level:** {quality['security_level']}")

        return "\n".join(parts)

    def _format_contract(self, contract: Dict[str, Any]) -> str:
        """Format output contract section."""
        lines = []
        if contract.get("required_sections"):
            lines.append("**Required sections:**")
            for section in contract["required_sections"]:
                lines.append(f"- {section}")

        if contract.get("required_files"):
            lines.append("\n**Required files:**")
            for file in contract["required_files"]:
                lines.append(f"- {file}")

        if contract.get("file_block_format"):
            lines.append(f"\n**File block format:** {contract['file_block_format']}")

        return "\n".join(lines)
