from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware import LoggingMiddleware
from app.routes import users, tasks, suggest, resumes
from app.logging_config import configure_logging, get_logger
from prometheus_fastapi_instrumentator import Instrumentator




configure_logging()
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="sprint-sync",
    description="Backend API for SprintSync application",
    version="0.1.0",
)

Instrumentator().instrument(app).expose(app)

app.add_middleware(LoggingMiddleware)
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(suggest.router)
app.include_router(resumes.router)