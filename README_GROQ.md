# PromptLang Compiler Platform + Groq Integration

🚀 **Ultra-fast LLM inference with Groq's LPU-powered models**

## ⚡ Quick Start (3 Commands)

```bash
# 1. Set your Groq API key
export GROQ_API_KEY="gsk_your_api_key_here"

# 2. Start with Groq
./start-groq.sh

# 3. Open browser
open http://localhost:3000
```

## 🎯 Alternative Start Options

### Groq Mode (Recommended)
```bash
./start-groq.sh
# or
./start.sh groq
```

### Mock Mode (Offline)
```bash
./start.sh
# or
./start.sh mock
```

### Ollama Mode (Local)
```bash
./start.sh ollama
```

## 🌟 What's New with Groq

✅ **Ultra-Fast Inference**: 3-5x faster than traditional LLMs  
✅ **Real-Time Generation**: Live IR translation and scaffold generation  
✅ **Free Tier Available**: 1,000 requests/day free  
✅ **High Quality**: Llama 3.1 8B Instant model  
✅ **Easy Setup**: Just 3 commands to get started  

## 🏗️ Architecture

PromptLang with Groq implements the same 8-stage pipeline:

1. **Stage 0**: Input normalization
2. **Stage 1**: Intent routing  
3. **Stage 1.5**: Clarification engine
4. **Stage 2**: **IR Translation** ← *Powered by Groq*
5. **Stage 3**: Schema validation
6. **Stage 4**: IR linting
7. **Stage 5**: Token optimization
8. **Stage 6**: Dialect compilation
9. **Stage 7**: **Scaffold Generation** ← *Powered by Groq*
10. **Stage 8**: Output validation

## 📊 Performance Metrics

With Groq Llama 3.1 8B Instant:
- **IR Translation**: ~600ms (Stage 2)
- **Scaffold Generation**: ~2.5s (Stage 7)
- **Total Pipeline**: ~3.5s
- **Response Quality**: High-fidelity, structured output

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- Node.js 16+
- Groq API key (free at https://console.groq.com)

### One-Time Setup
```bash
# Clone repository
git clone <repository_url>
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

## ⚙️ Configuration

### Environment Variables
```bash
# Required for Groq
export GROQ_API_KEY="gsk_your_api_key_here"
export LLM_PROVIDER=groq
export PROMPTLANG_PRIMARY_PROVIDER=groq

# Optional
export REDIS_URL=redis://localhost:6379/0
export PYTHONPATH=./src
```

### Using .env file
```bash
# Copy example configuration
cp .env.example .env

# Edit with your API key
nano .env
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🧪 Testing Groq Integration

### Test API Directly
```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Create a REST API for user management",
    "intent": "scaffold",
    "target_model": "oss",
    "token_budget": 4000
  }'
```

### Verify Groq is Being Used
Look for these indicators:
- Fast response times (~3.5s total)
- Dynamic, context-aware output
- Real-time generation (not template-based)
- Groq model usage in logs

## 📝 Usage Examples

### Web Interface
1. Open http://localhost:3000
2. Enter: "Create a blog API with user authentication"
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

## 🔧 Provider Switching

### Runtime Switching
```bash
# Switch to Groq
export LLM_PROVIDER=groq
./start.sh groq

# Switch to Mock (offline)
export LLM_PROVIDER=mock
./start.sh

# Switch to Ollama (local)
export LLM_PROVIDER=ollama
./start.sh ollama
```

### Fallback Behavior
- Groq → Mock (if API fails)
- Ollama → Mock (if server unavailable)
- Mock always available (offline mode)

## 🚨 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check logs
tail -f /tmp/promptlang-backend.log

# Verify API key
echo $GROQ_API_KEY

# Test API key
curl -H "Authorization: Bearer $GROQ_API_KEY" \
  https://api.groq.com/openai/v1/models
```

**Frontend issues:**
```bash
# Check logs
tail -f /tmp/promptlang-frontend.log

# Reinstall dependencies
cd webapp && rm -rf node_modules && npm install
```

**Groq not working:**
```bash
# Verify environment
env | grep -E "(GROQ|LLM_PROVIDER)"

# Check provider in logs
grep -i groq /tmp/promptlang-backend.log
```

## 📈 Monitoring

### Performance Metrics
```bash
# Check response times
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8000/health

# Monitor logs
tail -f /tmp/promptlang-backend.log | grep -E "(timing|latency|groq)"
```

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000

# API documentation
curl http://localhost:8000/docs
```

## 🎯 Next Steps

1. **Get Groq API Key**: https://console.groq.com
2. **Run `./start-groq.sh`**: Start with Groq integration
3. **Test Generation**: Create your first project
4. **Explore Features**: Check all pipeline stages
5. **Monitor Performance**: View timing metrics

## 📚 Documentation

- **Detailed Setup**: See `GROQ_SETUP.md`
- **API Reference**: http://localhost:8000/docs
- **Architecture**: See original README.md
- **Troubleshooting**: See `GROQ_SETUP.md` troubleshooting section

---

**🚀 Experience ultra-fast LLM inference with PromptLang + Groq!**
