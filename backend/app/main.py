from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="aihe backend", version="0.1.0")


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
