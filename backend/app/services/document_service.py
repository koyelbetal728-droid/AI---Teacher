# document_service.py
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.models.document import Document


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".txt",
}


class DocumentService:
    """
    Handles document upload, storage, and document records.

    The actual text extraction, chunking, embedding, and
    vector indexing will be handled by the RAG pipeline.
    """

    def __init__(self, db: Session):
        self.db = db

    async def save_uploaded_document(
        self,
        file: UploadFile,
    ) -> Document:
        """
        Save an uploaded educational document and create
        its database record.
        """

        if not file.filename:
            raise ValueError("Filename is required.")

        extension = Path(
            file.filename
        ).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError(
                "Unsupported file type. "
                "Supported formats: PDF, DOCX, PPTX, TXT."
            )

        contents = await file.read()

        max_size = (
            settings.max_upload_size_mb
            * 1024
            * 1024
        )

        if len(contents) > max_size:
            raise ValueError(
                f"File exceeds the maximum size of "
                f"{settings.max_upload_size_mb} MB."
            )

        upload_directory = settings.get_absolute_path(
            settings.upload_dir
        )

        upload_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Generate a unique identifier without exposing
        # the original filename as the stored filename.
        from uuid import uuid4

        document_id = str(uuid4())

        stored_filename = (
            f"{document_id}{extension}"
        )

        file_path = (
            upload_directory /
            stored_filename
        )

        file_path.write_bytes(contents)

        document = Document(
            document_id=document_id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_type=extension.replace(".", ""),
            file_size=len(contents),
            file_path=str(file_path),
            status="uploaded",
        )

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        return document

    def get_document(
        self,
        document_id: str,
    ) -> Document | None:
        """
        Get a document using its public document ID.
        """

        return (
            self.db.query(Document)
            .filter(
                Document.document_id == document_id
            )
            .first()
        )

    def list_documents(
        self,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Document]:
        """
        Return uploaded documents with pagination.
        """

        return (
            self.db.query(Document)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_status(
        self,
        document_id: str,
        status: str,
        error_message: str | None = None,
    ) -> Document | None:
        """
        Update the processing status of a document.
        """

        document = self.get_document(
            document_id
        )

        if document is None:
            return None

        document.status = status
        document.error_message = error_message

        self.db.commit()
        self.db.refresh(document)

        return document

    def update_processing_result(
        self,
        document_id: str,
        extracted_text: str,
        chunk_count: int,
    ) -> Document | None:
        """
        Store the result of document processing.
        """

        document = self.get_document(
            document_id
        )

        if document is None:
            return None

        document.extracted_text = extracted_text
        document.chunk_count = chunk_count
        document.status = "processed"
        document.error_message = None

        self.db.commit()
        self.db.refresh(document)

        return document

    def delete_document(
        self,
        document_id: str,
    ) -> bool:
        """
        Delete a document database record and its stored file.
        """

        document = self.get_document(
            document_id
        )

        if document is None:
            return False

        file_path = Path(
            document.file_path
        )

        if file_path.exists():
            file_path.unlink()

        self.db.delete(document)
        self.db.commit()

        return True


def get_document_service(
    db: Session,
) -> DocumentService:
    """
    Create a DocumentService instance.
    """

    return DocumentService(db)