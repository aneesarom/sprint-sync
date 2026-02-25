from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_groq import ChatGroq
from app.services.prompts import task_description_system_prompt
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware, ModelRetryMiddleware, ModelFallbackMiddleware
from langchain.agents.structured_output import ToolStrategy, ProviderStrategy
from tavily import TavilyClient
from dotenv import load_dotenv
from langchain_core.tools import tool
import os

load_dotenv()

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.5,
    max_bucket_size=5,
)

default_model = ChatGroq(model="openai/gpt-oss-120b", temperature=0.3, rate_limiter=rate_limiter)
fallback_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3, rate_limiter=rate_limiter)

@tool
def tavily_search(query: str) -> dict:
    """
    Perform a web search using the Tavily API and return the top results.

    This tool queries Tavily with the provided search string and retrieves
    up to three relevant results.

    Args:
        query (str): The search query string to send to Tavily.

    Returns:
        dict: A JSON response from Tavily containing search results,
              including titles, URLs, and content snippets.
    """
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = tavily_client.search(query, max_results=3, topic="general", search_depth="advanced")
    return response


