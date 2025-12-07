import os
import logging
from typing import Optional, Any
import io
import wave

logger = logging.getLogger(__name__)

# Lazy import flags for heavy dependencies
_sr = None
_torch = None
_transformers_pipeline = None
_np = None
SPEECH_RECOGNITION_AVAILABLE = False

def _lazy_import_speech_recognition():
    global _sr, SPEECH_RECOGNITION_AVAILABLE
    if _sr is not None:
        return _sr
    try:
        import speech_recognition as sr
        _sr = sr
        SPEECH_RECOGNITION_AVAILABLE = True
        return _sr
    except ImportError:
        logger.warning("speech_recognition not available")
        return None

def _lazy_import_torch():
    global _torch
    if _torch is not None:
        return _torch
    try:
        import torch
        _torch = torch
        return _torch
    except ImportError:
        logger.warning("torch not available")
        return None

def _lazy_import_transformers_pipeline():
    global _transformers_pipeline
    if _transformers_pipeline is not None:
        return _transformers_pipeline
    try:
        from transformers import pipeline
        _transformers_pipeline = pipeline
        return _transformers_pipeline
    except ImportError:
        logger.warning("transformers not available")
        return None

def _lazy_import_numpy():
    global _np
    if _np is not None:
        return _np
    try:
        import numpy as np
        _np = np
        return _np
    except ImportError:
        logger.warning("numpy not available")
        return None

AudioDataType = Any

class VoiceHandler:
    
    def __init__(self):
        logger.info("Initializing Voice Handler...")
        
        # Lazy load speech recognition
        sr = _lazy_import_speech_recognition()
        
        self.recognizer = sr.Recognizer() if sr else None
        try:
            self.microphone = sr.Microphone() if sr else None
        except Exception:
            self.microphone = None
        
        self.tts_pipeline = None
        
        if self.microphone and self.recognizer:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
            except Exception:
                self.microphone = None
    
    def _ensure_tts_pipeline(self):
        if self.tts_pipeline is not None:
            return
        # Lazy load torch and transformers only when TTS is actually needed
        torch = _lazy_import_torch()
        pipeline = _lazy_import_transformers_pipeline()
        if not torch or not pipeline:
            logger.warning("TTS dependencies not available")
            return
        try:
            self.tts_pipeline = pipeline(
                "text-to-speech",
                model="ResembleAI/chatterbox",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("✓ TTS model loaded successfully")
        except Exception as e:
            logger.warning(f"TTS model failed to load: {e}")
            self.tts_pipeline = None
    
    def speech_to_text(self, audio_data: AudioDataType) -> Optional[str]:
        sr = _lazy_import_speech_recognition()
        if not sr or not self.recognizer:
            return None
            
        try:
            text = self.recognizer.recognize_google(audio_data)
            logger.info(f"Recognized speech: {text}")
            return text
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            return None
    
    def text_to_speech(self, text: str) -> Optional[bytes]:
        np = _lazy_import_numpy()
        if not np:
            return None
            
        if self.tts_pipeline is None:
            self._ensure_tts_pipeline()
        if self.tts_pipeline:
            try:
                result = self.tts_pipeline(text)
                if isinstance(result, dict) and "audio" in result:
                    audio = result["audio"]
                    sample_rate = result.get("sampling_rate", 22050)
                    audio_np = np.array(audio)
                    if audio_np.dtype != np.int16:
                        audio_np = (audio_np * 32767).astype(np.int16)
                    buffer = io.BytesIO()
                    with wave.open(buffer, 'wb') as wav_file:
                        wav_file.setnchannels(1)
                        wav_file.setsampwidth(2)
                        wav_file.setframerate(sample_rate)
                        wav_file.writeframes(audio_np.tobytes())
                    return buffer.getvalue()
            except Exception as e:
                logger.error(f"TTS error: {e}")
        
        # Fallback: generate a simple tone
        try:
            duration = 1.0
            sample_rate = 22050
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = 0.2 * np.sin(2 * np.pi * 440 * t)
            audio_np = (tone * 32767).astype(np.int16)
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_np.tobytes())
            return buffer.getvalue()
        except Exception:
            return None
    
    def listen_for_speech(self, timeout: int = 5) -> Optional[str]:
        sr = _lazy_import_speech_recognition()
        if not sr or not self.recognizer or not self.microphone:
            return None
            
        try:
            with self.microphone as source:
                logger.info("Listening for speech...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                return self.speech_to_text(audio)
        except sr.WaitTimeoutError:
            logger.warning("Listening timeout")
            return None
        except Exception as e:
            logger.error(f"Listening error: {e}")
            return None
    
    def process_audio_file(self, audio_file) -> Optional[str]:
        sr = _lazy_import_speech_recognition()
        if not sr or not self.recognizer:
            return None
            
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                return self.speech_to_text(audio)
        except Exception as e:
            logger.error(f"Audio file processing error: {e}")
            return None
