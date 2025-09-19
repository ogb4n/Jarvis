from fastapi import FastAPI
from jarvis.core.config import settings

app = FastAPI(title="Jarvis", version="0.1.0")

@app.get("/")
def root():
    return {"message": "Jarvis is running"}
