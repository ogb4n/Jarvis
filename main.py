from jarvis.core.app import app
from jarvis.core.config import settings
import uvicorn

if __name__ == "__main__":
    uvicorn.run("jarvis.core.app:app", host=settings.api_host, port=settings.api_port, reload=True)
