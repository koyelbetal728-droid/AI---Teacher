# visual_planner.py
"""
Visual planning service for the AI Teacher.

This module decides what type of visual should accompany
a teacher explanation.

It does not generate the visual itself. Instead, it creates
a structured visual plan that can be passed to:

- Diagram generators
- Math visualizers
- Code visualizers
- Image generation systems
- Video/scene builders

The planner is intentionally lightweight and can work with
the local LLM service.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from app.ai.llm.llm_service import llm_service


class VisualPlanner:
    """
    Plans educational visuals based on lesson content.
    """

    VALID_VISUAL_TYPES = {
        "none",
        "diagram",
        "flowchart",
        "timeline",
        "comparison",
        "table",
        "formula",
        "math_graph",
        "code",
        "code_flow",
        "concept_map",
        "illustration",
        "process",
        "chart",
    }

    def __init__(self) -> None:
        self.llm = llm_service

    async def plan(
        self,
        topic: str,
        explanation: str,
        student_level: str = "beginner",
        subject: Optional[str] = None,
        language: str = "English",
    ) -> Dict[str, Any]:
        """
        Create a visual plan for an explanation.
        """

        prompt = f"""
You are an educational visual planner.

Determine whether a visual would improve the following
teacher explanation.

SUBJECT
{subject or "Not specified"}

TOPIC
{topic}

EXPLANATION
{explanation}

STUDENT LEVEL
{student_level}

LANGUAGE
{language}

Choose the most useful visual type.

Available visual types:

- none
- diagram
- flowchart
- timeline
- comparison
- table
- formula
- math_graph
- code
- code_flow
- concept_map
- illustration
- process
- chart

Rules:

1. Use a visual only when it improves understanding.
2. Keep visuals appropriate for the student's level.
3. Do not add decorative visuals without educational value.
4. For processes, prefer flowcharts or process diagrams.
5. For relationships, prefer diagrams or concept maps.
6. For numerical data, prefer charts or tables.
7. For mathematics, prefer formulas or graphs where useful.
8. For programming, prefer code or code-flow visuals.
9. Keep the visual simple and focused.

Return ONLY valid JSON:

{{
    "should_generate": true,
    "visual_type": "diagram",
    "title": "Visual title",
    "purpose": "Why this visual helps.",
    "description": "Detailed description of the visual.",
    "key_elements": [],
    "relationships": [],
    "generation_prompt": "Prompt for generating the visual.",
    "estimated_complexity": "low"
}}
"""

        result = await self.llm.generate_json(
            prompt=prompt,
            system_prompt=(
                "You are an expert educational visual planner. "
                "Return valid JSON only."
            ),
            temperature=0.2,
        )

        return self._normalize_plan(
            result,
            topic=topic,
        )

    async def plan_lesson_visuals(
        self,
        lesson_content: List[Dict[str, Any]],
        student_level: str = "beginner",
        language: str = "English",
    ) -> List[Dict[str, Any]]:
        """
        Create visual plans for multiple lesson sections.
        """

        plans: List[Dict[str, Any]] = []

        for section in lesson_content:
            topic = str(
                section.get(
                    "topic",
                    section.get("title", "Lesson section"),
                )
            )

            explanation = str(
                section.get(
                    "explanation",
                    section.get("content", ""),
                )
            )

            if not explanation.strip():
                continue

            plan = await self.plan(
                topic=topic,
                explanation=explanation,
                student_level=student_level,
                subject=section.get("subject"),
                language=language,
            )

            plans.append(plan)

        return plans

    async def plan_for_question(
        self,
        question: str,
        answer: str,
        student_level: str = "beginner",
        language: str = "English",
    ) -> Dict[str, Any]:
        """
        Determine whether an educational visual would help
        answer a student's question.
        """

        return await self.plan(
            topic=question,
            explanation=answer,
            student_level=student_level,
            language=language,
        )

    def choose_visual_type(
        self,
        topic: str,
        explanation: str,
    ) -> str:
        """
        Quickly select a visual type using lightweight
        rule-based heuristics.

        This method does not call the LLM.
        """

        text = f"{topic} {explanation}".lower()

        math_terms = {
            "equation",
            "equations",
            "function",
            "graph",
            "geometry",
            "algebra",
            "calculus",
            "formula",
            "derivative",
            "integral",
        }

        code_terms = {
            "code",
            "program",
            "programming",
            "function",
            "class",
            "algorithm",
            "python",
            "javascript",
            "java",
            "loop",
        }

        process_terms = {
            "process",
            "steps",
            "workflow",
            "pipeline",
            "how it works",
            "procedure",
        }

        comparison_terms = {
            "difference",
            "compare",
            "comparison",
            "versus",
            " vs ",
            "advantages",
            "disadvantages",
        }

        if any(term in text for term in code_terms):
            return "code_flow"

        if any(term in text for term in math_terms):
            return "math_graph"

        if any(term in text for term in process_terms):
            return "flowchart"

        if any(term in text for term in comparison_terms):
            return "comparison"

        return "diagram"

    def build_generation_prompt(
        self,
        plan: Dict[str, Any],
    ) -> str:
        """
        Convert a visual plan into a clean generation prompt.
        """

        visual_type = plan.get(
            "visual_type",
            "diagram",
        )

        title = plan.get(
            "title",
            "Educational Visual",
        )

        description = plan.get(
            "description",
            "",
        )

        key_elements = plan.get(
            "key_elements",
            [],
        )

        relationships = plan.get(
            "relationships",
            [],
        )

        elements_text = ", ".join(
            str(item)
            for item in key_elements
        )

        relationships_text = ", ".join(
            str(item)
            for item in relationships
        )

        return f"""
Create a clean educational {visual_type}.

TITLE:
{title}

DESCRIPTION:
{description}

KEY ELEMENTS:
{elements_text or "Use only elements necessary to explain the concept."}

RELATIONSHIPS:
{relationships_text or "Show relationships clearly where applicable."}

STYLE:

- Educational
- Clean
- Minimal
- Easy to understand
- Suitable for students
- Clear labels
- No unnecessary decoration
- High readability
- Avoid visual clutter

The visual should explain the concept rather than merely
decorate the lesson.
""".strip()

    def _normalize_plan(
        self,
        result: Any,
        topic: str,
    ) -> Dict[str, Any]:
        """
        Normalize and validate an LLM-generated visual plan.
        """

        if isinstance(result, str):
            result = self._parse_json(result)

        if not isinstance(result, dict):
            result = {}

        visual_type = str(
            result.get(
                "visual_type",
                "none",
            )
        ).strip().lower()

        if visual_type not in self.VALID_VISUAL_TYPES:
            visual_type = "none"

        should_generate = result.get(
            "should_generate",
            visual_type != "none",
        )

        if isinstance(
            should_generate,
            str,
        ):
            should_generate = (
                should_generate.lower()
                in {"true", "yes", "1"}
            )

        complexity = str(
            result.get(
                "estimated_complexity",
                "low",
            )
        ).lower()

        if complexity not in {
            "low",
            "medium",
            "high",
        }:
            complexity = "low"

        return {
            "should_generate": bool(
                should_generate
            ),
            "visual_type": visual_type,
            "title": str(
                result.get(
                    "title",
                    topic,
                )
            ),
            "purpose": str(
                result.get(
                    "purpose",
                    "",
                )
            ),
            "description": str(
                result.get(
                    "description",
                    "",
                )
            ),
            "key_elements": self._normalize_list(
                result.get(
                    "key_elements",
                    [],
                )
            ),
            "relationships": self._normalize_list(
                result.get(
                    "relationships",
                    [],
                )
            ),
            "generation_prompt": str(
                result.get(
                    "generation_prompt",
                    "",
                )
            ),
            "estimated_complexity": complexity,
        }

    @staticmethod
    def _normalize_list(
        value: Any,
    ) -> List[str]:
        """
        Normalize a value into a list of strings.
        """

        if value is None:
            return []

        if isinstance(value, list):
            return [
                str(item).strip()
                for item in value
                if str(item).strip()
            ]

        if isinstance(value, str):
            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

        return [str(value)]

    @staticmethod
    def _parse_json(
        value: str,
    ) -> Dict[str, Any]:
        """
        Safely parse JSON returned as plain text by an LLM.
        """

        text = value.strip()

        # Remove markdown JSON fences.
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\s*```$",
            "",
            text,
            flags=re.IGNORECASE,
        )

        try:
            parsed = json.loads(text)

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:
            pass

        return {}


# Default shared visual planner.
visual_planner = VisualPlanner()