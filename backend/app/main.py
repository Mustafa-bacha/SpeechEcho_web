"""
SpeechEcho Backend - Main Application Entry Point
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import STATIC_DIR, AUDIO_DIR, UPLOADS_DIR, AVATARS_DIR, CORS_ORIGINS
from app.database import init_db, SessionLocal
from app.routers import auth_router, voices_router, tts_router, documents_router, chat_router
from app.routers.voice_chat import router as voice_chat_router
from app.services.voice_service import create_predefined_voices

# Create FastAPI app
app = FastAPI(
    title="SpeechEcho API",
    description="Real-Time Voice Cloning and Conversational Synthesis Backend",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(AVATARS_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(voices_router, prefix="/api")
app.include_router(tts_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(voice_chat_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize database and create predefined voices on startup"""
    init_db()
    
    # Create predefined voices
    db = SessionLocal()
    try:
        create_predefined_voices(db)
    finally:
        db.close()
    
    # Check Chatterbox availability
    try:
        from app.services.chatterbox_service import chatterbox_service
        if chatterbox_service.is_available:
            print(f"🎙️  Chatterbox TTS engine available on {chatterbox_service.device}")
        else:
            print("⚠️  Chatterbox TTS not available - check dependencies")
    except Exception as e:
        print(f"⚠️  Chatterbox import error: {e}")
    
    # Check STT (Whisper) availability
    try:
        from app.services.stt_service import stt_service
        if stt_service.is_available:
            print(f"🎤 Speech-to-Text (Whisper) available on {stt_service.device}")
        else:
            print("⚠️  Speech-to-Text not available - check Whisper dependencies")
    except Exception as e:
        print(f"⚠️  STT import error: {e}")
    
    print("✅ SpeechEcho Backend started successfully!")
    print("📚 API Documentation: http://localhost:8000/api/docs")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "SpeechEcho API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
