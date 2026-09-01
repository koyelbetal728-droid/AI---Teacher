# exceptions.py
"""
Custom exceptions for the AI Teacher backend.

These exceptions provide a consistent way for services,
AI modules, database operations, and API routes to report
application-specific errors.
"""

from __future__ import annotations

from typing import Any, Optional


class AppException(Exception):
    """
    Base exception for application-specific errors.
    """

    status_code: int = 500
    error_code: str = "APP_ERROR"

    def __init__(
        self,
        message: str = "An application error occurred.",
        *,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)

        self.message = message
        self.status_code = (
            status_code
            if status_code is not None
            else self.status_code
        )
        self.error_code = (
            error_code
            if error_code is not None
            else self.error_code
        )
        self.details = details

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the exception into a JSON-friendly dictionary.
        """

        response = {
            "error": self.error_code,
            "message": self.message,
        }

        if self.details is not None:
            response["details"] = self.details

        return response


# ---------------------------------------------------------------------------
# Authentication / authorization
# ---------------------------------------------------------------------------

class AuthenticationError(AppException):
    """
    Raised when authentication fails.
    """

    status_code = 401
    error_code = "AUTHENTICATION_ERROR"

    def __init__(
        self,
        message: str = "Authentication failed.",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message,
            **kwargs,
        )


class AuthorizationError(AppException):
    """
    Raised when an authenticated user does not have permission.
    """

    status_code = 403
    error_code = "AUTHORIZATION_ERROR"

    def __init__(
        self,
        message: str = "You do not have permission to perform this action.",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message,
            **kwargs,
        )


# ---------------------------------------------------------------------------
# Resource errors
# ---------------------------------------------------------------------------

class NotFoundError(AppException):
    """
    Raised when a requested resource cannot be found.
    """

    status_code = 404
    error_code = "NOT_FOUND"

    def __init__(
        self,
        resource: str = "Resource",
        resource_id: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        if resource_id is not None:
            message = f"{resource} with ID '{resource_id}' was not found."
        else:
            message = f"{resource} was not found."

        super().__init__(
            message,
            **kwargs,
        )


class ConflictError(AppException):
    """
    Raised when an operation conflicts with existing data.
    """

    status_code = 409
    error_code = "CONFLICT"

    def __init__(
        self,
        message: str = "The requested operation conflicts with existing data.",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message,
            **kwargs,
        )


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------

class ValidationError(AppException):
    """
    Raised when supplied data is invalid.
    """

    status_code = 422
    error_code = "VALIDATION_ERROR"

    def __init__(
        self,
        message: str = "The supplied data is invalid.",
        *,
        details: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message,
            details=details,
            **kwargs,
        )


# ---------------------------------------------------------------------------
# Document / file errors
# ---------------------------------------------------------------------------

class FileProcessingError(AppException):
    """
    Raised when a document cannot be processed.
    """

    status_code = 422
    error_code = "FILE_PROCESSING_ERROR"

    def __init__(
        self,
        message: str = "The uploaded file could not be processed.",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message,
            **kwargs,
        )


class UnsupportedFileTypeError(FileProcessingError):
    """
    Raised when an uploaded file type is unsupported.
    """

    error_code = "UNSUPPORTED_FILE_TYPE"

    def __init__(
        self,
        file_type: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if file_type:
            message = (
                f"Unsupported file type: '{file_type}'."
            )
        else:
            message = "The uploaded file type is not supported."

        super().__init__(
            message,
            **kwargs,
        )


# ---------------------------------------------------------------------------
# AI / model errors
# ---------------------------------------------------------------------------

class AIServiceError(AppException):
    """
    Raised when an AI service operation fails.
    """

    status_code = 503
    error_code = "AI_SERVICE_ERROR"

    def __init__(
        self,
        message: str = "The AI service is currently unavailable.",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message,
            **kwargs,
        )


class LLMError(AIServiceError):
    """
    Raised when the local LLM fails.
    """

    error_code = "LLM_ERROR"


class RAGError(AIServiceError):
    """
    Raised when a RAG operation fails.
    """

    error_code = "RAG_ERROR"


class EmbeddingError(AIServiceError):
    """
    Raised when embedding generation fails.
    """

    error_code = "EMBEDDING_ERROR"


# ---------------------------------------------------------------------------
# Media errors
# ---------------------------------------------------------------------------

class MediaProcessingError(AppException):
    """
    Raised when audio, image, avatar, or video processing fails.
    """

    status_code = 422
    error_code = "MEDIA_PROCESSING_ERROR"

    def __init__(
        self,
        message: str = "Media processing failed.",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message,
            **kwargs,
        )


class SpeechProcessingError(MediaProcessingError):
    """
    Raised when speech-to-text or text-to-speech fails.
    """

    error_code = "SPEECH_PROCESSING_ERROR"


class VideoProcessingError(MediaProcessingError):
    """
    Raised when video generation or rendering fails.
    """

    error_code = "VIDEO_PROCESSING_ERROR"


# ---------------------------------------------------------------------------
# Database errors
# ---------------------------------------------------------------------------

class DatabaseError(AppException):
    """
    Raised when a database operation fails.
    """

    status_code = 500
    error_code = "DATABASE_ERROR"

    def __init__(
        self,
        message: str = "A database operation failed.",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message,
            **kwargs,
        )


# ---------------------------------------------------------------------------
# Convenience helper
# ---------------------------------------------------------------------------

def exception_to_response(
    exc: Exception,
) -> dict[str, Any]:
    """
    Convert an exception into a consistent response dictionary.

    Application-specific exceptions expose their structured data.
    Unknown exceptions receive a generic error response.
    """

    if isinstance(exc, AppException):
        return exc.to_dict()

    return {
        "error": "INTERNAL_SERVER_ERROR",
        "message": "An unexpected internal error occurred.",
    }