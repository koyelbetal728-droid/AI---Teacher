# text_cleaner.py
import re
import unicodedata


class TextCleaner:
    """
    Cleans extracted document text before it enters the
    chunking and embedding stages of the RAG pipeline.

    The cleaner removes extraction noise while preserving
    meaningful educational content.
    """

    # ---------------------------------------------------------
    # Main cleaning pipeline
    # ---------------------------------------------------------

    def clean(self, text: str) -> str:
        """
        Apply all text-cleaning operations.
        """

        if not text:
            return ""

        text = self.normalize_unicode(text)
        text = self.normalize_line_endings(text)
        text = self.remove_null_characters(text)
        text = self.remove_excessive_whitespace(text)
        text = self.fix_broken_lines(text)
        text = self.remove_repeated_page_markers(text)

        return text.strip()

    # ---------------------------------------------------------
    # Unicode normalization
    # ---------------------------------------------------------

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """
        Normalize Unicode characters while preserving
        non-English languages.
        """

        return unicodedata.normalize(
            "NFKC",
            text,
        )

    # ---------------------------------------------------------
    # Line endings
    # ---------------------------------------------------------

    @staticmethod
    def normalize_line_endings(text: str) -> str:
        """
        Convert Windows/Mac line endings to Unix style.
        """

        text = text.replace(
            "\r\n",
            "\n",
        )

        text = text.replace(
            "\r",
            "\n",
        )

        return text

    # ---------------------------------------------------------
    # Remove null characters
    # ---------------------------------------------------------

    @staticmethod
    def remove_null_characters(
        text: str,
    ) -> str:
        """
        Remove null/control characters that sometimes appear
        after PDF extraction.
        """

        return text.replace(
            "\x00",
            "",
        )

    # ---------------------------------------------------------
    # Whitespace normalization
    # ---------------------------------------------------------

    @staticmethod
    def remove_excessive_whitespace(
        text: str,
    ) -> str:
        """
        Clean unnecessary spaces and excessive blank lines.
        """

        # Replace tabs with spaces.
        text = text.replace(
            "\t",
            " ",
        )

        # Remove trailing spaces from each line.
        text = re.sub(
            r"[ \t]+$",
            "",
            text,
            flags=re.MULTILINE,
        )

        # Avoid very large whitespace sequences.
        text = re.sub(
            r"[ ]{2,}",
            " ",
            text,
        )

        # Keep a maximum of two consecutive blank lines.
        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text

    # ---------------------------------------------------------
    # Broken line repair
    # ---------------------------------------------------------

    @staticmethod
    def fix_broken_lines(
        text: str,
    ) -> str:
        """
        Join lines that were broken in the middle of a sentence.

        Example:

            Artificial intelligence is a field of
            computer science.

        becomes:

            Artificial intelligence is a field of computer science.
        """

        lines = text.split("\n")

        if not lines:
            return text

        result = []
        buffer = ""

        for line in lines:
            line = line.strip()

            if not line:
                if buffer:
                    result.append(
                        buffer.strip()
                    )
                    buffer = ""

                result.append("")
                continue

            if not buffer:
                buffer = line
                continue

            # Don't join obvious headings, bullets, numbered
            # lists, or page markers.
            if self_is_new_block(line):
                result.append(
                    buffer.strip()
                )
                buffer = line
                continue

            # If the previous line appears to continue naturally,
            # join it with the current line.
            if (
                buffer.endswith(
                    (
                        ".",
                        "?",
                        "!",
                        ":",
                        ";",
                        ")",
                        "]",
                        "}",
                    )
                )
            ):
                result.append(
                    buffer.strip()
                )
                buffer = line
            else:
                buffer += " " + line

        if buffer:
            result.append(
                buffer.strip()
            )

        return "\n".join(result)


# -------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------

def self_is_new_block(line: str) -> bool:
    """
    Detect whether a line looks like the beginning of a
    new logical block.
    """

    stripped = line.strip()

    if not stripped:
        return True

    # Existing page marker from PDF loader.
    if re.match(
        r"^\[Page\s+\d+\]",
        stripped,
        flags=re.IGNORECASE,
    ):
        return True

    # Markdown headings.
    if re.match(
        r"^#{1,6}\s+",
        stripped,
    ):
        return True

    # Bullet lists.
    if re.match(
        r"^[-*•]\s+",
        stripped,
    ):
        return True

    # Numbered lists.
    if re.match(
        r"^\d+[\.\)]\s+",
        stripped,
    ):
        return True

    # Lettered lists.
    if re.match(
        r"^[A-Za-z][\.\)]\s+",
        stripped,
    ):
        return True

    return False


# -------------------------------------------------------------
# Default cleaner
# -------------------------------------------------------------

text_cleaner = TextCleaner()