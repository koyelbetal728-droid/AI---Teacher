"""
File utilities for the AI Teacher backend.

This module provides safe and reusable helpers for:
- File validation
- File naming
- File storage
- File deletion
- File metadata
- Supported document types
"""

from __future__ import annotations

import mimetypes
import re
import uuid
from pathlib import Path
from typing import Optional

from app.config import settings


# ---------------------------------------------------------------------------
# Supported file types
# ---------------------------------------------------------------------------

SUPPORTED_EXTENSIONS = {
    ".pdf": "application/pdf",
    ".docx": (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
    ),
    ".txt": "text/plain",
    ".md": "text/markdown",
}


def get_supported_extensions() -> list[str]:
    """
    Return all supported document extensions.
    """

    return list(SUPPORTED_EXTENSIONS.keys())


def is_supported_extension(
    filename: str,
) -> bool:
    """
    Check whether a filename has a supported extension.
    """

    if not filename:
        return False

    extension = Path(filename).suffix.lower()

    return extension in SUPPORTED_EXTENSIONS


def get_file_extension(
    filename: str,
) -> str:
    """
    Return a normalized file extension.
    """

    if not filename:
        return ""

    return Path(filename).suffix.lower()


def get_mime_type(
    filename: str,
) -> str:
    """
    Determine the MIME type of a file.

    Falls back to the supported-extension mapping when needed.
    """

    extension = get_file_extension(filename)

    if extension in SUPPORTED_EXTENSIONS:
        return SUPPORTED_EXTENSIONS[extension]

    mime_type, _ = mimetypes.guess_type(filename)

    return mime_type or "application/octet-stream"


# ---------------------------------------------------------------------------
# File name utilities
# ---------------------------------------------------------------------------

def sanitize_filename(
    filename: str,
) -> str:
    """
    Convert a filename into a filesystem-safe filename.
    """

    if not filename:
        return "file"

    filename = Path(filename).name

    # Replace spaces with underscores.
    filename = filename.replace(" ", "_")

    # Remove unsafe characters.
    filename = re.sub(
        r"[^A-Za-z0-9._-]",
        "",
        filename,
    )

    # Prevent repeated dots.
    filename = re.sub(
        r"\.{2,}",
        ".",
        filename,
    )

    if not filename:
        return "file"

    return filename


def generate_unique_filename(
    filename: str,
) -> str:
    """
    Generate a unique filesystem-safe filename.
    """

    safe_name = sanitize_filename(filename)

    path = Path(safe_name)

    unique_id = uuid.uuid4().hex[:12]

    if path.suffix:
        return (
            f"{path.stem}_{unique_id}"
            f"{path.suffix.lower()}"
        )

    return f"{safe_name}_{unique_id}"


# ---------------------------------------------------------------------------
# Storage directories
# ---------------------------------------------------------------------------

def get_upload_directory() -> Path:
    """
    Return the configured upload directory.
    """

    directory = getattr(
        settings,
        "upload_directory",
        "data/uploads",
    )

    path = Path(directory)
    path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return path


def get_processed_directory() -> Path:
    """
    Return the configured processed-data directory.
    """

    directory = getattr(
        settings,
        "processed_directory",
        "data/processed",
    )

    path = Path(directory)
    path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return path


# ---------------------------------------------------------------------------
# File validation
# ---------------------------------------------------------------------------

def validate_file_extension(
    filename: str,
) -> None:
    """
    Validate that a file has a supported extension.

    Raises:
        ValueError: If the extension is unsupported.
    """

    if not is_supported_extension(filename):
        extension = get_file_extension(filename)

        supported = ", ".join(
            get_supported_extensions()
        )

        raise ValueError(
            f"Unsupported file extension '{extension}'. "
            f"Supported types: {supported}"
        )


def validate_file_size(
    file_size: int,
    *,
    max_size_mb: Optional[float] = None,
) -> None:
    """
    Validate a file's size.

    Args:
        file_size:
            Size in bytes.

        max_size_mb:
            Maximum allowed size in megabytes.
            Falls back to application settings.
    """

    if file_size < 0:
        raise ValueError("File size cannot be negative.")

    if max_size_mb is None:
        max_size_mb = getattr(
            settings,
            "max_upload_size_mb",
            20,
        )

    max_size_bytes = int(
        float(max_size_mb) * 1024 * 1024
    )

    if file_size > max_size_bytes:
        raise ValueError(
            f"File size exceeds the maximum allowed "
            f"size of {max_size_mb} MB."
        )


# ---------------------------------------------------------------------------
# File storage
# ---------------------------------------------------------------------------

def save_file(
    content: bytes,
    filename: str,
    *,
    directory: Optional[Path | str] = None,
    unique_name: bool = True,
) -> Path:
    """
    Save file bytes to disk.

    Returns:
        Path to the saved file.
    """

    if not isinstance(content, bytes):
        raise TypeError(
            "File content must be provided as bytes."
        )

    validate_file_extension(filename)
    validate_file_size(len(content))

    if directory is None:
        directory_path = get_upload_directory()
    else:
        directory_path = Path(directory)
        directory_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    if unique_name:
        safe_filename = generate_unique_filename(
            filename
        )
    else:
        safe_filename = sanitize_filename(
            filename
        )

    file_path = directory_path / safe_filename

    file_path.write_bytes(content)

    return file_path


def read_file(
    file_path: Path | str,
) -> bytes:
    """
    Read a file from disk.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    return path.read_bytes()


def delete_file(
    file_path: Path | str,
) -> bool:
    """
    Delete a file.

    Returns True if a file was deleted.
    Returns False if it did not exist.
    """

    path = Path(file_path)

    if not path.exists():
        return False

    if not path.is_file():
        return False

    path.unlink()

    return True


def file_exists(
    file_path: Path | str,
) -> bool:
    """
    Check whether a file exists.
    """

    path = Path(file_path)

    return path.exists() and path.is_file()


# ---------------------------------------------------------------------------
# File metadata
# ---------------------------------------------------------------------------

def get_file_size(
    file_path: Path | str,
) -> int:
    """
    Return the file size in bytes.
    """

    path = Path(file_path)

    if not file_exists(path):
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    return path.stat().st_size


def get_file_metadata(
    file_path: Path | str,
) -> dict:
    """
    Return useful metadata for a stored file.
    """

    path = Path(file_path)

    if not file_exists(path):
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    stat = path.stat()

    return {
        "filename": path.name,
        "extension": path.suffix.lower(),
        "mime_type": get_mime_type(path.name),
        "size": stat.st_size,
        "size_mb": round(
            stat.st_size / (1024 * 1024),
            3,
        ),
        "path": str(path),
    }


# ---------------------------------------------------------------------------
# Cleanup helpers
# ---------------------------------------------------------------------------

def clear_directory(
    directory: Path | str,
) -> int:
    """
    Delete files from a directory.

    Returns the number of files removed.

    Subdirectories are intentionally preserved.
    """

    path = Path(directory)

    if not path.exists():
        return 0

    if not path.is_dir():
        raise ValueError(
            f"Path is not a directory: {path}"
        )

    deleted_count = 0

    for item in path.iterdir():
        if item.is_file():
            item.unlink()
            deleted_count += 1

    return deleted_count