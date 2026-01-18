"""Quality checker for code quality metrics."""

import ast
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class QualityChecker:
    """Checks code quality metrics."""

    MAX_FUNCTION_LINES = 50

    def check(self, file_blocks: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Check quality of file blocks.

        Returns:
            List of quality findings
        """
        findings: List[Dict[str, Any]] = []

        for file_block in file_blocks:
            path = file_block.get("path", "")
            language = file_block.get("language", "text").lower()
            content = file_block.get("content", "")

            if language == "python":
                findings.extend(self._check_python_quality(content, path))

            # Check for TODO/FIXME (language-agnostic)
            findings.extend(self._check_todos(content, path))

        return findings

    def _check_python_quality(self, code: str, path: str) -> List[Dict[str, Any]]:
        """Check Python code quality."""
        findings = []

        try:
            tree = ast.parse(code, filename=path)

            # Check for missing docstrings
            if not self._has_module_docstring(tree):
                findings.append({
                    "severity": "warning",
                    "type": "quality",
                    "file": path,
                    "message": "Missing module docstring",
                    "suggestion": "Add module-level docstring",
                })

            # Check function length and docstrings
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check docstring
                    if not ast.get_docstring(node):
                        findings.append({
                            "severity": "warning",
                            "type": "quality",
                            "file": path,
                            "message": f"Function '{node.name}' missing docstring",
                            "line": node.lineno,
                            "suggestion": "Add function docstring",
                        })

                    # Check function length
                    if hasattr(node, "end_lineno") and node.end_lineno:
                        function_lines = node.end_lineno - node.lineno
                        if function_lines > self.MAX_FUNCTION_LINES:
                            findings.append({
                                "severity": "warning",
                                "type": "quality",
                                "file": path,
                                "message": f"Function '{node.name}' is {function_lines} lines (>{self.MAX_FUNCTION_LINES})",
                                "line": node.lineno,
                                "suggestion": "Consider breaking into smaller functions",
                            })

                    # Check for bare except
                    for child in ast.walk(node):
                        if isinstance(child, ast.ExceptHandler) and child.type is None:
                            findings.append({
                                "severity": "warning",
                                "type": "quality",
                                "file": path,
                                "message": f"Bare except clause in function '{node.name}'",
                                "line": child.lineno,
                                "suggestion": "Specify exception types",
                            })

        except SyntaxError:
            # Syntax errors handled by syntax validator
            pass

        return findings

    def _has_module_docstring(self, tree: ast.AST) -> bool:
        """Check if module has docstring."""
        if not tree.body:
            return False
        first_stmt = tree.body[0]
        return isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Str)

    def _check_todos(self, content: str, path: str) -> List[Dict[str, Any]]:
        """Check for TODO/FIXME comments."""
        findings = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()
            if "todo" in line_lower or "fixme" in line_lower:
                findings.append({
                    "severity": "info",
                    "type": "quality",
                    "file": path,
                    "message": "TODO/FIXME comment found",
                    "line": line_num,
                    "suggestion": "Address TODO/FIXME before production",
                })

        return findings
