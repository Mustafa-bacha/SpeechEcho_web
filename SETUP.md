# SpeechEcho - Complete Setup Guide for Fresh System

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [System Setup](#system-setup)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Database Setup](#database-setup)
6. [Chatterbox TTS Setup](#chatterbox-tts-setup)
7. [Environment Configuration](#environment-configuration)
8. [Running the Application](#running-the-application)
9. [Troubleshooting](#troubleshooting)
10. [Quick Start Script](#quick-start-script)

---

## Prerequisites

### Required Software
- **Git** (version 2.0+)
- **Node.js** (version 18.x or higher) - [Download](https://nodejs.org/)
- **Python** (version 3.10+) - [Download](https://www.python.org/)
- **pip** (Python package manager, comes with Python)
- **NVIDIA GPU** (optional but recommended for TTS)
  - CUDA 11.8+ (if using GPU)
  - cuDNN (if using GPU)

### System Requirements
- **RAM**: 8GB minimum (16GB recommended)
- **Disk Space**: 10GB minimum
- **OS**: Linux, macOS, or Windows
- **GPU VRAM**: 4GB minimum (8GB+ recommended for TTS)

### Verify Installation
```bash
# Check Python
python --version  # Should be 3.10 or higher

# Check Node.js
node --version    # Should be v18.0.0 or higher
npm --version     # Should be 9.0.0 or higher

# Check Git
git --version     # Should be 2.0 or higher
```

---

## System Setup

### 1. Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/Mustafa-bacha/SpeechEcho_web.git
cd SpeechEcho_web

# Or if using SSH
git clone git@github.com:Mustafa-bacha/SpeechEcho_web.git
cd SpeechEcho_web
```

### 2. Verify Directory Structure

```bash
# List main directories
ls -la

# Expected output:
# backend/                    # FastAPI backend
# frontend/                   # React frontend
# chatterbox-streaming/       # TTS model
# docs/                       # Documentation
# README.md                   # Project overview
# SETUP.md                    # This file
# MODEL_DOCUMENTATION.md      # Model details
# EVALUATION_REPORT.md        # Evaluation results
```

### 3. Choose Installation Method

**Option A: Automated Setup (Recommended)**
```bash
bash setup.sh
```

**Option B: Manual Setup (Detailed)**
Follow sections below step by step.

---

## Backend Setup

### Step 1: Create Backend Virtual Environment

**On Linux/macOS:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

**On Windows (PowerShell):**
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```bash
cd backend
python -m venv venv
venv\Scripts\activate.bat
```

### Step 2: Install Backend Dependencies

```bash
# Ensure you're in the backend directory and venv is activated
pip install --upgrade pip setuptools wheel

# Install all dependencies
pip install -r requirements.txt
```

**Note**: This may take 5-15 minutes depending on your internet and hardware.

### Step 3: Verify Installation

```bash
# Test FastAPI
python -c "import fastapi; print('FastAPI installed:', fastapi.__version__)"

# Test PyTorch
python -c "import torch; print('PyTorch version:', torch.__version__)"

# Test SQLAlchemy
python -c "import sqlalchemy; print('SQLAlchemy installed')"
```

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 2: Install Frontend Dependencies

```bash
npm install

# Or using Yarn (if installed)
yarn install

# Or using pnpm (if installed)
pnpm install
```

**Note**: This installs ~200 packages and takes 2-5 minutes.

### Step 3: Verify Installation

```bash
npm list react
npm list react-dom
npm list vite
```

---

## Database Setup

### Step 1: Create SQLite Database

The database is created automatically on first run, but you can initialize it manually:

```bash
cd backend

# Activate virtual environment first
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate  # Windows

# Create database
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine); print('Database created successfully')"
```

### Step 2: Verify Database

```bash
# Check if database file exists
ls -lh speechecho.db

# Expected output shows file size > 0 bytes
```

### Optional: Setup Cloud Database (Supabase)

If using PostgreSQL via Supabase instead of SQLite:

1. Create Supabase account at https://supabase.com
2. Create new project
3. Get credentials from project settings
4. Update `.env` file with Supabase connection string

---

## Chatterbox TTS Setup

### Option 1: Use Pre-trained Model (Recommended)

```bash
cd chatterbox-streaming

# The models are downloaded automatically on first use
# First initialization may take 2-5 minutes

# Test TTS
python -c "
from src.chatterbox.tts import ChatterboxTTS
model = ChatterboxTTS.from_pretrained(device='cpu')
print('Chatterbox TTS loaded successfully')
"
```

### Option 2: Use Fine-tuned Model (If Available)

```bash
cd chatterbox-streaming

# Copy fine-tuned checkpoints if available
# cp /path/to/checkpoints_lora/* ./checkpoints_lora/

# Load fine-tuned model
python -c "
from src.chatterbox.tts import ChatterboxTTS
model = ChatterboxTTS.from_pretrained(device='cpu')
model.load_lora_adapter('checkpoints_lora/final_lora_adapter.pt', r=32, alpha=64)
print('Fine-tuned model loaded successfully')
"
```

### GPU Setup (Optional)

For better performance, use NVIDIA GPU:

```bash
# Install PyTorch with CUDA support
# Get the correct command from https://pytorch.org/get-started/locally/

# Example for CUDA 12.1:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify GPU
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

---

## Environment Configuration

### Step 1: Create .env Files

**Backend Configuration:**

```bash
cd backend

# Copy example to .env
cp .env.example .env

# Edit with your settings
nano .env  # or use your editor
```

**Frontend Configuration:**

```bash
cd frontend

# Copy example to .env.local
cp .env.example .env.local

# Edit with your settings
nano .env.local
```

### Step 2: Configure Backend .env

Edit `backend/.env` with these settings:

```bash
# App environment
APP_ENV=development

# JWT Configuration
SECRET_KEY=your-super-secret-key-generate-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Gemini API Key (Optional)
# Get from https://makersuite.google.com/app/apikey
GEMINI_API_KEY=

# Database
DATABASE_URL=sqlite:///./speechecho.db

# CORS Origins
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Storage
STORAGE_BACKEND=local

# Auth Settings
AUTH_GUEST_BYPASS=true
```

### Step 3: Configure Frontend .env.local

Edit `frontend/.env.local`:

```bash
# API Base URL
VITE_API_BASE_URL=/api

# For remote API (if backend on different domain):
# VITE_API_BASE_URL=https://your-api-domain.com/api
```

### Generate Secure Secret Key

```bash
# Linux/macOS
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Then copy the output and paste into SECRET_KEY in .env
```

---

## Running the Application

### Option 1: Run Both Services Separately (Recommended for Development)

**Terminal 1 - Start Backend:**

```bash
cd backend
source venv/bin/activate  # Linux/macOS
# or .\venv\Scripts\activate  # Windows

uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Start Frontend:**

```bash
cd frontend
npm run dev
```

**Access the Application:**
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Option 2: Run with Docker (If Docker Installed)

```bash
# Build and start all services
docker-compose up

# Access at http://localhost
```

### Option 3: Production Build (For Deployment)

**Frontend Build:**

```bash
cd frontend
npm run build

# Output is in frontend/dist/
```

**Backend Production:**

```bash
cd backend
source venv/bin/activate

# Run with Gunicorn (production ASGI server)
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000 (backend)
lsof -i :8000

# Find process using port 5173 (frontend)
lsof -i :5173

# Kill process
kill -9 <PID>
```

### Python Virtual Environment Issues

```bash
# Deactivate current environment
deactivate

# Remove venv and recreate
rm -rf backend/venv
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Node Modules Issues

```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Database Issues

```bash
# Reset database
cd backend
rm speechecho.db

# Recreate
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### CUDA/GPU Issues

```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# If CUDA not found, reinstall PyTorch with CPU version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Chatterbox Model Download Issues

```bash
# Clear huggingface cache
rm -rf ~/.cache/huggingface

# Download model manually
python -c "from src.chatterbox.tts import ChatterboxTTS; ChatterboxTTS.from_pretrained()"
```

---

## Quick Start Script

### Create `setup.sh` for Automated Setup

Save this as `setup.sh` in project root:

```bash
#!/bin/bash

set -e

echo "🚀 SpeechEcho - Automated Setup"
echo "================================"

# Check prerequisites
echo "✓ Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 required"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js required"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "❌ Git required"; exit 1; }

# Backend setup
echo "✓ Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Backend .env created - Please edit with your settings"
fi

# Initialize database
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

cd ..

# Frontend setup
echo "✓ Setting up frontend..."
cd frontend
npm install

# Create .env.local if not exists
if [ ! -f .env.local ]; then
    cp .env.example .env.local
fi

cd ..

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📝 Next Steps:"
echo "1. Edit backend/.env with your configuration"
echo "2. Edit frontend/.env.local if needed"
echo "3. Run: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "4. In another terminal: cd frontend && npm run dev"
echo ""
echo "🌐 Access the app at http://localhost:5173"
```

### Make Script Executable and Run

```bash
chmod +x setup.sh
./setup.sh
```

---

## File Structure After Setup

```
SpeechEcho_web/
├── backend/
│   ├── venv/                    # Virtual environment
│   ├── app/
│   ├── static/
│   ├── .env                     # Configuration (git ignored)
│   ├── .env.example             # Example configuration
│   ├── requirements.txt
│   └── runtime.txt
│
├── frontend/
│   ├── node_modules/            # Dependencies (git ignored)
│   ├── src/
│   ├── public/
│   ├── .env.local               # Configuration (git ignored)
│   ├── .env.example
│   ├── package.json
│   └── vite.config.js
│
├── chatterbox-streaming/        # TTS Model
│   ├── src/chatterbox/
│   ├── checkpoints_lora/        # Fine-tuned adapters
│   └── README.md
│
├── docs/                        # Documentation
├── README.md
├── SETUP.md                     # This file
├── MODEL_DOCUMENTATION.md
├── EVALUATION_REPORT.md
├── setup.sh                     # Automated setup script
└── .gitignore
```

---

## Verification Checklist

After setup, verify everything works:

- [ ] Backend virtual environment activated
- [ ] Backend dependencies installed (`pip list` shows 50+ packages)
- [ ] Frontend dependencies installed (`npm list` succeeds)
- [ ] `.env` files created and configured
- [ ] Database created (`backend/speechecho.db` exists)
- [ ] Backend starts without errors (`uvicorn app.main:app --reload`)
- [ ] Frontend starts without errors (`npm run dev`)
- [ ] Browser loads http://localhost:5173
- [ ] API docs accessible at http://localhost:8000/api/docs
- [ ] Guest login button visible on login page

---

## Next Steps

1. **Read Documentation**
   - `README.md` - Project overview
   - `MODEL_DOCUMENTATION.md` - Model architecture and training
   - `EVALUATION_REPORT.md` - Evaluation results

2. **Explore the Code**
   - `backend/app/main.py` - FastAPI entry point
   - `frontend/src/App.jsx` - React entry point
   - `backend/app/routers/` - API endpoints
   - `frontend/src/pages/` - UI pages

3. **Customize**
   - Update `backend/.env` with your API keys
   - Modify UI components in `frontend/src/components/`
   - Add new API endpoints in `backend/app/routers/`

4. **Deploy**
   - See `README.md` for deployment options
   - Frontend can deploy to Vercel, Netlify
   - Backend can deploy to Render, Railway, Heroku

---

## Support & Issues

If you encounter issues:

1. Check **Troubleshooting** section above
2. Review error messages carefully
3. Check log output for specific errors
4. See `MODEL_DOCUMENTATION.md` for model-specific issues
5. Open GitHub issue with detailed error description

---

**Last Updated**: May 2026  
**Version**: 1.0  
**Status**: Production Ready ✅
