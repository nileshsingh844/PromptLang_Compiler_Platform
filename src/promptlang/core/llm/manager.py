# promptlang/core/llm/manager.py
"""Provider manager with automatic fallback"""

import asyncio
from typing import Dict, Optional
from .config import LLMConfig, LLMProviderType
from .base import LLMProvider, LLMResponse
from .providers.groq_provider import GroqProvider

# Try to import other providers gracefully
try:
    from .providers.huggingface_provider import HuggingFaceProvider
except ImportError:
    HuggingFaceProvider = None

try:
    from .providers.openrouter_provider import OpenRouterProvider
except ImportError:
    OpenRouterProvider = None


class LLMProviderManager:
    """Manages multiple LLM providers with fallback strategy"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.providers: Dict[LLMProviderType, LLMProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all configured providers"""
        provider_map = {
            LLMProviderType.GROQ: GroqProvider,
        }
        
        # Add other providers if available
        if HuggingFaceProvider is not None:
            provider_map[LLMProviderType.HUGGINGFACE] = HuggingFaceProvider
        if OpenRouterProvider is not None:
            provider_map[LLMProviderType.OPENROUTER] = OpenRouterProvider
        
        for provider_type, provider_class in provider_map.items():
            try:
                provider = provider_class(self.config.dict())
                if provider.is_available:
                    self.providers[provider_type] = provider
            except Exception as e:
                print(f"Failed to initialize {provider_type}: {e}")
    
    async def generate_with_fallback(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        """Generate completion with automatic fallback"""
        
        provider_chain = self.config.get_provider_chain()
        last_error = None
        
        for provider_type in provider_chain:
            if provider_type not in self.providers:
                continue
            
            provider = self.providers[provider_type]
            
            for attempt in range(self.config.max_retries):
                try:
                    response = await provider.generate(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs
                    )
                    return response
                
                except Exception as e:
                    last_error = e
                    print(f"Attempt {attempt + 1} failed for {provider_type}: {e}")
                    
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(self.config.retry_delay)
        
        raise RuntimeError(f"All providers failed. Last error: {last_error}")
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all providers"""
        results = {}
        for provider_type, provider in self.providers.items():
            try:
                results[provider_type.value] = await provider.health_check()
            except Exception:
                results[provider_type.value] = False
        return results
