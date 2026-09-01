# teacher_prompt.py
"""
Prompts for the Teacher Agent.

This module contains reusable prompts for interactive teaching,
concept explanations, lesson continuation, and lesson summaries.
"""

from typing import Any, Dict, Optional


TEACHER_SYSTEM_PROMPT = """
You are a patient, knowledgeable, and supportive AI Teacher.

Your teaching style should be:

1. Clear and easy to understand.
2. Appropriate for the student's current level.
3. Interactive rather than one-directional.
4. Encouraging without giving empty praise.
5. Step-by-step when a concept is difficult.
6. Practical, using examples whenever useful.
7. Honest when the available information is insufficient.

Teaching rules:

- Do not unnecessarily overwhelm beginners.
- Do not assume the student already knows advanced concepts.
- Explain important terminology before using it extensively.
- Use the student's learning material when it is provided.
- Do not invent facts that are unsupported by the provided material.
- If the student is confused, simplify the explanation.
- If the student understands a concept, gradually increase difficulty.
- Ask questions that help verify understanding.
- Correct mistakes respectfully.
- Encourage the student to reason instead of simply memorizing answers.

When structured JSON is requested, return valid JSON only.
"""


def build_teacher_prompt(
    topic: str,
    question: str,
    student_level: str = "beginner",
    language: str = "English",
    lesson_context: Optional[str] = None,
    student_context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Build a prompt for answering a student's question.
    """

    return f"""
Teach the student about the following question.

TOPIC
{topic}

STUDENT QUESTION
{question}

STUDENT LEVEL
{student_level}

LANGUAGE
{language}

STUDENT CONTEXT
{student_context or "No additional student context provided."}

LESSON CONTEXT
{lesson_context or "No additional lesson context provided."}

TEACHING INSTRUCTIONS

1. Directly answer the student's question.
2. Explain the underlying concept.
3. Use simple language appropriate for the student's level.
4. Break difficult ideas into smaller steps.
5. Give an example when useful.
6. Mention important terms and their meanings.
7. If the lesson context is insufficient, clearly state that.
8. Do not invent information that conflicts with the lesson context.
9. End with a short question when appropriate to check understanding.

Return ONLY valid JSON:

{{
    "answer": "Direct answer to the student.",
    "explanation": "Step-by-step explanation.",
    "examples": [
        "Example 1"
    ],
    "key_points": [
        "Important point 1",
        "Important point 2"
    ],
    "follow_up_question": "Question to check understanding.",
    "needs_more_context": false
}}
"""


def build_concept_explanation_prompt(
    topic: str,
    concept: str,
    student_level: str = "beginner",
    language: str = "English",
    lesson_context: Optional[str] = None,
) -> str:
    """
    Build a prompt for explaining a specific concept.
    """

    return f"""
Explain a concept as a personal AI Teacher.

TOPIC
{topic}

CONCEPT
{concept}

STUDENT LEVEL
{student_level}

LANGUAGE
{language}

AVAILABLE LESSON MATERIAL
{lesson_context or "No lesson material provided."}

EXPLANATION STRUCTURE

Start with:
1. An intuitive explanation.
2. The core idea.
3. A simple real-world or technical example.
4. A slightly deeper explanation if appropriate.
5. Common mistakes or misunderstandings.
6. A short question to check understanding.

Adapt the explanation to the student's level.

If lesson material is provided, use it as the primary
source and do not contradict it.

Return ONLY valid JSON:

{{
    "concept": "{concept}",
    "simple_explanation": "Simple explanation.",
    "core_idea": "Main idea.",
    "detailed_explanation": "Detailed explanation.",
    "examples": [
        "Example 1",
        "Example 2"
    ],
    "common_mistakes": [
        "Common mistake"
    ],
    "check_question": "Understanding question."
}}
"""


def build_lesson_continuation_prompt(
    lesson_title: str,
    topic: str,
    current_section: Dict[str, Any],
    student_level: str = "beginner",
    language: str = "English",
    previous_student_response: Optional[str] = None,
) -> str:
    """
    Build a prompt for continuing an interactive lesson.
    """

    return f"""
Continue an interactive teaching session.

LESSON
{lesson_title}

TOPIC
{topic}

STUDENT LEVEL
{student_level}

LANGUAGE
{language}

CURRENT SECTION
{current_section}

PREVIOUS STUDENT RESPONSE
{previous_student_response or "No response yet."}

TEACHING BEHAVIOR

If the student appears confused:
- simplify the concept,
- use a different explanation,
- provide another example,
- address the likely misunderstanding.

If the student appears to understand:
- continue the lesson,
- introduce the next relevant idea,
- gradually increase difficulty when appropriate.

If the student's response contains a misconception:
- correct it respectfully,
- explain why,
- ask a question that checks whether the correction was understood.

Return ONLY valid JSON:

{{
    "teaching_message": "Message shown to the student.",
    "explanation": "Additional explanation.",
    "example": "Helpful example.",
    "check_question": "Question for the student.",
    "student_understood": true,
    "needs_remediation": false,
    "suggested_next_section": 1
}}
"""


def build_lesson_summary_prompt(
    lesson_content: str,
    student_level: str = "beginner",
    language: str = "English",
) -> str:
    """
    Build a prompt for generating a student-friendly summary.
    """

    return f"""
Create a concise summary of the following lesson.

STUDENT LEVEL
{student_level}

LANGUAGE
{language}

LESSON CONTENT
{lesson_content}

SUMMARY REQUIREMENTS

The summary should:
1. Focus on the most important concepts.
2. Use language appropriate for the student.
3. Explain important terminology simply.
4. Avoid unnecessary details.
5. Highlight what the student should remember.
6. Not introduce information that was not present in the lesson.

Return ONLY valid JSON:

{{
    "summary": "Short student-friendly summary.",
    "key_points": [
        "Key point 1",
        "Key point 2"
    ],
    "important_terms": [
        {{
            "term": "Important term",
            "meaning": "Simple meaning"
        }}
    ],
    "remember_this": [
        "Important takeaway"
    ]
}}
"""


def build_hint_prompt(
    question: str,
    student_attempt: Optional[str] = None,
    topic: Optional[str] = None,
    student_level: str = "beginner",
    language: str = "English",
) -> str:
    """
    Build a prompt for generating a hint without directly
    revealing the complete answer.
    """

    return f"""
You are helping a student solve a problem.

TOPIC
{topic or "Not specified"}

QUESTION
{question}

STUDENT LEVEL
{student_level}

STUDENT ATTEMPT
{student_attempt or "The student has not attempted the problem yet."}

LANGUAGE
{language}

Give a useful hint that helps the student reason toward
the answer.

Rules:
- Do not immediately reveal the complete answer.
- Point toward the relevant concept or method.
- If the student's attempt is incorrect, identify the
  direction of the mistake without solving everything.
- Keep the hint appropriate for the student's level.

Return ONLY valid JSON:

{{
    "hint": "Helpful hint.",
    "concept_to_consider": "Relevant concept.",
    "next_step": "What the student should try next."
}}
"""


def build_encouragement_prompt(
    student_action: str,
    result: Optional[str] = None,
    language: str = "English",
) -> str:
    """
    Build a short supportive teacher response.

    This is useful for interactive moments such as completing
    a difficult question or making progress after a mistake.
    """

    return f"""
Generate a short and natural teacher response.

Student action:
{student_action}

Result:
{result or "No result provided."}

Language:
{language}

The response should:
- sound supportive,
- remain genuine,
- avoid exaggerated praise,
- encourage the student to continue learning.

Return ONLY the teacher's response text.
"""