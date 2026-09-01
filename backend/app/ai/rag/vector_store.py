# vector_store.py
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
from typing import Any


@dataclass
class VectorRecord:
    """
    A single vector stored in the local vector database.
    """

    record_id: str
    text: str
    embedding: list[float]
    metadata: dict[str, Any]


class VectorStore:
    """
    Simple local vector store for the AI Teacher RAG system.

    It stores embeddings and metadata in a JSON file and uses
    cosine similarity for semantic search.

    This implementation is intentionally simple and free:
    no paid vector database is required.
    """

    def __init__(
        self,
        storage_path: str | Path = "data/vector_store/vectors.json",
    ):
        self.storage_path = Path(storage_path)
        self.records: list[VectorRecord] = []

        self._ensure_storage_directory()
        self.load()

    # ---------------------------------------------------------
    # Storage setup
    # ---------------------------------------------------------

    def _ensure_storage_directory(self) -> None:
        """
        Create the vector-store directory if necessary.
        """

        self.storage_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ---------------------------------------------------------
    # Add one record
    # ---------------------------------------------------------

    def add(
        self,
        record_id: str,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> VectorRecord:
        """
        Add a single vector record.
        """

        if not record_id:
            raise ValueError(
                "record_id cannot be empty."
            )

        if not text or not text.strip():
            raise ValueError(
                "text cannot be empty."
            )

        if not embedding:
            raise ValueError(
                "embedding cannot be empty."
            )

        existing_index = self._find_index(
            record_id
        )

        record = VectorRecord(
            record_id=record_id,
            text=text.strip(),
            embedding=embedding,
            metadata=metadata or {},
        )

        if existing_index is not None:
            self.records[existing_index] = record
        else:
            self.records.append(record)

        return record

    # ---------------------------------------------------------
    # Add multiple records
    # ---------------------------------------------------------

    def add_many(
        self,
        records: list[VectorRecord],
    ) -> None:
        """
        Add multiple vector records.
        """

        for record in records:
            self.add(
                record_id=record.record_id,
                text=record.text,
                embedding=record.embedding,
                metadata=record.metadata,
            )

    # ---------------------------------------------------------
    # Delete record
    # ---------------------------------------------------------

    def delete(
        self,
        record_id: str,
    ) -> bool:
        """
        Delete a record by ID.
        """

        index = self._find_index(
            record_id
        )

        if index is None:
            return False

        del self.records[index]

        return True

    # ---------------------------------------------------------
    # Delete document
    # ---------------------------------------------------------

    def delete_by_document(
        self,
        document_id: str,
    ) -> int:
        """
        Delete all chunks belonging to a document.
        """

        original_count = len(
            self.records
        )

        self.records = [
            record
            for record in self.records
            if record.metadata.get(
                "document_id"
            )
            != document_id
        ]

        return (
            original_count
            - len(self.records)
        )

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        min_score: float = 0.0,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Find the most semantically similar records.
        """

        if not query_embedding:
            raise ValueError(
                "query_embedding cannot be empty."
            )

        if top_k <= 0:
            return []

        results = []

        for record in self.records:
            if metadata_filter:
                if not self._matches_filter(
                    record.metadata,
                    metadata_filter,
                ):
                    continue

            score = self.cosine_similarity(
                query_embedding,
                record.embedding,
            )

            if score < min_score:
                continue

            results.append(
                {
                    "record_id": record.record_id,
                    "text": record.text,
                    "metadata": record.metadata,
                    "score": score,
                }
            )

        results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return results[:top_k]

    # ---------------------------------------------------------
    # Cosine similarity
    # ---------------------------------------------------------

    @staticmethod
    def cosine_similarity(
        vector_a: list[float],
        vector_b: list[float],
    ) -> float:
        """
        Calculate cosine similarity between two vectors.
        """

        if len(vector_a) != len(vector_b):
            raise ValueError(
                "Vectors must have the same dimension."
            )

        dot_product = sum(
            a * b
            for a, b in zip(
                vector_a,
                vector_b,
            )
        )

        magnitude_a = math.sqrt(
            sum(
                value * value
                for value in vector_a
            )
        )

        magnitude_b = math.sqrt(
            sum(
                value * value
                for value in vector_b
            )
        )

        if (
            magnitude_a == 0
            or magnitude_b == 0
        ):
            return 0.0

        return (
            dot_product
            / (magnitude_a * magnitude_b)
        )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    def save(self) -> None:
        """
        Persist all vectors to disk.
        """

        self._ensure_storage_directory()

        data = [
            asdict(record)
            for record in self.records
        ]

        self.storage_path.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    # ---------------------------------------------------------
    # Load
    # ---------------------------------------------------------

    def load(self) -> None:
        """
        Load vectors from disk if the storage file exists.
        """

        if not self.storage_path.exists():
            self.records = []
            return

        try:
            data = json.loads(
                self.storage_path.read_text(
                    encoding="utf-8"
                )
            )

        except (
            json.JSONDecodeError,
            OSError,
        ):
            self.records = []
            return

        if not isinstance(data, list):
            self.records = []
            return

        self.records = []

        for item in data:
            try:
                self.records.append(
                    VectorRecord(
                        record_id=item[
                            "record_id"
                        ],
                        text=item["text"],
                        embedding=item[
                            "embedding"
                        ],
                        metadata=item.get(
                            "metadata",
                            {},
                        ),
                    )
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                continue

    # ---------------------------------------------------------
    # Count
    # ---------------------------------------------------------

    def count(self) -> int:
        """
        Return the number of stored vectors.
        """

        return len(self.records)

    # ---------------------------------------------------------
    # Clear
    # ---------------------------------------------------------

    def clear(self) -> None:
        """
        Remove all vectors.
        """

        self.records = []

        self.save()

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------

    def _find_index(
        self,
        record_id: str,
    ) -> int | None:
        """
        Find a record's list index.
        """

        for index, record in enumerate(
            self.records
        ):
            if record.record_id == record_id:
                return index

        return None

    @staticmethod
    def _matches_filter(
        metadata: dict[str, Any],
        metadata_filter: dict[str, Any],
    ) -> bool:
        """
        Check whether metadata satisfies all requested filters.
        """

        for key, expected_value in metadata_filter.items():
            if metadata.get(key) != expected_value:
                return False

        return True


# -------------------------------------------------------------
# Default vector store
# -------------------------------------------------------------

vector_store = VectorStore(
    storage_path="data/vector_store/vectors.json"
)