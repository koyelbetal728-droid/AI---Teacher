"""
Main API router for the AI Teacher backend.

This module combines all feature-specific routers into one
application-level API router.
"""

from fastapi import APIRouter

from app.api.routes import (
    assessment,
    documents,
    health,
    interaction,
    lessons,
    profile,
    progress,
    topics,
)


api_router = APIRouter()


# Health / system
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"],
)

# Documents
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"],
)

# Topics
api_router.include_router(
    topics.router,
    prefix="/topics",
    tags=["Topics"],
)

# Lessons
api_router.include_router(
    lessons.router,
    prefix="/lessons",
    tags=["Lessons"],
)

# Student interaction
api_router.include_router(
    interaction.router,
    prefix="/interaction",
    tags=["Interaction"],
)

# Assessment / quiz
api_router.include_router(
    assessment.router,
    prefix="/assessment",
    tags=["Assessment"],
)

# Student profile
api_router.include_router(
    profile.router,
    prefix="/profile",
    tags=["Profile"],
)

# Learning progress
api_router.include_router(
    progress.router,
    prefix="/progress",
    tags=["Progress"],
)