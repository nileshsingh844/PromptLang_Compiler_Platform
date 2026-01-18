# promptlang/core/llm/providers/groq_provider.py
"""Groq LPU-powered inference provider - Ultra-fast, free tier available"""

import os
import time
from typing import Dict, Any, Optional
from openai import AsyncOpenAI, APIError, RateLimitError as OpenAIRateLimitError
import asyncio

from ..base import (
    LLMProvider, LLMResponse, LLMProviderError,
    RateLimitError, AuthenticationError, InvalidResponseError,
    TimeoutError as LLMTimeoutError
)


class GroqProvider(LLMProvider):
    """Groq LPU-powered inference provider (Free: 1K req/day, 6K tokens/min)"""
    
    BASE_URL = "https://api.groq.com/openai/v1"
    AVAILABLE_MODELS = {
        "llama-3.1-8b-instant": "Meta Llama 3.1 8B (fastest)",
        "llama-3.1-70b-versatile": "Meta Llama 3.1 70B (most capable)",
        "mixtral-8x7b-32768": "Mixtral 8x7B (long context)",
    }
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("groq_api_key") or os.getenv("GROQ_API_KEY")
        self.default_model = config.get("groq_model", "llama-3.1-8b-instant")
        self.timeout = config.get("timeout", 30)
        
        if self.api_key:
            self.client = AsyncOpenAI(
                base_url=self.BASE_URL,
                api_key=self.api_key,
                timeout=self.timeout
            )
        else:
            self.client = None
    
    @property
    def is_available(self) -> bool:
        return self.api_key is not None and self.client is not None
    
    async def health_check(self) -> bool:
        if not self.is_available:
            return False
        try:
            await self.generate(prompt="test", max_tokens=5, temperature=0.0)
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
            raise RuntimeError("Groq provider not configured. Set GROQ_API_KEY.")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        model = kwargs.pop("model", self.default_model)
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                provider="groq",
                tokens_used=response.usage.total_tokens,
                latency_ms=latency_ms,
                metadata={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "finish_reason": response.choices[0].finish_reason
                }
            )
        
        except OpenAIRateLimitError as e:
            retry_after = getattr(e, "retry_after", None)
            raise RateLimitError(self.provider_name, retry_after)
        except APIError as e:
            if e.status_code == 401:
                raise AuthenticationError(self.provider_name, "Invalid API key")
            raise LLMProviderError(self.provider_name, f"API error: {e.message}")
        except asyncio.TimeoutError:
            raise LLMTimeoutError(self.provider_name, f"Timeout after {self.timeout}s")
        except Exception as e:
            raise LLMProviderError(self.provider_name, f"Error: {str(e)}")
