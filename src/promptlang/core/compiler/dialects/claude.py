"""Claude dialect compiler using XML tags with contract-first placement."""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ClaudeDialectCompiler:
    """Compiles IR to Claude-optimized prompt format."""

    def compile(self, ir: Dict[str, Any]) -> str:
        """Compile IR to Claude format with XML tags.

        Format:
        - Output contract injected first
        - XML tags for structure
        - Deterministic section ordering
        """
        parts = []

        # Contract first (CRITICAL)
        output_contract = ir.get("output_contract", {})
        parts.append("<output_contract>")
        parts.append(self._format_contract(output_contract))
        parts.append("</output_contract>")

        # Task description
        task = ir.get("task", {})
        parts.append("<task>")
        parts.append(f"<description>{task.get('description', '')}</description>")
        if task.get("scope"):
            parts.append(f"<scope>{task['scope']}</scope>")
        parts.append("</task>")

        # Constraints (especially must_avoid and security)
        constraints = ir.get("constraints", {})
        parts.append("<constraints>")
        if constraints.get("must_have"):
            parts.append(f"<must_have>{', '.join(constraints['must_have'])}</must_have>")
        if constraints.get("must_avoid"):
            parts.append(f"<must_avoid>{', '.join(constraints['must_avoid'])}</must_avoid>")
        if constraints.get("security_preserve"):
            parts.append("<security_preserve>true</security_preserve>")
        parts.append("</constraints>")

        # Context
        context = ir.get("context", {})
        if context:
            parts.append("<context>")
            if context.get("stack"):
                stack = context["stack"]
                parts.append(f"<stack>language={stack.get('language', '')}, framework={stack.get('framework', '')}</stack>")
            parts.append("</context>")

        # Quality checks
        quality = ir.get("quality_checks", {})
        if quality:
            parts.append("<quality_requirements>")
            if quality.get("validation_level"):
                parts.append(f"<validation_level>{quality['validation_level']}</validation_level>")
            if quality.get("security_level"):
                parts.append(f"<security_level>{quality['security_level']}</security_level>")
            parts.append("</quality_requirements>")

        return "\n\n".join(parts)

    def _format_contract(self, contract: Dict[str, Any]) -> str:
        """Format output contract section."""
        lines = []
        if contract.get("required_sections"):
            lines.append("Required sections:")
            for section in contract["required_sections"]:
                lines.append(f"  - {section}")

        if contract.get("required_files"):
            lines.append("\nRequired files:")
            for file in contract["required_files"]:
                lines.append(f"  - {file}")

        if contract.get("file_block_format"):
            lines.append(f"\nFile block format: {contract['file_block_format']}")

        return "\n".join(lines)
