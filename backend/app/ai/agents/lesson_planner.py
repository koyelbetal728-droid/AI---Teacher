# lesson_planner.py
"""
Lesson Planner Agent.

Creates structured, personalized lesson plans from a topic and
the student's learning context.

The agent uses the local LLM service and does not depend on
paid external AI APIs.
"""

from typing import Any, Dict, List, Optional

from app.ai.llm.llm_service import llm_service


class LessonPlannerAgent:
    """AI agent responsible for generating lesson plans."""

    def __init__(self):
        self.llm = llm_service

    async def create_lesson_plan(
        self,
        topic: str,
        student_level: str = "beginner",
        learning_goal: Optional[str] = None,
        duration_minutes: int = 30,
        language: str = "English",
        student_context: Optional[Dict[str, Any]] = None,
        available_material: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a structured lesson plan.

        Args:
            topic: Topic the student wants to learn.
            student_level: beginner, intermediate, or advanced.
            learning_goal: Specific goal of the lesson.
            duration_minutes: Target lesson duration.
            language: Language for the lesson.
            student_context: Optional information about the student.
            available_material: Relevant extracted material from RAG.

        Returns:
            Structured lesson plan as a dictionary.
        """

        if not topic or not topic.strip():
            raise ValueError("Topic cannot be empty.")

        if duration_minutes <= 0:
            raise ValueError("Duration must be greater than zero.")

        context = student_context or {}

        prompt = f"""
Create a personalized lesson plan for an AI Teacher.

Topic:
{topic}

Student level:
{student_level}

Learning goal:
{learning_goal or "Understand the topic clearly and practically."}

Lesson duration:
{duration_minutes} minutes

Teaching language:
{language}

Student context:
{context}

Available learning material:
{available_material or "No additional material provided."}

Design the lesson for an interactive AI teacher.

The lesson should:
1. Start with a short introduction.
2. Explain concepts from simple to more difficult.
3. Include examples.
4. Include questions to check understanding.
5. Include one practical activity or exercise.
6. Include a short assessment.
7. End with a concise recap.
8. Adapt explanations to the student's level.

Return ONLY valid JSON using this structure:

{{
    "title": "Lesson title",
    "topic": "{topic}",
    "level": "{student_level}",
    "language": "{language}",
    "duration_minutes": {duration_minutes},
    "learning_objectives": [
        "objective 1",
        "objective 2"
    ],
    "sections": [
        {{
            "title": "Section title",
            "duration_minutes": 5,
            "type": "explanation",
            "content": "What the teacher should explain.",
            "examples": [
                "Example 1"
            ],
            "check_questions": [
                "Question 1"
            ]
        }}
    ],
    "practice_activity": {{
        "instructions": "Activity instructions",
        "expected_outcome": "Expected result"
    }},
    "assessment": {{
        "questions": [
            {{
                "question": "Question text",
                "type": "short_answer",
                "answer": "Expected answer"
            }}
        ]
    }},
    "recap": [
        "Key point 1",
        "Key point 2"
    ]
}}
"""

        try:
            lesson_plan = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.3,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to generate lesson plan: {exc}"
            ) from exc

        return self._normalize_plan(
            lesson_plan,
            topic=topic,
            student_level=student_level,
            language=language,
            duration_minutes=duration_minutes,
        )

    async def create_from_document(
        self,
        topic: str,
        document_context: str,
        student_level: str = "beginner",
        duration_minutes: int = 30,
        language: str = "English",
    ) -> Dict[str, Any]:
        """
        Create a lesson plan based on uploaded learning material.

        This is useful when the student uploads a textbook, PDF,
        notes, or other study material.
        """

        return await self.create_lesson_plan(
            topic=topic,
            student_level=student_level,
            duration_minutes=duration_minutes,
            language=language,
            available_material=document_context,
        )

    async def create_adaptive_plan(
        self,
        topic: str,
        student_level: str,
        previous_performance: Optional[Dict[str, Any]] = None,
        misconceptions: Optional[List[str]] = None,
        duration_minutes: int = 30,
        language: str = "English",
    ) -> Dict[str, Any]:
        """
        Create a lesson plan adapted to previous student performance.

        The previous performance and detected misconceptions are
        passed to the planner so the next lesson can focus on
        weak areas.
        """

        context = {
            "previous_performance": previous_performance or {},
            "known_misconceptions": misconceptions or [],
        }

        return await self.create_lesson_plan(
            topic=topic,
            student_level=student_level,
            duration_minutes=duration_minutes,
            language=language,
            student_context=context,
        )

    def _normalize_plan(
        self,
        plan: Dict[str, Any],
        topic: str,
        student_level: str,
        language: str,
        duration_minutes: int,
    ) -> Dict[str, Any]:
        """
        Ensure the generated lesson plan has the expected fields.
        """

        if not isinstance(plan, dict):
            raise ValueError("LLM returned an invalid lesson plan.")

        plan.setdefault("title", f"Learning {topic}")
        plan.setdefault("topic", topic)
        plan.setdefault("level", student_level)
        plan.setdefault("language", language)
        plan.setdefault("duration_minutes", duration_minutes)
        plan.setdefault("learning_objectives", [])
        plan.setdefault("sections", [])
        plan.setdefault(
            "practice_activity",
            {
                "instructions": "",
                "expected_outcome": "",
            },
        )
        plan.setdefault(
            "assessment",
            {
                "questions": [],
            },
        )
        plan.setdefault("recap", [])

        return plan


# Default reusable instance
lesson_planner_agent = LessonPlannerAgent()