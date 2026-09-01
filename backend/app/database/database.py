"""
Database configuration and session management for the AI Teacher.

The project uses SQLAlchemy so the database can be switched easily
between SQLite for local development and PostgreSQL for production.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    Every database model should inherit from this class.
    """

    pass


def _get_database_url() -> str:
    """
    Return the configured database URL.

    SQLite is convenient for local development.
    PostgreSQL can be configured through the application settings.
    """

    database_url = getattr(settings, "database_url", None)

    if database_url:
        return database_url

    return "sqlite:///./data/ai_teacher.db"


DATABASE_URL = _get_database_url()

# SQLite requires this option when the same database is accessed
# from multiple threads, which can happen with FastAPI.
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False,
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def init_db() -> None:
    """
    Create all registered database tables.

    This should be called during application startup after all
    model modules have been imported.
    """

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    The session is automatically closed after the request finishes.

    Example:

        @router.get("/students")
        def get_students(db: Session = Depends(get_db)):
            ...
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    Context manager for database operations outside FastAPI routes.

    The transaction is committed when the operation succeeds.
    If an exception occurs, the transaction is rolled back.
    """

    db = SessionLocal()

    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_engine():
    """
    Return the configured SQLAlchemy engine.
    """

    return engine


def get_session_factory():
    """
    Return the SQLAlchemy session factory.
    """

    return SessionLocal