"""
Document database model for the AI Teacher backend.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.database import Base


class Document(Base):
    """
    Represents a learning document uploaded by a student.
    """

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String(255), nullable=False)

    file_path = Column(String(500), nullable=False)

    file_type = Column(String(50), nullable=True)

    content = Column(Text, nullable=True)

    status = Column(
        String(50),
        nullable=False,
        default="uploaded",
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
            f"<Document("
            f"id={self.id}, "
            f"filename='{self.filename}', "
            f"status='{self.status}'"
            f")>"
        )