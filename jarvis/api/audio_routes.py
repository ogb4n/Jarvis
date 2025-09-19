from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, FileResponse
from typing import Optional, Dict, Any
import io
import tempfile
import os
import time
from jarvis.services.audio_manager import AudioManager
from jarvis.services.command_service import CommandService
from jarvis.core.database import DatabaseService
from jarvis.models.command import Command, CommandType
from jarvis.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Services globaux (seront initialisés lors du premier appel)
db_service = None
command_service = None
audio_manager = None

def get_services():
    """Initialize services on first call"""
    global db_service, command_service, audio_manager
    
    if db_service is None:
        try:
            db_service = DatabaseService(settings.mongodb_url, settings.database_name)
            command_service = CommandService(db_service)
            logger.info("Database services initialized")
        except Exception as e:
            logger.warning(f"Database services not available: {e}")
    
    if audio_manager is None:
        try:
            audio_manager = AudioManager(
                input_device=settings.audio_input_device,
                output_device=settings.audio_output_device,
                sample_rate=settings.audio_sample_rate,
                channels=settings.audio_channels
            )
            logger.info("Audio manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize audio manager: {e}")
            raise HTTPException(status_code=500, detail="Audio services not available")
    
    return db_service, command_service, audio_manager

router = APIRouter(prefix="/api/audio", tags=["audio"])

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("fr"),
    satellite_id: str = Form("default")
):
    """
    Transcribe uploaded audio file
    """
    try:
        # Initialize services
        db_service, command_service, audio_manager = get_services()
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Set language for transcription
            audio_manager.set_language(language)
            
            # Transcribe audio
            result = audio_manager.transcribe_file(temp_path)
            
            if result.get("text") and command_service:
                # Save command to database
                command = Command(
                    satellite_id=satellite_id,
                    session_id=f"upload_{satellite_id}_{int(time.time())}",
                    transcription=result["text"],
                    command_type=CommandType.UNKNOWN
                )
                command_id = command_service.create_command(command)
                
                result["command_id"] = command_id
            
            return {
                "success": True,
                "transcription": result,
                "file_info": {
                    "filename": file.filename,
                    "size": len(content),
                    "content_type": file.content_type
                }
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/synthesize")
async def synthesize_speech(
    text: str = Form(...),
    output_format: str = Form("wav"),
    voice_rate: Optional[int] = Form(200),
    voice_volume: Optional[float] = Form(0.9)
):
    """
    Synthesize text to speech
    """
    try:
        # Initialize services
        _, _, audio_manager = get_services()
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Set TTS parameters
        if voice_rate:
            audio_manager.tts_service.set_rate(voice_rate)
        if voice_volume:
            audio_manager.tts_service.set_volume(voice_volume)
        
        # Generate audio bytes
        audio_bytes = audio_manager.tts_service.synthesize_to_bytes(text)
        
        if not audio_bytes:
            raise HTTPException(status_code=500, detail="Failed to synthesize speech")
        
        # Return audio file
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename=speech.{output_format}"}
        )
        
    except Exception as e:
        logger.error(f"Error synthesizing speech: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/record")
async def record_command(
    duration: float = Form(5.0),
    language: str = Form("fr"),
    satellite_id: str = Form("default")
):
    """
    Record a voice command for specified duration
    """
    try:
        if duration <= 0 or duration > 30:
            raise HTTPException(status_code=400, detail="Duration must be between 0 and 30 seconds")
        
        # Set language
        audio_manager.set_language(language)
        
        # Record command
        result = audio_manager.record_single_command(duration)
        
        if result.get("text"):
            # Save command to database
            command = Command(
                satellite_id=satellite_id,
                session_id=f"record_{satellite_id}_{int(time.time())}",
                transcription=result["text"],
                command_type=CommandType.UNKNOWN
            )
            command_id = command_service.create_command(command)
            
            result["command_id"] = command_id
        
        return {
            "success": True,
            "recording_duration": duration,
            "transcription": result
        }
        
    except Exception as e:
        logger.error(f"Error recording command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/speak")
async def speak_text(
    text: str = Form(...),
    blocking: bool = Form(True),
    voice_rate: Optional[int] = Form(None),
    voice_volume: Optional[float] = Form(None)
):
    """
    Speak text through the server's speakers
    """
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Set TTS parameters if provided
        if voice_rate:
            audio_manager.tts_service.set_rate(voice_rate)
        if voice_volume:
            audio_manager.tts_service.set_volume(voice_volume)
        
        # Speak text
        success = audio_manager.speak_response(text, blocking)
        
        return {
            "success": success,
            "text": text,
            "blocking": blocking,
            "message": "Text spoken successfully" if success else "Failed to speak text"
        }
        
    except Exception as e:
        logger.error(f"Error speaking text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devices")
async def get_audio_devices():
    """
    Get available audio devices
    """
    try:
        devices = audio_manager.get_audio_devices()
        return devices
    except Exception as e:
        logger.error(f"Error getting audio devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voices")
async def get_available_voices():
    """
    Get available TTS voices
    """
    try:
        voices = audio_manager.tts_service.get_available_voices()
        return {
            "voices": voices,
            "count": len(voices)
        }
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice/set")
async def set_voice(voice_id: str = Form(...)):
    """
    Set the TTS voice
    """
    try:
        success = audio_manager.tts_service.set_voice(voice_id)
        return {
            "success": success,
            "voice_id": voice_id,
            "message": "Voice set successfully" if success else "Failed to set voice"
        }
    except Exception as e:
        logger.error(f"Error setting voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_audio_status():
    """
    Get current audio system status
    """
    try:
        # Initialize services
        _, _, audio_manager = get_services()
        
        status = audio_manager.get_status()
        stt_info = audio_manager.stt_service.get_model_info()
        tts_info = audio_manager.tts_service.get_engine_info()
        
        return {
            "audio_manager": status,
            "stt_service": stt_info,
            "tts_service": tts_info
        }
    except Exception as e:
        logger.error(f"Error getting audio status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test_audio_services():
    """
    Test basic audio services functionality
    """
    try:
        # Initialize services
        _, _, audio_manager = get_services()
        
        # Test TTS
        test_text = "Bonjour, je suis Jarvis et mes services audio fonctionnent correctement."
        tts_success = audio_manager.speak_response(test_text, blocking=False)
        
        return {
            "success": True,
            "tts_test": tts_success,
            "test_text": test_text,
            "message": "Audio services are working correctly"
        }
    except Exception as e:
        logger.error(f"Error testing audio services: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Audio services are not working properly"
        }

@router.get("/models")
async def get_whisper_models():
    """
    Get information about available Whisper models
    """
    return {
        "available_models": [
            {"name": "tiny", "size": "39 MB", "description": "Fastest, least accurate"},
            {"name": "base", "size": "74 MB", "description": "Good balance of speed/accuracy"},
            {"name": "small", "size": "244 MB", "description": "Better accuracy, slower"},
            {"name": "medium", "size": "769 MB", "description": "Good accuracy, requires more resources"},
            {"name": "large", "size": "1550 MB", "description": "Best accuracy, slowest"}
        ],
        "current_model": audio_manager.stt_service.model_size,
        "supported_languages": audio_manager.stt_service.get_model_info()["supported_languages"]
    }

@router.get("/devices")
async def get_audio_devices():
    """
    Get available audio input/output devices
    """
    try:
        _, _, audio_manager = get_services()
        devices_info = audio_manager.get_audio_devices()
        
        return {
            "success": True,
            "current_input_device": audio_manager.input_device,
            "current_output_device": audio_manager.output_device,
            **devices_info
        }
    except Exception as e:
        logger.error(f"Error getting audio devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))