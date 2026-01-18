# PromptLang Compiler Platform

A production-grade MVP compiler-style system that transforms **Human Input → PromptLang IR → Optimized IR → Model Dialect → Contract Enforced Output → Validation Report + Provenance**.

## Architecture

PromptLang implements a **Hybrid Monolith-First** architecture with stage isolation:

- **IR Frontend Service** → Stages 1-3 (Intent Router, Clarification, IR Translation, Schema Validation)
- **Core Compiler Service** → Stages 4-6 (IR Linter, Token Optimizer, Dialect Compiler)
- **Generator Backend** → Stage 7 (Scaffold Generator)
- **Validation Engine** → Stage 8 (Output Validator with concurrent checks)

Each stage boundary is designed as a network contract (DTO in/out), even within the monolith, enabling future microservice migration.

## Pipeline Stages (0-8)

1. **Stage 0**: Input normalization DTO
2. **Stage 1**: Intent Router (scaffold/debug/refactor/explain/devops)
3. **Stage 1.5**: Clarification Engine (max 3 questions OR assumptions)
4. **Stage 2**: IR Translator (Human → PromptLang IR JSON)
5. **Stage 3**: Schema Validator (Draft-07 + retry + fallback)
6. **Stage 4**: IR Linter (deterministic)
7. **Stage 5**: Token Optimizer (semantic chunking, dedupe, priority compression)
8. **Stage 6**: Target Compiler (dialects: Claude/GPT/OSS)
9. **Stage 7**: Scaffold Generator (contract enforced)
10. **Stage 8**: Output Validator (parser + syntax + security + quality + contract)

**Parallelism**: Stages 4 and 5 run concurrently after Stage 3 and merge before Stage 6. Stage 8 sub-checks run concurrently.

## Features

✅ **Complete Pipeline Implementation** (stages 0-8)  
✅ **IR Schema v2.1** (Draft-07 JSON Schema validation)  
✅ **Token Optimization** (semantic chunking, deduplication, priority compression)  
✅ **Dialect Compilers** (Claude XML, GPT JSON, OSS Markdown)  
✅ **Output Contract Enforcement** (strict scaffold mode)  
✅ **Concurrent Validation** (syntax, security, quality, contract)  
✅ **Multi-tier Caching** (L1 in-memory LRU + TTL, L2 Redis optional)  
✅ **Zero-Budget LLM Providers** (Mock default, Ollama optional - no paid keys required)  
✅ **FastAPI REST API** (OpenAPI 3.1 endpoints)  
✅ **CLI Interface** (typer-based commands)  
✅ **Comprehensive Testing** (unit + integration tests)

## Setup

### Prerequisites

- Python 3.11+
- pip
- (Optional) Redis for L2 caching

### Installation

```bash
# Clone repository
cd /path/to/promptlang

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in editable mode
pip install -e .
```

### Environment Variables (Optional)

```bash
# Zero-budget providers (no API keys required)
export LLM_PROVIDER=mock  # Mock provider (default, deterministic, offline)
export LLM_PROVIDER=ollama  # Local Ollama instance (optional, requires local server)

# Ollama configuration (if using ollama provider)
export OLLAMA_BASE_URL=http://localhost:11434  # Default Ollama API URL
export OLLAMA_MODEL=llama2  # Model name (default: llama2)

# Optional caching
export REDIS_URL=redis://localhost:6379/0  # For L2 caching (optional)
export BUILD_HASH=dev  # Build hash for provenance
```

**⚠️ ZERO-BUDGET MODE**: The MVP works completely offline with `LLM_PROVIDER=mock` (default). No paid API keys are required. Optional `ollama` provider uses local HTTP client for local LLM inference.

## Usage

### CLI

```bash
# Generate scaffold
promptlang generate "Create a FastAPI REST API with user authentication" \
  --model oss --budget 5000 --security high --scaffold-mode full

# Validate IR
promptlang validate tests/fixtures/scaffold_fastapi.json

# Optimize IR
promptlang optimize tests/fixtures/scaffold_fastapi.json --budget 3000

# Cache management
promptlang cache stats
promptlang cache clear
```

### API Server

```bash
# Start API server
uvicorn promptlang.api.main:app --host 0.0.0.0 --port 8000 --reload

# API docs available at http://localhost:8000/docs
```

### API Endpoints

#### POST `/api/generate`

Generate prompt and scaffold from human input.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: my-key-123" \
  -d '{
    "input": "Create a FastAPI REST API",
    "intent": "scaffold",
    "target_model": "oss",
    "token_budget": 4000,
    "scaffold_mode": "full",
    "security_level": "high",
    "validation_mode": "strict"
  }'
```

**Response:**
```json
{
  "status": "success",
  "ir_json": { ... },
  "optimized_ir": { ... },
  "compiled_prompt": "## OUTPUT CONTRACT...",
  "output": "## Project Blueprint\n\n...",
  "validation_report": {
    "status": "success",
    "parallel": true,
    "findings": [],
    "contract_compliance": { ... }
  },
  "warnings": [],
  "provenance": {
    "request_id": "...",
    "build_hash": "...",
    "stage_timings_ms": { ... },
    "token_usage": { ... }
  },
  "cache_hit": false
}
```

#### POST `/api/validate`

Validate IR JSON schema.

#### POST `/api/optimize`

Optimize IR for token budget.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=promptlang --cov-report=html

# Run specific test file
pytest tests/unit/test_intent_router.py
pytest tests/integration/test_pipeline.py
```

## Docker

```bash
# Build and run with docker-compose
cd docker
docker-compose up --build

# API available at http://localhost:8000
# Redis available at localhost:6379
```

## Project Structure

```
promptlang/
├── cli/                    # CLI interface (typer)
├── core/
│   ├── pipeline/          # Pipeline orchestrator
│   ├── ir/                # IR schema validation
│   ├── intent/            # Intent routing
│   ├── clarification/     # Clarification engine
│   ├── translator/        # IR translation
│   ├── linter/            # IR linting
│   ├── optimizer/         # Token optimization
│   ├── compiler/          # Dialect compilation
│   ├── generator/         # Scaffold generation
│   ├── validator/         # Output validation
│   ├── cache/             # Cache management
│   └── utils/             # Utilities
├── api/                   # FastAPI application
│   ├── routes/            # API routes
│   └── models/            # Request/response models
├── schemas/               # JSON schemas
│   └── ir_v2.1.json       # IR schema v2.1
├── tests/                 # Tests
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures/          # Test fixtures
└── docker/                # Docker files
```

## Concurrency Implementation

### Stage 4+5 Parallelism

Stages 4 (IR Linter) and 5 (Token Optimizer) run concurrently using `asyncio.create_task()`:

```python
# In orchestrator.py
linter_task = asyncio.create_task(self._run_linter(ir))
optimizer_task = asyncio.create_task(self._run_optimizer(ir, token_budget, intent))

linter_valid, linter_findings = await linter_task
optimized_ir, optimization_warnings = await optimizer_task
```

Both tasks execute in thread pools (`run_in_executor`) for CPU-bound operations.

### Stage 8 Concurrent Validation

Stage 8 runs validation checks concurrently:

- Syntax validation (Python AST, JSON parsing)
- Security scanning (CWE-798, CWE-89, CWE-79)
- Quality checking (docstrings, function length, TODOs)

All validators run in parallel using `asyncio.create_task()` and results are merged.

## Cache Key Generation and Invalidation

### Cache Key Components

Cache keys are generated from:
- `IR_hash`: SHA256 hash of normalized IR (excluding volatile fields)
- `schema_version`: IR schema version (e.g., "2.1.0")
- `compiler_version`: Compiler version (e.g., "0.1.0")
- `target_model`: Target model name (e.g., "oss")

```python
cache_key = generate_cache_key(ir_hash, schema_version, compiler_version, target_model)
```

### Cache Invalidation

**L1 Cache (In-memory):**
- TTL: 5 minutes (configurable)
- LRU eviction when max size (100) reached
- Automatic expiry check on access

**L2 Cache (Redis):**
- TTL: 1 hour (configurable)
- Manual invalidation via `promptlang cache clear`
- Graceful degradation if Redis unavailable

Cache invalidation triggers:
- Schema version change
- Compiler version change
- Manual cache clear command
- TTL expiry

## Zero-Budget Mode (MANDATORY)

The MVP works completely offline with **zero-budget** providers:

### Mock Provider (Default)

- **Provider**: `LLM_PROVIDER=mock` (default)
- Returns deterministic IR JSON from templates
- Generates deterministic scaffold output
- **No external API calls required**
- **No API keys required**
- All tests pass offline

### Ollama Provider (Optional Local)

- **Provider**: `LLM_PROVIDER=ollama`
- Uses local Ollama HTTP API (requires local Ollama server running)
- Falls back to mock if Ollama unavailable
- **No paid API keys required**
- Configure with `OLLAMA_BASE_URL` and `OLLAMA_MODEL` env vars

### Stage 6 Dialect Compiler

- **No API calls** - purely deterministic formatting
- Generates GPT/Claude/OSS formatted prompts from IR
- Works completely offline

### Stage 2 and Stage 7

- **Stage 2** (IR Translation): Uses MockLLMProvider or OllamaProvider
- **Stage 7** (Scaffold Generation): Uses mock generation (works offline)
- Both stages support zero-budget operation

**⚠️ Paid Providers**: OpenAI/Anthropic providers are not implemented in MVP and require paid API keys. Use `mock` or `ollama` for zero-budget operation.

## License

MIT

## Contributing

Contributions welcome! Please ensure tests pass and follow the existing code style.
