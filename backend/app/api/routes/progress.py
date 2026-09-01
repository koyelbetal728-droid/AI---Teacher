# progress.py
"""
Progress API routes for the AI Teacher backend.

Handles student learning progress, progress updates,
and progress summaries.
"""

from fastapi import APIRouter, HTTPException, status

from app.services.progress_service import ProgressService


router = APIRouter()

progress_service = ProgressService()


@router.get("/{student_id}")
async def get_progress(student_id: str):
    """
    Retrieve the learning progress of a student.
    """
    try:
        result = await progress_service.get_progress(student_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress data not found",
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve progress: {exc}",
        ) from exc


@router.post("/{student_id}")
async def update_progress(
    student_id: str,
    progress_data: dict,
):
    """
    Update a student's learning progress.
    """
    try:
        result = await progress_service.update_progress(
            student_id,
            progress_data,
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to update progress",
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
            detail=f"Failed to update progress: {exc}",
        ) from exc


@router.get("/{student_id}/summary")
async def get_progress_summary(student_id: str):
    """
    Retrieve a summarized view of a student's learning progress.
    """
    try:
        if not hasattr(progress_service, "get_progress_summary"):
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Progress summary is not implemented yet",
            )

        result = await progress_service.get_progress_summary(student_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress summary not found",
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve progress summary: {exc}",
        ) from exc