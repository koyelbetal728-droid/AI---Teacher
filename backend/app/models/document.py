# document.py
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.database import Base


class Document(Base):
    """
    Stores information about educational documents uploaded
    by students for learning through the RAG pipeline.
    """

    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    document_id = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    original_filename = Column(
        String(255),
        nullable=False,
    )

    stored_filename = Column(
        String(255),
        nullable=False,
    )

    file_type = Column(
        String(20),
        nullable=False,
    )

    file_size = Column(
        Integer,
        nullable=False,
        default=0,
    )

    file_path = Column(
        String(1000),
        nullable=False,
    )

    status = Column(
        String(50),
        nullable=False,
        default="uploaded",
    )

    extracted_text = Column(
        Text,
        nullable=True,
    )

    chunk_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    error_message = Column(
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