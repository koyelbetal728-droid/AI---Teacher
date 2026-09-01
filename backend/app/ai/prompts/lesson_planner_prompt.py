# lesson_planner_prompt.py
"""
Prompts for the Lesson Planner Agent.

This module keeps lesson-planning instructions separate from
the agent implementation so prompts can be updated without
changing the core agent logic.
"""

from typing import Any, Dict, Optional


LESSON_PLANNER_SYSTEM_PROMPT = """
You are an expert AI Teacher and lesson planner.

Your goal is to create clear, structured, personalized,
and interactive lessons.

Teaching principles:

1. Adapt explanations to the student's level.
2. Move from simple concepts to more difficult concepts.
3. Use practical examples whenever useful.
4. Include questions that check understanding.
5. Include opportunities for practice.
6. Include a short assessment.
7. End with a useful recap.
8. Use the student's learning material when provided.
9. Do not invent facts that are not supported by the
   provided learning material when the material is being used.
10. Keep the lesson realistic for the requested duration.

Return structured information when JSON output is requested.
"""


def build_lesson_planner_prompt(
    topic: str,
    student_level: str = "beginner",
    learning_goal: Optional[str] = None,
    duration_minutes: int = 30,
    language: str = "English",
    student_context: Optional[Dict[str, Any]] = None,
    available_material: Optional[str] = None,
) -> str:
    """
    Build a complete lesson-planning prompt.

    Args:
        topic: Topic to teach.
        student_level: Student's current learning level.
        learning_goal: Desired learning outcome.
        duration_minutes: Target lesson duration.
        language: Language used for the lesson.
        student_context: Optional student-specific context.
        available_material: Optional content from uploaded
            learning material or RAG retrieval.

    Returns:
        A formatted prompt ready for the LLM.
    """

    context = student_context or {}

    return f"""
Create a personalized lesson plan.

TOPIC
{topic}

STUDENT LEVEL
{student_level}

LEARNING GOAL
{learning_goal or "Understand the topic clearly and apply the core concepts."}

DURATION
{duration_minutes} minutes

LANGUAGE
{language}

STUDENT CONTEXT
{context}

AVAILABLE LEARNING MATERIAL
{available_material or "No additional learning material was provided."}

LESSON REQUIREMENTS

Create a lesson that:

1. Begins with a short introduction.
2. Introduces prerequisite concepts when necessary.
3. Explains the main concepts progressively.
4. Uses simple explanations appropriate for the student level.
5. Includes relevant examples.
6. Includes interactive understanding checks.
7. Includes a practical activity.
8. Includes a short assessment.
9. Ends with a concise recap.
10. Fits approximately within the requested duration.

If learning material is provided, use it as the primary
source for the lesson content.

Do not invent information that conflicts with the provided
material.

Return ONLY valid JSON using exactly this general structure:

{{
    "title": "Lesson title",
    "topic": "{topic}",
    "level": "{student_level}",
    "language": "{language}",
    "duration_minutes": {duration_minutes},

    "learning_objectives": [
        "Objective 1",
        "Objective 2"
    ],

    "sections": [
        {{
            "title": "Section title",
            "duration_minutes": 5,
            "type": "explanation",
            "content": "What the teacher should teach.",
            "examples": [
                "Example 1"
            ],
            "check_questions": [
                "Question to check understanding"
            ]
        }}
    ],

    "practice_activity": {{
        "instructions": "Instructions for the student.",
        "expected_outcome": "Expected learning outcome."
    }},

    "assessment": {{
        "questions": [
            {{
                "question": "Assessment question",
                "type": "short_answer",
                "answer": "Expected answer"
            }}
        ]
    }},

    "recap": [
        "Important point 1",
        "Important point 2"
    ]
}}
"""


def build_adaptive_lesson_prompt(
    topic: str,
    student_level: str,
    previous_performance: Optional[Dict[str, Any]] = None,
    misconceptions: Optional[list] = None,
    duration_minutes: int = 30,
    language: str = "English",
) -> str:
    """
    Build a prompt for an adaptive lesson.

    The lesson is adjusted using previous performance and
    detected misconceptions.
    """

    return f"""
Create an adaptive lesson for a student.

TOPIC
{topic}

STUDENT LEVEL
{student_level}

PREVIOUS PERFORMANCE
{previous_performance or "No previous performance data available."}

DETECTED MISCONCEPTIONS
{misconceptions or "No known misconceptions."}

DURATION
{duration_minutes} minutes

LANGUAGE
{language}

ADAPTATION RULES

- Spend additional time on concepts the student struggles with.
- Address known misconceptions explicitly.
- Avoid repeating concepts the student has already mastered
  unless they are necessary prerequisites.
- Use simpler explanations when previous answers indicate
  confusion.
- Increase difficulty gradually when the student performs well.
- Include at least one question that verifies whether a
  previous misconception has been corrected.

Return ONLY valid JSON:

{{
    "title": "Adaptive lesson title",
    "topic": "{topic}",
    "level": "{student_level}",
    "duration_minutes": {duration_minutes},
    "focus_areas": [
        "Area requiring attention"
    ],
    "learning_objectives": [
        "Objective 1"
    ],
    "sections": [
        {{
            "title": "Section title",
            "duration_minutes": 5,
            "type": "remediation",
            "content": "Teaching content.",
            "examples": [],
            "check_questions": []
        }}
    ],
    "practice_activity": {{
        "instructions": "Practice instructions.",
        "expected_outcome": "Expected outcome."
    }},
    "assessment": {{
        "questions": []
    }},
    "recap": []
}}
"""


def build_quick_lesson_prompt(
    topic: str,
    student_level: str = "beginner",
    duration_minutes: int = 10,
    language: str = "English",
) -> str:
    """
    Build a lightweight prompt for a short lesson.

    Useful for quick-learning sessions where a full lesson
    plan would be unnecessary.
    """

    return f"""
Create a short interactive lesson.

Topic:
{topic}

Student level:
{student_level}

Duration:
{duration_minutes} minutes

Language:
{language}

The lesson should contain:

1. A simple introduction.
2. The most important concepts.
3. One or two examples.
4. One understanding question.
5. One short practice task.
6. A final recap.

Keep the lesson focused and avoid unnecessary details.

Return ONLY valid JSON:

{{
    "title": "Short lesson title",
    "topic": "{topic}",
    "duration_minutes": {duration_minutes},
    "introduction": "Introduction",
    "key_concepts": [
        "Concept 1",
        "Concept 2"
    ],
    "examples": [
        "Example 1"
    ],
    "check_question": "Understanding question",
    "practice_task": "Practice task",
    "recap": [
        "Key takeaway"
    ]
}}
"""