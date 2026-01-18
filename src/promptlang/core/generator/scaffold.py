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
        """Generate intelligent scaffold using Groq API with multi-language support."""
        try:
            # Extract the determined technology stack from IR
            stack = ir.get("context", {}).get("stack", {})
            language = stack.get("language", "determine")
            framework = stack.get("framework", "determine")
            architecture = stack.get("architecture", "determine")
            
            # Build intelligent system prompt
            system_prompt = f"""You are an expert software architect and polyglot developer. Generate detailed, practical scaffold output following the exact contract requirements.

TECHNOLOGY CONTEXT:
- Language: {language}
- Framework: {framework} 
- Architecture: {architecture}

INSTRUCTIONS:
1. Generate AUTHENTIC code for the determined technology stack
2. Do NOT default to Python unless explicitly specified
3. Use modern best practices and patterns for the chosen technology
4. Include realistic file contents with proper syntax
5. Add setup instructions specific to the chosen stack
6. Justify technology choices in the analysis section
7. Include comprehensive technology alternatives section at the end

TECHNOLOGY GUIDELINES:
- JavaScript/TypeScript: Use modern ES6+, npm/yarn, proper package.json
- Python: Use pip, requirements.txt, modern Python patterns
- Go: Use go.mod, proper module structure, idiomatic Go
- Rust: Use Cargo.toml, safe Rust patterns, proper error handling
- Java: Use Maven/Gradle, modern Java features, proper package structure
- C#: Use .NET CLI, modern C# features, proper project structure
- PHP: Use Composer, modern PHP practices, proper autoloading
- Ruby: Use Bundler, modern Ruby patterns, proper gem management

FRAMEWORK-SPECIFIC:
- React: Use functional components, hooks, modern patterns
- Vue: Use Composition API, modern Vue 3 patterns
- Angular: Use standalone components, modern Angular patterns
- Express: Use middleware, async/await, proper error handling
- FastAPI: Use dependency injection, Pydantic models, async endpoints
- Django: Use class-based views, modern Django patterns
- Spring Boot: Use annotations, dependency injection, modern Spring

TECHNOLOGY ANALYSIS REQUIREMENTS:
- Start with a clear "## Technology Analysis" section
- Explain why the chosen stack is optimal for this specific project
- Include performance, scalability, and ecosystem considerations
- Mention team expertise and learning curve factors
- Discuss maintenance and long-term viability

TECHNOLOGY ALTERNATIVES SECTION:
- Create a "## Technology Alternatives" section at the end
- List 3-4 viable alternative stacks with pros/cons for each
- For each alternative, explain when it would be a better choice
- Include specific scenarios where each alternative shines
- Format as bullet points with clear pros/cons separation

CRITICAL: The Technology Alternatives section MUST be included at the end of your response.

Generate comprehensive, production-ready scaffold output."""
            
            # Use the Groq provider's client to generate scaffold
            response = await self.llm_provider.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": compiled_prompt}
                ],
                temperature=0.3,
                max_tokens=6000,
            )
            
            generated_content = response.choices[0].message.content
            logger.info(f"Groq scaffold generation successful for {language}/{framework}")
            return generated_content
            
        except Exception as e:
            logger.error(f"Groq scaffold generation failed: {e}, falling back to mock")
            return self._generate_mock_scaffold(ir, required_sections, required_files, file_block_format)
