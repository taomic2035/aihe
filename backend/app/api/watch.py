from fastapi import APIRouter, Query
from pydantic import BaseModel
from backend.app.api.chat import memory_service
from backend.app.realtime.manager import manager

router = APIRouter()


@router.get("/v1/watch/sync")
def watch_sync(user_id: str = Query(...), since_version: int = 0):
    # naive version: count memories as version
    mems = []
    store = memory_service.store
    if hasattr(store, "store"):
        mems = [m for m in store.store.get(user_id, []) if not m["deleted"]]
    version = len(mems)
    # delta
    delta = mems[since_version:] if since_version < len(mems) else []
    return {
        "version": version,
        "memories": [{"id": m["id"], "content": m["content"]} for m in delta],
        "messages": delta,  # compat
    }


class PushRequest(BaseModel):
    user_id: str
    title: str
    body: str


@router.post("/v1/watch/push")
async def watch_push(req: PushRequest):
    # push via realtime
    await manager.broadcast(req.user_id, f"push:{req.title}:{req.body}")
    return {"ok": True, "pushed": req.user_id}


class IngestRequest(BaseModel):
    user_id: str
    heart_rate: float | None = None
    sleep: float | None = None


@router.post("/v1/watch/ingest")
def watch_ingest(req: IngestRequest):
    from backend.app.observability.langfuse import log_trace

    log_trace("watch.ingest", {"user_id": req.user_id, "heart_rate": req.heart_rate, "sleep": req.sleep})
    return {"ok": True}


@router.get("/v1/watch/health")
def watch_health():
    return {"status": "ok", "watch": "thin client"}
