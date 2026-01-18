# promptlang/core/llm/providers/openrouter_provider.py
"""OpenRouter multi-model aggregator provider"""

import os
import time
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from ..base import LLMProvider, LLMResponse, LLMProviderError


class OpenRouterProvider(LLMProvider):
    """OpenRouter (Access 100+ models, many free)"""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("openrouter_api_key") or os.getenv("OPENROUTER_API_KEY")
        self.client = AsyncOpenAI(
            base_url=self.BASE_URL,
            api_key=self.api_key
        ) if self.api_key else None
        self.default_model = config.get("openrouter_model", "meta-llama/llama-3.1-8b-instruct:free")
    
    @property
    def is_available(self) -> bool:
        return self.api_key is not None
    
    async def health_check(self) -> bool:
        if not self.is_available:
            return False
        try:
            await self.generate("test", max_tokens=5)
            return True
        except Exception:
            return False
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        if not self.is_available:
            raise RuntimeError("OpenRouter not configured. Set OPENROUTER_API_KEY.")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=kwargs.get("model", self.default_model),
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                provider="openrouter",
                tokens_used=response.usage.total_tokens,
                latency_ms=latency_ms
            )
        except Exception as e:
            raise LLMProviderError(self.provider_name, str(e))
