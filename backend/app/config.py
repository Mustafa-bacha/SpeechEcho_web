"""
Configuration settings for SpeechEcho Backend
"""
import os
from typing import List
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "speechecho-dev-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./speechecho.db")

    # App / CORS
    APP_ENV: str = os.getenv("APP_ENV", "development")
    CORS_ORIGINS_RAW: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    )
    
    # Groq API
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Google Gemini (legacy)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")

    # Storage strategy
    STORAGE_BACKEND: str = os.getenv("STORAGE_BACKEND", "local")  # local | supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_BUCKET_AVATARS: str = os.getenv("SUPABASE_BUCKET_AVATARS", "avatars")
    SUPABASE_BUCKET_UPLOADS: str = os.getenv("SUPABASE_BUCKET_UPLOADS", "uploads")
    SUPABASE_BUCKET_AUDIO: str = os.getenv("SUPABASE_BUCKET_AUDIO", "audio")

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"


settings = Settings()

# Legacy exports for backward compatibility
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
DATABASE_URL = settings.DATABASE_URL
GEMINI_API_KEY = settings.GEMINI_API_KEY
CORS_ORIGINS = settings.CORS_ORIGINS

# File paths
STATIC_DIR = "static"
AUDIO_DIR = f"{STATIC_DIR}/audio"
UPLOADS_DIR = f"{STATIC_DIR}/uploads"
AVATARS_DIR = f"{STATIC_DIR}/avatars"

# Audio settings (updated for Chatterbox)
MIN_CLONE_DURATION = 1  # seconds - minimum for any usable voice
MAX_CLONE_DURATION = None  # No limit - but recommend 3-10 seconds for best quality
