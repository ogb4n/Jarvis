import whisper
import numpy as np
import io
import wave
import tempfile
import os
from typing import Optional, Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class SpeechToTextService:
    def __init__(self, model_size: str = "base"):
        """
        Initialize the Speech-to-Text service with Whisper
        
        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
        """
        self.model_size = model_size
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model"""
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            logger.info(f"Whisper model {self.model_size} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe_audio_file(self, audio_path: str, language: str = "fr") -> Dict[str, Any]:
        """
        Transcribe audio from file
        
        Args:
            audio_path: Path to audio file
            language: Language code (fr, en, etc.)
        
        Returns:
            Dict with transcription results
        """
        try:
            logger.info(f"Transcribing audio file: {audio_path}")
            
            # Whisper transcription
            result = self.model.transcribe(
                audio_path,
                language=language,
                fp16=False  # Better compatibility
            )
            
            return {
                "text": result["text"].strip(),
                "language": result["language"],
                "segments": result["segments"],
                "confidence": self._calculate_confidence(result["segments"])
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return {
                "text": "",
                "error": str(e),
                "confidence": 0.0
            }
    
    def transcribe_audio_data(self, audio_data: bytes, sample_rate: int = 16000, language: str = "fr") -> Dict[str, Any]:
        """
        Transcribe audio from raw bytes
        
        Args:
            audio_data: Raw audio bytes
            sample_rate: Sample rate of audio
            language: Language code
        
        Returns:
            Dict with transcription results
        """
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                # Convert bytes to wav file
                self._save_audio_bytes_as_wav(audio_data, temp_file.name, sample_rate)
                
                # Transcribe the temporary file
                result = self.transcribe_audio_file(temp_file.name, language)
                
                # Clean up
                os.unlink(temp_file.name)
                
                return result
                
        except Exception as e:
            logger.error(f"Error transcribing audio data: {e}")
            return {
                "text": "",
                "error": str(e),
                "confidence": 0.0
            }
    
    def transcribe_numpy_array(self, audio_array: np.ndarray, sample_rate: int = 16000, language: str = "fr") -> Dict[str, Any]:
        """
        Transcribe audio from numpy array
        
        Args:
            audio_array: Audio data as numpy array
            sample_rate: Sample rate
            language: Language code
        
        Returns:
            Dict with transcription results
        """
        try:
            # Normalize audio array
            if audio_array.dtype != np.float32:
                audio_array = audio_array.astype(np.float32)
            
            # Ensure values are in [-1, 1] range
            if np.max(np.abs(audio_array)) > 1.0:
                audio_array = audio_array / np.max(np.abs(audio_array))
            
            # Use Whisper directly with numpy array
            result = self.model.transcribe(
                audio_array,
                language=language,
                fp16=False
            )
            
            return {
                "text": result["text"].strip(),
                "language": result["language"],
                "segments": result["segments"],
                "confidence": self._calculate_confidence(result["segments"])
            }
            
        except Exception as e:
            logger.error(f"Error transcribing numpy array: {e}")
            return {
                "text": "",
                "error": str(e),
                "confidence": 0.0
            }
    
    def _save_audio_bytes_as_wav(self, audio_data: bytes, output_path: str, sample_rate: int):
        """Save raw audio bytes as WAV file"""
        try:
            # Convert bytes to numpy array (assuming 16-bit PCM)
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Save as WAV file
            with wave.open(output_path, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data)
                
        except Exception as e:
            logger.error(f"Error saving audio bytes as WAV: {e}")
            raise
    
    def _calculate_confidence(self, segments) -> float:
        """Calculate average confidence from segments"""
        if not segments:
            return 0.0
        
        # Whisper doesn't provide confidence directly, 
        # but we can estimate it from segment properties
        total_confidence = 0.0
        total_duration = 0.0
        
        for segment in segments:
            duration = segment.get('end', 0) - segment.get('start', 0)
            # Simple heuristic: longer segments with fewer tokens are more confident
            tokens_count = len(segment.get('tokens', []))
            if tokens_count > 0:
                confidence = min(1.0, duration / tokens_count * 2)  # Adjust multiplier as needed
            else:
                confidence = 0.5
                
            total_confidence += confidence * duration
            total_duration += duration
        
        return total_confidence / total_duration if total_duration > 0 else 0.0
    
    def is_speech_detected(self, audio_array: np.ndarray, threshold: float = 0.01) -> bool:
        """
        Simple voice activity detection
        
        Args:
            audio_array: Audio data
            threshold: Energy threshold for speech detection
        
        Returns:
            True if speech is detected
        """
        try:
            # Calculate RMS energy
            rms_energy = np.sqrt(np.mean(audio_array ** 2))
            return rms_energy > threshold
        except:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "model_size": self.model_size,
            "is_loaded": self.model is not None,
            "supported_languages": [
                "fr", "en", "es", "de", "it", "pt", "nl", "pl", "ru", "ja", "ko", "zh"
            ]
        }