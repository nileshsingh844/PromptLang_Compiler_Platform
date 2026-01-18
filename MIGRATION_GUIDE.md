# Free LLM Integration - Migration Guide

## What Changed?

This migration adds support for **free LLM providers** (Groq, HuggingFace, OpenRouter) 
to replace mock providers in Stages 2 (IR Translation) and 7 (Scaffold Generation).

## New Files Added

```
promptlang/core/llm/
├── __init__.py              # Module exports
├── base.py                  # Abstract provider interface
├── config.py                # Configuration management
├── manager.py               # Provider manager with fallback
└── providers/
    ├── __init__.py
    ├── groq_provider.py     # Groq implementation
    ├── huggingface_provider.py
    └── openrouter_provider.py
```

## Dependencies Added

- `openai>=1.0.0` - For Groq and OpenRouter
- `huggingface-hub>=0.20.0` - For HuggingFace
- `aiohttp>=3.9.0` - Async HTTP
- `tenacity>=8.2.0` - Retry logic
- `python-dotenv>=1.0.0` - Environment variables

## Configuration Required

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Get Free API Keys (Choose One or More)

**Recommended: Groq (Fastest)**
1. Visit https://console.groq.com
2. Sign up (free)
3. Create API key
4. Copy key

**Alternative: HuggingFace**
1. Visit https://huggingface.co/settings/tokens
2. Create token with "read" access
3. Copy token

**Alternative: OpenRouter**
1. Visit https://openrouter.ai/keys
2. Sign up (free)
3. Create key
4. Copy key

### Step 3: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
# Set your API key(s):
GROQ_API_KEY=gsk_your_key_here
# OR
HF_TOKEN=hf_your_token_here
# OR
OPENROUTER_API_KEY=sk-or-your_key_here

# Set primary provider
PROMPTLANG_PRIMARY_PROVIDER=groq
```

### Step 4: Test Integration

```bash
# Test CLI
promptlang generate "Create a FastAPI REST API" --model oss

# Test Python
python -c "
from promptlang.core.llm.config import LLMConfig
from promptlang.core.llm.manager import LLMProviderManager
import asyncio

async def test():
    config = LLMConfig()
    manager = LLMProviderManager(config)
    response = await manager.generate_with_fallback('test')
    print(f'Provider: {response.provider}')
    print(f'Success: {response.content[:50]}...')

asyncio.run(test())
"
```

## Zero-Budget Mode (No API Keys)

If you don't have API keys yet, the system still works with Ollama or Mock:

```bash
# Use Ollama (local, unlimited)
export PROMPTLANG_PRIMARY_PROVIDER=ollama
ollama pull llama3.1

# OR use Mock (deterministic responses)
export PROMPTLANG_PRIMARY_PROVIDER=mock
```

## Provider Comparison

| Provider | Setup | Free Tier | Speed | Best For |
|----------|-------|-----------|-------|----------|
| Groq | 2 min | 1K/day | < 50ms | Production |
| HuggingFace | 2 min | 2K/mo | 200-500ms | Diversity |
| OpenRouter | 2 min | Varies | 100-300ms | Experimentation |
| Ollama | 5 min | Unlimited | 1-5s | Privacy/Offline |

## Troubleshooting

### Issue: "Provider not available"
```bash
# Check environment variable is set
echo $GROQ_API_KEY

# Verify in code
python -c "import os; print(os.getenv('GROQ_API_KEY'))"
```

### Issue: "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Issue: "Rate limit exceeded"
- Wait for reset (usually 1 minute)
- System automatically falls back to next provider
- Check usage on provider dashboard

## Rollback (if needed)

```bash
# Restore original requirements.txt
cp requirements.txt.backup requirements.txt

# Remove LLM module
rm -rf promptlang/core/llm/

# Restore .env.example
cp .env.example.backup .env.example

# Reinstall
pip install -r requirements.txt
```

## Support

- GitHub Issues: https://github.com/nileshsingh844/PromptLang_Compiler_Platform/issues
- Documentation: See README.md
