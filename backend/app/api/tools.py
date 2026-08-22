from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.tools.registry import registry

router = APIRouter()


class ToolCallRequest(BaseModel):
    tool: str
    args: dict


@router.post("/v1/tools/call")
def call_tool(req: ToolCallRequest):
    result = registry.call(req.tool, req.args)
    return result


@router.get("/v1/tools/list")
def list_tools():
    return {"tools": registry.list_tools()}
