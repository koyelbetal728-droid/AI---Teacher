# video_renderer.py
"""
Local video renderer for the AI Teacher.

This module renders structured educational scenes into a video
using FFmpeg when available.

The renderer supports:

- Text-only scenes
- Image/visual scenes
- Scene durations
- FPS configuration
- Resolution configuration
- Optional audio track
- Concatenation of multiple scenes
- Basic video metadata
- Temporary file cleanup

FFmpeg is intentionally used as an external local dependency
so that video rendering does not require a paid API.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


class VideoRenderer:
    """
    Render educational scenes into a video using FFmpeg.
    """

    def __init__(
        self,
        output_directory: str = "data/generated_videos",
        ffmpeg_binary: str = "ffmpeg",
        ffprobe_binary: str = "ffprobe",
    ) -> None:
        self.output_directory = Path(
            output_directory
        )

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.ffmpeg_binary = ffmpeg_binary
        self.ffprobe_binary = ffprobe_binary

    def render(
        self,
        scenes: Sequence[
            Dict[str, Any]
        ],
        output_filename: str = "ai_teacher_video",
        fps: int = 24,
        resolution: str = "1280x720",
        audio_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Render a sequence of scenes into an MP4 video.

        Each scene may contain:

            title
            narration
            on_screen_text
            visual_path
            duration
            scene_type
        """

        if not scenes:
            raise ValueError(
                "At least one scene is required."
            )

        if fps <= 0:
            raise ValueError(
                "fps must be greater than zero."
            )

        width, height = self._parse_resolution(
            resolution
        )

        if not self.is_available():
            return {
                "success": False,
                "available": False,
                "error": (
                    "FFmpeg was not found. "
                    "Install FFmpeg and make sure "
                    "it is available in PATH."
                ),
                "output_path": None,
            }

        output_path = (
            self.output_directory
            / self._safe_filename(
                output_filename
            )
        )

        if output_path.suffix.lower() != ".mp4":
            output_path = output_path.with_suffix(
                ".mp4"
            )

        temporary_directory = Path(
            tempfile.mkdtemp(
                prefix="ai_teacher_video_"
            )
        )

        try:
            scene_files = []

            for index, scene in enumerate(
                scenes
            ):
                scene_path = (
                    temporary_directory
                    / f"scene_{index:04d}.mp4"
                )

                self._render_scene(
                    scene=scene,
                    output_path=scene_path,
                    fps=fps,
                    width=width,
                    height=height,
                )

                scene_files.append(
                    scene_path
                )

            concat_file = (
                temporary_directory
                / "concat.txt"
            )

            self._create_concat_file(
                scene_files,
                concat_file,
            )

            self._concatenate_scenes(
                concat_file=concat_file,
                output_path=output_path,
            )

            if audio_path:
                output_path = (
                    self._add_audio(
                        video_path=output_path,
                        audio_path=Path(
                            audio_path
                        ),
                        temporary_directory=(
                            temporary_directory
                        ),
                    )
                )

            duration = self._get_duration(
                output_path
            )

            return {
                "success": True,
                "available": True,
                "output_path": str(
                    output_path
                ),
                "format": "mp4",
                "fps": fps,
                "resolution": resolution,
                "scene_count": len(
                    scenes
                ),
                "duration": duration,
            }

        except subprocess.CalledProcessError as exc:
            return {
                "success": False,
                "available": True,
                "error": self._format_process_error(
                    exc
                ),
                "output_path": None,
            }

        finally:
            shutil.rmtree(
                temporary_directory,
                ignore_errors=True,
            )

    def render_scene(
        self,
        scene: Dict[str, Any],
        output_filename: str = "scene",
        fps: int = 24,
        resolution: str = "1280x720",
    ) -> Dict[str, Any]:
        """
        Render a single scene into an MP4 file.
        """

        if not self.is_available():
            return {
                "success": False,
                "available": False,
                "error": "FFmpeg is not available.",
            }

        width, height = self._parse_resolution(
            resolution
        )

        output_path = (
            self.output_directory
            / self._safe_filename(
                output_filename
            )
        )

        if output_path.suffix.lower() != ".mp4":
            output_path = output_path.with_suffix(
                ".mp4"
            )

        temporary_directory = Path(
            tempfile.mkdtemp(
                prefix="ai_teacher_scene_"
            )
        )

        try:
            self._render_scene(
                scene=scene,
                output_path=output_path,
                fps=fps,
                width=width,
                height=height,
            )

            return {
                "success": True,
                "output_path": str(
                    output_path
                ),
                "duration": self._get_duration(
                    output_path
                ),
            }

        finally:
            shutil.rmtree(
                temporary_directory,
                ignore_errors=True,
            )

    def health_check(
        self,
    ) -> Dict[str, Any]:
        """
        Check FFmpeg and FFprobe availability.
        """

        ffmpeg_path = shutil.which(
            self.ffmpeg_binary
        )

        ffprobe_path = shutil.which(
            self.ffprobe_binary
        )

        return {
            "service": "video_renderer",
            "available": (
                ffmpeg_path is not None
            ),
            "ffmpeg_available": (
                ffmpeg_path is not None
            ),
            "ffprobe_available": (
                ffprobe_path is not None
            ),
            "ffmpeg_path": ffmpeg_path,
            "ffprobe_path": ffprobe_path,
        }

    def is_available(self) -> bool:
        """
        Return True when FFmpeg is available.
        """

        return (
            shutil.which(
                self.ffmpeg_binary
            )
            is not None
        )

    def get_video_info(
        self,
        video_path: str,
    ) -> Dict[str, Any]:
        """
        Return metadata about a video file.
        """

        path = Path(video_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Video not found: {video_path}"
            )

        if not shutil.which(
            self.ffprobe_binary
        ):
            return {
                "path": str(path),
                "size_bytes": path.stat().st_size,
                "ffprobe_available": False,
            }

        command = [
            self.ffprobe_binary,
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(path),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

        try:
            metadata = json.loads(
                result.stdout
            )
        except json.JSONDecodeError:
            metadata = {}

        return {
            "path": str(path),
            "size_bytes": path.stat().st_size,
            "ffprobe_available": True,
            "metadata": metadata,
        }

    def _render_scene(
        self,
        scene: Dict[str, Any],
        output_path: Path,
        fps: int,
        width: int,
        height: int,
    ) -> None:
        """
        Render one scene.

        If a valid visual is supplied, it is displayed as the
        scene background. Otherwise a generated color background
        is used and text is displayed over it.
        """

        duration = float(
            scene.get(
                "duration",
                5,
            )
        )

        duration = max(
            1.0,
            duration,
        )

        visual_path = scene.get(
            "visual_path"
        )

        title = str(
            scene.get(
                "title",
                "",
            )
        )

        text = str(
            scene.get(
                "on_screen_text",
                scene.get(
                    "narration",
                    "",
                ),
            )
        )

        if (
            visual_path
            and Path(
                visual_path
            ).exists()
        ):
            self._render_visual_scene(
                visual_path=Path(
                    visual_path
                ),
                output_path=output_path,
                duration=duration,
                fps=fps,
                width=width,
                height=height,
            )

        else:
            self._render_text_scene(
                title=title,
                text=text,
                output_path=output_path,
                duration=duration,
                fps=fps,
                width=width,
                height=height,
            )

    def _render_text_scene(
        self,
        title: str,
        text: str,
        output_path: Path,
        duration: float,
        fps: int,
        width: int,
        height: int,
    ) -> None:
        """
        Render a text-based scene.

        FFmpeg's drawtext filter is used when available.
        """

        title = self._escape_ffmpeg_text(
            title
        )

        text = self._escape_ffmpeg_text(
            text
        )

        font_size_title = max(
            28,
            width // 32,
        )

        font_size_text = max(
            22,
            width // 48,
        )

        filter_expression = (
            "drawtext="
            "text='"
            f"{title}"
            "':"
            "x=(w-text_w)/2:"
            "y=h*0.18:"
            f"fontsize={font_size_title}:"
            "fontcolor=white:"
            "enable='between(t,0,60)',"
            "drawtext="
            "text='"
            f"{text}"
            "':"
            "x=(w-text_w)/2:"
            "y=(h-text_h)/2:"
            f"fontsize={font_size_text}:"
            "fontcolor=white:"
            "line_spacing=12:"
            "box=1:"
            "boxborderw=18:"
            "boxcolor=black@0.45:"
            "text_align=center"
        )

        command = [
            self.ffmpeg_binary,
            "-y",
            "-f",
            "lavfi",
            "-i",
            (
                "color="
                "c=black:"
                f"s={width}x{height}:"
                f"r={fps}"
            ),
            "-t",
            str(duration),
            "-vf",
            filter_expression,
            "-r",
            str(fps),
            "-pix_fmt",
            "yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-movflags",
            "+faststart",
            str(output_path),
        ]

        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )

    def _render_visual_scene(
        self,
        visual_path: Path,
        output_path: Path,
        duration: float,
        fps: int,
        width: int,
        height: int,
    ) -> None:
        """
        Render an image/visual as a video scene.
        """

        command = [
            self.ffmpeg_binary,
            "-y",
            "-loop",
            "1",
            "-i",
            str(visual_path),
            "-t",
            str(duration),
            "-vf",
            (
                "scale="
                f"{width}:{height}:"
                "force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:"
                "(ow-iw)/2:"
                "(oh-ih)/2"
            ),
            "-r",
            str(fps),
            "-pix_fmt",
            "yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-movflags",
            "+faststart",
            str(output_path),
        ]

        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )

    def _create_concat_file(
        self,
        scene_files: Sequence[Path],
        concat_file: Path,
    ) -> None:
        """
        Create an FFmpeg concat-demuxer manifest.
        """

        lines = []

        for scene_file in scene_files:
            escaped = (
                str(
                    scene_file.resolve()
                )
                .replace(
                    "'",
                    "'\\''",
                )
            )

            lines.append(
                f"file '{escaped}'"
            )

        concat_file.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

    def _concatenate_scenes(
        self,
        concat_file: Path,
        output_path: Path,
    ) -> None:
        """
        Concatenate rendered scene videos.
        """

        command = [
            self.ffmpeg_binary,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            str(output_path),
        ]

        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )

    def _add_audio(
        self,
        video_path: Path,
        audio_path: Path,
        temporary_directory: Path,
    ) -> Path:
        """
        Add an audio track to a video.

        The resulting file replaces the original video path.
        """

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        output_path = (
            temporary_directory
            / "video_with_audio.mp4"
        )

        command = [
            self.ffmpeg_binary,
            "-y",
            "-i",
            str(video_path),
            "-i",
            str(audio_path),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-shortest",
            "-movflags",
            "+faststart",
            str(output_path),
        ]

        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )

        shutil.copy2(
            output_path,
            video_path,
        )

        return video_path

    def _get_duration(
        self,
        video_path: Path,
    ) -> Optional[float]:
        """
        Get video duration using FFprobe.
        """

        if not shutil.which(
            self.ffprobe_binary
        ):
            return None

        command = [
            self.ffprobe_binary,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

        try:
            return round(
                float(
                    result.stdout.strip()
                ),
                2,
            )
        except (
            ValueError,
            TypeError,
        ):
            return None

    @staticmethod
    def _parse_resolution(
        resolution: str,
    ) -> Tuple[int, int]:
        """
        Parse a resolution string such as 1280x720.
        """

        try:
            width_text, height_text = (
                resolution.lower()
                .split("x", 1)
            )

            width = int(
                width_text
            )

            height = int(
                height_text
            )

        except (
            ValueError,
            AttributeError,
        ) as exc:
            raise ValueError(
                "Resolution must use the format WIDTHxHEIGHT, "
                "for example 1280x720."
            ) from exc

        if width <= 0 or height <= 0:
            raise ValueError(
                "Resolution dimensions must be positive."
            )

        return width, height

    @staticmethod
    def _safe_filename(
        filename: str,
    ) -> str:
        """
        Prevent unsafe filesystem characters.
        """

        path = Path(
            filename
        )

        stem = path.stem

        safe = "".join(
            character
            if (
                character.isalnum()
                or character in {
                    "_",
                    "-",
                    " ",
                }
            )
            else "_"
            for character in stem
        )

        safe = "_".join(
            safe.split()
        )

        return (
            safe
            or "ai_teacher_video"
        ) + ".mp4"

    @staticmethod
    def _escape_ffmpeg_text(
        text: str,
    ) -> str:
        """
        Escape characters used by FFmpeg drawtext.
        """

        text = text.replace(
            "\\",
            r"\\",
        )

        text = text.replace(
            ":",
            r"\:",
        )

        text = text.replace(
            "'",
            r"\'",
        )

        text = text.replace(
            "%",
            r"\%",
        )

        text = text.replace(
            "\n",
            r"\n",
        )

        return text

    @staticmethod
    def _format_process_error(
        error: subprocess.CalledProcessError,
    ) -> str:
        """
        Produce a readable FFmpeg error.
        """

        stderr = (
            error.stderr
            if isinstance(
                error.stderr,
                str,
            )
            else ""
        )

        stderr = stderr.strip()

        if stderr:
            return stderr[-3000:]

        return (
            "FFmpeg failed while rendering "
            "the video."
        )


# Default shared video renderer.
video_renderer = VideoRenderer()