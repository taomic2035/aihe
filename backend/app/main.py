from fastapi import FastAPI
from fastapi.responses import JSONResponse
from backend.app.api.chat import router as chat_router
from backend.app.api.memories import router as memories_router
from backend.app.api.realtime import router as realtime_router
from backend.app.api.voice import router as voice_router

app = FastAPI(title="aihe backend", version="0.1.0")
app.include_router(chat_router)
app.include_router(memories_router)
app.include_router(realtime_router)
app.include_router(voice_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "services": {
            "postgres": "ok",
            "redis": "ok",
            "qdrant": "ok",
            "letta": "ok",
        },
    }


@app.get("/")
def root():
    return {"name": "aihe", "version": "0.1.0"}
