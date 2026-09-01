# avatar_service.py
"""
Avatar service for the AI Teacher.

This module manages the AI teacher avatar layer.

The first implementation keeps the avatar system provider-
independent. It can return avatar configuration and prepare
teacher speech/video data without requiring a paid avatar API.

A real avatar/video provider can be integrated later without
changing the rest of the application.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class AvatarConfig:
    """
    Configuration describing the AI Teacher avatar.
    """

    name: str = "AI Teacher"
    gender: str = "neutral"
    style: str = "friendly"
    language: str = "English"
    voice_id: Optional[str] = None
    image_path: Optional[str] = None
    video_enabled: bool = False


class AvatarService:
    """
    Provider-independent avatar service.

    The service is intentionally lightweight. It allows the
    frontend/backend to work with an avatar even when no paid
    avatar-generation provider is configured.
    """

    def __init__(
        self,
        config: Optional[AvatarConfig] = None,
    ) -> None:
        self.config = config or AvatarConfig()

    def get_config(self) -> Dict[str, Any]:
        """
        Return the current avatar configuration.
        """

        return asdict(self.config)

    def update_config(
        self,
        **updates: Any,
    ) -> Dict[str, Any]:
        """
        Update supported avatar configuration fields.
        """

        allowed_fields = {
            "name",
            "gender",
            "style",
            "language",
            "voice_id",
            "image_path",
            "video_enabled",
        }

        for key, value in updates.items():
            if key not in allowed_fields:
                continue

            setattr(self.config, key, value)

        return self.get_config()

    def set_voice(
        self,
        voice_id: Optional[str],
    ) -> Dict[str, Any]:
        """
        Set the voice associated with the avatar.
        """

        self.config.voice_id = voice_id

        return self.get_config()

    def set_image(
        self,
        image_path: Optional[str],
    ) -> Dict[str, Any]:
        """
        Set the avatar image.

        The image path may point to a local placeholder or
        a generated avatar image.
        """

        if image_path:
            path = Path(image_path)

            if not path.exists():
                raise FileNotFoundError(
                    f"Avatar image not found: {image_path}"
                )

            if not path.is_file():
                raise ValueError(
                    f"Avatar image path is not a file: {image_path}"
                )

        self.config.image_path = (
            str(image_path) if image_path else None
        )

        return self.get_config()

    def enable_video(self, enabled: bool = True) -> Dict[str, Any]:
        """
        Enable or disable avatar video generation.
        """

        self.config.video_enabled = bool(enabled)

        return self.get_config()

    def prepare_speech(
        self,
        text: str,
    ) -> Dict[str, Any]:
        """
        Prepare teacher text for avatar speech generation.

        Actual TTS generation is handled by the speech module.
        """

        if not text or not text.strip():
            raise ValueError("Avatar speech text cannot be empty.")

        return {
            "avatar": self.get_config(),
            "text": text.strip(),
            "voice_id": self.config.voice_id,
            "language": self.config.language,
        }

    def prepare_video(
        self,
        text: str,
        audio_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Prepare information required for avatar video generation.

        This method does not call an external avatar provider.
        It creates a provider-independent video job payload.
        """

        if not text or not text.strip():
            raise ValueError("Avatar video text cannot be empty.")

        if audio_path:
            audio = Path(audio_path)

            if not audio.exists():
                raise FileNotFoundError(
                    f"Audio file not found: {audio_path}"
                )

        return {
            "avatar": self.get_config(),
            "text": text.strip(),
            "audio_path": audio_path,
            "video_enabled": self.config.video_enabled,
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Return the current status of the avatar service.
        """

        image_available = False

        if self.config.image_path:
            image_available = Path(
                self.config.image_path
            ).exists()

        return {
            "status": "ok",
            "service": "avatar",
            "provider": "local/provider-independent",
            "video_enabled": self.config.video_enabled,
            "image_available": image_available,
            "voice_configured": bool(
                self.config.voice_id
            ),
        }


# Default shared avatar service.
avatar_service = AvatarService()