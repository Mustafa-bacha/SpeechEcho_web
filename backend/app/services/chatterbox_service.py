"""
Chatterbox TTS Service - Voice cloning and text-to-speech using Chatterbox model
"""
import os
import sys
import uuid
import torch
import torchaudio as ta
import re
from typing import Optional, Tuple, Generator, List
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import numpy as np

from app.config import AUDIO_DIR, UPLOADS_DIR
from app.services.storage_service import storage_service

# Add chatterbox-streaming to path
CHATTERBOX_PATH = Path(__file__).parent.parent.parent.parent.parent / "chatterbox-streaming" / "src"
sys.path.insert(0, str(CHATTERBOX_PATH))

# Import Chatterbox modules
try:
    from chatterbox.tts import ChatterboxTTS
    from chatterbox.vc import ChatterboxVC
    CHATTERBOX_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Chatterbox not available: {e}")
    CHATTERBOX_AVAILABLE = False


class ChatterboxService:
    """Chatterbox TTS and Voice Cloning service"""
    
    _instance = None
    _model = None
    _vc_model = None
    _executor = ThreadPoolExecutor(max_workers=2)
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._ensure_dirs()
        self._device = self._detect_device()
    
    def _ensure_dirs(self):
        """Ensure required directories exist"""
        os.makedirs(AUDIO_DIR, exist_ok=True)
        os.makedirs(UPLOADS_DIR, exist_ok=True)
    
    def _detect_device(self) -> str:
        """Detect best available device"""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    
    def _split_text_into_chunks(self, text: str, max_chars: int = 250) -> List[str]:
        """
        Split text into chunks that the model can handle.
        Tries to split at sentence boundaries for natural speech.
        
        Args:
            text: Full text to split
            max_chars: Maximum characters per chunk (Chatterbox limit ~300-400)
            
        Returns:
            List of text chunks
        """
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        
        # Split by sentences first (., !, ?)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        for sentence in sentences:
            # If single sentence is too long, split by commas or words
            if len(sentence) > max_chars:
                # Try splitting by commas first
                parts = re.split(r',\s*', sentence)
                for part in parts:
                    if len(part) > max_chars:
                        # Split by words if still too long
                        words = part.split()
                        word_chunk = ""
                        for word in words:
                            if len(word_chunk) + len(word) + 1 <= max_chars:
                                word_chunk = (word_chunk + " " + word).strip()
                            else:
                                if word_chunk:
                                    chunks.append(word_chunk)
                                word_chunk = word
                        if word_chunk:
                            if current_chunk and len(current_chunk) + len(word_chunk) + 1 <= max_chars:
                                current_chunk = (current_chunk + " " + word_chunk).strip()
                            else:
                                if current_chunk:
                                    chunks.append(current_chunk)
                                current_chunk = word_chunk
                    else:
                        if current_chunk and len(current_chunk) + len(part) + 2 <= max_chars:
                            current_chunk = (current_chunk + ", " + part).strip()
                        else:
                            if current_chunk:
                                chunks.append(current_chunk)
                            current_chunk = part
            elif len(current_chunk) + len(sentence) + 1 <= max_chars:
                current_chunk = (current_chunk + " " + sentence).strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks if chunks else [text[:max_chars]]
    
    @property
    def device(self) -> str:
        return self._device
    
    @property
    def is_available(self) -> bool:
        return CHATTERBOX_AVAILABLE
    
    def _load_model(self) -> Optional[ChatterboxTTS]:
        """Lazy load the TTS model"""
        if not CHATTERBOX_AVAILABLE:
            return None
            
        if self._model is None:
            print(f"Loading Chatterbox TTS model on {self._device}...")
            try:
                # Check for local fine-tuned model first
                local_model_path = CHATTERBOX_PATH.parent / "checkpoints_lora" / "merged_model"
                if local_model_path.exists():
                    print(f"Loading fine-tuned model from {local_model_path}")
                    self._model = ChatterboxTTS.from_local(str(local_model_path), device=self._device)
                else:
                    print("Loading pretrained Chatterbox model from HuggingFace...")
                    self._model = ChatterboxTTS.from_pretrained(device=self._device)
                print("Chatterbox TTS model loaded successfully!")
            except Exception as e:
                print(f"Error loading Chatterbox model: {e}")
                return None
        return self._model
    
    def _load_vc_model(self) -> Optional[ChatterboxVC]:
        """Lazy load the Voice Conversion model"""
        if not CHATTERBOX_AVAILABLE:
            return None
            
        if self._vc_model is None:
            print(f"Loading Chatterbox VC model on {self._device}...")
            try:
                self._vc_model = ChatterboxVC.from_pretrained(device=self._device)
                print("Chatterbox VC model loaded successfully!")
            except Exception as e:
                print(f"Error loading Chatterbox VC model: {e}")
                return None
        return self._vc_model
    
    def generate_audio(
        self,
        text: str,
        audio_prompt_path: Optional[str] = None,
        exaggeration: float = 0.5,
        cfg_weight: float = 0.5,
        temperature: float = 0.8
    ) -> Tuple[str, float]:
        """
        Generate audio from text using Chatterbox TTS.
        Automatically chunks long text to avoid CUDA errors.
        
        Args:
            text: Text to convert to speech
            audio_prompt_path: Path to reference audio for voice cloning
            exaggeration: Emotion exaggeration control (0.0 to 1.0)
            cfg_weight: CFG weight for pacing control (0.0 to 1.0)
            temperature: Generation temperature
            
        Returns:
            Tuple of (audio_url, duration_seconds)
        """
        model = self._load_model()
        if model is None:
            raise RuntimeError("Chatterbox model not available")
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.wav"
        output_path = os.path.join(AUDIO_DIR, filename)
        
        try:
            # Split text into manageable chunks
            text_chunks = self._split_text_into_chunks(text, max_chars=250)
            print(f"Processing text in {len(text_chunks)} chunk(s)")
            
            audio_segments = []
            
            effective_prompt = audio_prompt_path if (audio_prompt_path and os.path.exists(audio_prompt_path)) else None
            print(f"[Chatterbox] Using audio_prompt: {effective_prompt}")
            
            with torch.inference_mode():
                for i, chunk in enumerate(text_chunks):
                    print(f"Generating audio for chunk {i+1}/{len(text_chunks)}: {chunk[:50]}...")
                    
                    # Generate audio for each chunk
                    wav = model.generate(
                        chunk,
                        audio_prompt_path=effective_prompt,
                        exaggeration=exaggeration,
                        cfg_weight=cfg_weight,
                        temperature=temperature
                    )
                    audio_segments.append(wav.cpu())
                    
                    # Clear CUDA cache between chunks to prevent memory buildup
                    if self._device == "cuda":
                        torch.cuda.empty_cache()
                
                # Concatenate all audio segments
                if len(audio_segments) == 1:
                    final_wav = audio_segments[0]
                else:
                    # Add small silence between segments for natural flow
                    silence = torch.zeros(1, int(model.sr * 0.2))  # 200ms silence
                    segments_with_silence = []
                    for i, seg in enumerate(audio_segments):
                        segments_with_silence.append(seg)
                        if i < len(audio_segments) - 1:
                            segments_with_silence.append(silence)
                    final_wav = torch.cat(segments_with_silence, dim=-1)
                
                # Save local audio file
                ta.save(output_path, final_wav, model.sr)

                # Persist audio in configured storage backend (Supabase/local)
                audio_url = storage_service.save_file(
                    file_path=output_path,
                    filename=filename,
                    category="audio",
                    content_type="audio/wav",
                )
                
                # Calculate duration
                duration = final_wav.shape[-1] / model.sr
                
                return audio_url, duration
                
        except Exception as e:
            print(f"Error generating audio: {e}")
            # Clear CUDA cache on error
            if self._device == "cuda":
                torch.cuda.empty_cache()
            raise RuntimeError(f"Failed to generate audio: {str(e)}")
    
    async def generate_audio_async(
        self,
        text: str,
        audio_prompt_path: Optional[str] = None,
        exaggeration: float = 0.5,
        cfg_weight: float = 0.5,
        temperature: float = 0.8
    ) -> Tuple[str, float]:
        """Async wrapper for generate_audio"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            lambda: self.generate_audio(text, audio_prompt_path, exaggeration, cfg_weight, temperature)
        )
    
    def generate_audio_stream(
        self,
        text: str,
        audio_prompt_path: Optional[str] = None,
        exaggeration: float = 0.5,
        cfg_weight: float = 0.5,
        temperature: float = 0.8,
        chunk_size: int = 25
    ) -> Generator[Tuple[bytes, dict], None, None]:
        """
        Generate audio from text using streaming.
        
        Yields:
            Tuple of (audio_chunk_bytes, metrics_dict)
        """
        model = self._load_model()
        if model is None:
            raise RuntimeError("Chatterbox model not available")
        
        try:
            kwargs = {
                "text": text,
                "exaggeration": exaggeration,
                "cfg_weight": cfg_weight,
                "temperature": temperature,
                "chunk_size": chunk_size,
                # Always pass audio_prompt_path explicitly (None for default voice)
                "audio_prompt_path": audio_prompt_path if (audio_prompt_path and os.path.exists(audio_prompt_path)) else None,
            }
            
            for audio_chunk, metrics in model.generate_stream(**kwargs):
                # Convert to bytes for streaming
                import io
                buffer = io.BytesIO()
                ta.save(buffer, audio_chunk.cpu(), model.sr, format="wav")
                buffer.seek(0)
                
                metrics_dict = {
                    "chunk_count": metrics.chunk_count,
                    "rtf": metrics.rtf,
                    "latency_to_first_chunk": metrics.latency_to_first_chunk
                }
                
                yield buffer.read(), metrics_dict
                
        except Exception as e:
            print(f"Error in streaming generation: {e}")
            raise RuntimeError(f"Failed to generate audio stream: {str(e)}")
    
    def generate_audio_stream_with_text(
        self,
        text: str,
        audio_prompt_path: Optional[str] = None,
        exaggeration: float = 0.5,
        cfg_weight: float = 0.5,
        temperature: float = 0.8
    ) -> Generator[Tuple[bytes, float, str], None, None]:
        """
        Generate audio from text with streaming - yields immediately as each chunk is ready.
        
        This method splits text into chunks and generates audio for each chunk,
        yielding the audio bytes as soon as each chunk is ready. This enables
        immediate playback without waiting for the entire document.
        
        Yields:
            Tuple of (audio_bytes, duration_seconds, chunk_text)
        """
        model = self._load_model()
        if model is None:
            raise RuntimeError("Chatterbox model not available")
        
        # Split text into chunks for streaming
        text_chunks = self._split_text_into_chunks(text, max_chars=250)
        print(f"[Streaming] Processing {len(text_chunks)} chunks for immediate playback")
        
        try:
            with torch.inference_mode():
                for i, chunk_text in enumerate(text_chunks):
                    print(f"[Streaming] Generating chunk {i+1}/{len(text_chunks)}: {chunk_text[:50]}...")
                    
                    # Generate audio for this chunk
                    wav = model.generate(
                        chunk_text,
                        audio_prompt_path=audio_prompt_path if (audio_prompt_path and os.path.exists(audio_prompt_path)) else None,
                        exaggeration=exaggeration,
                        cfg_weight=cfg_weight,
                        temperature=temperature
                    )
                    
                    # Convert to bytes immediately
                    import io
                    buffer = io.BytesIO()
                    ta.save(buffer, wav.cpu(), model.sr, format="wav")
                    buffer.seek(0)
                    audio_bytes = buffer.read()
                    
                    # Calculate duration
                    duration = wav.shape[-1] / model.sr
                    
                    print(f"[Streaming] Chunk {i+1} ready: {duration:.2f}s")
                    
                    # Yield immediately - frontend can start playing this chunk
                    yield audio_bytes, duration, chunk_text
                    
                    # Clear CUDA cache between chunks
                    if self._device == "cuda":
                        torch.cuda.empty_cache()
                        
        except Exception as e:
            print(f"Error in streaming generation with text: {e}")
            if self._device == "cuda":
                torch.cuda.empty_cache()
            raise RuntimeError(f"Failed to generate audio stream: {str(e)}")
    
    def voice_conversion(
        self,
        source_audio_path: str,
        target_voice_path: str
    ) -> Tuple[str, float]:
        """
        Convert voice in source audio to target voice.
        
        Args:
            source_audio_path: Path to source audio file
            target_voice_path: Path to target voice reference
            
        Returns:
            Tuple of (audio_url, duration_seconds)
        """
        vc_model = self._load_vc_model()
        if vc_model is None:
            raise RuntimeError("Chatterbox VC model not available")
        
        # Generate unique filename
        filename = f"vc_{uuid.uuid4()}.wav"
        output_path = os.path.join(AUDIO_DIR, filename)
        
        try:
            with torch.inference_mode():
                wav = vc_model.generate(
                    audio=source_audio_path,
                    target_voice_path=target_voice_path
                )
                
                # Save local audio file
                ta.save(output_path, wav.cpu(), vc_model.sr)

                # Persist audio in configured storage backend (Supabase/local)
                audio_url = storage_service.save_file(
                    file_path=output_path,
                    filename=filename,
                    category="audio",
                    content_type="audio/wav",
                )
                
                # Calculate duration
                duration = wav.shape[-1] / vc_model.sr
                
                return audio_url, duration
                
        except Exception as e:
            print(f"Error in voice conversion: {e}")
            raise RuntimeError(f"Failed to convert voice: {str(e)}")
    
    async def voice_conversion_async(
        self,
        source_audio_path: str,
        target_voice_path: str
    ) -> Tuple[str, float]:
        """Async wrapper for voice_conversion"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            lambda: self.voice_conversion(source_audio_path, target_voice_path)
        )
    
    def get_model_info(self) -> dict:
        """Get model information and status"""
        return {
            "available": self.is_available,
            "device": self._device,
            "tts_loaded": self._model is not None,
            "vc_loaded": self._vc_model is not None,
            "sample_rate": self._model.sr if self._model else 24000
        }


# Singleton instance
chatterbox_service = ChatterboxService()
