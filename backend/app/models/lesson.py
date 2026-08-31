from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.database import Base


class Lesson(Base):
    """
    Stores a personalized lesson generated for a student.
    """

    __tablename__ = "lessons"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    lesson_id = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    student_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    document_id = Column(
        String(100),
        nullable=True,
        index=True,
    )

    topic = Column(
        String(500),
        nullable=False,
    )

    learner_level = Column(
        String(50),
        nullable=False,
        default="beginner",
    )

    language = Column(
        String(50),
        nullable=False,
        default="english",
    )

    learning_goal = Column(
        Text,
        nullable=True,
    )

    available_time = Column(
        Integer,
        nullable=False,
        default=20,
    )

    teaching_style = Column(
        String(100),
        nullable=True,
    )

    lesson_plan = Column(
        Text,
        nullable=True,
    )

    current_step = Column(
        Integer,
        nullable=False,
        default=0,
    )

    status = Column(
        String(50),
        nullable=False,
        default="created",
    )

    score = Column(
        Integer,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )