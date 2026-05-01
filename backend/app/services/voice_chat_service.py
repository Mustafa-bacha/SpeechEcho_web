"""
Voice Chat Service - Real-time voice-to-voice conversation
Combines STT (Whisper) + LLM (Groq) + TTS (Chatterbox) for natural voice chat
"""
import os
import uuid
import asyncio
from typing import Optional, Dict, Tuple, AsyncGenerator
from datetime import datetime
import io

from app.services.stt_service import stt_service
from app.services.chat_service import chat_service
from app.services.chatterbox_service import chatterbox_service
from app.config import AUDIO_DIR, UPLOADS_DIR
from app.database import SessionLocal
from app.models.voice_profile import VoiceProfile


class VoiceChatService:
    """
    Voice-to-voice chat service providing a seamless conversational experience.
    
    Flow:
    1. Receive audio input from user
    2. Transcribe to text using Whisper STT
    3. Process with LLM (Groq) to generate response
    4. Convert response to speech using Chatterbox TTS
    5. Return audio response
    """
    
    _instance = None
    
    # Voice chat session storage
    _sessions: Dict[str, Dict] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """Ensure required directories exist"""
        os.makedirs(AUDIO_DIR, exist_ok=True)
        os.makedirs(UPLOADS_DIR, exist_ok=True)
    
    def _get_voice_profile_audio_path(self, voice_id: int) -> Optional[str]:
        """
        Get the original audio path from a voice profile.
        
        Args:
            voice_id: Voice profile ID
            
        Returns:
            Path to the original audio file, or None if not found
        """
        try:
            db = SessionLocal()
            voice_profile = db.query(VoiceProfile).filter(VoiceProfile.id == voice_id).first()
            db.close()
            
            if voice_profile and voice_profile.original_audio_path:
                # Check if the file exists
                if os.path.exists(voice_profile.original_audio_path):
                    return voice_profile.original_audio_path
                # Try with uploads directory prefix
                full_path = os.path.join(UPLOADS_DIR, voice_profile.original_audio_path)
                if os.path.exists(full_path):
                    return full_path
                print(f"Voice profile audio file not found: {voice_profile.original_audio_path}")
            return None
        except Exception as e:
            print(f"Error fetching voice profile: {e}")
            return None
    
    def create_session(self, user_id: int, voice_id: Optional[int] = None) -> str:
        """
        Create a new voice chat session.
        
        Args:
            user_id: User ID
            voice_id: Optional voice profile ID for TTS
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {
            "user_id": user_id,
            "voice_id": voice_id,
            "created_at": datetime.utcnow().isoformat(),
            "messages": [],
            "audio_history": [],
            "language": "en"
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        return self._sessions.get(session_id)
    
    def update_session_voice(self, session_id: str, voice_id: int):
        """Update voice profile for session"""
        if session_id in self._sessions:
            self._sessions[session_id]["voice_id"] = voice_id
    
    def set_session_language(self, session_id: str, language: str):
        """Set preferred language for STT"""
        if session_id in self._sessions:
            self._sessions[session_id]["language"] = language
    
    async def process_voice_input(
        self,
        audio_bytes: bytes,
        session_id: str,
        audio_format: str = "wav",
        voice_id: Optional[int] = None,
        audio_prompt_path: Optional[str] = None,
        return_text_only: bool = False
    ) -> Dict:
        """
        Process voice input and generate voice response.
        
        Args:
            audio_bytes: Raw audio bytes from user
            session_id: Chat session ID
            audio_format: Audio format (wav, webm, mp3, etc.)
            voice_id: Optional voice profile ID
            audio_prompt_path: Optional path to voice reference audio
            return_text_only: If True, skip TTS and return text response only
            
        Returns:
            Dict with:
            - user_text: Transcribed user input
            - assistant_text: LLM response text
            - audio_url: URL to generated audio response (if not text_only)
            - audio_duration: Duration of audio response
            - stt_language: Detected language
            - processing_time: Total processing time
        """
        import time
        start_time = time.time()
        
        # Get or create session
        session = self.get_session(session_id)
        if not session:
            session_id = self.create_session(user_id=0, voice_id=voice_id)
            session = self.get_session(session_id)
        
        language = session.get("language", "en") if session else "en"
        
        # Step 1: Speech-to-Text
        stt_start = time.time()
        try:
            stt_result = await stt_service.transcribe_audio_bytes_async(
                audio_bytes=audio_bytes,
                format=audio_format,
                language=language,
                task="transcribe"
            )
            user_text = stt_result["text"]
            detected_language = stt_result.get("language", language)
            stt_time = time.time() - stt_start
        except Exception as e:
            raise RuntimeError(f"Speech recognition failed: {str(e)}")
        
        if not user_text or len(user_text.strip()) == 0:
            return {
                "user_text": "",
                "assistant_text": "I couldn't understand what you said. Please try again.",
                "audio_url": None,
                "audio_duration": 0,
                "stt_language": detected_language,
                "processing_time": time.time() - start_time,
                "error": "empty_transcription"
            }
        
        # Step 2: LLM Response
        llm_start = time.time()
        try:
            # Use streaming for faster perceived response
            assistant_text = await chat_service.get_response(
                user_message=user_text,
                session_id=session_id,
                system_prompt=self._get_voice_chat_prompt()
            )
            llm_time = time.time() - llm_start
        except Exception as e:
            raise RuntimeError(f"LLM processing failed: {str(e)}")
        
        # Store in session
        if session:
            session["messages"].append({
                "role": "user",
                "content": user_text,
                "timestamp": datetime.utcnow().isoformat()
            })
            session["messages"].append({
                "role": "assistant",
                "content": assistant_text,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        result = {
            "user_text": user_text,
            "assistant_text": assistant_text,
            "stt_language": detected_language,
            "session_id": session_id,
            "timings": {
                "stt_seconds": round(stt_time, 3),
                "llm_seconds": round(llm_time, 3)
            }
        }
        
        # Step 3: Text-to-Speech (optional)
        if not return_text_only:
            tts_start = time.time()
            try:
                # Use voice profile or default
                effective_audio_prompt = audio_prompt_path
                if voice_id and not effective_audio_prompt:
                    # Get audio prompt from voice profile
                    effective_audio_prompt = self._get_voice_profile_audio_path(voice_id)
                    if effective_audio_prompt:
                        print(f"Using voice profile {voice_id} audio: {effective_audio_prompt}")
                    else:
                        print(f"Voice profile {voice_id} has no audio path, using default voice")
                
                print(f"[VoiceChatTTS] Calling chatterbox with audio_prompt: {effective_audio_prompt}")
                audio_url, duration = await chatterbox_service.generate_audio_async(
                    text=assistant_text,
                    audio_prompt_path=effective_audio_prompt,
                    exaggeration=0.5,
                    cfg_weight=0.5,
                    temperature=0.8
                )
                tts_time = time.time() - tts_start
                
                result["audio_url"] = audio_url
                result["audio_duration"] = duration
                result["timings"]["tts_seconds"] = round(tts_time, 3)
                
                # Store audio in session
                if session:
                    session["audio_history"].append({
                        "audio_url": audio_url,
                        "duration": duration,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
            except Exception as e:
                print(f"TTS failed: {e}")
                result["audio_url"] = None
                result["audio_duration"] = 0
                result["tts_error"] = str(e)
        
        result["processing_time"] = round(time.time() - start_time, 3)
        return result
    
    def _split_into_sentences(self, text: str) -> list:
        """
        Split text into sentences for per-sentence TTS.
        Splits on sentence-ending punctuation while keeping the punctuation.
        """
        import re
        # Split on . ! ? followed by space or end-of-string, keeping the delimiter
        parts = re.split(r'(?<=[.!?])\s+', text.strip())
        return [p.strip() for p in parts if p.strip()]

    async def process_voice_input_streaming(
        self,
        audio_bytes: bytes,
        session_id: str,
        audio_format: str = "wav",
        voice_id: Optional[int] = None,
        audio_prompt_path: Optional[str] = None
    ) -> AsyncGenerator[Dict, None]:
        """
        Process voice input with streaming LLM + per-sentence TTS.
        
        Pipeline:
        1. STT (full transcription)
        2. LLM streaming → accumulate tokens into sentences
        3. As each sentence completes, generate TTS immediately → yield audio
        4. Frontend plays audio chunks in a queue for near-real-time playback
        
        Yields SSE events:
        - stt_complete: Transcription done, includes user text
        - llm_chunk: Partial LLM text for live display
        - tts_chunk: Base64 WAV audio for one sentence, play immediately
        - complete: All done, final texts
        - error: Something failed
        """
        import time
        import base64
        import re
        
        start_time = time.time()
        
        session = self.get_session(session_id)
        if not session:
            session_id = self.create_session(user_id=0, voice_id=voice_id)
            session = self.get_session(session_id)
        language = session.get("language", "en") if session else "en"
        
        # Resolve voice audio prompt
        effective_audio_prompt = audio_prompt_path
        if voice_id and not effective_audio_prompt:
            effective_audio_prompt = self._get_voice_profile_audio_path(voice_id)
        print(f"[StreamVoice] voice_id={voice_id}, audio_prompt={effective_audio_prompt}")
        
        # --- Phase 1: STT ---
        yield {"type": "stt_start", "message": "Listening..."}
        
        try:
            stt_result = await stt_service.transcribe_audio_bytes_async(
                audio_bytes=audio_bytes,
                format=audio_format,
                language=language,
                task="transcribe"
            )
            user_text = stt_result["text"]
            detected_language = stt_result.get("language", language)
            print(f"[StreamVoice] STT done: {user_text}")
            
            yield {
                "type": "stt_complete",
                "text": user_text,
                "language": detected_language
            }
        except Exception as e:
            yield {"type": "error", "phase": "stt", "message": str(e)}
            return
        
        if not user_text or len(user_text.strip()) == 0:
            yield {
                "type": "error",
                "phase": "stt",
                "message": "Could not understand audio"
            }
            return
        
        # --- Phase 2: LLM streaming + Phase 3: per-sentence TTS ---
        yield {"type": "llm_start", "message": "Thinking..."}
        
        full_response = ""
        sentence_buffer = ""  # Accumulates tokens until a sentence boundary
        tts_chunk_index = 0
        
        # Sentence boundary pattern: ends with . ! or ?
        sentence_end_pattern = re.compile(r'[.!?]\s*$')
        
        try:
            async for chunk in chat_service.get_response_stream(
                user_message=user_text,
                session_id=session_id,
                system_prompt=self._get_voice_chat_prompt()
            ):
                full_response += chunk
                sentence_buffer += chunk
                
                # Yield LLM text chunk for live display
                yield {"type": "llm_chunk", "content": chunk}
                
                # Check if we have a complete sentence
                if sentence_end_pattern.search(sentence_buffer):
                    # Extract complete sentences from the buffer
                    sentences = self._split_into_sentences(sentence_buffer)
                    
                    if len(sentences) > 1:
                        # All but last are complete sentences
                        complete_sentences = sentences[:-1]
                        sentence_buffer = sentences[-1]
                        # Check if the last piece also ends with punctuation
                        if sentence_end_pattern.search(sentences[-1]):
                            complete_sentences = sentences
                            sentence_buffer = ""
                    else:
                        complete_sentences = sentences
                        sentence_buffer = ""
                    
                    # Generate TTS for each complete sentence
                    for sentence_text in complete_sentences:
                        if len(sentence_text.strip()) < 2:
                            continue
                        print(f"[StreamVoice] TTS for sentence {tts_chunk_index}: {sentence_text}")
                        try:
                            audio_url, duration = await chatterbox_service.generate_audio_async(
                                text=sentence_text,
                                audio_prompt_path=effective_audio_prompt,
                                exaggeration=0.5,
                                cfg_weight=0.5,
                                temperature=0.8
                            )
                            
                            # Read the generated audio file and encode as base64
                            audio_file_path = audio_url.replace("/static/", "static/", 1)
                            with open(audio_file_path, "rb") as f:
                                audio_data = base64.b64encode(f.read()).decode("utf-8")
                            
                            yield {
                                "type": "tts_chunk",
                                "audio_data": audio_data,
                                "audio_url": audio_url,
                                "duration": duration,
                                "sentence": sentence_text,
                                "chunk_index": tts_chunk_index
                            }
                            tts_chunk_index += 1
                        except Exception as e:
                            print(f"[StreamVoice] TTS error for sentence: {e}")
                            # Continue with next sentence
            
            # Handle any remaining text in the buffer after LLM stream ends
            if sentence_buffer.strip() and len(sentence_buffer.strip()) >= 2:
                print(f"[StreamVoice] TTS for remaining: {sentence_buffer}")
                try:
                    audio_url, duration = await chatterbox_service.generate_audio_async(
                        text=sentence_buffer.strip(),
                        audio_prompt_path=effective_audio_prompt,
                        exaggeration=0.5,
                        cfg_weight=0.5,
                        temperature=0.8
                    )
                    
                    audio_file_path = audio_url.replace("/static/", "static/", 1)
                    with open(audio_file_path, "rb") as f:
                        audio_data = base64.b64encode(f.read()).decode("utf-8")
                    
                    yield {
                        "type": "tts_chunk",
                        "audio_data": audio_data,
                        "audio_url": audio_url,
                        "duration": duration,
                        "sentence": sentence_buffer.strip(),
                        "chunk_index": tts_chunk_index
                    }
                    tts_chunk_index += 1
                except Exception as e:
                    print(f"[StreamVoice] TTS error for remaining: {e}")
            
            yield {"type": "llm_complete", "text": full_response}
            
        except Exception as e:
            yield {"type": "error", "phase": "llm", "message": str(e)}
            return
        
        # Store in session
        if session:
            session["messages"].append({
                "role": "user",
                "content": user_text,
                "timestamp": datetime.utcnow().isoformat()
            })
            session["messages"].append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Final complete message
        processing_time = round(time.time() - start_time, 3)
        yield {
            "type": "complete",
            "user_text": user_text,
            "assistant_text": full_response,
            "session_id": session_id,
            "processing_time": processing_time,
            "tts_chunks": tts_chunk_index
        }
    
    def _get_voice_chat_prompt(self) -> str:
        """Get system prompt optimized for voice conversation"""
        return """You are a friendly voice assistant having a natural spoken conversation.

MATCH YOUR RESPONSE LENGTH TO THE QUESTION:
- Simple greetings, yes/no, or quick facts → 1-2 sentences. Example: "Hey!" → "Hey! What's up?"
- Medium questions (opinions, recommendations, how-to) → 3-5 sentences. Give a clear, helpful answer.
- Deep questions (explain a concept, tell me about X, compare things) → As many sentences as needed to explain well. Be thorough but stay focused.

STYLE RULES:
- Sound natural and conversational, like talking to a friend.
- NO markdown, NO bullet points, NO numbered lists, NO formatting.
- NO "I'd be happy to help" or filler phrases. Just answer directly.
- Use plain spoken language. Write how you'd actually say it out loud.
- When explaining something, use connecting words like "so", "basically", "the thing is" to sound natural.

Examples:
User: "Hello" → "Hey! What's up?"
User: "What is machine learning?" → Give a clear 4-6 sentence spoken explanation.
User: "Thanks" → "No problem!"
User: "Explain how the internet works" → Give a thorough but conversational explanation, as long as needed."""
    
    def transcribe_only(
        self,
        audio_bytes: bytes,
        audio_format: str = "wav",
        language: Optional[str] = None
    ) -> Dict:
        """
        Transcribe audio without generating a response.
        Useful for voice-to-text only features.
        """
        return stt_service.transcribe_audio_bytes(
            audio_bytes=audio_bytes,
            format=audio_format,
            language=language,
            task="transcribe"
        )
    
    async def transcribe_only_async(
        self,
        audio_bytes: bytes,
        audio_format: str = "wav",
        language: Optional[str] = None
    ) -> Dict:
        """Async version of transcribe_only"""
        return await stt_service.transcribe_audio_bytes_async(
            audio_bytes=audio_bytes,
            format=audio_format,
            language=language,
            task="transcribe"
        )
    
    def get_status(self) -> Dict:
        """Get voice chat service status"""
        return {
            "stt_available": stt_service.is_available,
            "stt_info": stt_service.get_model_info(),
            "tts_available": chatterbox_service.is_available,
            "tts_info": chatterbox_service.get_model_info(),
            "active_sessions": len(self._sessions)
        }
    
    def cleanup_session(self, session_id: str):
        """Clean up a voice chat session"""
        if session_id in self._sessions:
            del self._sessions[session_id]


# Singleton instance
voice_chat_service = VoiceChatService()
