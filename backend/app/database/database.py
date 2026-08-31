# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


# ---------------------------------------------------------
# Database URL
# ---------------------------------------------------------

DATABASE_URL = settings.database_url


# ---------------------------------------------------------
# SQLite configuration
# ---------------------------------------------------------

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


# ---------------------------------------------------------
# SQLAlchemy Engine
# ---------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)


# ---------------------------------------------------------
# Database Session
# ---------------------------------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ---------------------------------------------------------
# Base Model
# ---------------------------------------------------------

Base = declarative_base()


# ---------------------------------------------------------
# Initialize Database
# ---------------------------------------------------------

def init_database():
    """
    Create all database tables.

    Models are imported here before creating the tables
    so SQLAlchemy knows about every model.
    """

    from app.models.student import Student
    from app.models.document import Document
    from app.models.lesson import Lesson
    from app.models.question import Question
    from app.models.progress import Progress

    Base.metadata.create_all(
        bind=engine
    )