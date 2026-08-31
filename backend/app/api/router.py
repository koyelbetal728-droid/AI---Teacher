# router.py
from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.documents import router as documents_router
from app.api.routes.topics import router as topics_router


api_router = APIRouter()


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

api_router.include_router(
    health_router,
    tags=["Health"],
)


# ---------------------------------------------------------
# Documents
# ---------------------------------------------------------

api_router.include_router(
    documents_router,
    prefix="/documents",
    tags=["Documents"],
)


# ---------------------------------------------------------
# Topics
# ---------------------------------------------------------

api_router.include_router(
    topics_router,
    prefix="/topics",
    tags=["Topics"],
)