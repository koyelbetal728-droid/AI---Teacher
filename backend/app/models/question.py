# question.py
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.database import Base


class Question(Base):
    """
    Stores questions generated during a lesson or assessment.
    """

    __tablename__ = "questions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    question_id = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    lesson_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    student_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    question_text = Column(
        Text,
        nullable=False,
    )

    question_type = Column(
        String(50),
        nullable=False,
        default="conceptual",
    )

    difficulty = Column(
        String(50),
        nullable=False,
        default="medium",
    )

    options = Column(
        Text,
        nullable=True,
    )

    correct_answer = Column(
        Text,
        nullable=True,
    )

    student_answer = Column(
        Text,
        nullable=True,
    )

    is_correct = Column(
        Integer,
        nullable=True,
    )

    score = Column(
        Integer,
        nullable=True,
    )

    feedback = Column(
        Text,
        nullable=True,
    )

    misconception = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )