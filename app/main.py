from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Create FastAPI app
app = FastAPI(
    title="sprint-sync",
    description="Backend API for SprintSync application",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)