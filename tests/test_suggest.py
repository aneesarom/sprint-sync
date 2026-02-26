import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from app.routes.suggest import SuggestRequest
from app.routes.suggest import suggest_profile, SuggestProfileRequest, suggest_description
from fastapi.testclient import TestClient
from app.auth.dependencies import get_current_user # Adjust imports
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_suggest_description_ai_success():    
    mock_task = SuggestRequest(title="Develop API")
    mock_admin = {"is_admin": True}
    
    mock_ai_content = '{"description": ["Task 1", "Task 2"]}'
    mock_response = {"messages": [AsyncMock(content=mock_ai_content)]}
    
    with patch("app.routes.suggest.description_generator_agent.ainvoke", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = mock_response
        
        with patch.dict("os.environ", {"USE_LLM_STUB": "false"}):
            result = await suggest_description(task=mock_task, current_user=mock_admin)
            
            assert result == ["Task 1", "Task 2"]
            mock_invoke.assert_called_once()

@pytest.mark.asyncio
async def test_suggest_profile_success():
    
    mock_task = SuggestProfileRequest(title="Dev", description="Code")
    mock_admin = {"is_admin": True}
    
    mock_query_content = '{"keyword_search_queries": ["a"], "task_search_queries": ["b"]}'
    mock_ai_response = {"messages": [AsyncMock(content=mock_query_content)]}
    
    with patch("app.routes.suggest.query_generator_agent.ainvoke", new_callable=AsyncMock) as mock_ai, \
         patch("app.routes.suggest.multi_query_hybrid_search") as mock_search, \
         patch("app.routes.suggest.supabase") as mock_sb:
        
        mock_ai.return_value = mock_ai_response
        mock_search.return_value = [{"user_id": "123"}]
        mock_sb.rpc().execute.return_value.data = [{"username": "test_user"}]
        
        with patch.dict("os.environ", {"USE_LLM_STUB": "false"}):
            result = await suggest_profile(task=mock_task, current_user=mock_admin)
            assert result[0]["username"] == "test_user"


def test_integration_suggest_description_stub():
    with patch.dict("os.environ", {"USE_LLM_STUB": "true"}):
        app.dependency_overrides[get_current_user] = lambda: {"is_admin": True}
        payload = {"title": "Test Stub Task"}
        response = client.post("/ai/suggest", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        app.dependency_overrides.clear()