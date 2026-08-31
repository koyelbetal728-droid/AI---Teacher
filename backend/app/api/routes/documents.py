# documents.py
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings


router = APIRouter()


# Supported educational document formats
ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".txt",
}


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
):
    """
    Upload an educational document.

    The actual document processing and RAG pipeline
    will be connected in a later phase.
    """

    # ---------------------------------------------------------
    # Validate filename
    # ---------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was provided.",
        )

    # ---------------------------------------------------------
    # Validate extension
    # ---------------------------------------------------------

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Supported formats: PDF, DOCX, PPTX, TXT."
            ),
        )

    # ---------------------------------------------------------
    # Create upload directory
    # ---------------------------------------------------------

    upload_directory = settings.get_absolute_path(
        settings.upload_dir
    )

    upload_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------
    # Generate unique document ID
    # ---------------------------------------------------------

    document_id = str(uuid4())

    stored_filename = (
        f"{document_id}{extension}"
    )

    destination = (
        upload_directory /
        stored_filename
    )

    # ---------------------------------------------------------
    # Read uploaded file
    # ---------------------------------------------------------

    contents = await file.read()

    # ---------------------------------------------------------
    # Validate file size
    # ---------------------------------------------------------

    max_size = (
        settings.max_upload_size_mb
        * 1024
        * 1024
    )

    if len(contents) > max_size:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File is too large. "
                f"Maximum allowed size is "
                f"{settings.max_upload_size_mb} MB."
            ),
        )

    # ---------------------------------------------------------
    # Save file
    # ---------------------------------------------------------

    destination.write_bytes(contents)

    # ---------------------------------------------------------
    # Response
    # ---------------------------------------------------------

    return {
        "success": True,
        "document_id": document_id,
        "filename": file.filename,
        "stored_filename": stored_filename,
        "file_type": extension.replace(".", ""),
        "size": len(contents),
        "message": "Document uploaded successfully.",
    }