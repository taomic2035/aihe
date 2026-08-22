from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.scheduler.service import create_job, list_jobs, patch_job, trigger_job

router = APIRouter()


class JobCreate(BaseModel):
    user_id: str
    cron: str
    trigger: str


@router.post("/v1/scheduler/jobs")
def create(req: JobCreate):
    job = create_job(req.user_id, req.cron, req.trigger)
    return job


@router.get("/v1/scheduler/jobs")
def list_api(user_id: str):
    return {"jobs": list_jobs(user_id)}


class PatchReq(BaseModel):
    enabled: bool | None = None


@router.patch("/v1/scheduler/jobs/{jid}")
def patch(jid: str, req: PatchReq):
    job = patch_job(jid, req.enabled)
    if not job:
        raise HTTPException(404, "not found")
    return job


@router.post("/v1/scheduler/jobs/{jid}/trigger")
def trigger(jid: str):
    res = trigger_job(jid)
    if not res:
        raise HTTPException(404, "not found")
    return res
