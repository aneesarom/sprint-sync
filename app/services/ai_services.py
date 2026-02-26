from groq import APITimeoutError, RateLimitError
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_groq import ChatGroq
from app.services.prompts import task_description_system_prompt, resume_sparse_prompt, resume_semantic_prompt, query_generator_system_prompt
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware, ModelRetryMiddleware, ModelFallbackMiddleware, ToolCallLimitMiddleware
from langchain.agents.structured_output import ToolStrategy, ProviderStrategy
from tavily import TavilyClient
from dotenv import load_dotenv
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import List
import os

load_dotenv()

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.5,
    max_bucket_size=5,
)

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

default_model = ChatGroq(model="openai/gpt-oss-120b", temperature=0.3, rate_limiter=rate_limiter)
fallback_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3, rate_limiter=rate_limiter)
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", 
                                                output_dimensionality=768)

description_generator_agent = create_agent(
            model=default_model,
            tools=[tavily_search],
            system_prompt=task_description_system_prompt,
            middleware=[
                ToolCallLimitMiddleware(tool_name="tavily_search", thread_limit=3, run_limit=3),
                ModelFallbackMiddleware(first_model=fallback_model),
                ModelCallLimitMiddleware(thread_limit=3, run_limit=3),
                ModelRetryMiddleware(max_retries=3, 
                                     retry_on=(APITimeoutError, RateLimitError), 
                                     backoff_factor=1.5, 
                                     initial_delay=2.0)
            ]
        )

profile_skills_generator_agent = create_agent(
    model=default_model,
    system_prompt=resume_sparse_prompt,
    middleware=[
                ModelFallbackMiddleware(first_model=fallback_model),
                ModelCallLimitMiddleware(thread_limit=3, run_limit=3),
                ModelRetryMiddleware(max_retries=3, 
                                     retry_on=(APITimeoutError, RateLimitError), 
                                     backoff_factor=1.5, 
                                     initial_delay=2.0)
            ]
    )

profile_task_generator_agent = create_agent(
    model=default_model,
    system_prompt=resume_semantic_prompt,
    middleware=[
                ModelFallbackMiddleware(first_model=fallback_model),
                ModelCallLimitMiddleware(thread_limit=3, run_limit=3),
                ModelRetryMiddleware(max_retries=3, 
                                     retry_on=(APITimeoutError, RateLimitError), 
                                     backoff_factor=1.5, 
                                     initial_delay=2.0)
            ]
    )


class QueryVariations(BaseModel):

    keyword_search_queries: List[str] = Field(
        description=(
            "Technical noun phrases for sparse search. "
            "1-4 words maximum. No verbs. No sentences. "
            "Only tools, frameworks, technologies, or domain concepts."
        ),
        min_length=1,
        max_length=2
    )

    task_search_queries: List[str] = Field(
        description=(
            "Action-oriented professional task descriptions. "
            "Full sentence describing a real responsibility."
        ),
        min_length=1,
        max_length=3
    )

query_generator_agent = create_agent(
    model=default_model,
    system_prompt=query_generator_system_prompt,
    middleware=[
                ModelFallbackMiddleware(first_model=fallback_model),
                ModelCallLimitMiddleware(thread_limit=3, run_limit=3),
                ModelRetryMiddleware(max_retries=3, 
                                     retry_on=(APITimeoutError, RateLimitError), 
                                     backoff_factor=1.5, 
                                     initial_delay=2.0)
            ]
    )







