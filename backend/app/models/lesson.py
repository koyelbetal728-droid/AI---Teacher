"""
Lesson database model for the AI Teacher backend.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.database import Base


class Lesson(Base):
    """
    Represents an AI-generated lesson.
    """

    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)

    topic = Column(String(255), nullable=False)

    description = Column(Text, nullable=True)

    content = Column(Text, nullable=True)

    difficulty = Column(
        String(50),
        nullable=True,
        default="beginner",
    )

    language = Column(
        String(50),
        nullable=True,
        default="English",
    )

    duration_minutes = Column(
        Integer,
        nullable=True,
        default=30,
    )

    status = Column(
        String(50),
        nullable=False,
        default="draft",
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

    def __repr__(self) -> str:
        return (
            f"<Lesson("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"topic='{self.topic}'"
            f")>"
        )