# text_chunker.py
from dataclasses import dataclass
import re


@dataclass
class TextChunk:
    """
    Represents one searchable piece of a document.
    """

    text: str
    chunk_id: int
    start_index: int
    end_index: int
    metadata: dict


class TextChunker:
    """
    Splits cleaned educational documents into overlapping
    chunks suitable for embedding and vector retrieval.
    """

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
    ):
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than 0."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative."
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    # ---------------------------------------------------------
    # Main chunking method
    # ---------------------------------------------------------

    def chunk(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[TextChunk]:
        """
        Split text into overlapping chunks.

        The chunker first tries to preserve paragraphs and
        sentences before falling back to character boundaries.
        """

        if not text or not text.strip():
            return []

        metadata = metadata or {}

        text = text.strip()

        paragraphs = self._split_paragraphs(text)

        chunks: list[TextChunk] = []
        current_text = ""
        current_start = 0

        search_position = 0

        for paragraph in paragraphs:
            paragraph = paragraph.strip()

            if not paragraph:
                continue

            paragraph_start = text.find(
                paragraph,
                search_position,
            )

            if paragraph_start == -1:
                paragraph_start = search_position

            search_position = (
                paragraph_start + len(paragraph)
            )

            if len(paragraph) > self.chunk_size:
                if current_text:
                    chunks.append(
                        self._create_chunk(
                            text=current_text,
                            chunk_id=len(chunks),
                            start_index=current_start,
                            original_text=text,
                            metadata=metadata,
                        )
                    )

                    current_text = ""

                large_chunks = self._split_large_text(
                    paragraph,
                    paragraph_start,
                )

                for item_text, item_start in large_chunks:
                    chunks.append(
                        self._create_chunk(
                            text=item_text,
                            chunk_id=len(chunks),
                            start_index=item_start,
                            original_text=text,
                            metadata=metadata,
                        )
                    )

                continue

            candidate = (
                f"{current_text}\n\n{paragraph}"
                if current_text
                else paragraph
            )

            if len(candidate) <= self.chunk_size:
                if not current_text:
                    current_start = paragraph_start

                current_text = candidate

            else:
                if current_text:
                    chunks.append(
                        self._create_chunk(
                            text=current_text,
                            chunk_id=len(chunks),
                            start_index=current_start,
                            original_text=text,
                            metadata=metadata,
                        )
                    )

                overlap = self._get_overlap(
                    current_text
                )

                current_text = (
                    f"{overlap}\n\n{paragraph}"
                    if overlap
                    else paragraph
                )

                current_start = max(
                    0,
                    paragraph_start
                    - len(overlap),
                )

        if current_text:
            chunks.append(
                self._create_chunk(
                    text=current_text,
                    chunk_id=len(chunks),
                    start_index=current_start,
                    original_text=text,
                    metadata=metadata,
                )
            )

        return chunks

    # ---------------------------------------------------------
    # Paragraph splitting
    # ---------------------------------------------------------

    @staticmethod
    def _split_paragraphs(
        text: str,
    ) -> list[str]:
        """
        Split text using blank lines while preserving normal
        line breaks inside a paragraph.
        """

        return re.split(
            r"\n\s*\n+",
            text,
        )

    # ---------------------------------------------------------
    # Large paragraph splitting
    # ---------------------------------------------------------

    def _split_large_text(
        self,
        text: str,
        absolute_start: int,
    ) -> list[tuple[str, int]]:
        """
        Split a paragraph that is larger than chunk_size.

        Sentence boundaries are preferred whenever possible.
        """

        sentences = self._split_sentences(
            text
        )

        results = []

        current = ""
        current_start = absolute_start
        local_position = 0

        for sentence in sentences:
            sentence = sentence.strip()

            if not sentence:
                continue

            sentence_position = text.find(
                sentence,
                local_position,
            )

            if sentence_position == -1:
                sentence_position = local_position

            local_position = (
                sentence_position
                + len(sentence)
            )

            candidate = (
                f"{current} {sentence}"
                if current
                else sentence
            )

            if (
                current
                and len(candidate)
                > self.chunk_size
            ):
                results.append(
                    (
                        current.strip(),
                        current_start,
                    )
                )

                overlap = self._get_overlap(
                    current
                )

                current = (
                    f"{overlap} {sentence}"
                    if overlap
                    else sentence
                )

                current_start = max(
                    absolute_start,
                    sentence_position
                    - len(overlap),
                )

            else:
                if not current:
                    current_start = (
                        absolute_start
                        + sentence_position
                    )

                current = candidate

        if current.strip():
            results.append(
                (
                    current.strip(),
                    current_start,
                )
            )

        # Extremely long single sentence fallback.
        final_results = []

        for item_text, item_start in results:
            if len(item_text) <= self.chunk_size:
                final_results.append(
                    (
                        item_text,
                        item_start,
                    )
                )
                continue

            final_results.extend(
                self._split_by_character(
                    item_text,
                    item_start,
                )
            )

        return final_results

    # ---------------------------------------------------------
    # Sentence splitting
    # ---------------------------------------------------------

    @staticmethod
    def _split_sentences(
        text: str,
    ) -> list[str]:
        """
        Basic sentence segmentation.

        Supports common English punctuation and keeps
        the implementation dependency-free.
        """

        parts = re.split(
            r"(?<=[.!?।])\s+",
            text,
        )

        return [
            part.strip()
            for part in parts
            if part.strip()
        ]

    # ---------------------------------------------------------
    # Character fallback
    # ---------------------------------------------------------

    def _split_by_character(
        self,
        text: str,
        start_index: int,
    ) -> list[tuple[str, int]]:
        """
        Final fallback for very long sections where no useful
        sentence boundary exists.
        """

        results = []

        start = 0

        while start < len(text):
            end = min(
                start + self.chunk_size,
                len(text),
            )

            piece = text[
                start:end
            ].strip()

            if piece:
                results.append(
                    (
                        piece,
                        start_index + start,
                    )
                )

            if end >= len(text):
                break

            start = max(
                start + 1,
                end - self.chunk_overlap,
            )

        return results

    # ---------------------------------------------------------
    # Overlap
    # ---------------------------------------------------------

    def _get_overlap(
        self,
        text: str,
    ) -> str:
        """
        Return the last chunk_overlap characters from a chunk.

        Tries to start at a word boundary.
        """

        if not text:
            return ""

        if len(text) <= self.chunk_overlap:
            return text.strip()

        overlap = text[
            -self.chunk_overlap:
        :]

        # Avoid starting halfway through a word.
        first_space = overlap.find(" ")

        if (
            first_space != -1
            and first_space < len(overlap) // 2
        ):
            overlap = overlap[
                first_space + 1:
            ]

        return overlap.strip()

    # ---------------------------------------------------------
    # Create chunk object
    # ---------------------------------------------------------

    @staticmethod
    def _create_chunk(
        text: str,
        chunk_id: int,
        start_index: int,
        original_text: str,
        metadata: dict,
    ) -> TextChunk:
        """
        Create a TextChunk with metadata.
        """

        text = text.strip()

        end_index = min(
            start_index + len(text),
            len(original_text),
        )

        chunk_metadata = {
            **metadata,
            "chunk_id": chunk_id,
            "start_index": start_index,
            "end_index": end_index,
            "character_count": len(text),
        }

        return TextChunk(
            text=text,
            chunk_id=chunk_id,
            start_index=start_index,
            end_index=end_index,
            metadata=chunk_metadata,
        )


# -------------------------------------------------------------
# Default chunker
# -------------------------------------------------------------

text_chunker = TextChunker(
    chunk_size=800,
    chunk_overlap=120,
)