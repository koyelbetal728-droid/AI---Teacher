"""
Assessment API routes for the AI Teacher backend.

Handles quiz generation, answer evaluation, and assessment results.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.assessment import (
    AssessmentRequest,
    AssessmentResponse,
)
from app.services.assessment_service import AssessmentService


router = APIRouter()

assessment_service = AssessmentService()


@router.post(
    "/",
    response_model=AssessmentResponse,
    status_code=status.HTTP_200_OK,
)
async def create_assessment(request: AssessmentRequest):
    """
    Generate an assessment for a lesson or topic.
    """
    try:
        result = await assessment_service.create_assessment(request)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to create assessment",
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
            detail=f"Failed to create assessment: {exc}",
        ) from exc


@router.post("/evaluate")
async def evaluate_assessment(request: AssessmentRequest):
    """
    Evaluate a student's assessment answers.
    """
    try:
        result = await assessment_service.evaluate_assessment(request)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to evaluate assessment",
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
            detail=f"Failed to evaluate assessment: {exc}",
        ) from exc


@router.get("/{assessment_id}")
async def get_assessment(assessment_id: str):
    """
    Retrieve an assessment by its ID.
    """
    try:
        if not hasattr(assessment_service, "get_assessment"):
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Assessment retrieval is not implemented yet",
            )

        result = await assessment_service.get_assessment(assessment_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found",
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assessment: {exc}",
        ) from exc