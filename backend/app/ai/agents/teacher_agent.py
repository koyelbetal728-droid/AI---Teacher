# teacher_agent.py
"""
Teacher Agent.

Handles the actual interactive teaching experience.

The Teacher Agent uses the lesson plan, retrieved learning
material, student context, and the student's questions to
generate teacher-like explanations and responses.

All AI generation is performed through the local LLM service.
"""

from typing import Any, Dict, List, Optional

from app.ai.llm.llm_service import llm_service


class TeacherAgent:
    """AI agent responsible for interactive teaching."""

    def __init__(self):
        self.llm = llm_service

    async def teach(
        self,
        topic: str,
        question: str,
        lesson_context: Optional[str] = None,
        student_level: str = "beginner",
        language: str = "English",
        student_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Answer a student's question like a personal teacher.

        Args:
            topic: Current learning topic.
            question: Student's question.
            lesson_context: Relevant lesson/RAG context.
            student_level: Student's current level.
            language: Response language.
            student_context: Additional student information.

        Returns:
            Structured teacher response.
        """

        if not question or not question.strip():
            raise ValueError("Student question cannot be empty.")

        context = student_context or {}

        prompt = f"""
You are a patient and interactive AI Teacher.

Current topic:
{topic}

Student level:
{student_level}

Teaching language:
{language}

Student context:
{context}

Current lesson context:
{lesson_context or "No additional lesson context available."}

Student question:
{question}

Teach the student instead of simply giving a short answer.

Your response should:
1. Directly address the student's question.
2. Explain the concept at an appropriate level.
3. Use simple language where possible.
4. Give an example when useful.
5. Avoid unnecessary complexity.
6. Ask a short follow-up question if it helps check understanding.
7. If the provided lesson context does not contain enough information,
   clearly say that instead of inventing facts.

Return ONLY valid JSON:

{{
    "answer": "Main explanation for the student.",
    "explanation": "A clearer step-by-step explanation.",
    "examples": [
        "Example 1"
    ],
    "key_points": [
        "Important point 1",
        "Important point 2"
    ],
    "follow_up_question": "A short question to check understanding.",
    "needs_more_context": false
}}
"""

        try:
            response = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.3,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Teacher agent failed to generate a response: {exc}"
            ) from exc

        return self._normalize_response(response)

    async def explain(
        self,
        topic: str,
        concept: str,
        student_level: str = "beginner",
        language: str = "English",
        lesson_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Explain a specific concept in a teaching-oriented manner.
        """

        prompt = f"""
You are an AI Teacher explaining a concept to a student.

Topic:
{topic}

Concept:
{concept}

Student level:
{student_level}

Language:
{language}

Learning material:
{lesson_context or "No specific learning material provided."}

Explain the concept progressively:

1. Start with an intuitive explanation.
2. Explain the core idea.
3. Give a simple example.
4. Give a slightly deeper example if appropriate.
5. Mention common mistakes.
6. Finish with a short understanding question.

Do not invent information that conflicts with the provided
learning material.

Return ONLY valid JSON:

{{
    "concept": "{concept}",
    "simple_explanation": "Simple explanation.",
    "detailed_explanation": "Detailed explanation.",
    "examples": [
        "Example 1",
        "Example 2"
    ],
    "common_mistakes": [
        "Mistake 1"
    ],
    "check_question": "Question for the student."
}}
"""

        try:
            response = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.3,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to explain concept: {exc}"
            ) from exc

        return response

    async def continue_lesson(
        self,
        lesson_plan: Dict[str, Any],
        current_section: int,
        student_response: Optional[str] = None,
        student_level: str = "beginner",
        language: str = "English",
    ) -> Dict[str, Any]:
        """
        Continue an interactive lesson from the current section.

        The student's previous response can be provided so the
        teacher can adapt the next explanation.
        """

        sections: List[Dict[str, Any]] = lesson_plan.get(
            "sections",
            [],
        )

        if not sections:
            raise ValueError("Lesson plan contains no sections.")

        if current_section < 0 or current_section >= len(sections):
            raise ValueError("Invalid lesson section index.")

        section = sections[current_section]

        prompt = f"""
You are continuing an interactive AI teaching session.

Lesson:
{lesson_plan.get("title", "Untitled Lesson")}

Topic:
{lesson_plan.get("topic", "")}

Student level:
{student_level}

Language:
{language}

Current section:
{section}

Previous student response:
{student_response or "The student has not answered yet."}

Teach the current section interactively.

If the student response shows confusion:
- explain the concept more simply,
- provide another example,
- address the likely misunderstanding.

If the student understands:
- continue naturally,
- increase difficulty slightly when appropriate.

Return ONLY valid JSON:

{{
    "teaching_message": "Message shown to the student.",
    "explanation": "Additional explanation if needed.",
    "example": "Useful example.",
    "check_question": "Question to check understanding.",
    "student_understood": true,
    "suggested_next_section": {current_section + 1}
}}
"""

        try:
            response = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.3,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to continue lesson: {exc}"
            ) from exc

        return response

    async def summarize_lesson(
        self,
        lesson_content: str,
        student_level: str = "beginner",
        language: str = "English",
    ) -> Dict[str, Any]:
        """
        Generate a student-friendly lesson summary.
        """

        prompt = f"""
Summarize the following lesson for a student.

Student level:
{student_level}

Language:
{language}

Lesson content:
{lesson_content}

Create a concise but useful summary.

Return ONLY valid JSON:

{{
    "summary": "Short lesson summary.",
    "key_points": [
        "Key point 1",
        "Key point 2"
    ],
    "important_terms": [
        {{
            "term": "Term",
            "meaning": "Simple meaning"
        }}
    ],
    "remember_this": [
        "Important thing to remember"
    ]
}}
"""

        try:
            response = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.2,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to summarize lesson: {exc}"
            ) from exc

        return response

    def _normalize_response(
        self,
        response: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Ensure the teacher response contains the expected fields.
        """

        if not isinstance(response, dict):
            raise ValueError("LLM returned an invalid teacher response.")

        response.setdefault("answer", "")
        response.setdefault("explanation", "")
        response.setdefault("examples", [])
        response.setdefault("key_points", [])
        response.setdefault("follow_up_question", "")
        response.setdefault("needs_more_context", False)

        return response


# Default reusable instance
teacher_agent = TeacherAgent()