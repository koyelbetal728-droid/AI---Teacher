# scene_builder.py
"""
Scene builder for the AI Teacher.

This module converts lessons, scripts, explanations, and
visual assets into a standardized list of video scenes.

Each scene can contain:

- Title
- Narration text
- On-screen text
- Visual/image
- Duration
- Scene type
- Transition
- Metadata

The resulting scene objects are consumed by VideoRenderer.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Sequence


class SceneBuilder:
    """
    Build structured educational video scenes.
    """

    DEFAULT_DURATION = 5.0
    MIN_DURATION = 1.0
    MAX_DURATION = 60.0

    SUPPORTED_SCENE_TYPES = {
        "title",
        "introduction",
        "explanation",
        "example",
        "visual",
        "diagram",
        "formula",
        "code",
        "question",
        "summary",
        "transition",
        "conclusion",
    }

    def from_script(
        self,
        script: str,
        default_duration: float = DEFAULT_DURATION,
    ) -> List[Dict[str, Any]]:
        """
        Convert a plain teaching script into scenes.

        Blank lines separate scenes.

        Example:

            Introduction to Python.

            Python is a programming language.

            Let's look at a simple example.
        """

        if not script.strip():
            raise ValueError(
                "Script cannot be empty."
            )

        blocks = self._split_script(script)

        scenes: List[Dict[str, Any]] = []

        for index, block in enumerate(blocks):
            scene_type = (
                "introduction"
                if index == 0
                else "explanation"
            )

            scenes.append(
                self.create_scene(
                    narration=block,
                    on_screen_text=self._create_display_text(
                        block
                    ),
                    scene_type=scene_type,
                    duration=self.estimate_duration(
                        block,
                        default_duration,
                    ),
                )
            )

        return scenes

    def from_lesson(
        self,
        lesson: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Convert a lesson dictionary into video scenes.

        Expected optional fields:

            title
            topic
            introduction
            explanation
            objectives
            sections
            examples
            summary
            conclusion
        """

        if not lesson:
            raise ValueError(
                "Lesson cannot be empty."
            )

        scenes: List[Dict[str, Any]] = []

        title = str(
            lesson.get(
                "title",
                lesson.get(
                    "topic",
                    "AI Teacher Lesson",
                ),
            )
        )

        scenes.append(
            self.create_scene(
                title=title,
                narration=f"Today we will learn about {title}.",
                on_screen_text=title,
                scene_type="title",
                duration=4,
            )
        )

        introduction = lesson.get(
            "introduction"
        )

        if introduction:
            scenes.append(
                self.create_scene(
                    narration=str(
                        introduction
                    ),
                    on_screen_text=(
                        "Introduction"
                    ),
                    scene_type="introduction",
                    duration=self.estimate_duration(
                        str(introduction)
                    ),
                )
            )

        objectives = lesson.get(
            "objectives",
            [],
        )

        if objectives:
            scenes.append(
                self.create_bullet_scene(
                    title="Learning Objectives",
                    items=self._to_string_list(
                        objectives
                    ),
                    scene_type="explanation",
                )
            )

        sections = lesson.get(
            "sections",
            lesson.get(
                "content",
                [],
            ),
        )

        if isinstance(
            sections,
            str,
        ):
            sections = [
                sections
            ]

        for index, section in enumerate(
            sections or []
        ):
            scenes.extend(
                self._section_to_scenes(
                    section,
                    index,
                )
            )

        examples = lesson.get(
            "examples",
            [],
        )

        for index, example in enumerate(
            examples or []
        ):
            if isinstance(
                example,
                dict,
            ):
                explanation = str(
                    example.get(
                        "explanation",
                        example.get(
                            "description",
                            "",
                        ),
                    )
                )

                example_text = str(
                    example.get(
                        "example",
                        example.get(
                            "content",
                            "",
                        ),
                    )
                )

                narration = " ".join(
                    part
                    for part in [
                        explanation,
                        example_text,
                    ]
                    if part
                )

                scenes.append(
                    self.create_scene(
                        title=f"Example {index + 1}",
                        narration=narration,
                        on_screen_text=example_text,
                        scene_type="example",
                        duration=self.estimate_duration(
                            narration
                        ),
                    )
                )

            else:
                text = str(example)

                scenes.append(
                    self.create_scene(
                        title=f"Example {index + 1}",
                        narration=text,
                        on_screen_text=(
                            self._create_display_text(
                                text
                            )
                        ),
                        scene_type="example",
                        duration=self.estimate_duration(
                            text
                        ),
                    )
                )

        summary = lesson.get(
            "summary"
        )

        if summary:
            scenes.append(
                self.create_scene(
                    title="Summary",
                    narration=str(summary),
                    on_screen_text=self._create_display_text(
                        str(summary)
                    ),
                    scene_type="summary",
                    duration=self.estimate_duration(
                        str(summary)
                    ),
                )
            )

        conclusion = lesson.get(
            "conclusion"
        )

        if conclusion:
            scenes.append(
                self.create_scene(
                    title="Conclusion",
                    narration=str(conclusion),
                    on_screen_text=self._create_display_text(
                        str(conclusion)
                    ),
                    scene_type="conclusion",
                    duration=self.estimate_duration(
                        str(conclusion)
                    ),
                )
            )

        return scenes

    def from_explanation(
        self,
        topic: str,
        explanation: str,
        key_points: Optional[
            Sequence[str]
        ] = None,
    ) -> List[Dict[str, Any]]:
        """
        Build a short concept explanation video.
        """

        if not topic.strip():
            raise ValueError(
                "Topic cannot be empty."
            )

        if not explanation.strip():
            raise ValueError(
                "Explanation cannot be empty."
            )

        scenes = [
            self.create_scene(
                title=topic,
                narration=(
                    f"Let's learn about {topic}."
                ),
                on_screen_text=topic,
                scene_type="title",
                duration=4,
            ),
            self.create_scene(
                title="Concept",
                narration=explanation,
                on_screen_text=self._create_display_text(
                    explanation
                ),
                scene_type="explanation",
                duration=self.estimate_duration(
                    explanation
                ),
            ),
        ]

        if key_points:
            scenes.append(
                self.create_bullet_scene(
                    title="Key Points",
                    items=list(key_points),
                    scene_type="summary",
                )
            )

        return scenes

    def from_visual_lesson(
        self,
        title: str,
        explanation: str,
        visual_paths: Sequence[str],
    ) -> List[Dict[str, Any]]:
        """
        Create scenes from an explanation and a collection
        of generated educational visuals.
        """

        if not title.strip():
            raise ValueError(
                "Title cannot be empty."
            )

        if not explanation.strip():
            raise ValueError(
                "Explanation cannot be empty."
            )

        scenes: List[
            Dict[str, Any]
        ] = [
            self.create_scene(
                title=title,
                narration=(
                    f"Let's learn about {title}."
                ),
                on_screen_text=title,
                scene_type="title",
                duration=4,
            )
        ]

        paragraphs = self._split_script(
            explanation
        )

        for index, paragraph in enumerate(
            paragraphs
        ):
            visual = (
                visual_paths[index]
                if index < len(visual_paths)
                else None
            )

            scenes.append(
                self.create_scene(
                    title=f"Concept {index + 1}",
                    narration=paragraph,
                    on_screen_text=self._create_display_text(
                        paragraph
                    ),
                    visual_path=visual,
                    scene_type=(
                        "visual"
                        if visual
                        else "explanation"
                    ),
                    duration=self.estimate_duration(
                        paragraph
                    ),
                )
            )

        return scenes

    def create_scene(
        self,
        narration: str = "",
        title: Optional[str] = None,
        on_screen_text: Optional[str] = None,
        visual_path: Optional[str] = None,
        scene_type: str = "explanation",
        duration: Optional[float] = None,
        transition: str = "fade",
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Dict[str, Any]:
        """
        Create one standardized scene object.
        """

        scene_type = (
            scene_type.strip().lower()
        )

        if scene_type not in self.SUPPORTED_SCENE_TYPES:
            scene_type = "explanation"

        duration = (
            duration
            if duration is not None
            else self.estimate_duration(
                narration
            )
        )

        duration = max(
            self.MIN_DURATION,
            min(
                float(duration),
                self.MAX_DURATION,
            ),
        )

        return {
            "title": (
                title.strip()
                if title
                else None
            ),
            "narration": (
                narration.strip()
                if narration
                else ""
            ),
            "on_screen_text": (
                on_screen_text.strip()
                if on_screen_text
                else ""
            ),
            "visual_path": visual_path,
            "scene_type": scene_type,
            "duration": round(
                duration,
                2,
            ),
            "transition": (
                transition
                or "fade"
            ),
            "metadata": dict(
                metadata or {}
            ),
        }

    def create_bullet_scene(
        self,
        title: str,
        items: Sequence[str],
        scene_type: str = "explanation",
        duration: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Create a scene displaying a list of bullet points.
        """

        clean_items = [
            str(item).strip()
            for item in items
            if str(item).strip()
        ]

        if not clean_items:
            raise ValueError(
                "At least one bullet item is required."
            )

        on_screen_text = "\n".join(
            f"• {item}"
            for item in clean_items
        )

        narration = ". ".join(
            clean_items
        )

        return self.create_scene(
            title=title,
            narration=narration,
            on_screen_text=on_screen_text,
            scene_type=scene_type,
            duration=(
                duration
                or self.estimate_duration(
                    narration
                )
            ),
        )

    def create_question_scene(
        self,
        question: str,
        options: Optional[
            Sequence[str]
        ] = None,
        duration: float = 7.0,
    ) -> Dict[str, Any]:
        """
        Create an interactive-looking question scene.
        """

        if not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        text = question.strip()

        if options:
            text += "\n\n"
            text += "\n".join(
                f"{index + 1}. {option}"
                for index, option in enumerate(
                    options
                )
            )

        return self.create_scene(
            title="Question",
            narration=question,
            on_screen_text=text,
            scene_type="question",
            duration=duration,
        )

    def create_visual_scene(
        self,
        title: str,
        narration: str,
        visual_path: str,
        duration: Optional[float] = None,
        scene_type: str = "visual",
    ) -> Dict[str, Any]:
        """
        Create a scene containing an educational visual.
        """

        return self.create_scene(
            title=title,
            narration=narration,
            on_screen_text=self._create_display_text(
                narration
            ),
            visual_path=visual_path,
            scene_type=scene_type,
            duration=duration,
        )

    def create_code_scene(
        self,
        code: str,
        explanation: str = "",
        language: str = "python",
        duration: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Create a programming lesson scene.
        """

        if not code.strip():
            raise ValueError(
                "Code cannot be empty."
            )

        narration = explanation.strip()

        if not narration:
            narration = (
                "Let's look at this "
                f"{language} example."
            )

        return self.create_scene(
            title=f"{language.title()} Example",
            narration=narration,
            on_screen_text=code.strip(),
            scene_type="code",
            duration=(
                duration
                or self.estimate_duration(
                    narration
                )
            ),
            metadata={
                "language": language,
                "code": code.strip(),
            },
        )

    def create_formula_scene(
        self,
        formula: str,
        explanation: str = "",
        duration: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Create a mathematical formula scene.
        """

        if not formula.strip():
            raise ValueError(
                "Formula cannot be empty."
            )

        narration = explanation.strip()

        if not narration:
            narration = (
                f"The formula is {formula}."
            )

        return self.create_scene(
            title="Formula",
            narration=narration,
            on_screen_text=formula.strip(),
            scene_type="formula",
            duration=(
                duration
                or self.estimate_duration(
                    narration
                )
            ),
            metadata={
                "formula": formula.strip()
            },
        )

    def validate_scenes(
        self,
        scenes: Sequence[
            Dict[str, Any]
        ],
    ) -> List[Dict[str, Any]]:
        """
        Validate and normalize a collection of scenes.
        """

        if not scenes:
            raise ValueError(
                "At least one scene is required."
            )

        validated: List[
            Dict[str, Any]
        ] = []

        for scene in scenes:
            if not isinstance(
                scene,
                dict,
            ):
                raise TypeError(
                    "Each scene must be a dictionary."
                )

            narration = str(
                scene.get(
                    "narration",
                    "",
                )
            )

            duration = scene.get(
                "duration"
            )

            if duration is None:
                duration = self.estimate_duration(
                    narration
                )

            validated.append(
                self.create_scene(
                    narration=narration,
                    title=scene.get(
                        "title"
                    ),
                    on_screen_text=scene.get(
                        "on_screen_text",
                        "",
                    ),
                    visual_path=scene.get(
                        "visual_path"
                    ),
                    scene_type=scene.get(
                        "scene_type",
                        "explanation",
                    ),
                    duration=duration,
                    transition=scene.get(
                        "transition",
                        "fade",
                    ),
                    metadata=scene.get(
                        "metadata",
                        {},
                    ),
                )
            )

        return validated

    def estimate_duration(
        self,
        text: str,
        default: float = DEFAULT_DURATION,
        words_per_minute: int = 130,
    ) -> float:
        """
        Estimate narration duration from word count.

        Average educational narration speed is approximated
        at 130 words per minute.
        """

        if not text.strip():
            return float(default)

        words = len(
            re.findall(
                r"\S+",
                text,
            )
        )

        if words == 0:
            return float(default)

        duration = (
            words
            / words_per_minute
            * 60
        )

        return max(
            self.MIN_DURATION,
            min(
                duration,
                self.MAX_DURATION,
            ),
        )

    def total_duration(
        self,
        scenes: Sequence[
            Dict[str, Any]
        ],
    ) -> float:
        """
        Calculate total video duration.
        """

        return round(
            sum(
                float(
                    scene.get(
                        "duration",
                        self.DEFAULT_DURATION,
                    )
                )
                for scene in scenes
            ),
            2,
        )

    def add_transition(
        self,
        scenes: Sequence[
            Dict[str, Any]
        ],
        transition: str = "fade",
    ) -> List[Dict[str, Any]]:
        """
        Apply a transition to every scene.
        """

        result = []

        for scene in scenes:
            updated = dict(scene)

            updated[
                "transition"
            ] = transition

            result.append(
                updated
            )

        return result

    def _section_to_scenes(
        self,
        section: Any,
        index: int,
    ) -> List[Dict[str, Any]]:
        """
        Convert one lesson section into one or more scenes.
        """

        if isinstance(
            section,
            str,
        ):
            text = section.strip()

            if not text:
                return []

            return [
                self.create_scene(
                    title=f"Lesson Part {index + 1}",
                    narration=text,
                    on_screen_text=self._create_display_text(
                        text
                    ),
                    scene_type="explanation",
                    duration=self.estimate_duration(
                        text
                    ),
                )
            ]

        if not isinstance(
            section,
            dict,
        ):
            return []

        title = str(
            section.get(
                "title",
                f"Lesson Part {index + 1}",
            )
        )

        explanation = str(
            section.get(
                "explanation",
                section.get(
                    "content",
                    section.get(
                        "description",
                        "",
                    ),
                ),
            )
        )

        scene_type = str(
            section.get(
                "scene_type",
                "explanation",
            )
        )

        scenes = []

        if explanation:
            scenes.append(
                self.create_scene(
                    title=title,
                    narration=explanation,
                    on_screen_text=self._create_display_text(
                        explanation
                    ),
                    visual_path=section.get(
                        "visual_path"
                    ),
                    scene_type=scene_type,
                    duration=section.get(
                        "duration",
                        self.estimate_duration(
                            explanation
                        ),
                    ),
                    metadata={
                        key: value
                        for key, value in section.items()
                        if key
                        not in {
                            "title",
                            "explanation",
                            "content",
                            "description",
                            "scene_type",
                            "duration",
                            "visual_path",
                        }
                    },
                )
            )

        points = section.get(
            "key_points",
            section.get(
                "points",
                [],
            ),
        )

        if points:
            scenes.append(
                self.create_bullet_scene(
                    title=f"{title} - Key Points",
                    items=self._to_string_list(
                        points
                    ),
                    scene_type="summary",
                )
            )

        return scenes

    @staticmethod
    def _split_script(
        script: str,
    ) -> List[str]:
        """
        Split a script into meaningful scene blocks.
        """

        script = script.replace(
            "\r\n",
            "\n",
        )

        blocks = re.split(
            r"\n\s*\n+",
            script,
        )

        result = []

        for block in blocks:
            block = block.strip()

            if not block:
                continue

            result.append(
                block
            )

        return result

    @staticmethod
    def _create_display_text(
        text: str,
        max_length: int = 240,
    ) -> str:
        """
        Create concise on-screen text from narration.
        """

        text = re.sub(
            r"\s+",
            " ",
            text.strip(),
        )

        if len(text) <= max_length:
            return text

        shortened = text[
            :max_length
        ]

        last_space = shortened.rfind(
            " "
        )

        if last_space > 80:
            shortened = shortened[
                :last_space
            ]

        return shortened + "..."

    @staticmethod
    def _to_string_list(
        values: Any,
    ) -> List[str]:
        """
        Normalize a value into a list of strings.
        """

        if isinstance(
            values,
            str,
        ):
            return [
                values
            ]

        if not values:
            return []

        return [
            str(value).strip()
            for value in values
            if str(value).strip()
        ]


# Default shared scene builder.
scene_builder = SceneBuilder()