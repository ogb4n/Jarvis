from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "jarvis"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    audio_storage_path: str = "./audio_files"
    openai_api_key: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()
