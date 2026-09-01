# video_generator.py
"""
Educational video generation service for the AI Teacher.

This module provides a provider-independent interface for
creating teaching videos from:

- Text
- Audio
- Images
- Educational visuals
- Lesson scenes

The actual rendering is delegated to SceneBuilder and
VideoRenderer so that the system can later support
different local/free video backends.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from app.media.video.scene_builder import SceneBuilder
from app.media.video.video_renderer import VideoRenderer


class VideoGenerator:
    """
    High-level educational video generation service.

    The generator converts lesson content into scenes and
    passes those scenes to the local video renderer.
    """

    def __init__(
        self,
        output_directory: str = "data/generated_videos",
        scene_builder: Optional[SceneBuilder] = None,
        renderer: Optional[VideoRenderer] = None,
    ) -> None:
        self.output_directory = Path(
            output_directory
        )

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.scene_builder = (
            scene_builder
            or SceneBuilder()
        )

        self.renderer = (
            renderer
            or VideoRenderer(
                output_directory=str(
                    self.output_directory
                )
            )
        )

    def generate(
        self,
        title: str,
        scenes: Optional[
            Sequence[Dict[str, Any]]
        ] = None,
        script: Optional[str] = None,
        audio_path: Optional[str] = None,
        filename: Optional[str] = None,
        fps: int = 24,
        resolution: str = "1280x720",
    ) -> Dict[str, Any]:
        """
        Generate an educational video.

        Either `scenes` or `script` should be supplied.

        Example:

            generator.generate(
                title="Introduction to Python",
                script="Python is a programming language..."
            )
        """

        if not title.strip():
            raise ValueError(
                "Video title cannot be empty."
            )

        if not scenes and not script:
            raise ValueError(
                "Either scenes or script must be provided."
            )

        if scenes:
            scene_list = [
                dict(scene)
                for scene in scenes
            ]
        else:
            scene_list = (
                self.scene_builder
                .from_script(script or "")
            )

        scene_list = self.scene_builder.validate_scenes(
            scene_list
        )

        output_name = (
            filename
            or self._safe_filename(title)
        )

        result = self.renderer.render(
            scenes=scene_list,
            output_filename=output_name,
            fps=fps,
            resolution=resolution,
            audio_path=audio_path,
        )

        result.update(
            {
                "title": title,
                "scene_count": len(scene_list),
            }
        )

        return result

    def generate_from_lesson(
        self,
        lesson: Dict[str, Any],
        audio_path: Optional[str] = None,
        filename: Optional[str] = None,
        fps: int = 24,
        resolution: str = "1280x720",
    ) -> Dict[str, Any]:
        """
        Generate a video directly from a lesson object.

        The lesson may contain:

            title
            topic
            objectives
            sections
            explanation
            summary
        """

        title = str(
            lesson.get(
                "title",
                lesson.get(
                    "topic",
                    "AI Teacher Lesson",
                ),
            )
        )

        scenes = (
            self.scene_builder
            .from_lesson(lesson)
        )

        return self.generate(
            title=title,
            scenes=scenes,
            audio_path=audio_path,
            filename=filename,
            fps=fps,
            resolution=resolution,
        )

    def generate_from_script(
        self,
        title: str,
        script: str,
        audio_path: Optional[str] = None,
        filename: Optional[str] = None,
        fps: int = 24,
        resolution: str = "1280x720",
    ) -> Dict[str, Any]:
        """
        Convert a teaching script into scenes and render it.
        """

        if not script.strip():
            raise ValueError(
                "Script cannot be empty."
            )

        scenes = (
            self.scene_builder
            .from_script(script)
        )

        return self.generate(
            title=title,
            scenes=scenes,
            audio_path=audio_path,
            filename=filename,
            fps=fps,
            resolution=resolution,
        )

    def generate_explanation_video(
        self,
        topic: str,
        explanation: str,
        key_points: Optional[
            Sequence[str]
        ] = None,
        audio_path: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a short concept-explanation video.
        """

        if not topic.strip():
            raise ValueError(
                "Topic cannot be empty."
            )

        if not explanation.strip():
            raise ValueError(
                "Explanation cannot be empty."
            )

        scenes = (
            self.scene_builder
            .from_explanation(
                topic=topic,
                explanation=explanation,
                key_points=list(
                    key_points or []
                ),
            )
        )

        return self.generate(
            title=topic,
            scenes=scenes,
            audio_path=audio_path,
            filename=filename,
        )

    def generate_visual_lesson(
        self,
        title: str,
        explanation: str,
        visual_paths: Sequence[str],
        audio_path: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a lesson video using previously generated
        educational visuals.
        """

        if not explanation.strip():
            raise ValueError(
                "Explanation cannot be empty."
            )

        scenes = (
            self.scene_builder
            .from_visual_lesson(
                title=title,
                explanation=explanation,
                visual_paths=list(
                    visual_paths
                ),
            )
        )

        return self.generate(
            title=title,
            scenes=scenes,
            audio_path=audio_path,
            filename=filename,
        )

    def preview_scenes(
        self,
        title: str,
        script: Optional[str] = None,
        lesson: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Dict[str, Any]:
        """
        Build scenes without rendering a video.

        Useful for the frontend lesson editor and debugging.
        """

        if lesson:
            scenes = (
                self.scene_builder
                .from_lesson(lesson)
            )

        elif script:
            scenes = (
                self.scene_builder
                .from_script(script)
            )

        else:
            raise ValueError(
                "Either script or lesson must be provided."
            )

        scenes = self.scene_builder.validate_scenes(
            scenes
        )

        return {
            "success": True,
            "title": title,
            "scene_count": len(scenes),
            "scenes": scenes,
        }

    def get_video_info(
        self,
        video_path: str,
    ) -> Dict[str, Any]:
        """
        Return basic metadata for a generated video.
        """

        path = Path(video_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Video not found: {video_path}"
            )

        return self.renderer.get_video_info(
            str(path)
        )

    def delete_video(
        self,
        video_path: str,
    ) -> bool:
        """
        Delete a generated video.
        """

        path = Path(video_path)

        if not path.exists():
            return False

        if not path.is_file():
            raise ValueError(
                "The specified path is not a file."
            )

        path.unlink()

        return True

    def health_check(self) -> Dict[str, Any]:
        """
        Check whether the video rendering backend is available.
        """

        renderer_status = (
            self.renderer.health_check()
        )

        return {
            "service": "video_generator",
            "available": bool(
                renderer_status.get(
                    "available",
                    False,
                )
            ),
            "renderer": renderer_status,
            "output_directory": str(
                self.output_directory
            ),
        }

    @staticmethod
    def _safe_filename(
        value: str,
    ) -> str:
        """
        Convert a title into a filesystem-safe filename.
        """

        value = value.strip()

        value = re.sub(
            r"[^a-zA-Z0-9_\- ]+",
            "",
            value,
        )

        value = re.sub(
            r"\s+",
            "_",
            value,
        )

        value = value.strip(
            "_"
        )

        return (
            value[:100]
            or "ai_teacher_video"
        )

    @staticmethod
    def export_scene_manifest(
        scenes: Sequence[
            Dict[str, Any]
        ],
        output_path: str,
    ) -> str:
        """
        Save the scene configuration as JSON.

        This is useful for debugging and reproducing videos.
        """

        path = Path(output_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {
            "scene_count": len(scenes),
            "scenes": list(scenes),
        }

        path.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return str(path)


# Default shared video generator.
video_generator = VideoGenerator()