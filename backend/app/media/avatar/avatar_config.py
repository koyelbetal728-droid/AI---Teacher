# avatar_config.py
"""
Avatar configuration for the AI Teacher.

This module contains the default configuration and helper
functions used by the avatar service.

The configuration is provider-independent so the project
can start with a simple local avatar and later integrate
more advanced avatar/video providers.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class AvatarSettings:
    """
    Configuration for the AI Teacher avatar.
    """

    name: str = "AI Teacher"

    # Visual appearance
    style: str = "friendly"
    gender: str = "neutral"

    # Language and voice
    language: str = "English"
    voice_id: Optional[str] = None

    # Local avatar image
    image_path: Optional[str] = None

    # Video generation
    video_enabled: bool = False

    # Animation settings
    animation_enabled: bool = True
    speaking_animation: bool = True

    # Display settings
    background: str = "transparent"
    width: int = 512
    height: int = 512


def get_default_avatar_settings() -> AvatarSettings:
    """
    Return the default avatar configuration.

    Environment variables can override the most common
    configuration values.
    """

    return AvatarSettings(
        name=os.getenv(
            "AI_TEACHER_AVATAR_NAME",
            "AI Teacher",
        ),
        style=os.getenv(
            "AI_TEACHER_AVATAR_STYLE",
            "friendly",
        ),
        gender=os.getenv(
            "AI_TEACHER_AVATAR_GENDER",
            "neutral",
        ),
        language=os.getenv(
            "AI_TEACHER_AVATAR_LANGUAGE",
            "English",
        ),
        voice_id=os.getenv(
            "AI_TEACHER_AVATAR_VOICE_ID"
        ),
        image_path=os.getenv(
            "AI_TEACHER_AVATAR_IMAGE"
        ),
        video_enabled=_env_bool(
            "AI_TEACHER_AVATAR_VIDEO",
            False,
        ),
        animation_enabled=_env_bool(
            "AI_TEACHER_AVATAR_ANIMATION",
            True,
        ),
        speaking_animation=_env_bool(
            "AI_TEACHER_AVATAR_SPEAKING_ANIMATION",
            True,
        ),
        background=os.getenv(
            "AI_TEACHER_AVATAR_BACKGROUND",
            "transparent",
        ),
        width=_env_int(
            "AI_TEACHER_AVATAR_WIDTH",
            512,
        ),
        height=_env_int(
            "AI_TEACHER_AVATAR_HEIGHT",
            512,
        ),
    )


def _env_bool(
    name: str,
    default: bool,
) -> bool:
    """
    Read a boolean value from an environment variable.
    """

    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
        "enabled",
    }


def _env_int(
    name: str,
    default: int,
) -> int:
    """
    Read an integer from an environment variable safely.
    """

    value = os.getenv(name)

    if value is None:
        return default

    try:
        parsed = int(value)

        if parsed <= 0:
            return default

        return parsed

    except ValueError:
        return default


def validate_avatar_settings(
    settings: AvatarSettings,
) -> None:
    """
    Validate avatar configuration.

    Raises
    ------
    ValueError
        If an invalid configuration is supplied.
    """

    if not settings.name.strip():
        raise ValueError(
            "Avatar name cannot be empty."
        )

    if not settings.style.strip():
        raise ValueError(
            "Avatar style cannot be empty."
        )

    if not settings.language.strip():
        raise ValueError(
            "Avatar language cannot be empty."
        )

    if settings.width <= 0:
        raise ValueError(
            "Avatar width must be greater than zero."
        )

    if settings.height <= 0:
        raise ValueError(
            "Avatar height must be greater than zero."
        )

    if settings.background.strip() == "":
        raise ValueError(
            "Avatar background cannot be empty."
        )


def avatar_settings_to_dict(
    settings: AvatarSettings,
) -> Dict[str, Any]:
    """
    Convert avatar settings into a dictionary.
    """

    validate_avatar_settings(settings)

    return asdict(settings)


def create_avatar_settings(
    **overrides: Any,
) -> AvatarSettings:
    """
    Create avatar settings with optional overrides.

    Example:

        create_avatar_settings(
            name="Professor Nova",
            language="English",
            style="professional",
        )
    """

    settings = get_default_avatar_settings()

    allowed_fields = {
        "name",
        "style",
        "gender",
        "language",
        "voice_id",
        "image_path",
        "video_enabled",
        "animation_enabled",
        "speaking_animation",
        "background",
        "width",
        "height",
    }

    for key, value in overrides.items():
        if key in allowed_fields:
            setattr(settings, key, value)

    validate_avatar_settings(settings)

    return settings


# Shared default configuration.
avatar_settings = get_default_avatar_settings()

# Validate configuration when the module is initialized.
validate_avatar_settings(avatar_settings)