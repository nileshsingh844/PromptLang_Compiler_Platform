"""Syntax validation for extracted code blocks."""

import ast
import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class SyntaxValidator:
    """Validates syntax of code blocks in output."""

    def validate(self, file_blocks: List[Dict[str, str]]) -> tuple[bool, List[Dict[str, Any]]]:
        """Validate syntax of file blocks.

        Returns:
            Tuple of (is_valid, findings_list)
        """
        findings: List[Dict[str, Any]] = []

        for file_block in file_blocks:
            path = file_block.get("path", "")
            language = file_block.get("language", "text").lower()
            content = file_block.get("content", "")

            if language == "python":
                syntax_valid, syntax_errors = self._validate_python(content, path)
                if not syntax_valid:
                    findings.extend(syntax_errors)

            elif language == "json":
                syntax_valid, syntax_errors = self._validate_json(content, path)
                if not syntax_valid:
                    findings.extend(syntax_errors)

            # YAML and TS/JS are optional for MVP

        is_valid = len(findings) == 0
        return is_valid, findings

    def _validate_python(self, code: str, path: str) -> tuple[bool, List[Dict[str, Any]]]:
        """Validate Python syntax using ast.parse."""
        findings = []
        try:
            ast.parse(code, filename=path)
        except SyntaxError as e:
            findings.append({
                "severity": "error",
                "type": "syntax",
                "file": path,
                "message": f"Python syntax error: {e.msg}",
                "line": e.lineno,
                "offset": e.offset,
            })
            return False, findings
        except Exception as e:
            findings.append({
                "severity": "error",
                "type": "syntax",
                "file": path,
                "message": f"Parse error: {str(e)}",
            })
            return False, findings

        return True, []

    def _validate_json(self, content: str, path: str) -> tuple[bool, List[Dict[str, Any]]]:
        """Validate JSON syntax."""
        findings = []
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            findings.append({
                "severity": "error",
                "type": "syntax",
                "file": path,
                "message": f"JSON syntax error: {e.msg}",
                "line": e.lineno,
                "column": e.colno,
            })
            return False, findings

        return True, []
