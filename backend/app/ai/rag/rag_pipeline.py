# rag_pipeline.py
from typing import Any
from uuid import uuid4

from app.ai.llm.llm_service import (
    LLMService,
    llm_service,
)
from app.ai.rag.document_loader import (
    DocumentLoader,
    document_loader,
)
from app.ai.rag.embeddings import (
    EmbeddingService,
    embedding_service,
)
from app.ai.rag.retriever import (
    Retriever,
    retriever,
)
from app.ai.rag.text_cleaner import (
    TextCleaner,
    text_cleaner,
)
from app.ai.rag.text_chunker import (
    TextChunk,
    TextChunker,
    text_chunker,
)
from app.ai.rag.vector_store import (
    VectorRecord,
    VectorStore,
    vector_store,
)


class RAGPipeline:
    """
    Complete Retrieval-Augmented Generation pipeline.

    Responsibilities:

    1. Load uploaded documents.
    2. Clean extracted text.
    3. Split text into chunks.
    4. Generate embeddings.
    5. Store chunks and embeddings.
    6. Retrieve relevant chunks for questions.
    7. Send retrieved context to the LLM.
    8. Generate grounded AI Teacher responses.
    """

    def __init__(
        self,
        loader: DocumentLoader | None = None,
        cleaner: TextCleaner | None = None,
        chunker: TextChunker | None = None,
        embeddings: EmbeddingService | None = None,
        store: VectorStore | None = None,
        retriever_instance: Retriever | None = None,
        llm: LLMService | None = None,
    ):
        self.loader = (
            loader
            or document_loader
        )

        self.cleaner = (
            cleaner
            or text_cleaner
        )

        self.chunker = (
            chunker
            or text_chunker
        )

        self.embeddings = (
            embeddings
            or embedding_service
        )

        self.store = (
            store
            or vector_store
        )

        self.retriever = (
            retriever_instance
            or retriever
        )

        self.llm = (
            llm
            or llm_service
        )

    # =========================================================
    # DOCUMENT INGESTION
    # =========================================================

    async def ingest_document(
        self,
        file_path: str,
        document_id: str | None = None,
        student_id: str | None = None,
        extra_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Process a document and add it to the vector store.

        Pipeline:

        File
          ↓
        Load
          ↓
        Clean
          ↓
        Chunk
          ↓
        Embed
          ↓
        Store
        """

        document_id = (
            document_id
            or str(uuid4())
        )

        loaded = self.loader.load(
            file_path
        )

        raw_text = loaded.get(
            "text",
            "",
        )

        if not raw_text.strip():
            raise ValueError(
                "No readable text was found "
                "in the document."
            )

        cleaned_text = self.cleaner.clean(
            raw_text
        )

        if not cleaned_text:
            raise ValueError(
                "Document contains no usable text "
                "after cleaning."
            )

        metadata = {
            **loaded.get(
                "metadata",
                {},
            ),
            **(
                extra_metadata
                or {}
            ),
            "document_id": document_id,
        }

        if student_id:
            metadata["student_id"] = (
                student_id
            )

        chunks = self.chunker.chunk(
            cleaned_text,
            metadata=metadata,
        )

        if not chunks:
            raise ValueError(
                "Unable to create document chunks."
            )

        texts = [
            chunk.text
            for chunk in chunks
        ]

        embeddings = (
            self.embeddings.embed_many(
                texts
            )
        )

        if len(embeddings) != len(chunks):
            raise RuntimeError(
                "Number of embeddings does not "
                "match number of chunks."
            )

        records = []

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):
            record_id = (
                f"{document_id}:"
                f"{chunk.chunk_id}"
            )

            chunk_metadata = {
                **chunk.metadata,
                "document_id": document_id,
            }

            if student_id:
                chunk_metadata[
                    "student_id"
                ] = student_id

            records.append(
                VectorRecord(
                    record_id=record_id,
                    text=chunk.text,
                    embedding=embedding,
                    metadata=chunk_metadata,
                )
            )

        # Remove old chunks when re-ingesting
        # the same document.
        self.store.delete_by_document(
            document_id
        )

        self.store.add_many(
            records
        )

        self.store.save()

        return {
            "document_id": document_id,
            "filename": metadata.get(
                "filename"
            ),
            "character_count": len(
                cleaned_text
            ),
            "chunk_count": len(
                chunks
            ),
            "student_id": student_id,
            "metadata": metadata,
        }

    # =========================================================
    # INGEST MULTIPLE DOCUMENTS
    # =========================================================

    async def ingest_documents(
        self,
        file_paths: list[str],
        student_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Ingest multiple documents.
        """

        results = []

        for file_path in file_paths:
            result = await self.ingest_document(
                file_path=file_path,
                student_id=student_id,
            )

            results.append(result)

        return results

    # =========================================================
    # RETRIEVAL
    # =========================================================

    def retrieve(
        self,
        question: str,
        top_k: int = 5,
        min_score: float = 0.25,
        student_id: str | None = None,
        document_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve relevant educational content.
        """

        metadata_filter = None

        if student_id:
            metadata_filter = {
                "student_id": student_id,
            }

        if document_id:
            metadata_filter = {
                **(
                    metadata_filter
                    or {}
                ),
                "document_id": document_id,
            }

        return self.retriever.retrieve_context(
            query=question,
            top_k=top_k,
            min_score=min_score,
            metadata_filter=metadata_filter,
        )

    # =========================================================
    # ASK AI TEACHER
    # =========================================================

    async def ask(
        self,
        question: str,
        student_id: str | None = None,
        document_id: str | None = None,
        student_level: str = "beginner",
        language: str = "english",
        top_k: int = 5,
        min_score: float = 0.25,
    ) -> dict[str, Any]:
        """
        Ask a question using RAG.

        The retrieved learning material is supplied to the
        LLM so the answer can remain grounded in the student's
        uploaded content.
        """

        if not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        retrieval = self.retrieve(
            question=question,
            top_k=top_k,
            min_score=min_score,
            student_id=student_id,
            document_id=document_id,
        )

        context = retrieval.get(
            "context",
            "",
        )

        answer = await self.llm.answer(
            question=question,
            context=context,
            student_level=student_level,
            language=language,
        )

        return {
            "question": question,
            "answer": answer,
            "sources": retrieval.get(
                "results",
                [],
            ),
            "source_count": retrieval.get(
                "result_count",
                0,
            ),
        }

    # =========================================================
    # EXPLAIN TOPIC
    # =========================================================

    async def explain_topic(
        self,
        topic: str,
        student_id: str | None = None,
        document_id: str | None = None,
        student_level: str = "beginner",
        language: str = "english",
        top_k: int = 5,
    ) -> dict[str, Any]:
        """
        Explain a topic using uploaded learning material.
        """

        retrieval = self.retrieve(
            question=topic,
            top_k=top_k,
            student_id=student_id,
            document_id=document_id,
        )

        context = retrieval.get(
            "context",
            "",
        )

        explanation = await self.llm.explain(
            concept=topic,
            context=context,
            student_level=student_level,
            language=language,
        )

        return {
            "topic": topic,
            "explanation": explanation,
            "sources": retrieval.get(
                "results",
                [],
            ),
            "source_count": retrieval.get(
                "result_count",
                0,
            ),
        }

    # =========================================================
    # DOCUMENT DELETE
    # =========================================================

    def delete_document(
        self,
        document_id: str,
    ) -> int:
        """
        Remove all vector chunks belonging to a document.
        """

        deleted = (
            self.store.delete_by_document(
                document_id
            )
        )

        self.store.save()

        return deleted

    # =========================================================
    # STORE INFORMATION
    # =========================================================

    def get_store_info(
        self,
    ) -> dict[str, Any]:
        """
        Return information about the current vector store.
        """

        return {
            "vector_count": self.store.count(),
            "embedding_dimension": (
                self.embeddings.dimension()
            ),
        }


# =============================================================
# DEFAULT PIPELINE
# =============================================================

rag_pipeline = RAGPipeline()