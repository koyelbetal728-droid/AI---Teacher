# lesson.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LessonBase(BaseModel):
    """
    Common fields for a lesson.
    """

    topic: str = Field(
        ...,
        min_length=2,
        max_length=500,
    )

    learner_level: str = Field(
        default="beginner",
        max_length=50,
    )

    language: str = Field(
        default="english",
        max_length=50,
    )

    learning_goal: str | None = Field(
        default=None,
        max_length=1000,
    )

    available_time: int = Field(
        default=20,
        ge=1,
        le=10080,
    )

    teaching_style: str | None = Field(
        default=None,
        max_length=100,
    )


class LessonCreate(LessonBase):
    """
    Schema used when creating a new lesson.
    """

    student_id: int | None = None

    document_id: str | None = Field(
        default=None,
        max_length=100,
    )


class LessonUpdate(BaseModel):
    """
    Schema used when updating a lesson.
    """

    current_step: int | None = Field(
        default=None,
        ge=0,
    )

    status: str | None = Field(
        default=None,
        max_length=50,
    )

    lesson_plan: str | None = None

    score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )


class LessonResponse(LessonBase):
    """
    Schema returned by the API.
    """

    id: int

    lesson_id: str

    student_id: int | None

    document_id: str | None

    lesson_plan: str | None

    current_step: int

    status: str

    score: int | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )