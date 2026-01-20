"""LLM Providers"""

from .groq_provider import GroqProvider

# Try to import other providers, but handle missing dependencies gracefully
try:
    from .huggingface_provider import HuggingFaceProvider
except ImportError:
    HuggingFaceProvider = None

try:
    from .openrouter_provider import OpenRouterProvider
except ImportError:
    OpenRouterProvider = None

providers = ["GroqProvider"]
if HuggingFaceProvider:
    providers.append("HuggingFaceProvider")
if OpenRouterProvider:
    providers.append("OpenRouterProvider")

__all__ = providers
