import json
import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.supabase_client import supabase
from app.auth.dependencies import get_current_user
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_core.rate_limiters import InMemoryRateLimiter
from app.services.ai_services import description_generator_agent, query_generator_agent
from app.services.retrieval import multi_query_hybrid_search
from app.logging_config import get_logger

logger = get_logger(__name__)

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.5,
    max_bucket_size=5,
)

load_dotenv()

router = APIRouter(prefix="/ai", tags=["suggest"])

class SuggestRequest(BaseModel):
    title: str

class SuggestProfileRequest(BaseModel):
    title: str
    description: str


@router.post("/suggest")
async def suggest_description(task: SuggestRequest, current_user: dict = Depends(get_current_user)):
    try:
        if json.loads(os.getenv("USE_LLM_STUB", "false").lower()):
            logger.info("Using LLM stub for suggest_description")
            return ["This is a stubbed task description one for testing purposes.", 
                                         "This is a stubbed task description two for testing purposes.", 
                                         "This is a stubbed task description three for testing purposes."]
        
        if not current_user["is_admin"]:
            logger.error(reason="User doesn't have Admin privilege")
            raise HTTPException(status_code=403, detail="Admin privileges required to generate task description")
        
        

        message = HumanMessage(content=f"Task title: {task.title}")
        response = await description_generator_agent.ainvoke({"messages": message})
        return json.loads(response["messages"][-1].content)["description"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/suggest_profile")
async def suggest_profile(task: SuggestProfileRequest, current_user: dict = Depends(get_current_user)):
    # Fetch user's resume snippets from Supabase
    
    try:
        if json.loads(os.getenv("USE_LLM_STUB", "false").lower()):
            logger.info("Using LLM stub for suggest_profile")
            return [
                {"id": "18bfb1c2-5c9a-328a-9b3a-8f1e769df1e6",
                "username": "user1"},
                {"id": "434356d4-9c3a-4c8e-9b3a-8f1e769df1e6",
                "username": "user2"}
                ]
        if not current_user["is_admin"]:
            logger.error(reason="User doesn't have Admin privilege")
            raise HTTPException(status_code=403, detail="Admin privileges required to generate task description")
        
        messages = [
            HumanMessage(content=f"Generate search query variations for the following: \ntask title: {task.title}\nAnd task description: {task.description}"),
        ]
        query_generator_response = await query_generator_agent.ainvoke({"messages": messages})
        query_generator_response = json.loads(query_generator_response["messages"][-1].content)

        # Do hybrid search for the given task
        finalized_profiles = multi_query_hybrid_search(keyword_search_queries=query_generator_response["keyword_search_queries"],
                                                       vector_search_queries=query_generator_response["task_search_queries"],
                                                       num_profiles=3)
        finalized_user_ids = [profile['user_id'] for profile in finalized_profiles]

        supabase_response = supabase.rpc(
            "get_users_by_ids_ordered",
            {"input_ids": finalized_user_ids}
        ).execute()

        if not supabase_response.data:
            logger.warning(reason="No profile matches found")

        return supabase_response.data or []
    except HTTPException:
        raise
    except Exception as e:
        logger.error(error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))