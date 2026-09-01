"""Pydantic schemas for API request and response validation."""

from .document import (
    DocumentBase,
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
)

from .lesson import (
    LessonBase,
    LessonCreate,
    LessonResponse,
    LessonUpdate,
    LessonPlan,
    LessonGenerateRequest,
    LessonGenerateResponse,
)

from .student import (
    StudentBase,
    StudentCreate,
    StudentUpdate,
    StudentResponse,
)

from .interaction import (
    InteractionRequest,
    InteractionResponse,
)

from .assessment import (
    AssessmentBase,
    AssessmentCreate,
    AssessmentQuestion,
    AssessmentAnswer,
    AssessmentSubmit,
    AssessmentResult,
    AssessmentResponse,
)

__all__ = [
    "DocumentBase",
    "DocumentCreate",
    "DocumentResponse",
    "DocumentUpdate",
    "LessonBase",
    "LessonCreate",
    "LessonResponse",
    "LessonUpdate",
    "LessonPlan",
    "LessonGenerateRequest",
    "LessonGenerateResponse",
    "StudentBase",
    "StudentCreate",
    "StudentUpdate",
    "StudentResponse",
    "InteractionRequest",
    "InteractionResponse",
    "AssessmentBase",
    "AssessmentCreate",
    "AssessmentQuestion",
    "AssessmentAnswer",
    "AssessmentSubmit",
    "AssessmentResult",
    "AssessmentResponse",
]