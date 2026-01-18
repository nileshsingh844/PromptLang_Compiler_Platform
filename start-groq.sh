#!/bin/bash

# PromptLang + Groq Startup Script
# Ultra-fast LLM inference with Groq integration

echo "🚀 Starting PromptLang with Groq integration..."

# Check for Groq API key
if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ GROQ_API_KEY not found!"
    echo ""
    echo "Please set your Groq API key:"
    echo "export GROQ_API_KEY=\"gsk_your_api_key_here\""
    echo ""
    echo "Get your free API key at: https://console.groq.com"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3.11 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies if needed
if [ ! -d "src/promptlang/core" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt -q
    pip install -e . -q
fi

# Set environment variables for Groq
export GROQ_API_KEY="$GROQ_API_KEY"
export LLM_PROVIDER=groq
export PROMPTLANG_PRIMARY_PROVIDER=groq
export PYTHONPATH="./src"

echo "🔧 Starting FastAPI backend with Groq on port 8000..."
uvicorn promptlang.api.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/promptlang-backend-groq.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "⚠️  Backend failed to start. Check logs:"
    echo "tail -f /tmp/promptlang-backend-groq.log"
    exit 1
fi

echo "✅ Backend with Groq is running on http://localhost:8000"

# Start Next.js frontend
if [ ! -d "webapp/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd webapp
    npm install
    cd ..
fi

echo "🎨 Starting Next.js frontend on port 3000..."
cd webapp
npm run dev > /tmp/promptlang-frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "Frontend PID: $FRONTEND_PID"

# Wait for frontend to start
sleep 5

echo ""
echo "🎉 PromptLang + Groq is running!"
echo ""
echo "📊 Backend API (Groq-powered): http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "🤖 Using Groq Llama 3.1 8B Instant for ultra-fast inference"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped"
    exit
}

# Trap Ctrl+C
trap cleanup INT

# Wait for processes
wait
