"""
Text-to-Speech Service - Generate audio from text with voice parameters
"""
import os
import uuid
import tempfile
from typing import Optional, Tuple
from pydub import AudioSegment

from app.config import AUDIO_DIR


class TTSService:
    """Text-to-Speech service using pyttsx3 and pydub for audio manipulation"""
    
    def __init__(self):
        self._ensure_audio_dir()
    
    def _ensure_audio_dir(self):
        """Ensure audio directory exists"""
        os.makedirs(AUDIO_DIR, exist_ok=True)
    
    def generate_audio(
        self,
        text: str,
        pitch_shift: float = 1.0,
        speed_rate: float = 1.0,
        volume: float = 1.0
    ) -> Tuple[str, float]:
        """
        Generate audio from text with voice modifications.
        
        Args:
            text: Text to convert to speech
            pitch_shift: Pitch modification (0.5 to 2.0)
            speed_rate: Speed modification (0.5 to 2.0)
            volume: Volume level (0.0 to 1.0)
            
        Returns:
            Tuple of (file_path, duration_seconds)
        """
        import pyttsx3
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.wav"
        temp_path = os.path.join(tempfile.gettempdir(), f"temp_{filename}")
        final_path = os.path.join(AUDIO_DIR, filename)
        
        try:
            # Initialize TTS engine
            engine = pyttsx3.init()
            
            # Set base properties
            engine.setProperty('rate', int(150 * speed_rate))  # Default rate is ~150 wpm
            engine.setProperty('volume', volume)
            
            # Get available voices and use first one
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)
            
            # Save to temp file
            engine.save_to_file(text, temp_path)
            engine.runAndWait()
            
            # Apply pitch shift using pydub
            if os.path.exists(temp_path):
                audio = AudioSegment.from_wav(temp_path)
                
                # Apply pitch shift by changing sample rate
                if pitch_shift != 1.0:
                    # Pitch shifting approximation
                    new_sample_rate = int(audio.frame_rate * pitch_shift)
                    pitched_audio = audio._spawn(audio.raw_data, overrides={
                        "frame_rate": new_sample_rate
                    })
                    audio = pitched_audio.set_frame_rate(44100)
                
                # Export final audio
                audio.export(final_path, format="wav")
                duration = len(audio) / 1000.0  # Convert ms to seconds
                
                # Cleanup temp file
                os.remove(temp_path)
                
                return f"/static/audio/{filename}", duration
            else:
                # If pyttsx3 fails, create a silent placeholder
                return self._create_placeholder_audio(filename)
                
        except Exception as e:
            print(f"TTS Error: {e}")
            # Return placeholder on error
            return self._create_placeholder_audio(filename)
    
    def _create_placeholder_audio(self, filename: str) -> Tuple[str, float]:
        """Create a short silent audio file as placeholder"""
        final_path = os.path.join(AUDIO_DIR, filename)
        
        # Create 1 second of silence
        silence = AudioSegment.silent(duration=1000)
        silence.export(final_path, format="wav")
        
        return f"/static/audio/{filename}", 1.0
    
    def delete_audio(self, audio_url: str) -> bool:
        """Delete an audio file"""
        try:
            filename = audio_url.split("/")[-1]
            filepath = os.path.join(AUDIO_DIR, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception:
            return False


# Singleton instance
tts_service = TTSService()
