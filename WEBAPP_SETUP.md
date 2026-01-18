# PromptLang Web App - Setup and Usage

## 🎨 Web Application Created

The web application has been created with:

- **Next.js 14** frontend
- **shadcn/ui** components (Button, Tabs, Card)
- **Tailwind CSS** for styling
- **TypeScript** for type safety
- **Axios** for API communication

## 🚀 Quick Start

### Option 1: Use the Start Script (Recommended)

```bash
cd /home/nilesh/Desktop/Cursor
./start.sh
```

This will:
1. Create/activate Python virtual environment
2. Install Python dependencies
3. Start FastAPI backend on port 8000
4. Start Next.js frontend on port 3000
5. Open browser automatically

### Option 2: Manual Start

#### Start Backend

```bash
cd /home/nilesh/Desktop/Cursor

# Create virtual environment (if not exists)
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Start backend
export LLM_PROVIDER=mock
uvicorn promptlang.api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Start Frontend (in another terminal)

```bash
cd /home/nilesh/Desktop/Cursor/webapp

# Install dependencies (first time only)
npm install

# Start frontend
npm run dev
```

## 🌐 Access URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📋 Features

### Main Interface

1. **Input Section**: Enter your request text
2. **Generate Button**: Trigger pipeline execution
3. **Results Tabs**:
   - **Output**: Generated scaffold output
   - **IR**: Original and optimized IR JSON
   - **Validation Report**: Validation status, findings, contract compliance
   - **Metrics**: Request ID, timings, token usage, warnings

### UI Components

- Clean, modern design with Tailwind CSS
- Responsive layout
- Tabbed interface for results
- Syntax-highlighted JSON display
- Status indicators with color coding

## 🛠️ Development

### Frontend Structure

```
webapp/
├── app/
│   ├── page.tsx        # Main page component
│   ├── layout.tsx      # Root layout
│   └── globals.css     # Global styles
├── components/
│   └── ui/             # shadcn/ui components
├── lib/
│   ├── api.ts          # API client
│   └── utils.ts        # Utilities
└── package.json        # Dependencies
```

### Backend Integration

The frontend connects to the FastAPI backend via:
- API endpoint: `/api/generate`
- Next.js proxy configured in `next.config.js`
- Axios client in `lib/api.ts`

## 🎯 Usage Example

1. Open http://localhost:3000
2. Enter input: "Create a FastAPI REST API with user authentication"
3. Click "Generate"
4. View results in tabs:
   - **Output**: Generated scaffold with file structure
   - **IR**: Intermediate representation JSON
   - **Validation Report**: Validation results and findings
   - **Metrics**: Performance metrics and timings

## ✅ Status Check

```bash
# Check backend
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000
```

## 🔧 Troubleshooting

### Backend not starting
- Check Python virtual environment is activated
- Verify dependencies installed: `pip list | grep promptlang`
- Check logs: `tail -f /tmp/promptlang-backend.log`

### Frontend not starting
- Verify Node.js is installed: `node --version`
- Install dependencies: `cd webapp && npm install`
- Check logs: `tail -f /tmp/promptlang-frontend.log`

### API connection issues
- Verify backend is running on port 8000
- Check CORS settings in `api/main.py`
- Verify proxy config in `webapp/next.config.js`
