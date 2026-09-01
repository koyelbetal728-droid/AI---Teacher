# tts.py
"""
Text-to-speech (TTS) service for the AI Teacher.

This module converts teacher responses into spoken audio.

The default implementation uses the local `pyttsx3` engine,
so the AI Teacher can generate speech without requiring a
paid cloud TTS API.
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional


class TextToSpeech:
    """
    Local text-to-speech service.

    `pyttsx3` is imported lazily because some systems may not
    have a working native speech engine configured.
    """

    def __init__(
        self,
        rate: int = 165,
        volume: float = 1.0,
        voice: Optional[str] = None,
    ) -> None:
        self.rate = rate
        self.volume = max(0.0, min(1.0, volume))
        self.voice = voice

    def _create_engine(self):
        """
        Create a pyttsx3 engine instance.
        """

        try:
            import pyttsx3
        except ImportError as exc:
            raise RuntimeError(
                "pyttsx3 is not installed. "
                "Install it with: pip install pyttsx3"
            ) from exc

        engine = pyttsx3.init()

        engine.setProperty("rate", self.rate)
        engine.setProperty("volume", self.volume)

        if self.voice:
            engine.setProperty("voice", self.voice)

        return engine

    def list_voices(self) -> List[Dict[str, Any]]:
        """
        Return voices available on the local machine.
        """

        engine = self._create_engine()

        voices = []

        try:
            for voice in engine.getProperty("voices"):
                voices.append(
                    {
                        "id": getattr(voice, "id", None),
                        "name": getattr(voice, "name", None),
                        "languages": self._normalize_languages(
                            getattr(voice, "languages", [])
                        ),
                        "gender": getattr(voice, "gender", None),
                        "age": getattr(voice, "age", None),
                    }
                )
        finally:
            try:
                engine.stop()
            except Exception:
                pass

        return voices

    def _normalize_languages(
        self,
        languages: Any,
    ) -> List[str]:
        """
        Convert pyttsx3 language metadata into readable strings.
        """

        if languages is None:
            return []

        if isinstance(languages, (str, bytes)):
            languages = [languages]

        result = []

        for language in languages:
            if isinstance(language, bytes):
                try:
                    language = language.decode("utf-8")
                except UnicodeDecodeError:
                    language = language.decode(
                        "utf-8",
                        errors="ignore",
                    )

            result.append(str(language))

        return result

    def synthesize(
        self,
        text: str,
        output_path: Optional[str | Path] = None,
        voice: Optional[str] = None,
        rate: Optional[int] = None,
        volume: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Convert text into an audio file.

        Parameters
        ----------
        text:
            Text that should be spoken.

        output_path:
            Destination audio file.

        voice:
            Optional local voice ID.

        rate:
            Optional speaking rate.

        volume:
            Optional volume from 0.0 to 1.0.

        Returns
        -------
        dict
            Information about the generated audio file.
        """

        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        if output_path is None:
            temporary_directory = Path(tempfile.gettempdir())
            output_path = (
                temporary_directory
                / "ai_teacher_speech.wav"
            )

        output = Path(output_path)
        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        engine = self._create_engine()

        try:
            if voice:
                engine.setProperty("voice", voice)

            if rate is not None:
                if rate <= 0:
                    raise ValueError(
                        "Speech rate must be greater than zero."
                    )

                engine.setProperty("rate", rate)

            if volume is not None:
                if not 0.0 <= volume <= 1.0:
                    raise ValueError(
                        "Volume must be between 0.0 and 1.0."
                    )

                engine.setProperty("volume", volume)

            engine.save_to_file(
                text.strip(),
                str(output),
            )

            engine.runAndWait()

        finally:
            try:
                engine.stop()
            except Exception:
                pass

        if not output.exists():
            raise RuntimeError(
                f"TTS engine failed to create audio file: {output}"
            )

        return {
            "path": str(output),
            "format": output.suffix.lstrip(".").lower(),
            "text": text.strip(),
            "size_bytes": output.stat().st_size,
        }

    async def synthesize_async(
        self,
        text: str,
        output_path: Optional[str | Path] = None,
        voice: Optional[str] = None,
        rate: Optional[int] = None,
        volume: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Asynchronous wrapper around the blocking TTS operation.

        TTS engines are generally blocking, so the actual work
        is executed in a background thread.
        """

        return await asyncio.to_thread(
            self.synthesize,
            text,
            output_path,
            voice,
            rate,
            volume,
        )

    def speak(
        self,
        text: str,
        voice: Optional[str] = None,
        rate: Optional[int] = None,
        volume: Optional[float] = None,
    ) -> None:
        """
        Speak text directly through the computer's speakers.

        This is useful for local development and testing.
        """

        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        engine = self._create_engine()

        try:
            if voice:
                engine.setProperty("voice", voice)

            if rate is not None:
                engine.setProperty("rate", rate)

            if volume is not None:
                if not 0.0 <= volume <= 1.0:
                    raise ValueError(
                        "Volume must be between 0.0 and 1.0."
                    )

                engine.setProperty("volume", volume)

            engine.say(text.strip())
            engine.runAndWait()

        finally:
            try:
                engine.stop()
            except Exception:
                pass

    def is_available(self) -> bool:
        """
        Check whether the local TTS engine is available.
        """

        try:
            engine = self._create_engine()

            try:
                engine.getProperty("voices")
            finally:
                engine.stop()

            return True

        except Exception:
            return False

    def get_default_voice(self) -> Optional[str]:
        """
        Return the first available local voice ID.
        """

        voices = self.list_voices()

        if not voices:
            return None

        return voices[0].get("id")


# Default shared TTS service.
text_to_speech = TextToSpeech()