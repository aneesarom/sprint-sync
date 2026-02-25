import json
import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth.jwt_handler import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_user
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_core.rate_limiters import InMemoryRateLimiter
from app.services.ai_services import  description_generator_agent

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.5,
    max_bucket_size=5,
)

load_dotenv()

USE_LLM_STUB = json.loads(os.getenv("USE_LLM_STUB", "false").lower())

router = APIRouter(prefix="/ai", tags=["suggest"])

class SuggestRequest(BaseModel):
    title: str

class TaskDescription(BaseModel):
    description: list[str] = Field(..., description="List of suggested task descriptions", min_length=3, max_length=5)


@router.post("/suggest")
async def suggest_description(task: SuggestRequest, current_user: dict = Depends(get_current_user)):
    try:
        if USE_LLM_STUB:
            return {"task_description": ["This is a stubbed task description one for testing purposes.", 
                                         "This is a stubbed task description two for testing purposes.", 
                                         "This is a stubbed task description three for testing purposes."]}
        
        if not current_user["is_admin"]:
            raise HTTPException(status_code=403, detail="Admin privileges required to generate task description")
        
        

        message = HumanMessage(content=f"Task title: {task.title}")
        response = await description_generator_agent.ainvoke({"messages": message})
        return {"task_description": json.loads(response["messages"][-1].content)["description"]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))