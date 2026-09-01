# students.py
"""
CRUD operations for students.

This module contains database operations for creating,
retrieving, updating, and deleting student profiles.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.student import Student


def create_student(
    db: Session,
    *,
    name: str,
    email: Optional[str] = None,
    age: Optional[int] = None,
    grade: Optional[str] = None,
    preferred_language: Optional[str] = None,
    learning_style: Optional[str] = None,
    **extra_fields: Any,
) -> Student:
    """
    Create and persist a new student.
    """

    student_data = {
        "name": name,
        "email": email,
        "age": age,
        "grade": grade,
        "preferred_language": preferred_language,
        "learning_style": learning_style,
    }

    student_data.update(extra_fields)

    # Only pass fields that actually exist on the model.
    valid_fields = {
        column.name
        for column in Student.__table__.columns
    }

    student_data = {
        key: value
        for key, value in student_data.items()
        if key in valid_fields
    }

    student = Student(**student_data)

    db.add(student)
    db.commit()
    db.refresh(student)

    return student


def get_student(
    db: Session,
    student_id: int,
) -> Optional[Student]:
    """
    Get a student by ID.
    """

    return db.get(Student, student_id)


def get_student_by_email(
    db: Session,
    email: str,
) -> Optional[Student]:
    """
    Get a student by email address.
    """

    statement = select(Student).where(
        Student.email == email
    )

    return db.scalars(statement).first()


def get_students(
    db: Session,
    *,
    grade: Optional[str] = None,
    preferred_language: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Student]:
    """
    Retrieve students with optional filters.
    """

    statement = select(Student)

    if grade is not None:
        statement = statement.where(
            Student.grade == grade
        )

    if preferred_language is not None:
        statement = statement.where(
            Student.preferred_language == preferred_language
        )

    statement = (
        statement
        .order_by(Student.id.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def update_student(
    db: Session,
    student_id: int,
    **updates: Any,
) -> Optional[Student]:
    """
    Update an existing student.

    Only fields that exist on the Student model are updated.
    """

    student = db.get(Student, student_id)

    if student is None:
        return None

    valid_fields = {
        column.name
        for column in Student.__table__.columns
    }

    for field, value in updates.items():
        if field in valid_fields:
            setattr(student, field, value)

    db.commit()
    db.refresh(student)

    return student


def delete_student(
    db: Session,
    student_id: int,
) -> bool:
    """
    Delete a student by ID.

    Returns True if the student existed and was deleted.
    """

    student = db.get(Student, student_id)

    if student is None:
        return False

    db.delete(student)
    db.commit()

    return True


def student_exists(
    db: Session,
    student_id: int,
) -> bool:
    """
    Check whether a student exists.
    """

    return db.get(Student, student_id) is not None


def count_students(
    db: Session,
) -> int:
    """
    Return the total number of students.
    """

    statement = select(Student)

    return len(list(db.scalars(statement).all()))