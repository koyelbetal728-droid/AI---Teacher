# progress.py
"""
CRUD operations for student progress.

This module handles database operations related to:
- Learning progress
- Lesson completion
- Scores
- Performance tracking
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.progress import Progress


def create_progress(
    db: Session,
    *,
    student_id: int,
    lesson_id: Optional[int] = None,
    topic: Optional[str] = None,
    score: Optional[float] = None,
    completed: bool = False,
    **extra_fields: Any,
) -> Progress:
    """
    Create and persist a new progress record.
    """

    progress_data = {
        "student_id": student_id,
        "lesson_id": lesson_id,
        "topic": topic,
        "score": score,
        "completed": completed,
    }

    progress_data.update(extra_fields)

    # Only use fields that exist in the Progress model.
    valid_fields = {
        column.name
        for column in Progress.__table__.columns
    }

    progress_data = {
        key: value
        for key, value in progress_data.items()
        if key in valid_fields
    }

    progress = Progress(**progress_data)

    db.add(progress)
    db.commit()
    db.refresh(progress)

    return progress


def get_progress(
    db: Session,
    progress_id: int,
) -> Optional[Progress]:
    """
    Get a progress record by ID.
    """

    return db.get(Progress, progress_id)


def get_student_progress(
    db: Session,
    student_id: int,
    *,
    skip: int = 0,
    limit: int = 100,
) -> list[Progress]:
    """
    Retrieve progress records belonging to a student.
    """

    statement = (
        select(Progress)
        .where(Progress.student_id == student_id)
        .order_by(Progress.id.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def get_lesson_progress(
    db: Session,
    lesson_id: int,
) -> list[Progress]:
    """
    Retrieve all progress records for a lesson.
    """

    statement = (
        select(Progress)
        .where(Progress.lesson_id == lesson_id)
        .order_by(Progress.id.desc())
    )

    return list(db.scalars(statement).all())


def get_topic_progress(
    db: Session,
    student_id: int,
    topic: str,
) -> list[Progress]:
    """
    Retrieve a student's progress for a specific topic.
    """

    statement = (
        select(Progress)
        .where(
            Progress.student_id == student_id,
            Progress.topic == topic,
        )
        .order_by(Progress.id.desc())
    )

    return list(db.scalars(statement).all())


def update_progress(
    db: Session,
    progress_id: int,
    **updates: Any,
) -> Optional[Progress]:
    """
    Update an existing progress record.
    """

    progress = db.get(Progress, progress_id)

    if progress is None:
        return None

    valid_fields = {
        column.name
        for column in Progress.__table__.columns
    }

    for field, value in updates.items():
        if field in valid_fields:
            setattr(progress, field, value)

    db.commit()
    db.refresh(progress)

    return progress


def mark_completed(
    db: Session,
    progress_id: int,
    *,
    score: Optional[float] = None,
) -> Optional[Progress]:
    """
    Mark a progress record as completed.

    Optionally update the final score.
    """

    progress = db.get(Progress, progress_id)

    if progress is None:
        return None

    if hasattr(progress, "completed"):
        progress.completed = True

    if score is not None and hasattr(progress, "score"):
        progress.score = score

    db.commit()
    db.refresh(progress)

    return progress


def delete_progress(
    db: Session,
    progress_id: int,
) -> bool:
    """
    Delete a progress record by ID.
    """

    progress = db.get(Progress, progress_id)

    if progress is None:
        return False

    db.delete(progress)
    db.commit()

    return True


def progress_exists(
    db: Session,
    progress_id: int,
) -> bool:
    """
    Check whether a progress record exists.
    """

    return db.get(Progress, progress_id) is not None


def get_completed_progress(
    db: Session,
    student_id: int,
) -> list[Progress]:
    """
    Retrieve all completed progress records for a student.
    """

    statement = (
        select(Progress)
        .where(
            Progress.student_id == student_id,
            Progress.completed.is_(True),
        )
        .order_by(Progress.id.desc())
    )

    return list(db.scalars(statement).all())


def get_average_score(
    db: Session,
    student_id: int,
) -> Optional[float]:
    """
    Calculate the average score for a student.

    Returns None when the student has no scored progress records.
    """

    records = get_student_progress(
        db,
        student_id,
        skip=0,
        limit=100000,
    )

    scores = [
        float(record.score)
        for record in records
        if getattr(record, "score", None) is not None
    ]

    if not scores:
        return None

    return sum(scores) / len(scores)


def count_completed_lessons(
    db: Session,
    student_id: int,
) -> int:
    """
    Count completed progress records for a student.
    """

    records = get_completed_progress(
        db,
        student_id,
    )

    return len(records)