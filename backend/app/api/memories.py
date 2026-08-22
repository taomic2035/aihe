from fastapi import APIRouter

router = APIRouter()

# placeholder, real implementation in Task 7
@router.get("/v1/memories/ping")
def ping():
    return {"ok": True}
