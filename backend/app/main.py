# main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.router import api_router
from app.database.database import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs when the FastAPI application starts and stops.
    """

    # Initialize the database when the server starts.
    init_database()

    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "AI Teacher - a personalized AI-powered "
        "learning and teaching platform."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------

app.include_router(
    api_router,
    prefix="/api",
)


# ---------------------------------------------------------
# ROOT ENDPOINT
# ---------------------------------------------------------

@app.get("/")
async def root():
    return {
        "success": True,
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "message": "AI Teacher API is running.",
    }