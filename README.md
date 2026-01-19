# PromptLang Compiler Platform

🚀 **Transform Human Input → PromptLang IR → Optimized IR → Model Dialect → Contract Enforced Output**

A production-grade compiler system with **ultra-fast Groq LLM integration** for real-time generation.

## ⚡ Quick Start (3 Commands)

```bash
# 1. Set your Groq API key (get free at https://console.groq.com)
export GROQ_API_KEY="gsk_your_api_key_here"

# 2. Start the application
./start-groq.sh

# 3. Open your browser
open http://localhost:3000
```

## 🎯 Alternative Startup Options

```bash
# Groq Mode (Ultra-fast - Recommended)
./start-groq.sh
# or
./start.sh groq

# Mock Mode (Offline - No API key)
./start.sh

# Ollama Mode (Local LLM)
./start.sh ollama
```

## 🌟 Key Features

✅ **Ultra-Fast Groq Integration** - Llama 3.1 8B Instant model  
✅ **Real-Time Generation** - Live IR translation and scaffold generation  
✅ **3-Command Setup** - Get running in under 30 seconds  
✅ **Free Tier Available** - 1,000 requests/day free  
✅ **Smart Fallbacks** - Automatic fallback to offline mode  
✅ **Modern Web UI** - Next.js frontend with Tailwind CSS  
✅ **Complete Pipeline** - All 8 stages working seamlessly  
✅ **Production Ready** - FastAPI backend with OpenAPI docs  

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 16+**
- **Groq API Key** (free at https://console.groq.com)

## 🔧 One-Time Installation

```bash
# Clone the repository
git clone https://github.com/nileshsingh844/PromptLang_Compiler_Platform.git
cd PromptLang_Compiler_Platform

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Setup frontend
cd webapp && npm install && cd ..

# Make scripts executable
chmod +x start-groq.sh start.sh
```

## 🏗️ Project Structure

```
PromptLang_Compiler_Platform/
├── 📁 src/                          # Backend Python Application
│   ├── 📁 promptlang/               # Main application package
│   │   ├── 📁 api/                  # FastAPI REST API
│   │   │   ├── 📁 models/           # Pydantic request/response models
│   │   │   │   ├── 📄 requests.py   # API request schemas
│   │   │   │   └── 📄 responses.py  # API response schemas
│   │   │   ├── 📁 routes/           # API endpoint handlers
│   │   │   │   ├── 📄 generate.py   # Main generation endpoint
│   │   │   │   ├── 📄 diagrams.py    # Diagram generation endpoint
│   │   │   │   ├── 📄 optimize.py    # IR optimization endpoint
│   │   │   │   ├── 📄 validate.py    # Validation endpoint
│   │   │   │   └── 📄 __init__.py
│   │   │   └── 📄 main.py            # FastAPI application entry point
│   │   ├── 📁 cli/                   # Command-line interface
│   │   │   ├── 📄 main.py            # CLI entry point
│   │   │   └── 📄 __init__.py
│   │   └── 📁 core/                 # Core processing modules
│   │       ├── 📁 cache/             # Multi-level caching system
│   │       │   ├── 📄 l1_cache.py    # In-memory cache
│   │       │   ├── 📄 l2_cache.py    # Persistent cache
│   │       │   ├── 📄 manager.py     # Cache orchestration
│   │       │   └── 📄 __init__.py
│   │       ├── 📁 clarification/     # Input clarification engine
│   │       │   ├── 📄 engine.py      # Clarification logic
│   │       │   └── 📄 __init__.py
│   │       ├── 📁 compiler/          # Dialect compilation
│   │       │   ├── 📁 dialects/      # Model-specific dialects
│   │       │   │   ├── 📄 claude.py   # Claude model dialect
│   │       │   │   ├── 📄 gpt.py      # GPT model dialect
│   │       │   │   ├── 📄 oss.py      # Open-source model dialect
│   │       │   │   └── 📄 __init__.py
│   │       │   ├── 📄 dialect_compiler.py # Dialect compiler
│   │       │   └── 📄 __init__.py
│   │       ├── 📁 diagram/           # Diagram generation system
│   │       │   ├── 📄 analyzer.py    # Project context analysis
│   │       │   ├── 📄 catalog.py     # Diagram type catalog
│   │       │   ├── 📄 generator_simple.py # Simple diagram generator
│   │       │   ├── 📄 pipeline.py    # Diagram generation pipeline
│   │       │   ├── 📄 scorer.py      # Diagram relevance scoring
│   │       │   └── 📄 __init__.py
│   │       ├── 📁 generator/         # Code generation
│   │       │   ├── 📄 scaffold.py    # Project scaffolding
│   │       │   └── 📄 __init__.py
│   │       ├── 📁 intent/            # Intent recognition
│   │       │   ├── 📄 router.py      # Intent routing logic
│   │       │   └── 📄 __init__.py
│   │       ├── 📁 ir/                # Intermediate Representation
│   │       │   ├── 📄 schema_loader.py # IR schema loading
│   │       │   ├── 📄 validator.py   # IR validation
│   │       │   └── 📄 __init__.py
│   │       ├── 📁 linter/            # Code linting and quality
│   │       │   ├── 📄 rules.py       # Linting rules
│   │       │   └── 📄 __init__.py
│   │       ├── 📁 llm/               # LLM provider abstraction
│   │       │   ├── 📁 providers/     # LLM provider implementations
│   │       │   │   ├── 📄 groq_provider.py # Groq API provider
│   │       │   │   ├── 📄 huggingface_provider.py # HuggingFace provider
│   │       │   │   ├── 📄 openrouter_provider.py # OpenRouter provider
│   │       │   │   └── 📄 __init__.py
│   │       │   ├── 📄 base.py        # Base LLM interface
│   │       │   ├── 📄 config.py      # LLM configuration
│   │       │   ├── 📄 manager.py     # LLM provider manager
│   │       │   └── 📄 __init__.py
│   │       ├── 📁 optimizer/         # Token optimization
│   │       │   ├── 📄 strategies.py   # Optimization strategies
│   │       │   ├── 📄 token_optimizer.py # Token optimization logic
│   │       │   └── 📄 __init__.py
│   │       ├── 📁 pipeline/          # Processing pipeline
│   │       │   ├── 📄 orchestrator.py # Pipeline orchestration
│   │       │   ├── 📄 stages.py      # Pipeline stage definitions
│   │       │   └── 📄 __init__.py
│   │       ├── 📁 translator/        # IR translation
│   │       │   ├── 📄 ir_builder.py  # IR construction
│   │       │   ├── 📄 llm_provider.py # LLM-based translation
│   │       │   └── 📄 __init__.py
│   │       ├── 📁 utils/             # Utility functions
│   │       │   ├── 📄 hashing.py     # Hashing utilities
│   │       │   ├── 📄 timing.py      # Timing utilities
│   │       │   └── 📄 __init__.py
│   │       ├── 📁 validator/         # Output validation
│   │       │   ├── 📄 contract.py    # Contract validation
│   │       │   ├── 📄 output_validator.py # Output validation
│   │       │   ├── 📄 parsers.py     # Validation parsers
│   │       │   ├── 📄 quality.py     # Quality validation
│   │       │   ├── 📄 security.py    # Security validation
│   │       │   ├── 📄 syntax.py      # Syntax validation
│   │       │   └── 📄 __init__.py
│   │       └── 📄 __init__.py
│   └── 📁 schemas/                  # JSON schemas
│       └── 📄 ir_v2.1.json          # IR schema definition
├── 📁 webapp/                       # Next.js Frontend Application
│   ├── 📁 app/                      # Next.js app directory
│   │   ├── 📁 test-mermaid/         # Mermaid testing page
│   │   │   └── 📄 page.tsx          # Test page component
│   │   ├── 📄 globals.css           # Global styles
│   │   ├── 📄 layout.tsx            # Root layout component
│   │   └── 📄 page.tsx              # Main page component
│   ├── 📁 components/               # React components
│   │   ├── 📁 ui/                   # UI component library
│   │   │   ├── 📄 badge.tsx         # Badge component
│   │   │   ├── 📄 button.tsx        # Button component
│   │   │   ├── 📄 card.tsx          # Card component
│   │   │   ├── 📄 copy-button.tsx   # Copy button component
│   │   │   ├── 📄 tabs.tsx          # Tabs component
│   │   │   ├── 📄 textarea.tsx      # Textarea component
│   │   │   └── 📄 theme-toggle.tsx  # Theme toggle component
│   │   ├── 📄 mermaid-diagram.tsx   # Mermaid diagram component
│   │   └── 📄 theme-provider.tsx   # Theme context provider
│   ├── 📁 lib/                      # Utility libraries
│   │   ├── 📄 api.ts                # API client
│   │   ├── 📄 mermaid-utils.ts      # Mermaid utilities
│   │   └── 📄 utils.ts              # General utilities
│   ├── 📄 next.config.js            # Next.js configuration
│   ├── 📄 next-env.d.ts             # Next.js type definitions
│   ├── 📄 package.json              # Node.js dependencies
│   ├── 📄 package-lock.json         # Locked dependencies
│   ├── 📄 postcss.config.js         # PostCSS configuration
│   ├── 📄 tailwind.config.js        # Tailwind CSS configuration
│   └── 📄 tsconfig.json             # TypeScript configuration
├── 📁 tests/                        # Test suite
│   ├── 📁 fixtures/                 # Test fixtures
│   │   ├── 📄 debug_python.json     # Debug test fixture
│   │   ├── 📄 refactor_react.json   # Refactor test fixture
│   │   └── 📄 scaffold_fastapi.json # Scaffold test fixture
│   ├── 📁 integration/              # Integration tests
│   │   ├── 📄 test_pipeline.py      # Pipeline integration tests
│   │   └── 📄 __init__.py
│   ├── 📁 unit/                     # Unit tests
│   │   ├── 📄 test_intent_router.py # Intent router tests
│   │   ├── 📄 test_ir_validator.py  # IR validator tests
│   │   ├── 📄 test_token_optimizer.py # Token optimizer tests
│   │   └── 📄 __init__.py
│   └── 📄 __init__.py
├── 📁 diagrams/                     # Generated diagram assets
│   ├── 📄 adr.svg                   # Architecture Decision Records
│   ├── 📄 api_overview.svg          # API overview diagram
│   ├── 📄 blockchain_architecture.svg # Blockchain architecture
│   ├── 📄 business_model_canvas.svg # Business model canvas
│   ├── 📄 c4_l1_context.svg         # C4 Level 1 Context
│   ├── 📄 c4_l2_container.svg        # C4 Level 2 Container
│   ├── 📄 c4_l3_component.svg        # C4 Level 3 Component
│   ├── 📄 c4_l4_code.svg             # C4 Level 4 Code
│   ├── 📄 ci_pipeline.svg           # CI/CD pipeline
│   ├── 📄 class_diagram.svg          # UML class diagram
│   ├── 📄 cloud_architecture.svg     # Cloud architecture
│   ├── 📄 compliance_matrix.svg      # Compliance matrix
│   ├── 📄 database_schema.svg        # Database schema
│   ├── 📄 domain_model.svg           # Domain model
│   ├── 📄 er_diagram.svg             # Entity-relationship diagram
│   ├── 📄 gantt_chart.svg            # Gantt chart
│   ├── 📄 hld.svg                    # High-level design
│   ├── 📄 iot_architecture.svg       # IoT architecture
│   ├── 📄 lld.svg                    # Low-level design
│   ├── 📄 ml_pipeline.svg            # Machine learning pipeline
│   ├── 📄 monitoring_dashboard.svg    # Monitoring dashboard
│   ├── 📄 performance_architecture.svg # Performance architecture
│   ├── 📄 service_dependency_graph.svg # Service dependencies
│   ├── 📄 swimlane_diagram.svg       # Swimlane diagram
│   ├── 📄 system_context.svg         # System context
│   ├── 📄 system_landscape.svg       # System landscape
│   ├── 📄 test_pyramid.svg           # Testing pyramid
│   ├── 📄 threat_model.svg           # Threat model
│   ├── 📄 uml_sequence.svg           # UML sequence diagram
│   ├── 📄 use_case_diagram.svg       # Use case diagram
│   └── 📄 user_flow.svg              # User flow diagram
├── 📁 docker/                       # Docker configuration
│   ├── 📄 docker-compose.yml        # Docker Compose configuration
│   └── 📄 Dockerfile                # Docker image definition
├── 📄 FREE_LLM_SETUP.md             # Free LLM setup guide
├── 📄 GROQ_SETUP.md                 # Groq API setup guide
├── 📄 MIGRATION_GUIDE.md            # Migration instructions
├── 📄 pyproject.toml                # Python project configuration
├── 📄 README_GROQ.md               # Groq-specific README
├── 📄 README.md                     # Main project documentation
├── 📄 requirements.txt              # Python dependencies
├── 📄 start-groq.sh                 # Groq startup script
├── 📄 start.sh                     # General startup script
├── 📄 WEBAPP_SETUP.md              # Webapp setup guide
└── 📄 ZERO_BUDGET_MODE.md           # Zero-budget mode guide
```

## 🚀 Architecture Overview

### Backend Architecture (Python/FastAPI)

The backend follows a modular, microservice-oriented architecture with clear separation of concerns:

#### **Core Processing Pipeline**
```
Human Input → Intent Recognition → IR Generation → Optimization → Compilation → Output
```

#### **Key Components**

1. **API Layer** (`src/promptlang/api/`)
   - FastAPI REST endpoints
   - Request/response validation
   - Error handling and logging

2. **Core Processing** (`src/promptlang/core/`)
   - **Intent Router**: Identifies user intent and routes to appropriate processors
   - **IR System**: Intermediate Representation for structured data
   - **Compiler**: Translates IR to model-specific dialects
   - **LLM Manager**: Abstraction layer for multiple LLM providers
   - **Validator**: Ensures output quality and compliance
   - **Cache System**: Multi-level caching for performance

3. **Diagram Generation** (`src/promptlang/core/diagram/`)
   - **Analyzer**: Extracts project context
   - **Scorer**: Ranks diagram relevance
   - **Pipeline**: Orchestrates diagram generation
   - **Generator**: Creates Mermaid diagrams

### Frontend Architecture (Next.js/React)

Modern React application with TypeScript and Tailwind CSS:

#### **Component Structure**
```
webapp/
├── app/                    # Next.js app router
├── components/             # React components
│   ├── ui/                # Reusable UI components
│   └── specialized/       # Feature-specific components
└── lib/                   # Utility libraries
```

#### **Key Features**
- **Responsive Design**: Mobile-first approach
- **Dark Mode**: Theme switching support
- **Real-time Updates**: Live diagram generation
- **Copy/Export**: Multiple export options
- **Error Handling**: Comprehensive error states

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.12+
- **LLM Providers**: Groq, OpenRouter, HuggingFace
- **Caching**: Redis (L2), Memory (L1)
- **Validation**: Pydantic
- **Testing**: pytest

### Frontend
- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom component library
- **State Management**: React hooks
- **Diagrams**: Mermaid.js

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Version Control**: Git
- **Package Management**: pip (Python), npm (Node.js)

## 📊 Data Flow

### Generation Pipeline
1. **Input Processing**: Parse and validate user input
2. **Intent Recognition**: Identify generation intent (scaffold, debug, refactor)
3. **IR Generation**: Create structured intermediate representation
4. **Optimization**: Token usage and quality optimization
5. **Compilation**: Convert to model-specific dialect
6. **Validation**: Ensure output quality and compliance
7. **Response**: Return structured results

### Diagram Pipeline
1. **Context Analysis**: Extract project information
2. **Diagram Selection**: Score and rank relevant diagrams
3. **Generation**: Create Mermaid diagram syntax
4. **Validation**: Ensure diagram quality
5. **Export**: Multiple format options

## 🔧 Configuration

### Environment Variables
```bash
# Backend
GROQ_API_KEY=your_groq_api_key
OPENROUTER_API_KEY=your_openrouter_key
HUGGINGFACE_API_KEY=your_huggingface_key
REDIS_URL=redis://localhost:6379

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MERMAID_CONFIG=your_mermaid_config
```

### Model Configuration
```python
# pyproject.toml
[tool.promptlang]
default_model = "groq"
max_tokens = 4000
cache_ttl = 3600
validation_mode = "strict"
```

## 🧪 Testing Strategy

### Backend Tests
- **Unit Tests**: Individual component testing
- **Integration Tests**: Pipeline testing
- **Fixtures**: Sample data for testing

### Frontend Tests
- **Component Tests**: React component testing
- **E2E Tests**: Full user flows
- **Visual Tests**: UI consistency

## 📦 Deployment

### Development
promptlang optimize tests/fixtures/scaffold_fastapi.json --budget 3000
```

## 📊 Performance with Groq

- **IR Translation**: ~600ms (Stage 2)
- **Scaffold Generation**: ~2.5s (Stage 7)  
- **Total Pipeline**: ~3.5s
- **Model**: Llama 3.1 8B Instant
- **Quality**: High-fidelity, structured output

## 🔄 Provider Switching

```bash
# Switch providers at runtime
export LLM_PROVIDER=groq     # Ultra-fast (requires API key)
export LLM_PROVIDER=mock     # Offline mode (default)
export LLM_PROVIDER=ollama   # Local LLM
```

## 🚨 Troubleshooting

### Backend Issues
```bash
# Check logs
tail -f /tmp/promptlang-backend.log

# Restart backend
pkill -f uvicorn && ./start-groq.sh
```

### Frontend Issues  
```bash
# Check logs
tail -f /tmp/promptlang-frontend.log

# Reinstall dependencies
cd webapp && rm -rf node_modules && npm install
```

### Groq API Issues
```bash
# Verify API key
curl -H "Authorization: Bearer $GROQ_API_KEY" \
  https://api.groq.com/openai/v1/models

# Check environment
echo $GROQ_API_KEY
```

## 📚 Documentation

- **📖 Groq Setup Guide**: See `GROQ_SETUP.md`
- **📖 Detailed Architecture**: See `README_GROQ.md`  
- **📖 API Reference**: http://localhost:8000/docs
- **📖 Testing Guide**: See `tests/` directory

## 🏗️ Architecture Overview

PromptLang implements an 8-stage pipeline:

1. **Input Normalization** → 2. **Intent Routing** → 3. **Clarification** → 4. **IR Translation** → 5. **Schema Validation** → 6. **IR Linting** → 7. **Token Optimization** → 8. **Dialect Compilation** → 9. **Scaffold Generation** → 10. **Output Validation**

**Stages 4 & 5 run concurrently. Stage 8 sub-checks run concurrently.**

## 🎯 Next Steps

1. **Get Groq API Key**: https://console.groq.com
2. **Run `./start-groq.sh`**: Start with ultra-fast inference
3. **Open Browser**: http://localhost:3000
4. **Generate Projects**: Create with real-time LLM power
5. **Explore Features**: Check all pipeline stages and metrics

---

**🚀 Experience ultra-fast LLM inference with PromptLang + Groq!**

**GitHub**: https://github.com/nileshsingh844/PromptLang_Compiler_Platform  
**License**: MIT