"""Output parsers for extracting sections and file blocks."""

import re
from typing import Any, Dict, List

logger = None  # Lazy import if needed


class OutputParser:
    """Parses generated output to extract sections and file blocks."""

    SECTION_PATTERN = re.compile(r"^##\s+(.+)$", re.MULTILINE)
    FILE_BLOCK_PATTERN = re.compile(
        r"FILE:\s*(.+?)\n```(?:lang|(\w+))?\n(.*?)```", re.DOTALL
    )

    def parse(self, output: str) -> Dict[str, Any]:
        """Parse output and extract structured data.

        Returns:
            Dictionary with sections, file_blocks, raw_output
        """
        sections = self._extract_sections(output)
        file_blocks = self._extract_file_blocks(output)

        return {
            "sections": sections,
            "file_blocks": file_blocks,
            "raw_output": output,
        }

    def _extract_sections(self, output: str) -> List[Dict[str, str]]:
        """Extract markdown sections from output."""
        sections = []
        matches = self.SECTION_PATTERN.finditer(output)

        for match in matches:
            section_name = match.group(1).strip()
            start_pos = match.end()

            # Find next section or end of string
            next_match = self.SECTION_PATTERN.search(output, start_pos)
            end_pos = next_match.start() if next_match else len(output)

            section_content = output[start_pos:end_pos].strip()

            sections.append({
                "name": section_name,
                "content": section_content,
            })

        return sections

    def _extract_file_blocks(self, output: str) -> List[Dict[str, str]]:
        """Extract file blocks from output."""
        file_blocks = []
        matches = self.FILE_BLOCK_PATTERN.finditer(output)

        for match in matches:
            file_path = match.group(1).strip()
            language = match.group(2) or "text"
            code_content = match.group(3).strip()

            file_blocks.append({
                "path": file_path,
                "language": language,
                "content": code_content,
            })

        return file_blocks
