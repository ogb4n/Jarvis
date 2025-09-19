import time
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class SessionState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    RESPONDING = "responding"

@dataclass
class ConversationMessage:
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: float = field(default_factory=time.time)
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversationSession:
    session_id: str
    satellite_id: str
    started_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    messages: List[ConversationMessage] = field(default_factory=list)
    state: SessionState = SessionState.IDLE
    context: Dict[str, Any] = field(default_factory=dict)

class ConversationManager:
    def __init__(
        self,
        wake_word_detector,
        audio_manager,
        llm_service=None,
        session_timeout: float = 300.0,  # 5 minutes
        max_messages_per_session: int = 50
    ):
        """
        Conversation Manager for handling voice interactions
        
        Args:
            wake_word_detector: WakeWordDetector instance
            audio_manager: AudioManager instance
            llm_service: LLM service for generating responses
            session_timeout: Session timeout in seconds
            max_messages_per_session: Maximum messages per session
        """
        self.wake_word_detector = wake_word_detector
        self.audio_manager = audio_manager
        self.llm_service = llm_service
        self.session_timeout = session_timeout
        self.max_messages_per_session = max_messages_per_session
        
        # Session management
        self.active_sessions: Dict[str, ConversationSession] = {}
        self.current_session: Optional[ConversationSession] = None
        
        # Callbacks
        self.on_session_started: Optional[Callable[[ConversationSession], None]] = None
        self.on_session_ended: Optional[Callable[[ConversationSession], None]] = None
        self.on_message_received: Optional[Callable[[ConversationMessage], None]] = None
        self.on_response_generated: Optional[Callable[[ConversationMessage], None]] = None
        
        # Setup wake word detector callbacks
        self.wake_word_detector.on_wake_detected = self._on_wake_detected
        self.wake_word_detector.on_command_received = self._on_command_received
        self.wake_word_detector.on_state_changed = self._on_detector_state_changed
        
        logger.info("ConversationManager initialized")
    
    def start(self):
        """Start the conversation manager"""
        try:
            self.wake_word_detector.start_listening()
            logger.info("ConversationManager started")
        except Exception as e:
            logger.error(f"Error starting ConversationManager: {e}")
            raise
    
    def stop(self):
        """Stop the conversation manager"""
        try:
            self.wake_word_detector.stop_listening()
            self._cleanup_expired_sessions()
            logger.info("ConversationManager stopped")
        except Exception as e:
            logger.error(f"Error stopping ConversationManager: {e}")
    
    def _on_wake_detected(self):
        """Handle wake word detection"""
        try:
            # Start new session or reactivate existing one
            session = self._get_or_create_session("default")  # TODO: Get actual satellite_id
            session.state = SessionState.LISTENING
            session.last_activity = time.time()
            
            logger.info(f"Wake word detected, session {session.session_id} activated")
            
            # Optional: Play wake sound or give feedback
            # self.audio_manager.speak_response("Je vous écoute", blocking=False)
            
        except Exception as e:
            logger.error(f"Error handling wake detection: {e}")
    
    def _on_command_received(self, command_text: str):
        """Handle received voice command"""
        try:
            if not self.current_session:
                logger.warning("Received command but no active session")
                return
            
            session = self.current_session
            session.state = SessionState.PROCESSING
            session.last_activity = time.time()
            
            # Create user message
            user_message = ConversationMessage(
                role="user",
                content=command_text
            )
            session.messages.append(user_message)
            
            logger.info(f"Command received in session {session.session_id}: '{command_text}'")
            
            # Notify callback
            if self.on_message_received:
                self.on_message_received(user_message)
            
            # Process the command
            self._process_command(session, command_text)
            
        except Exception as e:
            logger.error(f"Error handling command: {e}")
            if self.current_session:
                self.current_session.state = SessionState.IDLE
    
    def _process_command(self, session: ConversationSession, command_text: str):
        """Process a voice command"""
        try:
            session.state = SessionState.PROCESSING
            
            # Check for built-in commands first
            response = self._handle_builtin_commands(command_text)
            
            if not response and self.llm_service:
                # Use LLM for response generation
                try:
                    # Build context from conversation history
                    context = self._build_llm_context(session)
                    response = self.llm_service.generate_response(command_text, context)
                except Exception as e:
                    logger.error(f"Error getting LLM response: {e}")
                    response = "Désolé, j'ai eu un problème pour traiter votre demande."
            
            if not response:
                # Default response
                response = self._get_default_response(command_text)
            
            # Create assistant message
            assistant_message = ConversationMessage(
                role="assistant",
                content=response
            )
            session.messages.append(assistant_message)
            
            # Notify callback
            if self.on_response_generated:
                self.on_response_generated(assistant_message)
            
            # Speak response
            session.state = SessionState.RESPONDING
            success = self.wake_word_detector.speak_response(response)
            
            if success:
                logger.info(f"Response spoken: '{response}'")
            else:
                logger.error("Failed to speak response")
            
            # Return to idle state
            session.state = SessionState.IDLE
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            session.state = SessionState.IDLE
    
    def _handle_builtin_commands(self, command_text: str) -> Optional[str]:
        """Handle built-in commands"""
        command_lower = command_text.lower().strip()
        
        # Greeting commands
        if any(word in command_lower for word in ["bonjour", "salut", "hello", "bonsoir"]):
            return "Bonjour ! Comment puis-je vous aider ?"
        
        # Status commands
        if any(word in command_lower for word in ["statut", "status", "comment vas-tu", "ça va"]):
            return "Je vais bien, merci ! Tous mes systèmes fonctionnent correctement."
        
        # Time commands
        if any(word in command_lower for word in ["heure", "temps", "quelle heure"]):
            current_time = time.strftime("%H:%M", time.localtime())
            return f"Il est {current_time}."
        
        # Goodbye commands
        if any(word in command_lower for word in ["au revoir", "bye", "à bientôt", "stop"]):
            return "Au revoir ! N'hésitez pas à me rappeler si vous avez besoin d'aide."
        
        # Help commands
        if any(word in command_lower for word in ["aide", "help", "que peux-tu faire"]):
            return "Je peux vous aider avec diverses tâches. Posez-moi des questions ou donnez-moi des instructions !"
        
        return None
    
    def _get_default_response(self, command_text: str) -> str:
        """Get default response when no specific handler is found"""
        responses = [
            "Je ne suis pas sûr de comprendre. Pouvez-vous reformuler ?",
            "Désolé, je n'ai pas bien saisi votre demande.",
            "Pouvez-vous répéter ou être plus précis ?",
            "Je n'ai pas compris. Pouvez-vous m'expliquer différemment ?"
        ]
        import random
        return random.choice(responses)
    
    def _build_llm_context(self, session: ConversationSession) -> List[Dict[str, str]]:
        """Build context for LLM from conversation history"""
        context = []
        
        # Add system message
        context.append({
            "role": "system",
            "content": "Tu es Jarvis, un assistant vocal intelligent et serviable. Réponds de manière concise et naturelle en français."
        })
        
        # Add recent conversation history (last 10 messages)
        recent_messages = session.messages[-10:] if len(session.messages) > 10 else session.messages
        
        for message in recent_messages:
            context.append({
                "role": message.role,
                "content": message.content
            })
        
        return context
    
    def _get_or_create_session(self, satellite_id: str) -> ConversationSession:
        """Get existing session or create new one"""
        # Clean up expired sessions first
        self._cleanup_expired_sessions()
        
        # Look for existing active session for this satellite
        for session in self.active_sessions.values():
            if (session.satellite_id == satellite_id and 
                time.time() - session.last_activity < self.session_timeout):
                self.current_session = session
                return session
        
        # Create new session
        session_id = str(uuid.uuid4())
        session = ConversationSession(
            session_id=session_id,
            satellite_id=satellite_id
        )
        
        self.active_sessions[session_id] = session
        self.current_session = session
        
        logger.info(f"Created new session {session_id} for satellite {satellite_id}")
        
        # Notify callback
        if self.on_session_started:
            self.on_session_started(session)
        
        return session
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if current_time - session.last_activity > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            session = self.active_sessions.pop(session_id)
            logger.info(f"Session {session_id} expired")
            
            # Notify callback
            if self.on_session_ended:
                self.on_session_ended(session)
            
            # Clear current session if it was the expired one
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = None
    
    def _on_detector_state_changed(self, state):
        """Handle wake word detector state changes"""
        if self.current_session:
            # Map detector states to session states
            if state.value == "listening":
                self.current_session.state = SessionState.LISTENING
            elif state.value == "processing":
                self.current_session.state = SessionState.PROCESSING
            elif state.value == "speaking":
                self.current_session.state = SessionState.RESPONDING
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "active_sessions": len(self.active_sessions),
            "current_session": self.current_session.session_id if self.current_session else None,
            "detector_status": self.wake_word_detector.get_status(),
            "session_timeout": self.session_timeout
        }
    
    def get_session_history(self, session_id: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """Get conversation history for a session"""
        session = None
        
        if session_id:
            session = self.active_sessions.get(session_id)
        elif self.current_session:
            session = self.current_session
        
        if not session:
            return None
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "confidence": msg.confidence
            }
            for msg in session.messages
        ]