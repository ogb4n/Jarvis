import sounddevice as sd
import numpy as np
import threading
import queue
import time
from typing import Optional, Callable, Dict, Any
import logging
from .speech_to_text import SpeechToTextService
from .text_to_speech import TextToSpeechService

logger = logging.getLogger(__name__)

class AudioManager:
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_duration: float = 1.0,
        whisper_model: str = "base",
        language: str = "fr",
        input_device: Optional[int] = None,
        output_device: Optional[int] = None
    ):
        """
        Audio Manager for handling recording, playback, STT and TTS
        
        Args:
            sample_rate: Audio sample rate
            channels: Number of audio channels
            chunk_duration: Duration of audio chunks in seconds
            whisper_model: Whisper model size
            language: Default language for STT
            input_device: Audio input device ID (None = default)
            output_device: Audio output device ID (None = default)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = int(sample_rate * chunk_duration)
        self.language = language
        self.input_device = input_device
        self.output_device = output_device
        
        # Services
        self.stt_service = SpeechToTextService(model_size=whisper_model)
        self.tts_service = TextToSpeechService()
        
        # Recording state
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.recording_thread = None
        
        # Callbacks
        self.on_transcription: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_audio_chunk: Optional[Callable[[np.ndarray], None]] = None
        
        logger.info("AudioManager initialized")
    
    def start_recording(self, callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        """
        Start continuous audio recording and transcription
        
        Args:
            callback: Function to call when transcription is ready
        """
        if self.is_recording:
            logger.warning("Recording already in progress")
            return
            
        self.on_transcription = callback
        self.is_recording = True
        
        # Start recording thread
        self.recording_thread = threading.Thread(target=self._recording_loop, daemon=True)
        self.recording_thread.start()
        
        logger.info("Audio recording started")
    
    def stop_recording(self):
        """Stop audio recording"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2.0)
        
        # Clear queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
                
        logger.info("Audio recording stopped")
    
    def _recording_loop(self):
        """Main recording loop"""
        try:
            # Audio recording callback
            def audio_callback(indata, frames, time_info, status):
                if status:
                    logger.warning(f"Audio callback status: {status}")
                    
                # Convert to mono if needed
                if self.channels == 1 and indata.shape[1] > 1:
                    audio_data = np.mean(indata, axis=1)
                else:
                    audio_data = indata[:, 0] if indata.shape[1] > 0 else indata
                
                # Add to queue for processing
                if self.is_recording:
                    self.audio_queue.put(audio_data.copy())
            
            # Start audio stream
            with sd.InputStream(
                callback=audio_callback,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                dtype=np.float32,
                device=self.input_device
            ):
                logger.info("Audio stream started")
                
                # Process audio chunks
                accumulated_audio = np.array([], dtype=np.float32)
                silence_threshold = 0.01
                silence_duration = 0
                max_silence = 2.0  # seconds
                min_audio_length = 1.0  # seconds
                
                while self.is_recording:
                    try:
                        # Get audio chunk
                        chunk = self.audio_queue.get(timeout=0.1)
                        
                        # Call chunk callback if set
                        if self.on_audio_chunk:
                            self.on_audio_chunk(chunk)
                        
                        # Check for voice activity
                        if self.stt_service.is_speech_detected(chunk, silence_threshold):
                            # Speech detected, accumulate audio
                            accumulated_audio = np.append(accumulated_audio, chunk)
                            silence_duration = 0
                        else:
                            # Silence detected
                            silence_duration += len(chunk) / self.sample_rate
                            
                            # If we have accumulated audio and enough silence, process it
                            if (len(accumulated_audio) > 0 and 
                                silence_duration >= max_silence and
                                len(accumulated_audio) / self.sample_rate >= min_audio_length):
                                
                                # Process accumulated audio
                                self._process_audio_chunk(accumulated_audio)
                                accumulated_audio = np.array([], dtype=np.float32)
                                silence_duration = 0
                        
                    except queue.Empty:
                        continue
                    except Exception as e:
                        logger.error(f"Error in recording loop: {e}")
                        break
                        
        except Exception as e:
            logger.error(f"Error in recording loop: {e}")
        finally:
            logger.info("Recording loop ended")
    
    def _process_audio_chunk(self, audio_data: np.ndarray):
        """Process audio chunk for transcription"""
        try:
            logger.info("Processing audio chunk for transcription")
            
            # Transcribe audio
            result = self.stt_service.transcribe_numpy_array(
                audio_data, 
                self.sample_rate, 
                self.language
            )
            
            if result.get("text") and self.on_transcription:
                self.on_transcription(result)
                
        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}")
    
    def record_single_command(self, duration: float = 5.0) -> Dict[str, Any]:
        """
        Record a single voice command
        
        Args:
            duration: Recording duration in seconds
        
        Returns:
            Transcription result
        """
        try:
            logger.info(f"Recording single command for {duration} seconds")
            
            # Record audio
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32
            )
            sd.wait()  # Wait for recording to complete
            
            # Convert to mono if needed
            if self.channels == 1 and audio_data.shape[1] > 1:
                audio_data = np.mean(audio_data, axis=1)
            elif audio_data.shape[1] > 0:
                audio_data = audio_data[:, 0]
            
            # Transcribe
            result = self.stt_service.transcribe_numpy_array(
                audio_data,
                self.sample_rate,
                self.language
            )
            
            logger.info(f"Command recorded: {result.get('text', 'No text')}")
            return result
            
        except Exception as e:
            logger.error(f"Error recording single command: {e}")
            return {"text": "", "error": str(e), "confidence": 0.0}
    
    def speak_response(self, text: str, blocking: bool = True) -> bool:
        """
        Speak a text response
        
        Args:
            text: Text to speak
            blocking: Whether to wait for speech completion
        
        Returns:
            True if successful
        """
        try:
            return self.tts_service.speak(text, blocking)
        except Exception as e:
            logger.error(f"Error speaking response: {e}")
            return False
    
    def transcribe_file(self, file_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file
        
        Args:
            file_path: Path to audio file
        
        Returns:
            Transcription result
        """
        return self.stt_service.transcribe_audio_file(file_path, self.language)
    
    def synthesize_to_file(self, text: str, output_path: str) -> bool:
        """
        Synthesize text to audio file
        
        Args:
            text: Text to synthesize
            output_path: Output file path
        
        Returns:
            True if successful
        """
        return self.tts_service.synthesize_to_file(text, output_path)
    
    def get_audio_devices(self) -> Dict[str, Any]:
        """Get available audio devices"""
        try:
            devices = sd.query_devices()
            return {
                "default_input": sd.default.device[0],
                "default_output": sd.default.device[1],
                "devices": [
                    {
                        "id": i,
                        "name": device["name"],
                        "max_input_channels": device["max_input_channels"],
                        "max_output_channels": device["max_output_channels"],
                        "default_samplerate": device["default_samplerate"]
                    }
                    for i, device in enumerate(devices)
                ]
            }
        except Exception as e:
            logger.error(f"Error getting audio devices: {e}")
            return {"error": str(e)}
    
    def set_language(self, language: str):
        """Set the language for STT"""
        self.language = language
        logger.info(f"Language set to: {language}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "is_recording": self.is_recording,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "language": self.language,
            "stt_model": self.stt_service.model_size,
            "queue_size": self.audio_queue.qsize() if hasattr(self.audio_queue, 'qsize') else 0
        }
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.stop_recording()
            self.tts_service.cleanup()
            logger.info("AudioManager cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up AudioManager: {e}")