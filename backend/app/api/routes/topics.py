# topics.py
from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter()


class TopicRequest(BaseModel):
    """
    Data received when a student wants to learn a topic.
    """

    topic: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="Topic the student wants to learn",
    )

    learner_level: str = Field(
        default="beginner",
        description="beginner, intermediate or advanced",
    )

    language: str = Field(
        default="english",
        description="Preferred teaching language",
    )

    available_time: int = Field(
        default=20,
        ge=1,
        le=10080,
        description="Available learning time in minutes",
    )

    learning_goal: str | None = Field(
        default=None,
        max_length=1000,
        description="What the student wants to achieve",
    )


@router.post("/start")
async def start_topic_learning(
    request: TopicRequest,
):
    """
    Start a topic-based learning session.

    The actual AI lesson planner will be connected later.
    """

    return {
        "success": True,
        "topic": request.topic,
        "learner_level": request.learner_level,
        "language": request.language,
        "available_time": request.available_time,
        "learning_goal": request.learning_goal,
        "message": (
            "Topic received successfully. "
            "AI lesson planning will be connected next."
        ),
    }