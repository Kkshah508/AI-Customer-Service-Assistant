try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    sr = None
    SPEECH_RECOGNITION_AVAILABLE = False

import torch
from transformers import pipeline
import tempfile
import os
import logging
from typing import Optional, Tuple, Union, Any
import io
import wave
import numpy as np
from scipy.io.wavfile import write

# Define AudioData type for when speech_recognition is not available
if SPEECH_RECOGNITION_AVAILABLE:
    AudioDataType = sr.AudioData
else:
    AudioDataType = Any

logger = logging.getLogger(__name__)

class VoiceHandler:
    
    def __init__(self):
        logger.info("Initializing Voice Handler...")
        
        if not SPEECH_RECOGNITION_AVAILABLE:
            raise ImportError("speech_recognition module is not available")
            
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
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
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    def speech_to_text(self, audio_data: AudioDataType) -> Optional[str]:
        if not SPEECH_RECOGNITION_AVAILABLE:
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
        if not self.tts_pipeline:
            return None
        
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
            
            return None
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None
    
    def listen_for_speech(self, timeout: int = 5) -> Optional[str]:
        if not SPEECH_RECOGNITION_AVAILABLE:
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
        if not SPEECH_RECOGNITION_AVAILABLE:
            return None
            
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                return self.speech_to_text(audio)
        except Exception as e:
            logger.error(f"Audio file processing error: {e}")
            return None
