# PromptLang + Groq Setup Guide

## 🚀 Quick Start (3 Commands)

```bash
# 1. Set your Groq API key
export GROQ_API_KEY="your_groq_api_key_here"

# 2. Start the application
./start-groq.sh

# 3. Open browser
open http://localhost:3000
```

## 📋 Prerequisites

- Python 3.11+
- Node.js 16+
- Groq API key (get free at https://console.groq.com)

## 🔧 Installation (One-time setup)

```bash
# Clone and navigate to project
cd /path/to/PromptLang_Compiler_Platform

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Setup frontend
cd webapp
npm install
cd ..

# Make startup scripts executable
chmod +x start-groq.sh start.sh
```

## 🎯 Running the Application

### Option 1: Groq Mode (Recommended)
```bash
./start-groq.sh
```

### Option 2: Mock Mode (Offline)
```bash
./start.sh
```

### Option 3: Manual Start
```bash
# Backend
export GROQ_API_KEY="your_key"
export LLM_PROVIDER=groq
source venv/bin/activate
PYTHONPATH=./src uvicorn promptlang.api.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (new terminal)
cd webapp && npm run dev
```

## 🌐 Access URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## ⚙️ Configuration

### Environment Variables
```bash
# Required for Groq
export GROQ_API_KEY="gsk_your_api_key_here"
export LLM_PROVIDER=groq
export PROMPTLANG_PRIMARY_PROVIDER=groq

# Optional
export REDIS_URL=redis://localhost:6379/0  # For L2 caching
export BUILD_HASH=dev  # Build identifier
```

### Create .env file (Optional)
```bash
# Create .env file in project root
cat > .env << EOF
GROQ_API_KEY=your_groq_api_key_here
LLM_PROVIDER=groq
PROMPTLANG_PRIMARY_PROVIDER=groq
EOF
```

## 🎨 Features with Groq

✅ **Ultra-Fast Inference**: Groq's LPU-powered models  
✅ **Real-Time Generation**: Dynamic IR translation and scaffold generation  
✅ **Smart Pipeline**: All 8 stages working with Groq  
✅ **Cost Effective**: Free tier available (1K requests/day)  
✅ **High Quality**: Llama 3.1 models for superior output  

## 🛠️ Development

### Test Groq Integration
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

### Switch Providers
```bash
# Mock (offline)
export LLM_PROVIDER=mock

# Groq (requires API key)
export LLM_PROVIDER=groq

# Ollama (local)
export LLM_PROVIDER=ollama
```

## 🔍 Troubleshooting

### Backend Issues
```bash
# Check logs
tail -f /tmp/promptlang-backend.log

# Restart backend
pkill -f uvicorn
./start-groq.sh
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
echo $LLM_PROVIDER
```

## 📊 Performance

With Groq integration:
- **IR Translation**: ~600ms (Stage 2)
- **Scaffold Generation**: ~2.5s (Stage 7)
- **Total Pipeline**: ~3.5s
- **Model**: Llama 3.1 8B Instant

## 🎯 Next Steps

1. **Get Groq API Key**: https://console.groq.com
2. **Run `./start-groq.sh`**: Start with Groq integration
3. **Open Browser**: http://localhost:3000
4. **Generate**: Create projects with ultra-fast Groq inference

---

**🚀 Your PromptLang application is now ready with Groq integration!**
