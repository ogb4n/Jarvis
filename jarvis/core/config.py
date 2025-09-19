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
