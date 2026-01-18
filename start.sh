#!/bin/bash

# Start script for PromptLang Platform (Backend + Frontend)

echo "🚀 Starting PromptLang Compiler Platform..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3.11 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies if needed
if [ ! -d "promptlang/core" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt -q
    pip install -e . -q
fi

# Start FastAPI backend in background
echo "🔧 Starting FastAPI backend on port 8000..."
uvicorn promptlang.api.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/promptlang-backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "⚠️  Backend failed to start. Check /tmp/promptlang-backend.log"
    exit 1
fi

echo "✅ Backend is running on http://localhost:8000"

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
echo "✅ PromptLang Platform is running!"
echo ""
echo "📊 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

wait
