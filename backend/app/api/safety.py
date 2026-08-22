from fastapi import APIRouter, Query
from backend.app.safety.filter import check

router = APIRouter()


@router.get("/v1/safety/check")
def safety_check(text: str = Query(...)):
    res = check(text)
    return res
