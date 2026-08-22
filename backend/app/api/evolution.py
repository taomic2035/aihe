from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.evolution.gepa import run_gepa, list_prs

router = APIRouter()


class RunReq(BaseModel):
    user_id: str


@router.post("/v1/evolution/run")
def run(req: RunReq):
    pr = run_gepa(req.user_id)
    return pr


@router.get("/v1/evolution/prs")
def list_api():
    return {"prs": list_prs()}
