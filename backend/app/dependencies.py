# dependencies.py
from typing import Generator

from sqlalchemy.orm import Session

from app.database.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Provides a database session for FastAPI endpoints.

    The session is automatically closed after
    the request is completed.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()