# misconception_prompt.py
"""
Prompts for the Misconception Agent.

This module contains reusable prompts for:

- Detecting conceptual misconceptions
- Analyzing a student's understanding
- Creating remediation strategies
- Finding recurring misconceptions
"""

from typing import Any, Dict, List, Optional


MISCONCEPTION_SYSTEM_PROMPT = """
You are an expert AI Teacher specializing in identifying
student misconceptions.

Your goal is to understand WHY a student's answer may be
incorrect, not merely determine whether it is incorrect.

Evaluation principles:

1. Look for conceptual misunderstandings.
2. Distinguish misconceptions from simple mistakes.
3. Look for confusion between related concepts.
4. Identify incorrect assumptions.
5. Identify missing prerequisite knowledge.
6. Use evidence from the student's response.
7. Do not invent a misconception without evidence.
8. Consider the student's current learning level.
9. Explain the correct mental model clearly.
10. Recommend a teaching strategy to correct the misunderstanding.

Never embarrass or blame the student.

When structured JSON is requested, return valid JSON only.
"""


def build_misconception_detection_prompt(
    question: str,
    student_answer: str,
    expected_answer: Optional[str] = None,
    lesson_context: Optional[str] = None,
    student_level: str = "beginner",
    language: str = "English",
) -> str:
    """
    Build a prompt for detecting misconceptions in a student's answer.
    """

    return f"""
Analyze the student's answer for possible misconceptions.

QUESTION
{question}

STUDENT ANSWER
{student_answer}

EXPECTED / REFERENCE ANSWER
{expected_answer or "No reference answer provided."}

LESSON CONTEXT
{lesson_context or "No lesson context provided."}

STUDENT LEVEL
{student_level}

LANGUAGE
{language}

ANALYSIS REQUIREMENTS

Look for:

1. Incorrect conceptual understanding.
2. Confusion between related concepts.
3. Incorrect assumptions.
4. Misuse of terminology.
5. Logical reasoning errors.
6. Missing prerequisite knowledge.
7. Patterns suggesting the student guessed.

Important:

- A wrong answer does not automatically mean there is a misconception.
- A small calculation or spelling error may simply be a mistake.
- Different wording should not be treated as a misconception if
  the underlying concept is correct.
- Do not invent a misconception without evidence.
- If there is insufficient evidence, report that clearly.

Return ONLY valid JSON:

{{
    "has_misconception": false,
    "confidence": 0,
    "severity": "none",

    "misconceptions": [
        {{
            "concept": "Concept involved",
            "description": "What the student misunderstands.",
            "evidence": "Evidence from the student's answer.",
            "correct_understanding": "Correct mental model.",
            "likely_cause": "Possible cause.",
            "recommended_strategy": "Teaching strategy."
        }}
    ],

    "prerequisite_gaps": [],

    "teacher_action": "Recommended immediate action."
}}

CONFIDENCE
Must be an integer from 0 to 100.

SEVERITY
Must be one of:

- "none"
- "low"
- "medium"
- "high"
"""


def build_concept_analysis_prompt(
    concept: str,
    student_explanation: str,
    reference_explanation: Optional[str] = None,
    student_level: str = "beginner",
    language: str = "English",
) -> str:
    """
    Build a prompt for analyzing a student's explanation of
    a particular concept.
    """

    return f"""
Analyze the student's understanding of a concept.

CONCEPT
{concept}

STUDENT EXPLANATION
{student_explanation}

REFERENCE EXPLANATION
{reference_explanation or "No reference explanation provided."}

STUDENT LEVEL
{student_level}

LANGUAGE
{language}

Determine:

1. What the student understands correctly.
2. What the student misunderstands.
3. What important information is missing.
4. Whether there are conceptual misconceptions.
5. Whether prerequisite knowledge appears to be missing.

Do not penalize the student for using different wording
when the underlying meaning is correct.

Return ONLY valid JSON:

{{
    "understanding_level": "good",
    "confidence": 0,
    "has_misconception": false,

    "misconceptions": [],

    "what_student_understands": [],

    "what_student_is_missing": [],

    "recommended_next_step": "Recommended teaching action."
}}

UNDERSTANDING LEVEL

Must be one of:

- "strong"
- "good"
- "partial"
- "weak"
- "insufficient_evidence"

CONFIDENCE
Must be an integer from 0 to 100.
"""


def build_remediation_prompt(
    misconception: Dict[str, Any],
    topic: str,
    student_level: str = "beginner",
    language: str = "English",
) -> str:
    """
    Build a prompt for creating a targeted remediation lesson.
    """

    return f"""
Create a targeted teaching intervention for a student who
has a conceptual misconception.

TOPIC
{topic}

STUDENT LEVEL
{student_level}

DETECTED MISCONCEPTION
{misconception}

LANGUAGE
{language}

REMEDIATION REQUIREMENTS

The intervention should:

1. Explain the misconception respectfully.
2. Explain the correct concept.
3. Rebuild the idea from a simple foundation.
4. Use an intuitive example.
5. Contrast the incorrect and correct mental models.
6. Avoid unnecessary advanced terminology.
7. Include a question to verify understanding.
8. Suggest what should be learned next.

The goal is to replace the incorrect mental model with a
correct and useful understanding.

Do not simply provide the answer.

Return ONLY valid JSON:

{{
    "misconception": "Short description.",
    "correction": "Correct understanding.",

    "teaching_strategy": "Recommended teaching strategy.",

    "explanation": "Teacher explanation.",

    "example": "Simple example.",

    "contrast": {{
        "incorrect_idea": "What the student may currently believe.",
        "correct_idea": "What the student should understand."
    }},

    "check_question": "Question to verify understanding.",

    "next_topic": "Suggested next topic."
}}
"""


def build_history_analysis_prompt(
    interactions: List[Dict[str, Any]],
    topic: str,
    student_level: str = "beginner",
    language: str = "English",
) -> str:
    """
    Build a prompt for detecting recurring misconceptions
    across multiple student interactions.
    """

    return f"""
Analyze the student's learning history for recurring
misconceptions.

TOPIC
{topic}

STUDENT LEVEL
{student_level}

LANGUAGE
{language}

PREVIOUS INTERACTIONS
{interactions}

ANALYSIS REQUIREMENTS

Look for recurring patterns such as:

- The same concept being misunderstood repeatedly.
- The same reasoning error appearing in multiple answers.
- Repeated confusion between related concepts.
- Missing prerequisite knowledge.
- Concepts that repeatedly require teacher correction.

Do not treat every individual mistake as a recurring
misconception.

Only identify a recurring misconception when there is
reasonable evidence across the interactions.

Return ONLY valid JSON:

{{
    "has_recurring_misconceptions": false,

    "recurring_misconceptions": [
        {{
            "concept": "Concept",
            "description": "Recurring misunderstanding.",
            "frequency": 0,
            "evidence": [
                "Evidence from interaction"
            ],
            "priority": "medium"
        }}
    ],

    "strengths": [],

    "recommendations": [
        "Recommended teaching action."
    ]
}}

PRIORITY

Must be one of:

- "low"
- "medium"
- "high"
"""


def build_prerequisite_gap_prompt(
    topic: str,
    student_response: str,
    known_prerequisites: Optional[List[str]] = None,
    student_level: str = "beginner",
    language: str = "English",
) -> str:
    """
    Build a prompt for identifying prerequisite knowledge gaps.
    """

    return f"""
Determine whether the student is missing prerequisite knowledge
needed to understand a topic.

TOPIC
{topic}

STUDENT RESPONSE
{student_response}

KNOWN PREREQUISITES
{known_prerequisites or "No prerequisite list provided."}

STUDENT LEVEL
{student_level}

LANGUAGE
{language}

Identify only prerequisite gaps supported by the student's
response.

Do not assume a student lacks knowledge simply because they
made one isolated mistake.

Return ONLY valid JSON:

{{
    "has_prerequisite_gap": false,

    "gaps": [
        {{
            "concept": "Prerequisite concept",
            "reason": "Evidence that this may be missing.",
            "importance": "high"
        }}
    ],

    "recommended_order": [
        "Prerequisite to teach first"
    ],

    "teacher_action": "Recommended action."
}}

IMPORTANCE

Must be one of:

- "low"
- "medium"
- "high"
"""


def build_misconception_check_prompt(
    concept: str,
    verification_question: str,
    student_answer: str,
    student_level: str = "beginner",
    language: str = "English",
) -> str:
    """
    Build a prompt for checking whether a previously detected
    misconception has been corrected.
    """

    return f"""
Determine whether the student's previous misconception has
been corrected.

CONCEPT
{concept}

VERIFICATION QUESTION
{verification_question}

STUDENT ANSWER
{student_answer}

STUDENT LEVEL
{student_level}

LANGUAGE
{language}

Evaluate the student's current understanding.

Return ONLY valid JSON:

{{
    "misconception_resolved": true,
    "confidence": 0,
    "evidence": "Evidence supporting the decision.",
    "remaining_confusion": [],
    "recommended_action": "Continue to the next concept."
}}

CONFIDENCE
Must be an integer from 0 to 100.

If the student's answer does not provide enough evidence,
set misconception_resolved to false and explain why.
"""