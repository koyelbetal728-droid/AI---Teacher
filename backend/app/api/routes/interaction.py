"""
Interaction API routes for the AI Teacher backend.

Handles student questions, answers, feedback, and
AI teacher interactions.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.interaction import InteractionRequest, InteractionResponse
from app.services.interaction_service import InteractionService


router = APIRouter()

interaction_service = InteractionService()


@router.post(
    "/",
    response_model=InteractionResponse,
    status_code=status.HTTP_200_OK,
)
async def interact(request: InteractionRequest):
    """
    Process a student interaction with the AI teacher.
    """
    try:
        result = await interaction_service.process_interaction(request)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to process interaction",
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
            detail=f"Failed to process interaction: {exc}",
        ) from exc


@router.post("/question")
async def ask_question(request: InteractionRequest):
    """
    Ask the AI teacher a question.
    """
    try:
        result = await interaction_service.ask_question(request)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to answer question",
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
            detail=f"Failed to answer question: {exc}",
        ) from exc


@router.post("/answer")
async def submit_answer(request: InteractionRequest):
    """
    Submit a student's answer for AI evaluation and feedback.
    """
    try:
        result = await interaction_service.submit_answer(request)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to evaluate answer",
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
            detail=f"Failed to evaluate answer: {exc}",
        ) from exc