# embeddings.py
from typing import Sequence

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Generates vector embeddings for document chunks and
    student queries.

    The model runs locally, so no paid embedding API is required.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        self.model_name = model_name
        self._model = None

    # ---------------------------------------------------------
    # Load model lazily
    # ---------------------------------------------------------

    @property
    def model(self) -> SentenceTransformer:
        """
        Load the embedding model only when it is first needed.
        """

        if self._model is None:
            self._model = SentenceTransformer(
                self.model_name
            )

        return self._model

    # ---------------------------------------------------------
    # Single text
    # ---------------------------------------------------------

    def embed(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding for a single text.
        """

        if not text or not text.strip():
            raise ValueError(
                "Text cannot be empty."
            )

        vector = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return vector.tolist()

    # ---------------------------------------------------------
    # Multiple texts
    # ---------------------------------------------------------

    def embed_many(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """

        if not texts:
            return []

        cleaned_texts = [
            text.strip()
            for text in texts
            if text and text.strip()
        ]

        if not cleaned_texts:
            return []

        vectors = self.model.encode(
            cleaned_texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return vectors.tolist()

    # ---------------------------------------------------------
    # Query embedding
    # ---------------------------------------------------------

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        """
        Generate an embedding for a student's question.

        This uses the same embedding model as the document
        chunks so they can be compared in vector space.
        """

        return self.embed(query)

    # ---------------------------------------------------------
    # Embedding dimension
    # ---------------------------------------------------------

    def dimension(self) -> int:
        """
        Return the dimensionality of the embedding vectors.
        """

        return self.model.get_sentence_embedding_dimension()


# -------------------------------------------------------------
# Default embedding service
# -------------------------------------------------------------

embedding_service = EmbeddingService()