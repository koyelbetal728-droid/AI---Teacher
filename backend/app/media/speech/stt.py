# stt.py
"""
Speech-to-text (STT) service for the AI Teacher.

This module converts spoken student input into text.

The implementation uses the local Whisper model through
the `faster-whisper` package, so speech recognition can
run locally without a paid speech API.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Union

from faster_whisper import WhisperModel


class SpeechToText:
    """
    Local speech-to-text service using Faster-Whisper.

    The model is loaded lazily so importing the application
    does not immediately download or initialize the model.
    """

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model: Optional[WhisperModel] = None

    @property
    def model(self) -> WhisperModel:
        """
        Lazily initialize the Whisper model.
        """

        if self._model is None:
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )

        return self._model

    def transcribe(
        self,
        audio_path: Union[str, Path],
        language: Optional[str] = None,
        task: str = "transcribe",
        beam_size: int = 5,
        vad_filter: bool = True,
    ) -> Dict[str, Any]:
        """
        Transcribe an audio file into text.

        Parameters
        ----------
        audio_path:
            Path to the audio file.

        language:
            Optional language code such as "en" or "bn".
            If omitted, Whisper automatically detects the language.

        task:
            "transcribe" or "translate".

        beam_size:
            Beam size used during decoding.

        vad_filter:
            Removes sections without detected speech.

        Returns
        -------
        dict
            {
                "text": "...",
                "language": "en",
                "language_probability": 0.99,
                "segments": [...]
            }
        """

        path = Path(audio_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Audio path is not a file: {path}"
            )

        if task not in {"transcribe", "translate"}:
            raise ValueError(
                "task must be either 'transcribe' or 'translate'."
            )

        segments, info = self.model.transcribe(
            str(path),
            language=language,
            task=task,
            beam_size=beam_size,
            vad_filter=vad_filter,
        )

        segment_list = []
        text_parts = []

        for segment in segments:
            segment_text = segment.text.strip()

            if segment_text:
                text_parts.append(segment_text)

            segment_list.append(
                {
                    "id": segment.id,
                    "start": round(segment.start, 3),
                    "end": round(segment.end, 3),
                    "text": segment_text,
                }
            )

        text = " ".join(text_parts).strip()

        return {
            "text": text,
            "language": info.language,
            "language_probability": round(
                info.language_probability,
                4,
            ),
            "duration": getattr(
                info,
                "duration",
                None,
            ),
            "segments": segment_list,
        }

    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: Optional[str] = None,
        task: str = "transcribe",
    ) -> Dict[str, Any]:
        """
        Transcribe audio provided as raw bytes.

        A temporary file is created because Faster-Whisper
        accepts a file path or supported audio input.
        """

        if not audio_bytes:
            raise ValueError("Audio data is empty.")

        suffix = Path(filename).suffix or ".wav"

        temporary_path: Optional[str] = None

        try:
            with tempfile.NamedTemporaryFile(
                suffix=suffix,
                delete=False,
            ) as temporary_file:
                temporary_file.write(audio_bytes)
                temporary_path = temporary_file.name

            return self.transcribe(
                temporary_path,
                language=language,
                task=task,
            )

        finally:
            if temporary_path and os.path.exists(temporary_path):
                os.remove(temporary_path)

    def detect_language(
        self,
        audio_path: Union[str, Path],
    ) -> Dict[str, Any]:
        """
        Detect the spoken language in an audio file.
        """

        result = self.transcribe(audio_path)

        return {
            "language": result["language"],
            "confidence": result["language_probability"],
        }

    def is_available(self) -> bool:
        """
        Check whether the STT model can be initialized.

        Returns False instead of raising an exception so this
        method can safely be used by health-check endpoints.
        """

        try:
            _ = self.model
            return True
        except Exception:
            return False

    def unload_model(self) -> None:
        """
        Release the loaded model from memory.

        Useful when the application needs to free RAM.
        """

        self._model = None


# Default shared STT service.
speech_to_text = SpeechToText()
