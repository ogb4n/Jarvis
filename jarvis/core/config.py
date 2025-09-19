from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    mongodb_url: str
    database_name: str 
    api_host: str 
    api_port: int 
    audio_storage_path: str = "./audio_files"
    openai_api_key: Optional[str] = None
    
    # Audio device configuration
    audio_input_device: Optional[int] = None  # None = default device
    audio_output_device: Optional[int] = None  # None = default device
    audio_sample_rate: int = 16000
    audio_channels: int = 1

    class Config:
        env_file = ".env"

settings = Settings()

class OpenAPISettings():
    title: str = "Jarvis Voice Assistant API"
    version: str = "0.1.0"
    description: str = (
        """
    ## 🛰️ Jarvis Satellite-Based Voice Assistant API
    
    A distributed voice assistant system with centralized intelligence and satellite-based audio processing.
    
    ### 🏗️ Architecture
    **Server-Satellite Distributed System:**
    - 🖥️ **Central Server** (this API): Command processing, AI logic, database
    - 🛰️ **Satellites**: Audio capture, speech-to-text, text-to-speech
    - � **Communication**: REST API / WebSocket
    
    ### 🔧 Core Features
    - 💬 **Command Processing**: Natural language understanding
    - �️ **Session Management**: Multi-satellite conversation tracking  
    - 📊 **Satellite Monitoring**: Real-time status and health
    - 🔍 **Command History**: Full audit trail and analytics
    - 🎯 **Extensible Logic**: Easy to add new commands and integrations
    
    ### 🚀 Getting Started
    1. **Check system health**: `GET /health`
    2. **View active satellites**: `GET /api/audio/satellites`
    3. **Process a command**: `POST /api/audio/process-command`
    4. **Start conversation mode**: `POST /api/conversation/start`
    
    ### 🛰️ Satellite Integration
    **Your satellites should:**
    1. Capture audio locally
    2. Convert speech-to-text (using Whisper, etc.)
    3. Send text commands to `/api/audio/process-command`
    4. Receive response and convert to speech
    5. Play audio response to user
    
    ### 📖 Example Satellite Flow
    ```
    User: "Hey Jarvis, quelle heure est-il ?"
    Satellite: [Audio capture] → [STT] → "quelle heure est-il"
    API: Process command → {"type": "time", "text": "Il est 14:30"}
    Satellite: [TTS] → [Audio playback] → "Il est 14:30"
    ```
    """
    )
    contact_name: str = "Jarvis Assistant"
    contact_url: str = "https://github.com/ogb4n/Jarvis"
    license_name: str = "MIT License"
    license_url: str = "https://opensource.org/licenses/MIT"
    openapi_tags: list = [
        {
            "name": "system",
            "description": "🔧 System health, status, and core information endpoints",
        },
        {
            "name": "satellite-audio", 
            "description": "🛰️ Satellite-based audio processing and command handling",
        },
        {
            "name": "conversation",
            "description": "💬 Conversation management and session tracking (satellite coordination)",
        },
    ]