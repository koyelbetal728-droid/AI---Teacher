# lessons.py
"""
Lesson API routes for the AI Teacher backend.

Handles lesson creation, retrieval, generation, and deletion.
"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, status

from app.schemas.lesson import LessonCreate, LessonResponse
from app.services.lesson_service import LessonService


router = APIRouter()

lesson_service = LessonService()


@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(lesson: LessonCreate):
    """
    Create a new AI-generated lesson.
    """
    try:
        result = await lesson_service.create_lesson(lesson)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to create lesson",
            )

        return result

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create lesson: {exc}",
        ) from exc


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(lesson_id: str):
    """
    Retrieve a lesson by its ID.
    """
    try:
        result = await lesson_service.get_lesson(lesson_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found",
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve lesson: {exc}",
        ) from exc


@router.get("/")
async def list_lessons():
    """
    Retrieve all available lessons.
    """
    try:
        if hasattr(lesson_service, "list_lessons"):
            return await lesson_service.list_lessons()

        return {
            "lessons": [],
            "count": 0,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve lessons: {exc}",
        ) from exc


@router.delete("/{lesson_id}")
async def delete_lesson(lesson_id: str):
    """
    Delete a lesson by its ID.
    """
    try:
        if not hasattr(lesson_service, "delete_lesson"):
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Lesson deletion is not implemented yet",
            )

        deleted = await lesson_service.delete_lesson(lesson_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found",
            )

        return {
            "success": True,
            "message": "Lesson deleted successfully",
            "lesson_id": lesson_id,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete lesson: {exc}",
        ) from exc