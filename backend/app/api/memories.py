from fastapi import APIRouter, Query, HTTPException
from backend.app.api.chat import memory_service

router = APIRouter()


@router.get("/v1/memories")
def list_memories(user_id: str = Query(..., description="user_id required"), q: str | None = None, limit: int = 20):
    # recall with query or list all
    if q:
        hits = memory_service.recall(user_id=user_id, query=q, limit=limit)
    else:
        # list all non-deleted
        store = memory_service.store
        # InMemoryStore specific
        if hasattr(store, "store"):
            mems = [m for m in store.store.get(user_id, []) if not m["deleted"]]
            hits = []
            from backend.app.memory.service import MemoryHit

            for m in mems[:limit]:
                hits.append(MemoryHit(id=m["id"], content=m["content"], importance=m["importance"]))
        else:
            hits = memory_service.recall(user_id=user_id, query="", limit=limit)
    return {"memories": [{"id": h.id, "content": h.content, "importance": h.importance} for h in hits]}


@router.delete("/v1/memories/{memory_id}")
def delete_memory(memory_id: str, user_id: str = Query(...)):
    # verify exists
    store = memory_service.store
    found = False
    if hasattr(store, "store"):
        for m in store.store.get(user_id, []):
            if m["id"] == memory_id and not m["deleted"]:
                found = True
                break
    if not found:
        # also try via recall
        hits = memory_service.recall(user_id=user_id, query="", limit=100)
        for h in hits:
            if h.id == memory_id:
                found = True
                break
    if not found:
        raise HTTPException(status_code=404, detail="memory not found")
    memory_service.delete(user_id=user_id, memory_id=memory_id)
    return {"deleted": memory_id}


@router.get("/v1/memories/ping")
def ping():
    return {"ok": True}
