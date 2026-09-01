# profile.py
"""
Profile API routes for the AI Teacher backend.

Handles student profile creation, retrieval, and updates.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.student import StudentCreate, StudentResponse
from app.services.personalization_service import PersonalizationService


router = APIRouter()

personalization_service = PersonalizationService()


@router.post(
    "/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(student: StudentCreate):
    """
    Create a student learning profile.
    """
    try:
        if hasattr(personalization_service, "create_profile"):
            result = await personalization_service.create_profile(student)

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to create student profile",
                )

            return result

        return student

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
            detail=f"Failed to create profile: {exc}",
        ) from exc


@router.get("/{student_id}", response_model=StudentResponse)
async def get_profile(student_id: str):
    """
    Retrieve a student profile by student ID.
    """
    try:
        if not hasattr(personalization_service, "get_profile"):
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Profile retrieval is not implemented yet",
            )

        result = await personalization_service.get_profile(student_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found",
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve profile: {exc}",
        ) from exc


@router.put("/{student_id}", response_model=StudentResponse)
async def update_profile(
    student_id: str,
    student: StudentCreate,
):
    """
    Update an existing student profile.
    """
    try:
        if not hasattr(personalization_service, "update_profile"):
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Profile update is not implemented yet",
            )

        result = await personalization_service.update_profile(
            student_id,
            student,
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found",
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
            detail=f"Failed to update profile: {exc}",
        ) from exc