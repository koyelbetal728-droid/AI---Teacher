# logging.py
"""
Logging configuration for the AI Teacher backend.

This module provides a centralized logging setup so that
API requests, AI operations, errors, and background tasks
use a consistent logging format.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

from app.config import settings


DEFAULT_LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | "
    "%(name)s | %(message)s"
)

DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _get_log_level() -> int:
    """
    Read the configured log level.
    """

    level = getattr(
        settings,
        "log_level",
        "INFO",
    )

    if isinstance(level, int):
        return level

    level_name = str(level).upper()

    return getattr(
        logging,
        level_name,
        logging.INFO,
    )


def _get_log_file() -> Optional[Path]:
    """
    Get the configured log file path.

    Returns None when file logging is disabled.
    """

    enabled = getattr(
        settings,
        "log_to_file",
        False,
    )

    if not enabled:
        return None

    configured_path = getattr(
        settings,
        "log_file",
        "data/logs/ai_teacher.log",
    )

    return Path(configured_path)


def configure_logging() -> None:
    """
    Configure application-wide logging.

    Logging is sent to stdout and optionally to a log file.
    """

    log_level = _get_log_level()
    log_file = _get_log_file()

    formatter = logging.Formatter(
        fmt=DEFAULT_LOG_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT,
    )

    handlers: list[logging.Handler] = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    # Optional file handler
    if log_file is not None:
        log_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_handler = logging.FileHandler(
            log_file,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    root_logger = logging.getLogger()

    # Remove handlers installed by previous configuration.
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    root_logger.setLevel(log_level)

    for handler in handlers:
        root_logger.addHandler(handler)

    # Keep noisy third-party libraries under control.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(
    name: Optional[str] = None,
) -> logging.Logger:
    """
    Return a logger for the requested module.

    Example:

        logger = get_logger(__name__)
        logger.info("Lesson generated successfully")
    """

    return logging.getLogger(
        name or "ai_teacher"
    )


def log_exception(
    logger: logging.Logger,
    message: str,
    exception: Exception,
) -> None:
    """
    Log an exception together with its traceback.
    """

    logger.exception(
        "%s: %s",
        message,
        exception,
    )


def set_log_level(
    level: str | int,
) -> None:
    """
    Change the application's logging level at runtime.
    """

    if isinstance(level, str):
        level = getattr(
            logging,
            level.upper(),
            logging.INFO,
        )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    for handler in root_logger.handlers:
        handler.setLevel(level)


# Configure logging when this module is imported.
configure_logging()

logger = get_logger("ai_teacher")