import pyttsx3
import io
import wave
import tempfile
import os
from typing import Optional, Dict, Any, List
import logging
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

class TextToSpeechService:
    def __init__(self, voice_rate: int = 200, voice_volume: float = 0.9, voice_id: Optional[str] = None):
        """
        Initialize the Text-to-Speech service with pyttsx3
        
        Args:
            voice_rate: Speech rate (words per minute)
            voice_volume: Voice volume (0.0 to 1.0)
            voice_id: Specific voice ID to use
        """
        self.voice_rate = voice_rate
        self.voice_volume = voice_volume
        self.voice_id = voice_id
        self.engine = None
        self._lock = threading.Lock()
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the TTS engine"""
        try:
            logger.info("Initializing TTS engine...")
            self.engine = pyttsx3.init()
            
            # Set voice properties
            self.engine.setProperty('rate', self.voice_rate)
            self.engine.setProperty('volume', self.voice_volume)
            
            # Set specific voice if provided
            if self.voice_id:
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if self.voice_id in voice.id:
                        self.engine.setProperty('voice', voice.id)
                        break
            
            logger.info("TTS engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            raise
    
    def speak(self, text: str, blocking: bool = True) -> bool:
        """
        Speak text directly through speakers
        
        Args:
            text: Text to speak
            blocking: Whether to wait for speech completion
        
        Returns:
            True if successful
        """
        try:
            if not text.strip():
                return False
                
            logger.info(f"Speaking text: {text[:50]}...")
            
            with self._lock:
                self.engine.say(text)
                if blocking:
                    self.engine.runAndWait()
                else:
                    # Run in separate thread for non-blocking
                    threading.Thread(target=self.engine.runAndWait, daemon=True).start()
            
            return True
            
        except Exception as e:
            logger.error(f"Error speaking text: {e}")
            return False
    
    def synthesize_to_file(self, text: str, output_path: str) -> bool:
        """
        Synthesize text to audio file
        
        Args:
            text: Text to synthesize
            output_path: Output file path
        
        Returns:
            True if successful
        """
        try:
            if not text.strip():
                return False
                
            logger.info(f"Synthesizing text to file: {output_path}")
            
            with self._lock:
                # Save to file
                self.engine.save_to_file(text, output_path)
                self.engine.runAndWait()
            
            # Verify file was created
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"Audio file created successfully: {output_path}")
                return True
            else:
                logger.error(f"Failed to create audio file: {output_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error synthesizing to file: {e}")
            return False
    
    def synthesize_to_bytes(self, text: str) -> Optional[bytes]:
        """
        Synthesize text to audio bytes
        
        Args:
            text: Text to synthesize
        
        Returns:
            Audio bytes or None if failed
        """
        try:
            if not text.strip():
                return None
                
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Synthesize to temporary file
            if self.synthesize_to_file(text, temp_path):
                # Read file as bytes
                with open(temp_path, 'rb') as f:
                    audio_bytes = f.read()
                
                # Clean up
                os.unlink(temp_path)
                
                return audio_bytes
            else:
                # Clean up on failure
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                return None
                
        except Exception as e:
            logger.error(f"Error synthesizing to bytes: {e}")
            return None
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available voices
        
        Returns:
            List of voice information
        """
        try:
            voices = []
            if self.engine:
                for voice in self.engine.getProperty('voices'):
                    voices.append({
                        'id': voice.id,
                        'name': voice.name,
                        'languages': getattr(voice, 'languages', []),
                        'gender': getattr(voice, 'gender', 'unknown'),
                        'age': getattr(voice, 'age', 'unknown')
                    })
            return voices
            
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return []
    
    def set_voice(self, voice_id: str) -> bool:
        """
        Set the voice to use
        
        Args:
            voice_id: Voice ID to set
        
        Returns:
            True if successful
        """
        try:
            with self._lock:
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if voice_id in voice.id:
                        self.engine.setProperty('voice', voice.id)
                        self.voice_id = voice_id
                        logger.info(f"Voice set to: {voice.name}")
                        return True
                
                logger.warning(f"Voice not found: {voice_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False
    
    def set_rate(self, rate: int) -> bool:
        """
        Set speech rate
        
        Args:
            rate: Speech rate (words per minute)
        
        Returns:
            True if successful
        """
        try:
            with self._lock:
                self.engine.setProperty('rate', rate)
                self.voice_rate = rate
                logger.info(f"Speech rate set to: {rate} WPM")
                return True
                
        except Exception as e:
            logger.error(f"Error setting speech rate: {e}")
            return False
    
    def set_volume(self, volume: float) -> bool:
        """
        Set speech volume
        
        Args:
            volume: Volume level (0.0 to 1.0)
        
        Returns:
            True if successful
        """
        try:
            volume = max(0.0, min(1.0, volume))  # Clamp to valid range
            
            with self._lock:
                self.engine.setProperty('volume', volume)
                self.voice_volume = volume
                logger.info(f"Speech volume set to: {volume}")
                return True
                
        except Exception as e:
            logger.error(f"Error setting speech volume: {e}")
            return False
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about the TTS engine"""
        try:
            return {
                "engine_name": "pyttsx3",
                "is_initialized": self.engine is not None,
                "current_rate": self.voice_rate,
                "current_volume": self.voice_volume,
                "current_voice_id": self.voice_id,
                "available_voices_count": len(self.get_available_voices())
            }
        except Exception as e:
            logger.error(f"Error getting engine info: {e}")
            return {"error": str(e)}
    
    def cleanup(self):
        """Clean up TTS resources"""
        try:
            if self.engine:
                self.engine.stop()
                logger.info("TTS engine stopped")
        except Exception as e:
            logger.error(f"Error cleaning up TTS engine: {e}")