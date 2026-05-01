# SpeechEcho - Quick Start Guide

Get SpeechEcho running in minutes!

## 🚀 Fastest Way to Start

### Option 1: Automated Setup (Recommended)

**On Linux/macOS:**
```bash
bash setup.sh
```

**On Windows (PowerShell):**
```powershell
.\setup.bat
```

**Cross-platform (Python - Works on all OS):**
```bash
python setup.py
```

Then follow the instructions printed at the end of the script.

---

### Option 2: Manual 5-Minute Setup

#### Prerequisites Check
```bash
# Verify you have these installed
python --version     # Should be 3.10+
node --version       # Should be v18+
npm --version        # Should be 9+
```

#### 1. Backend Setup (2 minutes)
```bash
cd backend

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# OR on Windows
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. Frontend Setup (2 minutes)
```bash
cd ../frontend
npm install
```

#### 3. Configure Environment
```bash
# Backend config
cd ../backend
cp .env.example .env

# Frontend config (if needed)
cd ../frontend
cp .env.example .env.local
```

#### 4. Start the App (1 minute)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # Linux/macOS or .\venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

#### 5. Open in Browser
```
http://localhost:5173
```

✅ **Done!** You're running SpeechEcho!

---

## 🎯 Verify It's Working

### Check Backend
```bash
# Should show API documentation
curl http://localhost:8000/api/docs
```

### Check Frontend
```bash
# Should show the web interface
open http://localhost:5173
```

### Login to App
- Click "Login as Guest" button
- Access all features without authentication

---

## 📁 Where Are Things?

```
SpeechEcho_web/
├── backend/           ← API Server (port 8000)
├── frontend/          ← Web UI (port 5173)
├── chatterbox-streaming/ ← TTS Model
└── docs/              ← Documentation
```

---

## 🔧 Common Commands

### Run Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Run Frontend
```bash
cd frontend
npm run dev
```

### Build Frontend for Production
```bash
cd frontend
npm run build
```

### Access Documentation
- API Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

---

## ⚠️ Troubleshooting

### "Port Already in Use"
```bash
# Find what's using the port
lsof -i :8000      # Backend
lsof -i :5173      # Frontend

# Kill the process
kill -9 <PID>
```

### "Python Not Found"
Make sure Python 3.10+ is installed and in PATH
```bash
python --version   # Should show 3.10+
```

### "npm Not Found"
Make sure Node.js 18+ is installed and in PATH
```bash
npm --version      # Should show 9+
```

### "ModuleNotFoundError"
Make sure virtual environment is activated
```bash
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate   # Windows
```

### "Cannot Find Module"
Reinstall dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt --force-reinstall

# Frontend
cd frontend
rm -rf node_modules
npm install
```

---

## 📚 Next Steps

1. **Explore the Features**
   - Voice cloning on Dashboard
   - Text-to-speech Studio
   - Document voiceover
   - Chat with voice

2. **Read Full Documentation**
   - `SETUP.md` - Detailed setup guide
   - `README.md` - Project overview
   - `MODEL_DOCUMENTATION.md` - Model architecture
   - `EVALUATION_REPORT.md` - Model evaluation

3. **Configure API Keys** (Optional)
   - Get Gemini API key from: https://makersuite.google.com/app/apikey
   - Add to `backend/.env` → `GEMINI_API_KEY=`

4. **Customize**
   - Edit colors in `frontend/src/index.css`
   - Add new features in `backend/app/routers/`
   - Modify UI in `frontend/src/components/`

---

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:5173 | Web interface |
| Backend API | http://localhost:8000 | REST API |
| API Docs (Swagger) | http://localhost:8000/api/docs | Interactive API docs |
| ReDoc | http://localhost:8000/api/redoc | API reference docs |
| Database | ./backend/speechecho.db | SQLite database file |

---

## 🎓 What You Can Do

✅ Clone voices from 3-5 second audio samples
✅ Generate speech from text with custom voices
✅ Upload PDFs and convert to audio voiceovers
✅ Chat with AI assistant that responds with voice
✅ Adjust emotion/expressiveness of synthesized speech
✅ Save and manage multiple voice profiles

---

## 📞 Need Help?

Check these resources:
1. **SETUP.md** - Detailed setup troubleshooting
2. **MODEL_DOCUMENTATION.md** - Model-specific issues
3. **GitHub Issues** - https://github.com/Mustafa-bacha/SpeechEcho_web/issues

---

## 🎉 Success!

If you see:
- ✅ Frontend loads at localhost:5173
- ✅ "Login as Guest" button visible
- ✅ Dashboard accessible
- ✅ API docs at localhost:8000/api/docs

**You're all set!** Start creating with SpeechEcho! 🚀

---

**Happy coding!** 💻✨
