"""Scaffold generator for stage 7 - generates contract-enforced output."""

import logging
import os
from typing import Any, Dict, Optional

from promptlang.core.translator.llm_provider import LLMProvider, get_llm_provider

logger = logging.getLogger(__name__)


class ScaffoldGenerator:
    """Generates scaffold output enforcing output contract."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """Initialize scaffold generator.

        Args:
            llm_provider: LLM provider instance (uses mock by default)
        """
        self.llm_provider = llm_provider or get_llm_provider()

    async def generate(
        self,
        compiled_prompt: str,
        ir: Dict[str, Any],
        scaffold_mode: str = "full",
    ) -> str:
        """Generate scaffold output from compiled prompt.

        Args:
            compiled_prompt: Compiled prompt from stage 6
            ir: IR with output contract
            scaffold_mode: scaffold mode (quick/full)

        Returns:
            Generated scaffold output
        """
        output_contract = ir.get("output_contract", {})
        required_sections = output_contract.get("required_sections", [])
        required_files = output_contract.get("required_files", [])
        file_block_format = output_contract.get("file_block_format", "strict")

        # Check provider type - use mock generation for mock and ollama (zero-budget)
        from promptlang.core.translator.llm_provider import MockLLMProvider, OllamaProvider, GroqProvider

        if isinstance(self.llm_provider, MockLLMProvider):
            # Mock provider - generate deterministic output
            return self._generate_mock_scaffold(ir, required_sections, required_files, file_block_format)
        elif isinstance(self.llm_provider, OllamaProvider):
            # For Ollama, use mock generation (could be enhanced to use Ollama API)
            logger.debug("Using mock scaffold generation for Ollama provider")
            return self._generate_mock_scaffold(ir, required_sections, required_files, file_block_format)
        elif isinstance(self.llm_provider, GroqProvider):
            # For Groq, use real API generation
            logger.debug("Using Groq API for scaffold generation")
            return await self._generate_groq_scaffold(compiled_prompt, ir, required_sections, required_files, file_block_format)
        else:
            # For other providers (OpenAI/Anthropic) - not implemented in MVP
            logger.warning("Paid LLM provider not implemented for scaffold generation, using mock")
            return self._generate_mock_scaffold(ir, required_sections, required_files, file_block_format)

    def _generate_mock_scaffold(
        self,
        ir: Dict[str, Any],
        required_sections: list,
        required_files: list,
        file_block_format: str,
    ) -> str:
        """Generate deterministic mock scaffold output."""
        task = ir.get("task", {})
        intent = ir.get("meta", {}).get("intent", "scaffold")
        task_description = task.get("description", "")

        parts = []

        # Always include required sections in order
        for section in required_sections:
            parts.append(f"## {section}")

            if section == "Project Blueprint":
                parts.append(f"\nThis project implements: {task_description}")
                parts.append("")

            elif section == "Directory Structure":
                parts.append("\n```")
                parts.append("project/")
                parts.append("├── README.md")
                parts.append("├── requirements.txt")
                parts.append("└── src/")
                parts.append("    └── main.py")
                parts.append("```")
                parts.append("")

            elif section == "File Contents":
                # Generate file blocks with strict format
                if file_block_format == "strict":
                    for file_path in required_files or ["README.md", "src/main.py"]:
                        parts.append(f"FILE: {file_path}")
                        parts.append(f"```lang")
                        if file_path.endswith(".md"):
                            parts.append(f"# {task_description}")
                            parts.append("")
                            parts.append("Project description and setup instructions.")
                        elif file_path.endswith(".py"):
                            parts.append("def main():")
                            parts.append('    """Main entry point."""')
                            parts.append('    print("Hello, World!")')
                        parts.append("```")
                        parts.append("")

            elif section == "Verification Steps":
                parts.append("\n1. Install dependencies: `pip install -r requirements.txt`")
                parts.append("2. Run the application: `python src/main.py`")
                parts.append("3. Verify output matches expected behavior")
                parts.append("")

        return "\n".join(parts)

    async def _generate_groq_scaffold(
        self,
        compiled_prompt: str,
        ir: Dict[str, Any],
        required_sections: list,
        required_files: list,
        file_block_format: str,
    ) -> str:
        """Generate scaffold using Groq API."""
        try:
            # Use the Groq provider's client to generate scaffold
            response = await self.llm_provider.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a expert software architect. Generate detailed, practical scaffold output following the exact contract requirements."
                    },
                    {"role": "user", "content": compiled_prompt}
                ],
                temperature=0.3,
                max_tokens=4000,
            )
            
            generated_content = response.choices[0].message.content
            logger.info("Groq scaffold generation successful")
            return generated_content
            
        except Exception as e:
            logger.error(f"Groq scaffold generation failed: {e}, falling back to mock")
            return self._generate_mock_scaffold(ir, required_sections, required_files, file_block_format)
