"""
Language utilities for the AI Teacher backend.

This module provides helpers for:
- Language normalization
- Language detection
- Supported language validation
- Language display names
- Speech/AI language mapping
"""

from __future__ import annotations

from typing import Optional


# ---------------------------------------------------------------------------
# Supported languages
# ---------------------------------------------------------------------------

SUPPORTED_LANGUAGES = {
    "en": {
        "name": "English",
        "native_name": "English",
        "speech_code": "en",
    },
    "bn": {
        "name": "Bengali",
        "native_name": "বাংলা",
        "speech_code": "bn",
    },
    "hi": {
        "name": "Hindi",
        "native_name": "हिन्दी",
        "speech_code": "hi",
    },
}


LANGUAGE_ALIASES = {
    "english": "en",
    "eng": "en",
    "en-us": "en",
    "en_us": "en",
    "en-gb": "en",
    "en_gb": "en",

    "bengali": "bn",
    "bangla": "bn",
    "ben": "bn",
    "bn-bd": "bn",
    "bn_bd": "bn",
    "bn-in": "bn",
    "bn_in": "bn",

    "hindi": "hi",
    "hin": "hi",
    "hi-in": "hi",
    "hi_in": "hi",
}


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def normalize_language(
    language: Optional[str],
    default: str = "en",
) -> str:
    """
    Normalize a language name or language code.

    Examples:
        "English" -> "en"
        "Bengali" -> "bn"
        "bn-BD" -> "bn"
    """

    if not language:
        return default

    value = str(language).strip().lower()

    if value in SUPPORTED_LANGUAGES:
        return value

    if value in LANGUAGE_ALIASES:
        return LANGUAGE_ALIASES[value]

    # Handle regional codes such as en-US or bn-IN.
    base_code = value.replace("_", "-").split("-")[0]

    if base_code in SUPPORTED_LANGUAGES:
        return base_code

    if base_code in LANGUAGE_ALIASES:
        return LANGUAGE_ALIASES[base_code]

    return default


def is_supported_language(
    language: Optional[str],
) -> bool:
    """
    Check whether a language is supported.
    """

    if not language:
        return False

    value = str(language).strip().lower()

    if value in SUPPORTED_LANGUAGES:
        return True

    if value in LANGUAGE_ALIASES:
        return True

    base_code = value.replace("_", "-").split("-")[0]

    return base_code in SUPPORTED_LANGUAGES


# ---------------------------------------------------------------------------
# Language information
# ---------------------------------------------------------------------------

def get_language_name(
    language: Optional[str],
) -> str:
    """
    Return the English display name of a language.
    """

    code = normalize_language(language)

    return SUPPORTED_LANGUAGES[code]["name"]


def get_native_language_name(
    language: Optional[str],
) -> str:
    """
    Return the language's native display name.
    """

    code = normalize_language(language)

    return SUPPORTED_LANGUAGES[code]["native_name"]


def get_speech_language_code(
    language: Optional[str],
) -> str:
    """
    Return the language code used by speech services.
    """

    code = normalize_language(language)

    return SUPPORTED_LANGUAGES[code]["speech_code"]


def get_supported_languages() -> list[dict[str, str]]:
    """
    Return information about all supported languages.
    """

    return [
        {
            "code": code,
            "name": info["name"],
            "native_name": info["native_name"],
            "speech_code": info["speech_code"],
        }
        for code, info in SUPPORTED_LANGUAGES.items()
    ]


# ---------------------------------------------------------------------------
# Text language helpers
# ---------------------------------------------------------------------------

def contains_bengali(
    text: str,
) -> bool:
    """
    Check whether text contains Bengali Unicode characters.
    """

    if not text:
        return False

    return any(
        "\u0980" <= character <= "\u09ff"
        for character in text
    )


def contains_devanagari(
    text: str,
) -> bool:
    """
    Check whether text contains Devanagari characters.
    """

    if not text:
        return False

    return any(
        "\u0900" <= character <= "\u097f"
        for character in text
    )


def contains_latin(
    text: str,
) -> bool:
    """
    Check whether text contains basic Latin alphabet characters.
    """

    if not text:
        return False

    return any(
        ("a" <= character.lower() <= "z")
        for character in text
    )


def detect_script(
    text: str,
) -> str:
    """
    Detect the dominant script in a text string.

    Returns:
        "bengali"
        "devanagari"
        "latin"
        "unknown"
    """

    if not text or not text.strip():
        return "unknown"

    bengali_count = sum(
        1
        for character in text
        if "\u0980" <= character <= "\u09ff"
    )

    devanagari_count = sum(
        1
        for character in text
        if "\u0900" <= character <= "\u097f"
    )

    latin_count = sum(
        1
        for character in text
        if "a" <= character.lower() <= "z"
    )

    counts = {
        "bengali": bengali_count,
        "devanagari": devanagari_count,
        "latin": latin_count,
    }

    dominant_script = max(
        counts,
        key=counts.get,
    )

    if counts[dominant_script] == 0:
        return "unknown"

    return dominant_script


def detect_language(
    text: str,
    default: str = "en",
) -> str:
    """
    Perform lightweight language detection based on Unicode scripts.

    This is intentionally simple and local.
    For mixed-language text, the dominant script is used.
    """

    script = detect_script(text)

    if script == "bengali":
        return "bn"

    if script == "devanagari":
        return "hi"

    if script == "latin":
        return "en"

    return default


# ---------------------------------------------------------------------------
# Language formatting
# ---------------------------------------------------------------------------

def language_to_prompt_instruction(
    language: Optional[str],
) -> str:
    """
    Create a short instruction for AI prompts.
    """

    code = normalize_language(language)
    name = get_language_name(code)

    return (
        f"Respond in {name}. "
        f"Use clear, student-friendly language."
    )


def language_to_speech_instruction(
    language: Optional[str],
) -> str:
    """
    Create a short instruction for speech generation.
    """

    code = normalize_language(language)
    name = get_language_name(code)

    return (
        f"Generate speech in {name} "
        f"using natural pronunciation."
    )


def translate_language_name(
    language: Optional[str],
    target_language: Optional[str] = "en",
) -> str:
    """
    Return a simple localized language name.

    This does not perform general translation; it only provides
    known native names for the supported languages.
    """

    source_code = normalize_language(language)
    target_code = normalize_language(target_language)

    if target_code == "en":
        return SUPPORTED_LANGUAGES[source_code]["name"]

    if target_code == source_code:
        return SUPPORTED_LANGUAGES[source_code]["native_name"]

    # For unsupported localized names, return the English name.
    return SUPPORTED_LANGUAGES[source_code]["name"]


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_language(
    language: Optional[str],
) -> str:
    """
    Validate and normalize a language.

    Raises:
        ValueError: If the language is not supported.
    """

    if not language:
        raise ValueError("Language is required.")

    if not is_supported_language(language):
        supported = ", ".join(
            SUPPORTED_LANGUAGES.keys()
        )

        raise ValueError(
            f"Unsupported language '{language}'. "
            f"Supported languages: {supported}"
        )

    return normalize_language(language)