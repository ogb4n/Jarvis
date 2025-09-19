import numpy as np
import threading
import time
import queue
from typing import List, Callable, Optional, Dict, Any
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class WakeWordState(Enum):
    LISTENING = "listening"
    WAKE_DETECTED = "wake_detected"
    COMMAND_MODE = "command_mode"
    PROCESSING = "processing"
    SPEAKING = "speaking"

@dataclass
class WakeWordConfig:
    wake_phrases: List[str]
    sensitivity: float = 0.7
    timeout_seconds: float = 5.0
    min_confidence: float = 0.6
    language: str = "fr"

class WakeWordDetector:
    def __init__(
        self,
        audio_manager,
        config: WakeWordConfig,
        on_wake_detected: Optional[Callable] = None,
        on_command_received: Optional[Callable[[str], None]] = None,
        on_state_changed: Optional[Callable[[WakeWordState], None]] = None
    ):
        """
        Wake Word Detector for continuous listening
        
        Args:
            audio_manager: AudioManager instance
            config: Wake word configuration
            on_wake_detected: Callback when wake word is detected
            on_command_received: Callback when command is transcribed
            on_state_changed: Callback when state changes
        """
        self.audio_manager = audio_manager
        self.config = config
        self.on_wake_detected = on_wake_detected
        self.on_command_received = on_command_received
        self.on_state_changed = on_state_changed
        
        # State management
        self.state = WakeWordState.LISTENING
        self.is_running = False
        self.listening_thread = None
        
        # Audio processing
        self.audio_buffer = queue.Queue()
        self.accumulated_audio = np.array([], dtype=np.float32)
        self.last_activity_time = time.time()
        
        # Configuration
        self.chunk_duration = 1.0  # seconds
        self.buffer_duration = 3.0  # seconds of audio to keep for wake word detection
        self.command_timeout = self.config.timeout_seconds
        
        logger.info("WakeWordDetector initialized")
    
    def start_listening(self):
        """Start continuous listening for wake words"""
        if self.is_running:
            logger.warning("Wake word detector already running")
            return
        
        self.is_running = True
        self.state = WakeWordState.LISTENING
        self._notify_state_change()
        
        # Start audio recording
        self.audio_manager.start_recording(self._on_audio_chunk)
        
        # Start processing thread
        self.listening_thread = threading.Thread(target=self._listening_loop, daemon=True)
        self.listening_thread.start()
        
        logger.info("Wake word detector started")
    
    def stop_listening(self):
        """Stop listening for wake words"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.audio_manager.stop_recording()
        
        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join(timeout=2.0)
        
        # Clear buffers
        while not self.audio_buffer.empty():
            try:
                self.audio_buffer.get_nowait()
            except queue.Empty:
                break
        
        self.accumulated_audio = np.array([], dtype=np.float32)
        self.state = WakeWordState.LISTENING
        
        logger.info("Wake word detector stopped")
    
    def _on_audio_chunk(self, audio_chunk: np.ndarray):
        """Callback for audio chunks from AudioManager"""
        if self.is_running:
            self.audio_buffer.put(audio_chunk.copy())
    
    def _listening_loop(self):
        """Main listening loop"""
        try:
            while self.is_running:
                try:
                    # Get audio chunk
                    chunk = self.audio_buffer.get(timeout=0.1)
                    
                    # Add to accumulated buffer
                    self.accumulated_audio = np.append(self.accumulated_audio, chunk)
                    
                    # Keep only last buffer_duration seconds
                    max_samples = int(self.buffer_duration * self.audio_manager.sample_rate)
                    if len(self.accumulated_audio) > max_samples:
                        self.accumulated_audio = self.accumulated_audio[-max_samples:]
                    
                    # Check for voice activity
                    if self.audio_manager.stt_service.is_speech_detected(chunk):
                        self.last_activity_time = time.time()
                        
                        # Process based on current state
                        if self.state == WakeWordState.LISTENING:
                            self._check_for_wake_word()
                        elif self.state == WakeWordState.COMMAND_MODE:
                            # Continue accumulating for command
                            pass
                    else:
                        # Handle silence based on state
                        silence_duration = time.time() - self.last_activity_time
                        
                        if self.state == WakeWordState.COMMAND_MODE and silence_duration > 1.5:
                            # End of command, process accumulated audio
                            self._process_command()
                        elif self.state == WakeWordState.WAKE_DETECTED and silence_duration > 0.5:
                            # Timeout waiting for command
                            self._reset_to_listening()
                
                except queue.Empty:
                    # Check for timeouts
                    if self.state == WakeWordState.COMMAND_MODE:
                        silence_duration = time.time() - self.last_activity_time
                        if silence_duration > self.command_timeout:
                            logger.info("Command timeout, returning to listening mode")
                            self._reset_to_listening()
                    continue
                except Exception as e:
                    logger.error(f"Error in listening loop: {e}")
                    
        except Exception as e:
            logger.error(f"Fatal error in listening loop: {e}")
        finally:
            logger.info("Listening loop ended")
    
    def _check_for_wake_word(self):
        """Check if accumulated audio contains wake word"""
        try:
            # Only check if we have enough audio
            min_samples = int(1.0 * self.audio_manager.sample_rate)  # At least 1 second
            if len(self.accumulated_audio) < min_samples:
                return
            
            # Transcribe recent audio
            result = self.audio_manager.stt_service.transcribe_numpy_array(
                self.accumulated_audio,
                self.audio_manager.sample_rate,
                self.config.language
            )
            
            transcription = result.get("text", "").lower().strip()
            confidence = result.get("confidence", 0.0)
            
            if not transcription:
                return
            
            logger.debug(f"Checking transcription: '{transcription}' (confidence: {confidence:.2f})")
            
            # Check for wake phrases
            for wake_phrase in self.config.wake_phrases:
                if wake_phrase.lower() in transcription and confidence >= self.config.min_confidence:
                    logger.info(f"Wake word detected: '{wake_phrase}' in '{transcription}'")
                    self._handle_wake_detected(transcription)
                    return
                    
        except Exception as e:
            logger.error(f"Error checking for wake word: {e}")
    
    def _handle_wake_detected(self, transcription: str):
        """Handle wake word detection"""
        self.state = WakeWordState.WAKE_DETECTED
        self._notify_state_change()
        
        # Clear accumulated audio and start fresh for command
        self.accumulated_audio = np.array([], dtype=np.float32)
        self.last_activity_time = time.time()
        
        # Notify callback
        if self.on_wake_detected:
            try:
                self.on_wake_detected()
            except Exception as e:
                logger.error(f"Error in wake detected callback: {e}")
        
        # Transition to command mode
        time.sleep(0.5)  # Brief pause
        self.state = WakeWordState.COMMAND_MODE
        self._notify_state_change()
        
        logger.info("Entering command mode - listening for command...")
    
    def _process_command(self):
        """Process accumulated command audio"""
        try:
            self.state = WakeWordState.PROCESSING
            self._notify_state_change()
            
            # Transcribe command
            if len(self.accumulated_audio) > 0:
                result = self.audio_manager.stt_service.transcribe_numpy_array(
                    self.accumulated_audio,
                    self.audio_manager.sample_rate,
                    self.config.language
                )
                
                command_text = result.get("text", "").strip()
                confidence = result.get("confidence", 0.0)
                
                if command_text and confidence >= self.config.min_confidence:
                    logger.info(f"Command received: '{command_text}' (confidence: {confidence:.2f})")
                    
                    # Notify callback
                    if self.on_command_received:
                        try:
                            self.on_command_received(command_text)
                        except Exception as e:
                            logger.error(f"Error in command callback: {e}")
                else:
                    logger.info("No valid command detected")
            
            # Reset to listening mode
            self._reset_to_listening()
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            self._reset_to_listening()
    
    def _reset_to_listening(self):
        """Reset to listening state"""
        self.accumulated_audio = np.array([], dtype=np.float32)
        self.last_activity_time = time.time()
        self.state = WakeWordState.LISTENING
        self._notify_state_change()
        logger.info("Returned to listening mode")
    
    def speak_response(self, text: str):
        """Speak a response (temporarily stops listening)"""
        try:
            self.state = WakeWordState.SPEAKING
            self._notify_state_change()
            
            # Speak the response
            success = self.audio_manager.speak_response(text, blocking=True)
            
            # Brief pause after speaking
            time.sleep(0.5)
            
            # Return to listening
            self._reset_to_listening()
            
            return success
            
        except Exception as e:
            logger.error(f"Error speaking response: {e}")
            self._reset_to_listening()
            return False
    
    def _notify_state_change(self):
        """Notify state change callback"""
        if self.on_state_changed:
            try:
                self.on_state_changed(self.state)
            except Exception as e:
                logger.error(f"Error in state change callback: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "state": self.state.value,
            "is_running": self.is_running,
            "wake_phrases": self.config.wake_phrases,
            "sensitivity": self.config.sensitivity,
            "language": self.config.language,
            "buffer_size": len(self.accumulated_audio),
            "last_activity": time.time() - self.last_activity_time
        }
    
    def update_config(self, **kwargs):
        """Update configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Updated config: {key} = {value}")