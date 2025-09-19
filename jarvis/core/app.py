from fastapi import FastAPI
from jarvis.core.config import settings
from jarvis.api.audio_routes import router as audio_router
from jarvis.api.conversation_routes import router as conversation_router

app = FastAPI(title="Jarvis", version="0.1.0", description="Assistant vocal auto-hébergé")

# Include routers
app.include_router(audio_router)
app.include_router(conversation_router)

@app.get("/")
def root():
    return {"message": "Jarvis is running", "version": "0.1.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "services": ["audio", "database"]}

@app.on_event("startup")
async def startup_event():
    print("🤖 Jarvis is starting up...")

@app.on_event("shutdown") 
async def shutdown_event():
    print("🤖 Jarvis is shutting down...")
