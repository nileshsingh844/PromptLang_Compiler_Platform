# promptlang/core/llm/config.py
"""Configuration management for LLM providers"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, validator
import os


class LLMProviderType(str, Enum):
    """Available LLM provider types"""
    GROQ = "groq"
    HUGGINGFACE = "huggingface"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    MOCK = "mock"


class LLMConfig(BaseModel):
    """Configuration for LLM Provider Manager"""
    
    # Provider selection
    primary_provider: LLMProviderType = Field(
        default=LLMProviderType.GROQ,
        description="Primary provider to use"
    )
    fallback_providers: List[LLMProviderType] = Field(
        default=[
            LLMProviderType.HUGGINGFACE,
            LLMProviderType.OPENROUTER,
            LLMProviderType.OLLAMA,
            LLMProviderType.MOCK
        ],
        description="Ordered list of fallback providers"
    )
    
    # API Keys (Optional - free tiers available)
    groq_api_key: Optional[str] = Field(default=None)
    hf_token: Optional[str] = Field(default=None)
    gemini_api_key: Optional[str] = Field(default=None)
    openrouter_api_key: Optional[str] = Field(default=None)
    
    # Ollama configuration
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="llama3.1")
    
    # Model defaults
    groq_model: str = Field(default="llama-3.1-8b-instant")
    hf_model: str = Field(default="mistralai/Mistral-7B-Instruct-v0.3")
    openrouter_model: str = Field(default="meta-llama/llama-3.1-8b-instruct:free")
    
    # Retry & timeout settings
    max_retries: int = Field(default=3, ge=1, le=10)
    retry_delay: float = Field(default=1.0, ge=0.1, le=10.0)
    timeout: int = Field(default=30, ge=5, le=120)
    
    # Caching
    enable_response_cache: bool = Field(default=True)
    cache_ttl: int = Field(default=3600)
    
    class Config:
        env_prefix = "PROMPTLANG_"
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @validator("groq_api_key", pre=True, always=True)
    def set_groq_key(cls, v):
        return v or os.getenv("GROQ_API_KEY")
    
    @validator("hf_token", pre=True, always=True)
    def set_hf_token(cls, v):
        return v or os.getenv("HF_TOKEN")
    
    @validator("gemini_api_key", pre=True, always=True)
    def set_gemini_key(cls, v):
        return v or os.getenv("GEMINI_API_KEY")
    
    @validator("openrouter_api_key", pre=True, always=True)
    def set_openrouter_key(cls, v):
        return v or os.getenv("OPENROUTER_API_KEY")
    
    def get_provider_chain(self) -> List[LLMProviderType]:
        """Get ordered provider chain for fallback"""
        chain = [self.primary_provider]
        chain.extend([p for p in self.fallback_providers if p != self.primary_provider])
        return chain


def get_zero_budget_config() -> LLMConfig:
    """Configuration for zero-budget mode (no API keys required)"""
    return LLMConfig(
        primary_provider=LLMProviderType.OLLAMA,
        fallback_providers=[LLMProviderType.MOCK]
    )


def get_free_tier_config() -> LLMConfig:
    """Configuration using free tier providers (requires API keys)"""
    return LLMConfig(
        primary_provider=LLMProviderType.GROQ,
        fallback_providers=[
            LLMProviderType.HUGGINGFACE,
            LLMProviderType.OPENROUTER,
            LLMProviderType.OLLAMA,
            LLMProviderType.MOCK
        ]
    )
