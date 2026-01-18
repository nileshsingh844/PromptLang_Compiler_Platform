"""Security scanner with regex-based CWE-aware patterns."""

import re
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class SecurityScanner:
    """Security scanner for common vulnerabilities (CWE-aware)."""

    # CWE-798: Hardcoded secrets
    SECRET_PATTERNS = [
        (r'password\s*=\s*["\']([^"\']+)["\']', "CWE-798", "Hardcoded password"),
        (r'api[_-]?key\s*=\s*["\']([^"\']+)["\']', "CWE-798", "Hardcoded API key"),
        (r'secret\s*=\s*["\']([^"\']+)["\']', "CWE-798", "Hardcoded secret"),
        (r'["\']([A-Za-z0-9]{32,})["\']', "CWE-798", "Potential hardcoded token"),
    ]

    # CWE-89: SQL injection
    SQL_INJECTION_PATTERNS = [
        (r'SELECT\s+.*\s+FROM\s+.*%s|%\(', "CWE-89", "Potential SQL injection (string formatting)"),
        (r'execute\s*\(\s*f["\']([^"\']*%[sd])', "CWE-89", "Potential SQL injection (f-string)"),
    ]

    # CWE-79: XSS
    XSS_PATTERNS = [
        (r'innerHTML\s*=\s*[^;]*\+.*request', "CWE-79", "Potential XSS (innerHTML with user input)"),
        (r'document\.write\s*\([^)]*\+', "CWE-79", "Potential XSS (document.write with concatenation)"),
    ]

    def scan(self, file_blocks: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Scan file blocks for security issues.

        Returns:
            List of security findings
        """
        findings: List[Dict[str, Any]] = []

        for file_block in file_blocks:
            path = file_block.get("path", "")
            content = file_block.get("content", "")

            # Scan for secrets
            findings.extend(self._scan_secrets(content, path))

            # Scan for SQL injection
            findings.extend(self._scan_sql_injection(content, path))

            # Scan for XSS (if JavaScript/TypeScript)
            if file_block.get("language", "").lower() in ["javascript", "typescript", "js", "ts"]:
                findings.extend(self._scan_xss(content, path))

        return findings

    def _scan_secrets(self, content: str, path: str) -> List[Dict[str, Any]]:
        """Scan for hardcoded secrets (CWE-798)."""
        findings = []

        for pattern, cwe, message in self.SECRET_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count("\n") + 1
                findings.append({
                    "severity": "error",
                    "type": "security",
                    "cwe": cwe,
                    "file": path,
                    "message": message,
                    "line": line_num,
                    "suggestion": "Use environment variables or secure configuration management",
                })

        return findings

    def _scan_sql_injection(self, content: str, path: str) -> List[Dict[str, Any]]:
        """Scan for SQL injection patterns (CWE-89)."""
        findings = []

        for pattern, cwe, message in self.SQL_INJECTION_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count("\n") + 1
                findings.append({
                    "severity": "error",
                    "type": "security",
                    "cwe": cwe,
                    "file": path,
                    "message": message,
                    "line": line_num,
                    "suggestion": "Use parameterized queries or ORM methods",
                })

        return findings

    def _scan_xss(self, content: str, path: str) -> List[Dict[str, Any]]:
        """Scan for XSS patterns (CWE-79)."""
        findings = []

        for pattern, cwe, message in self.XSS_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count("\n") + 1
                findings.append({
                    "severity": "error",
                    "type": "security",
                    "cwe": cwe,
                    "file": path,
                    "message": message,
                    "line": line_num,
                    "suggestion": "Use textContent or proper sanitization",
                })

        return findings
