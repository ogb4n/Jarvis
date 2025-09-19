from fastapi import APIRouter, HTTPException, Form
from typing import Optional, List, Dict, Any
import logging
from jarvis.services.wake_word_detector import WakeWordDetector, WakeWordConfig
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.audio_manager import AudioManager

logger = logging.getLogger(__name__)

# Global services
conversation_manager = None
wake_word_detector = None

def get_conversation_services():
    """Initialize conversation services on first call"""
    global conversation_manager, wake_word_detector
    
    if wake_word_detector is None:
        try:
            # Get audio manager from audio routes
            from jarvis.api.audio_routes import get_services
            _, _, audio_manager = get_services()
            
            # Initialize wake word detector
            config = WakeWordConfig(
                wake_phrases=["hey jarvis", "jarvis", "salut jarvis", "bonjour jarvis"],
                sensitivity=0.7,
                timeout_seconds=5.0,
                min_confidence=0.6,
                language="fr"
            )
            
            wake_word_detector = WakeWordDetector(
                audio_manager=audio_manager,
                config=config
            )
            
            # Initialize conversation manager
            conversation_manager = ConversationManager(
                wake_word_detector=wake_word_detector,
                audio_manager=audio_manager
            )
            
            logger.info("Conversation services initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize conversation services: {e}")
            raise HTTPException(status_code=500, detail="Conversation services not available")
    
    return conversation_manager, wake_word_detector

router = APIRouter(prefix="/api/conversation", tags=["conversation"])

@router.post("/start")
async def start_conversation_mode():
    """
    Start continuous listening mode with wake word detection
    """
    try:
        conversation_manager, wake_word_detector = get_conversation_services()
        
        if wake_word_detector.is_running:
            return {
                "success": True,
                "message": "Conversation mode already active",
                "status": wake_word_detector.get_status()
            }
        
        # Start conversation manager
        conversation_manager.start()
        
        return {
            "success": True,
            "message": "Conversation mode started - listening for wake words",
            "wake_phrases": wake_word_detector.config.wake_phrases,
            "status": wake_word_detector.get_status()
        }
        
    except Exception as e:
        logger.error(f"Error starting conversation mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_conversation_mode():
    """
    Stop continuous listening mode
    """
    try:
        conversation_manager, wake_word_detector = get_conversation_services()
        
        if not wake_word_detector.is_running:
            return {
                "success": True,
                "message": "Conversation mode already stopped"
            }
        
        # Stop conversation manager
        conversation_manager.stop()
        
        return {
            "success": True,
            "message": "Conversation mode stopped"
        }
        
    except Exception as e:
        logger.error(f"Error stopping conversation mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_conversation_status():
    """
    Get current conversation system status
    """
    try:
        conversation_manager, wake_word_detector = get_conversation_services()
        
        return {
            "conversation_manager": conversation_manager.get_status(),
            "wake_word_detector": wake_word_detector.get_status()
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_conversation_history(session_id: Optional[str] = None):
    """
    Get conversation history for current or specified session
    """
    try:
        conversation_manager, _ = get_conversation_services()
        
        history = conversation_manager.get_session_history(session_id)
        
        if history is None:
            return {
                "success": False,
                "message": "No active session found",
                "history": []
            }
        
        return {
            "success": True,
            "session_id": session_id or (conversation_manager.current_session.session_id if conversation_manager.current_session else None),
            "history": history,
            "message_count": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config/wake-words")
async def update_wake_words(wake_phrases: List[str] = Form(...)):
    """
    Update wake word phrases
    """
    try:
        conversation_manager, wake_word_detector = get_conversation_services()
        
        # Update configuration
        wake_word_detector.update_config(wake_phrases=wake_phrases)
        
        return {
            "success": True,
            "message": "Wake words updated successfully",
            "wake_phrases": wake_phrases
        }
        
    except Exception as e:
        logger.error(f"Error updating wake words: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config/sensitivity")
async def update_sensitivity(
    sensitivity: float = Form(...),
    min_confidence: Optional[float] = Form(None),
    timeout_seconds: Optional[float] = Form(None)
):
    """
    Update wake word detection sensitivity and parameters
    """
    try:
        conversation_manager, wake_word_detector = get_conversation_services()
        
        # Validate parameters
        if not 0.0 <= sensitivity <= 1.0:
            raise HTTPException(status_code=400, detail="Sensitivity must be between 0.0 and 1.0")
        
        # Update configuration
        config_updates = {"sensitivity": sensitivity}
        
        if min_confidence is not None:
            if not 0.0 <= min_confidence <= 1.0:
                raise HTTPException(status_code=400, detail="Min confidence must be between 0.0 and 1.0")
            config_updates["min_confidence"] = min_confidence
        
        if timeout_seconds is not None:
            if not 1.0 <= timeout_seconds <= 30.0:
                raise HTTPException(status_code=400, detail="Timeout must be between 1.0 and 30.0 seconds")
            config_updates["timeout_seconds"] = timeout_seconds
        
        wake_word_detector.update_config(**config_updates)
        
        return {
            "success": True,
            "message": "Configuration updated successfully",
            "config": {
                "sensitivity": wake_word_detector.config.sensitivity,
                "min_confidence": wake_word_detector.config.min_confidence,
                "timeout_seconds": wake_word_detector.config.timeout_seconds
            }
        }
        
    except Exception as e:
        logger.error(f"Error updating sensitivity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate-wake")
async def simulate_wake_word():
    """
    Simulate wake word detection for testing
    """
    try:
        conversation_manager, wake_word_detector = get_conversation_services()
        
        if not wake_word_detector.is_running:
            raise HTTPException(status_code=400, detail="Conversation mode is not active")
        
        # Simulate wake word detection
        wake_word_detector._handle_wake_detected("simulated wake word")
        
        return {
            "success": True,
            "message": "Wake word simulated successfully",
            "status": wake_word_detector.get_status()
        }
        
    except Exception as e:
        logger.error(f"Error simulating wake word: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-command")
async def send_text_command(command: str = Form(...)):
    """
    Send a text command directly (for testing without voice)
    """
    try:
        conversation_manager, wake_word_detector = get_conversation_services()
        
        if not wake_word_detector.is_running:
            raise HTTPException(status_code=400, detail="Conversation mode is not active")
        
        # Process command directly
        conversation_manager._on_command_received(command)
        
        return {
            "success": True,
            "message": "Command processed successfully",
            "command": command
        }
        
    except Exception as e:
        logger.error(f"Error processing text command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-responses")
async def test_builtin_responses():
    """
    Test built-in response system
    """
    try:
        conversation_manager, wake_word_detector = get_conversation_services()
        
        test_commands = [
            "bonjour",
            "comment vas-tu",
            "quelle heure est-il",
            "aide"
        ]
        
        responses = {}
        
        for command in test_commands:
            response = conversation_manager._handle_builtin_commands(command)
            responses[command] = response or "No built-in response"
        
        return {
            "success": True,
            "test_responses": responses
        }
        
    except Exception as e:
        logger.error(f"Error testing responses: {e}")
        raise HTTPException(status_code=500, detail=str(e))