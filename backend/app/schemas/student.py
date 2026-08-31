# student.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StudentBase(BaseModel):
    """
    Common fields shared by student request and response schemas.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    email: str | None = Field(
        default=None,
        max_length=255,
    )

    learner_level: str = Field(
        default="beginner",
        description="beginner, intermediate or advanced",
    )

    preferred_language: str = Field(
        default="english",
        description="Preferred teaching language",
    )

    learning_goal: str | None = Field(
        default=None,
        max_length=1000,
    )

    learning_style: str | None = Field(
        default=None,
        max_length=100,
    )

    strong_topics: str | None = None

    weak_topics: str | None = None


class StudentCreate(StudentBase):
    """
    Schema used when creating a new student.
    """

    pass


class StudentUpdate(BaseModel):
    """
    Schema used when updating a student's learning profile.
    """

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    email: str | None = Field(
        default=None,
        max_length=255,
    )

    learner_level: str | None = None

    preferred_language: str | None = None

    learning_goal: str | None = Field(
        default=None,
        max_length=1000,
    )

    learning_style: str | None = None

    strong_topics: str | None = None

    weak_topics: str | None = None


class StudentResponse(StudentBase):
    """
    Schema returned by the API for a student.
    """

    id: int

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )