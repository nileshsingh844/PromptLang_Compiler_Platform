# promptlang/core/llm/base.py
"""
Abstract base classes for LLM providers in PromptLang Compiler Platform
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class LLMResponse(BaseModel):
    """Standardized LLM response across all providers"""
    
    content: str = Field(..., description="Generated text content")
    model: str = Field(..., description="Model identifier used")
    provider: str = Field(..., description="Provider name (groq, huggingface, etc)")
    tokens_used: int = Field(..., description="Total tokens consumed")
    latency_ms: float = Field(..., description="Response latency in milliseconds")
    cached: bool = Field(default=False, description="Whether response was cached")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Generated IR JSON...",
                "model": "llama-3.1-8b-instant",
                "provider": "groq",
                "tokens_used": 1250,
                "latency_ms": 85.3,
                "cached": False
            }
        }


class LLMProvider(ABC):
    """Abstract base class for all LLM providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        """Generate completion from prompt"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is healthy and responding"""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider has valid configuration"""
        pass
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider metadata"""
        return {
            "name": self.provider_name,
            "available": self.is_available,
            "config_keys": list(self.config.keys())
        }


class LLMProviderError(Exception):
    """Base exception for LLM provider errors"""
    def __init__(self, provider: str, message: str):
        self.provider = provider
        self.message = message
        super().__init__(f"[{provider}] {message}")


class RateLimitError(LLMProviderError):
    """Rate limit exceeded error"""
    def __init__(self, provider: str, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        message = f"Rate limit exceeded"
        if retry_after:
            message += f", retry after {retry_after}s"
        super().__init__(provider, message)


class AuthenticationError(LLMProviderError):
    """Invalid API key or authentication error"""
    pass


class InvalidResponseError(LLMProviderError):
    """Provider returned invalid/unparseable response"""
    pass


class TimeoutError(LLMProviderError):
    """Request timed out"""
    pass
