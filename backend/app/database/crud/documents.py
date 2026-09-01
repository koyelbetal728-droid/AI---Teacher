# documents.py
"""
CRUD operations for documents.

This module contains database operations related to uploaded
learning documents.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document


def create_document(
    db: Session,
    *,
    filename: str,
    file_path: str,
    file_type: Optional[str] = None,
    file_size: Optional[int] = None,
    student_id: Optional[int] = None,
    title: Optional[str] = None,
) -> Document:
    """
    Create and persist a new document.
    """

    document = Document(
        filename=filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        student_id=student_id,
        title=title or filename,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_document(
    db: Session,
    document_id: int,
) -> Optional[Document]:
    """
    Get a document by its ID.
    """

    return db.get(Document, document_id)


def get_documents(
    db: Session,
    *,
    student_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Document]:
    """
    Get a list of documents.

    If student_id is provided, only documents belonging to that
    student are returned.
    """

    statement = select(Document)

    if student_id is not None:
        statement = statement.where(Document.student_id == student_id)

    statement = (
        statement
        .order_by(Document.id.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def update_document(
    db: Session,
    document_id: int,
    **updates,
) -> Optional[Document]:
    """
    Update an existing document.

    Only attributes that actually exist on the Document model
    are updated.
    """

    document = db.get(Document, document_id)

    if document is None:
        return None

    for field, value in updates.items():
        if hasattr(document, field):
            setattr(document, field, value)

    db.commit()
    db.refresh(document)

    return document


def mark_document_processed(
    db: Session,
    document_id: int,
    *,
    processed: bool = True,
) -> Optional[Document]:
    """
    Mark a document as processed or unprocessed.
    """

    document = db.get(Document, document_id)

    if document is None:
        return None

    if hasattr(document, "processed"):
        document.processed = processed

    db.commit()
    db.refresh(document)

    return document


def delete_document(
    db: Session,
    document_id: int,
) -> bool:
    """
    Delete a document by ID.

    Returns True if the document existed and was deleted.
    """

    document = db.get(Document, document_id)

    if document is None:
        return False

    db.delete(document)
    db.commit()

    return True


def document_exists(
    db: Session,
    document_id: int,
) -> bool:
    """
    Check whether a document exists.
    """

    return db.get(Document, document_id) is not None