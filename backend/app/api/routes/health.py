from datetime import datetime, timezone

from fastapi import APIRouter

from app.config import settings


router = APIRouter(
    prefix="/health"
)


@router.get("")
async def health_check():
    """
    Check whether the AI Teacher backend is running.
    """

    return {
        "success": True,
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.app_env,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }