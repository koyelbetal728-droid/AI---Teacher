from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.database import Base


class Progress(Base):
    """
    Stores a student's learning progress for a topic or lesson.
    """

    __tablename__ = "progress"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    student_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    lesson_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    topic = Column(
        String(500),
        nullable=False,
    )

    mastery_score = Column(
        Integer,
        nullable=False,
        default=0,
    )

    questions_attempted = Column(
        Integer,
        nullable=False,
        default=0,
    )

    questions_correct = Column(
        Integer,
        nullable=False,
        default=0,
    )

    misconceptions = Column(
        Text,
        nullable=True,
    )

    strengths = Column(
        Text,
        nullable=True,
    )

    weaknesses = Column(
        Text,
        nullable=True,
    )

    recommended_topics = Column(
        Text,
        nullable=True,
    )

    time_spent_minutes = Column(
        Integer,
        nullable=False,
        default=0,
    )

    status = Column(
        String(50),
        nullable=False,
        default="in_progress",
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