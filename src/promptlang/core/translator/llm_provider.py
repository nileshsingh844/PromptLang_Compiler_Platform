"""LLM provider interface and implementations."""

import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def translate_to_ir(
        self, input_text: str, intent: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Translate human input to PromptLang IR.

        Args:
            input_text: Human input text
            intent: Detected intent
            context: Additional context

        Returns:
            PromptLang IR dictionary
        """
        pass


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for deterministic testing without API keys."""

    def __init__(self):
        """Initialize mock provider."""
        self.intent_templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load deterministic IR templates by intent."""
        return {
            "scaffold": {
                "meta": {
                    "intent": "scaffold",
                    "name": "project_scaffold",
                    "tags": ["project", "structure"],
                    "schema_version": "2.1.0",
                    "compiler_version": "0.1.0",
                },
                "task": {
                    "description": "{input_text}",
                    "scope": "full_project",
                    "success_criteria": [
                        "All required files generated",
                        "Structure matches specifications",
                    ],
                },
                "context": {
                    "stack": {"language": "python", "framework": "fastapi"},
                },
                "constraints": {
                    "must_have": ["README.md", "requirements.txt"],
                    "must_avoid": ["hardcoded_secrets", "insecure_patterns"],
                    "token_budget": 4000,
                    "security_preserve": True,
                },
                "output_contract": {
                    "required_sections": [
                        "Project Blueprint",
                        "Directory Structure",
                        "File Contents",
                        "Verification Steps",
                    ],
                    "required_files": [],
                    "file_block_format": "strict",
                    "scaffold_mode": "full",
                },
                "quality_checks": {
                    "syntax": True,
                    "security": True,
                    "quality": True,
                    "validation_level": "strict",
                    "security_level": "high",
                },
            },
            "debug": {
                "meta": {
                    "intent": "debug",
                    "name": "debug_session",
                    "tags": ["debug", "error"],
                    "schema_version": "2.1.0",
                    "compiler_version": "0.1.0",
                },
                "task": {
                    "description": "{input_text}",
                    "scope": "error_resolution",
                    "success_criteria": ["Error identified", "Solution provided"],
                },
                "context": {
                    "stack": {"language": "python"},
                    "inputs": {"error_log": ""},
                },
                "constraints": {
                    "must_avoid": ["breaking_changes"],
                    "token_budget": 2000,
                    "security_preserve": True,
                },
                "output_contract": {
                    "required_sections": ["Error Analysis", "Root Cause", "Solution"],
                    "file_block_format": "flexible",
                },
                "quality_checks": {
                    "syntax": True,
                    "validation_level": "progressive",
                    "security_level": "low",
                },
            },
        }

    async def translate_to_ir(
        self, input_text: str, intent: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate deterministic IR from template."""
        # Get template for intent or use scaffold as default
        template = self.intent_templates.get(intent, self.intent_templates["scaffold"])

        # Deep copy template
        ir = json.loads(json.dumps(template))

        # Fill in input text
        ir["task"]["description"] = input_text

        # Apply context if provided
        if context:
            if "language" in context:
                ir["context"]["stack"]["language"] = context["language"]
            if "framework" in context:
                ir["context"]["stack"]["framework"] = context["framework"]

        logger.info(f"MockLLMProvider generated IR for intent: {intent}")
        return ir


class OpenAIProvider(LLMProvider):
    """OpenAI provider (optional, requires API key - NOT FOR ZERO-BUDGET MODE)."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI provider."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")

    async def translate_to_ir(
        self, input_text: str, intent: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Translate using OpenAI (not implemented in MVP)."""
        raise NotImplementedError("OpenAI provider not implemented in MVP - use 'mock' or 'ollama' for zero-budget mode")


class AnthropicProvider(LLMProvider):
    """Anthropic provider (optional, requires API key - NOT FOR ZERO-BUDGET MODE)."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Anthropic provider."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key required")

    async def translate_to_ir(
        self, input_text: str, intent: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Translate using Anthropic (not implemented in MVP)."""
        raise NotImplementedError("Anthropic provider not implemented in MVP - use 'mock' or 'ollama' for zero-budget mode")


class GroqProvider(LLMProvider):
    """Groq provider for ultra-fast inference (free tier available)."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq provider."""
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key required. Set GROQ_API_KEY environment variable.")
        
        # Import here to avoid dependency issues if not using Groq
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.groq.com/openai/v1"
            )
        except ImportError:
            raise ImportError("openai package required for Groq provider. Install with: pip install openai")

    async def translate_to_ir(
        self, input_text: str, intent: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Translate using Groq's fast inference."""
        # Build prompt for IR generation
        prompt = self._build_ir_prompt(input_text, intent, context)

        try:
            response = await self.client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Fast model
                messages=[
                    {"role": "system", "content": "You are a PromptLang IR generator. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000,
            )

            generated_text = response.choices[0].message.content
            
            # Clean up JSON if wrapped in markdown code blocks
            if "```json" in generated_text:
                start = generated_text.find("```json") + 7
                end = generated_text.find("```", start)
                generated_text = generated_text[start:end].strip()
            elif "```" in generated_text:
                start = generated_text.find("```") + 3
                end = generated_text.find("```", start)
                generated_text = generated_text[start:end].strip()

            ir = json.loads(generated_text)
            logger.info(f"GroqProvider generated IR for intent: {intent}")
            return ir

        except Exception as e:
            logger.error(f"Groq provider error: {e}")
            # Fall back to mock on error
            mock_provider = MockLLMProvider()
            return await mock_provider.translate_to_ir(input_text, intent, context)

    def _build_ir_prompt(self, input_text: str, intent: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build intelligent prompt for IR generation with multi-language/framework analysis."""
        prompt_parts = [
            "You are an intelligent PromptLang IR generator. Analyze the request and determine the BEST approach, language, and framework.",
            "",
            "IMPORTANT: Do NOT default to Python unless explicitly specified. Consider:",
            "- Multiple programming languages (JavaScript/TypeScript, Python, Java, Go, Rust, C#, PHP, Ruby, etc.)",
            "- Various frameworks (React, Vue, Angular, Express, FastAPI, Django, Spring Boot, etc.)",
            "- Different architectures (SPA, MPA, microservices, serverless, CLI, mobile, desktop)",
            "- Modern vs traditional approaches based on requirements",
            "",
            f"Intent: {intent}",
            f"Input: {input_text}",
            "",
            "Analyze the request and generate a JSON object with the following EXACT structure:",
            "",
            "```json",
            "{",
            '  "meta": {',
            '    "intent": "' + intent + '",',
            '    "name": "project_scaffold",',
            '    "tags": ["project", "structure"],',
            '    "schema_version": "2.1.0",',
            '    "compiler_version": "0.1.0"',
            "  },",
            '  "task": {',
            '    "description": "' + input_text + '",',
            '    "scope": "full_project",',
            '    "success_criteria": ["Optimal technology stack chosen", "All required files generated", "Structure matches specifications"]',
            "  },",
            '  "context": {',
            '    "stack": {',
            '      "language": "ANALYZE_AND_CHOOSE_BEST_LANGUAGE",',
            '      "framework": "ANALYZE_AND_CHOOSE_BEST_FRAMEWORK",',
            '      "architecture": "ANALYZE_AND_CHOOSE_BEST_ARCHITECTURE"',
            "    }",
            "  },",
            '  "constraints": {',
            '    "must_have": ["README.md", "package.json/requirements.txt/Cargo.toml/pom.xml"],',
            '    "must_avoid": ["hardcoded_secrets", "insecure_patterns", "outdated_dependencies"],',
            '    "token_budget": 4000,',
            '    "security_preserve": true',
            "  },",
            '  "output_contract": {',
            '    "required_sections": ["Project Blueprint", "Technology Analysis", "Directory Structure", "File Contents", "Setup Instructions", "Verification Steps"],',
            '    "required_files": [],',
            '    "file_block_format": "strict",',
            '    "scaffold_mode": "full"',
            "  },",
            '  "quality_checks": {',
            '    "syntax": true,',
            '    "security": true,',
            '    "quality": true,',
            '    "validation_level": "strict",',
            '    "security_level": "high"',
            "  }",
            "}",
            "```",
            "",
            "GUIDELINES:",
            "- Choose the BEST technology stack based on the request context",
            "- For web apps: Consider React/Vue/Angular + Node.js/Python/Go",
            "- For APIs: Consider FastAPI/Express/Spring Boot/Django",
            "- For CLI tools: Consider Go/Rust/Python/Node.js",
            "- For mobile: Consider React Native/Flutter/Swift/Kotlin",
            "- For desktop: Consider Electron/Tauri/.NET MAUI",
            "- Always justify your technology choices in the output",
            "",
            "CRITICAL: Replace 'ANALYZE_AND_CHOOSE_BEST_*' with actual values:",
            "- language: Replace with actual language (e.g., 'TypeScript', 'Go', 'Kotlin')",
            "- framework: Replace with actual framework (e.g., 'React', 'Express', 'Spring Boot')",
            "- architecture: Replace with actual architecture (e.g., 'SPA', 'microservices', 'MVC')",
            "",
            "IMPORTANT: Include comprehensive technology analysis:",
            "- In the task.description, explain why the chosen stack is optimal",
            "- At the end, include a 'technology_alternatives' section with all viable options",
            "- For each alternative, briefly explain pros/cons and when to use it",
            "- Format alternatives as a clear, structured comparison",
            "",
            "Respond ONLY with valid JSON, no additional text.",
            "CRITICAL REQUIREMENTS:",
            "- success_criteria MUST be an array of strings",
            "- file_block_format MUST be either 'strict' or 'flexible'",
            "- validation_level MUST be either 'strict' or 'progressive'", 
            "- security_level MUST be either 'low' or 'high'",
            "- Respond ONLY with the JSON object, no additional text or markdown formatting",
        ]

        if context:
            context_str = json.dumps(context)
            prompt_parts.append(f"Additional context: {context_str}")

        return "\n".join(prompt_parts)


class OllamaProvider(LLMProvider):
    """Ollama provider for local LLM inference (zero-budget, optional)."""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        """Initialize Ollama provider.

        Args:
            base_url: Ollama API base URL (default: http://localhost:11434)
            model: Model name (default: llama2 or from OLLAMA_MODEL env var)
        """
        if not HTTPX_AVAILABLE:
            raise ImportError("httpx is required for Ollama provider. Install with: pip install httpx")

        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama2")

    async def translate_to_ir(
        self, input_text: str, intent: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Translate human input to IR using local Ollama.

        This uses the Ollama API to generate IR JSON from the input.
        Falls back to mock if Ollama is unavailable.
        """
        # Build prompt for IR generation
        prompt = self._build_ir_prompt(input_text, intent, context)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json",
                    },
                )
                response.raise_for_status()
                result = response.json()

                # Extract JSON from response
                generated_text = result.get("response", "")
                
                # Try to parse JSON from response
                try:
                    # Clean up JSON if wrapped in markdown code blocks
                    if "```json" in generated_text:
                        start = generated_text.find("```json") + 7
                        end = generated_text.find("```", start)
                        generated_text = generated_text[start:end].strip()
                    elif "```" in generated_text:
                        start = generated_text.find("```") + 3
                        end = generated_text.find("```", start)
                        generated_text = generated_text[start:end].strip()

                    ir = json.loads(generated_text)
                    logger.info(f"OllamaProvider generated IR for intent: {intent}")
                    return ir
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON from Ollama response: {e}, falling back to mock")
                    # Fall back to mock
                    mock_provider = MockLLMProvider()
                    return await mock_provider.translate_to_ir(input_text, intent, context)

        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.warning(f"Ollama request failed: {e}, falling back to mock")
            # Fall back to mock if Ollama unavailable
            mock_provider = MockLLMProvider()
            return await mock_provider.translate_to_ir(input_text, intent, context)

    def _build_ir_prompt(self, input_text: str, intent: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build prompt for IR generation."""
        prompt_parts = [
            "You are a PromptLang IR generator. Convert the following request into a valid PromptLang IR JSON structure.",
            "",
            f"Intent: {intent}",
            f"Input: {input_text}",
            "",
            "Generate a JSON object with the following structure:",
            "- meta: { intent, schema_version: '2.1.0', compiler_version: '0.1.0' }",
            "- task: { description, scope, success_criteria }",
            "- context: { stack: { language, framework } }",
            "- constraints: { must_avoid: [], token_budget }",
            "- output_contract: { required_sections: [], file_block_format }",
            "- quality_checks: { syntax, security, validation_level, security_level }",
            "",
            "Respond ONLY with valid JSON, no additional text.",
        ]

        if context:
            context_str = json.dumps(context)
            prompt_parts.append(f"Additional context: {context_str}")

        return "\n".join(prompt_parts)


def get_llm_provider(provider_name: Optional[str] = None) -> LLMProvider:
    """Factory function to get LLM provider.

    Zero-budget providers (default):
    - 'mock': Deterministic mock provider (default, no API keys needed)
    - 'ollama': Local Ollama instance (optional, requires local Ollama server)
    - 'groq': Groq LPU-powered inference (free tier, requires API key)

    Paid providers (not recommended for MVP):
    - 'openai': Requires API key (raises NotImplementedError)
    - 'anthropic': Requires API key (raises NotImplementedError)
    """
    provider_name = provider_name or os.getenv("LLM_PROVIDER", "groq")  # Default to groq
    logger.info(f"Initializing LLM provider: {provider_name}")

    if provider_name == "mock":
        return MockLLMProvider()
    elif provider_name == "ollama":
        try:
            return OllamaProvider()
        except ImportError:
            logger.warning("httpx not available, falling back to mock provider")
            return MockLLMProvider()
        except Exception as e:
            logger.warning(f"Ollama provider initialization failed: {e}, falling back to mock")
            return MockLLMProvider()
    elif provider_name == "groq":
        try:
            return GroqProvider({})
        except ImportError:
            logger.warning("Groq provider not available, falling back to mock provider")
            return MockLLMProvider()
        except Exception as e:
            logger.warning(f"Groq provider initialization failed: {e}, falling back to mock")
            return MockLLMProvider()
    elif provider_name == "openai":
        logger.warning("OpenAI provider requires paid API key - not recommended for zero-budget mode")
        return OpenAIProvider()
    elif provider_name == "anthropic":
        logger.warning("Anthropic provider requires paid API key - not recommended for zero-budget mode")
        return AnthropicProvider()
    else:
        logger.warning(f"Unknown provider {provider_name}, using mock (zero-budget)")
        return MockLLMProvider()
