# document.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentBase(BaseModel):
    """
    Common document fields.
    """

    original_filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    file_type: str = Field(
        ...,
        max_length=20,
    )


class DocumentCreate(DocumentBase):
    """
    Schema used internally when creating a document record.
    """

    document_id: str = Field(
        ...,
        max_length=100,
    )

    stored_filename: str = Field(
        ...,
        max_length=255,
    )

    file_size: int = Field(
        default=0,
        ge=0,
    )

    file_path: str = Field(
        ...,
        max_length=1000,
    )


class DocumentResponse(DocumentBase):
    """
    Schema returned by the API.
    """

    id: int

    document_id: str

    stored_filename: str

    file_size: int

    file_path: str

    status: str

    chunk_count: int

    error_message: str | None = None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )