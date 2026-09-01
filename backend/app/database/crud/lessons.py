# lessons.py
"""
CRUD operations for lessons.

This module contains database operations for creating,
retrieving, updating, and deleting AI-generated lessons.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lesson import Lesson


def create_lesson(
    db: Session,
    *,
    title: str,
    topic: str,
    student_id: Optional[int] = None,
    content: Optional[Any] = None,
    difficulty: Optional[str] = None,
    document_id: Optional[int] = None,
) -> Lesson:
    """
    Create and persist a new lesson.
    """

    lesson = Lesson(
        title=title,
        topic=topic,
        student_id=student_id,
        content=content,
        difficulty=difficulty,
        document_id=document_id,
    )

    db.add(lesson)
    db.commit()
    db.refresh(lesson)

    return lesson


def get_lesson(
    db: Session,
    lesson_id: int,
) -> Optional[Lesson]:
    """
    Get a lesson by its ID.
    """

    return db.get(Lesson, lesson_id)


def get_lessons(
    db: Session,
    *,
    student_id: Optional[int] = None,
    document_id: Optional[int] = None,
    difficulty: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Lesson]:
    """
    Retrieve lessons with optional filters.
    """

    statement = select(Lesson)

    if student_id is not None:
        statement = statement.where(
            Lesson.student_id == student_id
        )

    if document_id is not None:
        statement = statement.where(
            Lesson.document_id == document_id
        )

    if difficulty is not None:
        statement = statement.where(
            Lesson.difficulty == difficulty
        )

    statement = (
        statement
        .order_by(Lesson.id.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def get_lessons_by_student(
    db: Session,
    student_id: int,
    *,
    skip: int = 0,
    limit: int = 100,
) -> list[Lesson]:
    """
    Retrieve all lessons belonging to a student.
    """

    return get_lessons(
        db,
        student_id=student_id,
        skip=skip,
        limit=limit,
    )


def get_lessons_by_document(
    db: Session,
    document_id: int,
    *,
    skip: int = 0,
    limit: int = 100,
) -> list[Lesson]:
    """
    Retrieve all lessons generated from a document.
    """

    return get_lessons(
        db,
        document_id=document_id,
        skip=skip,
        limit=limit,
    )


def update_lesson(
    db: Session,
    lesson_id: int,
    **updates,
) -> Optional[Lesson]:
    """
    Update an existing lesson.

    Only attributes present on the Lesson model are modified.
    """

    lesson = db.get(Lesson, lesson_id)

    if lesson is None:
        return None

    for field, value in updates.items():
        if hasattr(lesson, field):
            setattr(lesson, field, value)

    db.commit()
    db.refresh(lesson)

    return lesson


def delete_lesson(
    db: Session,
    lesson_id: int,
) -> bool:
    """
    Delete a lesson by ID.

    Returns True if the lesson existed and was deleted.
    """

    lesson = db.get(Lesson, lesson_id)

    if lesson is None:
        return False

    db.delete(lesson)
    db.commit()

    return True


def lesson_exists(
    db: Session,
    lesson_id: int,
) -> bool:
    """
    Check whether a lesson exists.
    """

    return db.get(Lesson, lesson_id) is not None


def count_lessons(
    db: Session,
    *,
    student_id: Optional[int] = None,
) -> int:
    """
    Count lessons.

    If student_id is supplied, only that student's lessons
    are counted.
    """

    lessons = get_lessons(
        db,
        student_id=student_id,
        skip=0,
        limit=100000,
    )

    return len(lessons)