"""
Student database model for the AI Teacher backend.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.database import Base


class Student(Base):
    """
    Represents a student using the AI Teacher platform.
    """

    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)

    email = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    grade = Column(String(50), nullable=True)

    language = Column(
        String(50),
        nullable=True,
        default="English",
    )

    learning_style = Column(
        String(100),
        nullable=True,
    )

    interests = Column(Text, nullable=True)

    preferred_difficulty = Column(
        String(50),
        nullable=True,
        default="beginner",
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
            f"<Student("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"email='{self.email}'"
            f")>"
        )