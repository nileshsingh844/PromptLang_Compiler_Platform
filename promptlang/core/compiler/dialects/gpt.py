"""GPT dialect compiler using JSON messages with contract-first placement."""

import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class GPTDialectCompiler:
    """Compiles IR to GPT-optimized prompt format."""

    def compile(self, ir: Dict[str, Any]) -> str:
        """Compile IR to GPT format with JSON messages.

        Format:
        - Output contract injected first
        - JSON-structured messages
        - Deterministic section ordering
        """
        messages: List[Dict[str, str]] = []

        # Contract first (CRITICAL)
        output_contract = ir.get("output_contract", {})
        contract_msg = {
            "role": "system",
            "content": f"OUTPUT CONTRACT (MANDATORY):\n{self._format_contract(output_contract)}",
        }
        messages.append(contract_msg)

        # Task
        task = ir.get("task", {})
        task_content = f"Task: {task.get('description', '')}"
        if task.get("scope"):
            task_content += f"\nScope: {task['scope']}"
        messages.append({"role": "user", "content": task_content})

        # Constraints
        constraints = ir.get("constraints", {})
        constraint_lines = ["Constraints:"]
        if constraints.get("must_have"):
            constraint_lines.append(f"Must have: {', '.join(constraints['must_have'])}")
        if constraints.get("must_avoid"):
            constraint_lines.append(f"Must avoid: {', '.join(constraints['must_avoid'])}")
        if constraints.get("security_preserve"):
            constraint_lines.append("Security preservation: required")

        if len(constraint_lines) > 1:
            messages.append({"role": "user", "content": "\n".join(constraint_lines)})

        # Context
        context = ir.get("context", {})
        if context.get("stack"):
            stack = context["stack"]
            stack_str = f"Stack: language={stack.get('language', '')}, framework={stack.get('framework', '')}"
            messages.append({"role": "user", "content": stack_str})

        # Format as JSON
        return json.dumps({"messages": messages}, indent=2)

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
