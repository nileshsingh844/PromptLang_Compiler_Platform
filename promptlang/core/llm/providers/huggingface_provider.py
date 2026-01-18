# promptlang/core/llm/providers/huggingface_provider.py
"""HuggingFace Serverless Inference provider"""

import os
import time
from typing import Dict, Any, Optional
from huggingface_hub import AsyncInferenceClient
from ..base import LLMProvider, LLMResponse, LLMProviderError


class HuggingFaceProvider(LLMProvider):
    """HuggingFace Serverless Inference (Free: 2K req/mo)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.token = config.get("hf_token") or os.getenv("HF_TOKEN")
        self.client = AsyncInferenceClient(token=self.token) if self.token else None
        self.default_model = config.get("hf_model", "mistralai/Mistral-7B-Instruct-v0.3")
    
    @property
    def is_available(self) -> bool:
        return self.token is not None
    
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
            raise RuntimeError("HuggingFace provider not configured. Set HF_TOKEN.")
        
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        start_time = time.time()
        
        try:
            response = await self.client.text_generation(
                model=kwargs.get("model", self.default_model),
                prompt=full_prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                return_full_text=False
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return LLMResponse(
                content=response,
                model=kwargs.get("model", self.default_model),
                provider="huggingface",
                tokens_used=len(response.split()),
                latency_ms=latency_ms
            )
        except Exception as e:
            raise LLMProviderError(self.provider_name, str(e))
