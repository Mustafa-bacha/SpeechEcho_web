# SpeechEcho — Real‑Time Voice Cloning & Conversational Synthesis

SpeechEcho is a full‑stack web application for voice cloning, text‑to‑speech synthesis, document voiceover, and AI‑powered conversational interfaces.

## 🎯 Features

- **Voice Cloning**: Clone voices from 3-5 second audio samples
- **Text-to-Speech Studio**: Convert text to natural sounding speech
- **Document Voiceover**: Upload PDFs and convert them to audio
- **AI Chat**: Conversational interface with voice responses
- **Multiple Voice Profiles**: Use predefined or cloned voices

## 📁 Project Structure

```
SpeechEcho_web/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── main.py         # FastAPI application entry
│   │   ├── config.py       # Configuration settings
│   │   ├── database.py     # SQLAlchemy setup
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── routers/        # API endpoints
│   │   └── services/       # Business logic
│   ├── static/             # Generated audio files
│   └── requirements.txt    # Python dependencies
│
└── frontend/               # React Frontend
    ├── src/
    │   ├── components/     # Reusable components
    │   ├── contexts/       # React Context providers
    │   ├── pages/          # Page components
    │   ├── services/       # API service layer
    │   └── App.jsx         # Main application
    ├── package.json        # Node dependencies
    └── vite.config.js      # Vite configuration
```

## 🚀 Getting Started

### Quick Start (local)

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

App: `http://localhost:5173` • API: `http://localhost:8000/api/docs`

### Prerequisites

- **Node.js** >= 18.x
- **Python** >= 3.10
- **pip** (Python package manager)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment file:
   ```bash
   cp .env.example .env
   ```

5. Edit `.env` and add your configurations:
   ```env
   SECRET_KEY=your-super-secret-key
   GEMINI_API_KEY=your-gemini-api-key  # Optional, for AI chat
   ```

6. Start the backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`
   - API Docs: `http://localhost:8000/api/docs`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:5173`

## 🔧 Configuration

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret key | Required |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | 30 |
| `GEMINI_API_KEY` | Google Gemini API key | Optional |
| `DATABASE_URL` | SQLite database URL | sqlite:///./speechecho.db |

### Frontend Features (Mock Mode)

The frontend can work without the backend using:
- **localStorage** for data persistence
- **Web Speech API** for TTS
- **Mock responses** for chat

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `GET /api/auth/me` - Get current user

### Voice Cloning
- `POST /api/voices/clone` - Clone a voice from audio
- `GET /api/voices/` - Get all voices
- `DELETE /api/voices/{id}` - Delete a voice

### Text-to-Speech
- `POST /api/tts/generate` - Generate speech from text
- `POST /api/tts/preview` - Preview a voice

### Documents
- `POST /api/documents/upload` - Upload and extract PDF text
- `POST /api/documents/convert` - Convert text to audio

### Chat
- `POST /api/chat/message` - Send message and get response
- `WebSocket /api/chat/ws/{session_id}` - Real-time chat
- `GET /api/chat/history/{session_id}` - Get chat history

## 🎨 Design System

### Color Palette
- **Primary**: Indigo (#4F46E5)
- **Secondary**: Slate Gray (#64748B)
- **Background**: White/Off-white
- **Accents**: Gradient blues and purples

### Typography
- Font: Inter
- Weights: 300, 400, 500, 600, 700

## 🛠️ Tech Stack

### Frontend
- React 18 + Vite
- Tailwind CSS
- React Router DOM
- Axios
- Lucide React (icons)
- Framer Motion (animations)

### Backend
- FastAPI
- SQLAlchemy + SQLite
- Pydantic
- python-jose (JWT)
- pyttsx3 (TTS)
- pydub (Audio processing)
- PyPDF2 (PDF extraction)
- Google Generative AI (optional)

## 📝 Notes

### Repository Notes
- Large model artifacts and virtual environments are excluded via `.gitignore`.
- If you need Chatterbox models locally, place them under `chatterbox-streaming/` after cloning.

### Mock Implementation
This is an MVP demo. The voice cloning feature uses random parameters instead of actual AI training. The real implementation would require:
- Voice cloning model (e.g., Coqui TTS, XTTS)
- GPU resources for training
- Larger audio samples

### Browser Compatibility
- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Limited Web Speech API support

## 👨‍💻 Development

### Running Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Building for Production
```bash
# Frontend
cd frontend
npm run build
```

## 📄 License

This project is part of a Final Year Project (FYP) for GIKI.

---

**SpeechEcho** - Real-Time Voice Cloning and Conversational Synthesis System
