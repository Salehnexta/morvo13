from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ai.master_agent import MasterAgent

router = APIRouter()


class MasterAgentRequest(BaseModel):
    user_input: str
    website_url: str


@router.post("/process_request")
async def process_master_agent_request(request: MasterAgentRequest) -> dict[str, Any]:
    try:
        master_agent = MasterAgent()
        response = await master_agent.process_request(request.user_input, request.website_url)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
