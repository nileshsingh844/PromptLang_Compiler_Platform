# Free LLM Providers - Setup Guide

## Quick Start (5 Minutes)

### 1. Choose Provider

We recommend **Groq** for fastest performance:

**Groq** (Recommended)
- Speed: < 50ms latency
- Free: 1,000 requests/day
- Signup: https://console.groq.com

**Alternatives:**
- HuggingFace: https://huggingface.co/settings/tokens
- OpenRouter: https://openrouter.ai/keys
- Ollama: Local, unlimited (requires installation)

### 2. Get API Key

1. Visit provider website (links above)
2. Sign up for free account
3. Create API key
4. Copy the key

### 3. Configure

```bash
# Set environment variable
export GROQ_API_KEY="gsk_your_key_here"
export PROMPTLANG_PRIMARY_PROVIDER=groq

# OR create .env file
echo "GROQ_API_KEY=gsk_your_key_here" > .env
echo "PROMPTLANG_PRIMARY_PROVIDER=groq" >> .env
```

### 4. Test

```bash
# Test with PromptLang CLI
promptlang generate "Create a REST API" --model oss

# Should see output from Groq (not mock)
```

## Provider Details

### Groq (Recommended)

**Pros:**
- Ultra-fast (< 50ms)
- Reliable
- Good free tier
- OpenAI-compatible API

**Setup:**
```bash
# 1. Get key from https://console.groq.com
# 2. Configure
export GROQ_API_KEY="gsk_..."
export PROMPTLANG_PRIMARY_PROVIDER=groq

# 3. Test
python -c "
from promptlang.core.llm.providers.groq_provider import GroqProvider
import asyncio

async def test():
    provider = GroqProvider({'groq_api_key': 'gsk_...'})
    print('Available:', provider.is_available)
    
asyncio.run(test())
"
```

### HuggingFace

**Pros:**
- 500K+ models
- Good for experimentation
- Active community

**Setup:**
```bash
export HF_TOKEN="hf_..."
export PROMPTLANG_PRIMARY_PROVIDER=huggingface
```

### OpenRouter

**Pros:**
- Access 100+ models
- Unified API
- Free models available

**Setup:**
```bash
export OPENROUTER_API_KEY="sk-or-..."
export PROMPTLANG_PRIMARY_PROVIDER=openrouter
```

### Ollama (Local)

**Pros:**
- Completely free
- Unlimited usage
- Privacy
- Works offline

**Setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama3.1

# Configure PromptLang
export PROMPTLANG_PRIMARY_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama3.1
```

## Multi-Provider Fallback

Configure automatic fallback:

```python
# In .env
PROMPTLANG_PRIMARY_PROVIDER=groq
PROMPTLANG_FALLBACK_PROVIDERS=huggingface,openrouter,ollama,mock

# Or in code
from promptlang.core.llm.config import LLMConfig

config = LLMConfig(
    primary_provider="groq",
    fallback_providers=["huggingface", "openrouter", "ollama", "mock"]
)
```

System will try providers in order until one succeeds.

## Monitoring Usage

Check your usage on provider dashboards:

- Groq: https://console.groq.com/settings/limits
- HuggingFace: https://huggingface.co/settings/billing
- OpenRouter: https://openrouter.ai/activity

## Cost Estimates

All providers have generous free tiers:

| Provider | Free Tier | Cost After |
|----------|-----------|------------|
| Groq | 1K req/day | Contact sales |
| HuggingFace | 2K req/mo | Pay-as-you-go |
| OpenRouter | Varies | $0.06-$1.50/M tokens |
| Ollama | Unlimited | $0 (local) |

For PromptLang typical usage (~2500 tokens/pipeline):
- Groq: ~1000 pipelines/day free
- HuggingFace: ~800 pipelines/month free

## Best Practices

1. **Start with Groq** - Fastest and most reliable
2. **Add fallbacks** - HuggingFace or OpenRouter as backup
3. **Keep Ollama** - Ultimate fallback for offline
4. **Monitor usage** - Check dashboards regularly
5. **Rotate keys** - Every 90 days for security

## Need Help?

- Issues: https://github.com/nileshsingh844/PromptLang_Compiler_Platform/issues
- Docs: See MIGRATION_GUIDE.md
- Provider docs: Links in this file
