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

## 🌐 Access Points

Once running, access the application at:

- **🎨 Frontend**: http://localhost:3000
- **📊 Backend API**: http://localhost:8000  
- **📚 API Documentation**: http://localhost:8000/docs
- **❤️ Health Check**: http://localhost:8000/health

## ⚙️ Configuration

### Environment Variables
```bash
# Required for Groq
export GROQ_API_KEY="your_groq_api_key"
export LLM_PROVIDER=groq
export PROMPTLANG_PRIMARY_PROVIDER=groq

# Optional
export REDIS_URL=redis://localhost:6379/0  # For L2 caching
export PYTHONPATH=./src
```

### Using .env File
```bash
# Copy and configure
cp .env.example .env
nano .env  # Add your GROQ_API_KEY
```

## 🎨 Usage Examples

### Web Interface
1. Open http://localhost:3000
2. Enter: "Create a REST API for user management"
3. Click "Generate"
4. View results in tabs:
   - **Output**: Generated scaffold
   - **IR**: Intermediate representation  
   - **Validation**: Compliance report
   - **Metrics**: Performance data

### CLI Interface
```bash
# Generate with Groq
promptlang generate "Create a FastAPI app" \
  --model oss --budget 5000 --scaffold-mode full

# Validate IR
promptlang validate tests/fixtures/scaffold_fastapi.json

# Optimize IR
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