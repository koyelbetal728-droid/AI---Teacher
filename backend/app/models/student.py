from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Student(Base):
    """
    Stores the student's profile and learning preferences.
    """

    __tablename__ = "students"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
    )

    learner_level = Column(
        String(50),
        nullable=False,
        default="beginner",
    )

    preferred_language = Column(
        String(50),
        nullable=False,
        default="english",
    )

    learning_goal = Column(
        Text,
        nullable=True,
    )

    learning_style = Column(
        String(100),
        nullable=True,
    )

    strong_topics = Column(
        Text,
        nullable=True,
    )

    weak_topics = Column(
        Text,
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

    # Relationships will be connected with the remaining
    # models after those files are created.