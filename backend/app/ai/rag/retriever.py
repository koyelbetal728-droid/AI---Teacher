# retriever.py
from typing import Any

from app.ai.rag.embeddings import (
    EmbeddingService,
    embedding_service,
)
from app.ai.rag.vector_store import (
    VectorStore,
    vector_store,
)


class Retriever:
    """
    Retrieves the most relevant pieces of a student's
    uploaded learning material for a given question.
    """

    def __init__(
        self,
        embedding_service_instance: EmbeddingService | None = None,
        vector_store_instance: VectorStore | None = None,
    ):
        self.embedding_service = (
            embedding_service_instance
            or embedding_service
        )

        self.vector_store = (
            vector_store_instance
            or vector_store
        )

    # ---------------------------------------------------------
    # Retrieve
    # ---------------------------------------------------------

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.25,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve the most relevant document chunks.
        """

        if not query or not query.strip():
            return []

        query_embedding = (
            self.embedding_service.embed_query(
                query.strip()
            )
        )

        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            min_score=min_score,
            metadata_filter=metadata_filter,
        )

        return results

    # ---------------------------------------------------------
    # Retrieve by document
    # ---------------------------------------------------------

    def retrieve_from_document(
        self,
        query: str,
        document_id: str,
        top_k: int = 5,
        min_score: float = 0.25,
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant chunks only from a particular document.
        """

        return self.retrieve(
            query=query,
            top_k=top_k,
            min_score=min_score,
            metadata_filter={
                "document_id": document_id,
            },
        )

    # ---------------------------------------------------------
    # Retrieve by student
    # ---------------------------------------------------------

    def retrieve_for_student(
        self,
        query: str,
        student_id: str,
        top_k: int = 5,
        min_score: float = 0.25,
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant chunks belonging to a student's
        uploaded learning materials.
        """

        return self.retrieve(
            query=query,
            top_k=top_k,
            min_score=min_score,
            metadata_filter={
                "student_id": student_id,
            },
        )

    # ---------------------------------------------------------
    # Build context
    # ---------------------------------------------------------

    def build_context(
        self,
        results: list[dict[str, Any]],
    ) -> str:
        """
        Convert retrieved chunks into context that can be
        supplied to the LLM.
        """

        if not results:
            return ""

        context_parts = []

        for index, result in enumerate(
            results,
            start=1,
        ):
            metadata = result.get(
                "metadata",
                {},
            )

            filename = metadata.get(
                "filename",
                "Unknown document",
            )

            score = result.get(
                "score",
                0.0,
            )

            text = result.get(
                "text",
                "",
            ).strip()

            if not text:
                continue

            context_parts.append(
                f"""
--- Source {index} ---
Document: {filename}
Relevance: {score:.3f}

{text}
""".strip()
            )

        return "\n\n".join(
            context_parts
        )

    # ---------------------------------------------------------
    # Retrieve + context
    # ---------------------------------------------------------

    def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.25,
        metadata_filter: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve relevant chunks and return a ready-to-use
        context object.
        """

        results = self.retrieve(
            query=query,
            top_k=top_k,
            min_score=min_score,
            metadata_filter=metadata_filter,
        )

        return {
            "query": query,
            "results": results,
            "context": self.build_context(
                results
            ),
            "result_count": len(results),
        }

    # ---------------------------------------------------------
    # Search with relaxed threshold
    # ---------------------------------------------------------

    def retrieve_with_fallback(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.25,
        fallback_score: float = 0.10,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Try normal retrieval first.

        If nothing relevant is found, retry with a lower
        similarity threshold.
        """

        results = self.retrieve(
            query=query,
            top_k=top_k,
            min_score=min_score,
            metadata_filter=metadata_filter,
        )

        if results:
            return results

        return self.retrieve(
            query=query,
            top_k=top_k,
            min_score=fallback_score,
            metadata_filter=metadata_filter,
        )


# -------------------------------------------------------------
# Default retriever
# -------------------------------------------------------------

retriever = Retriever()