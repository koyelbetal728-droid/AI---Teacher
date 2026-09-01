# misconception_agent.py
"""
Misconception Agent.

Detects conceptual misunderstandings in a student's response,
explains the likely misconception, and suggests a corrective
teaching strategy.

All AI generation is performed through the local LLM service.
"""

from typing import Any, Dict, List, Optional

from app.ai.llm.llm_service import llm_service


class MisconceptionAgent:
    """AI agent responsible for detecting student misconceptions."""

    def __init__(self):
        self.llm = llm_service

    async def detect(
        self,
        question: str,
        student_answer: str,
        expected_answer: Optional[str] = None,
        lesson_context: Optional[str] = None,
        student_level: str = "beginner",
        language: str = "English",
    ) -> Dict[str, Any]:
        """
        Detect misconceptions from a student's answer.

        Args:
            question: Question presented to the student.
            student_answer: Student's response.
            expected_answer: Optional reference answer.
            lesson_context: Relevant lesson/RAG context.
            student_level: Student's learning level.
            language: Language for the analysis.

        Returns:
            Structured misconception analysis.
        """

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        if not student_answer or not student_answer.strip():
            raise ValueError("Student answer cannot be empty.")

        prompt = f"""
You are an educational AI that specializes in identifying
student misconceptions.

Question:
{question}

Student answer:
{student_answer}

Expected/reference answer:
{expected_answer or "No reference answer provided."}

Lesson context:
{lesson_context or "No additional lesson context provided."}

Student level:
{student_level}

Analysis language:
{language}

Analyze the student's response carefully.

Your job is NOT simply to decide whether the answer is correct.

Look for:
1. Incorrect understanding of a concept.
2. Confusion between related concepts.
3. Incorrect assumptions.
4. Misuse of terminology.
5. Logical reasoning errors.
6. Missing prerequisite knowledge.
7. Signs that the student may have guessed.

If there is no clear misconception, say so.

Do not invent a misconception when the evidence is insufficient.

Return ONLY valid JSON:

{{
    "has_misconception": false,
    "confidence": 0,
    "severity": "none",
    "misconceptions": [
        {{
            "concept": "Concept involved",
            "description": "What the student appears to misunderstand.",
            "evidence": "Evidence from the student's response.",
            "correct_understanding": "Correct understanding.",
            "likely_cause": "Possible cause.",
            "recommended_strategy": "How the teacher should address it."
        }}
    ],
    "prerequisite_gaps": [],
    "teacher_action": "Recommended immediate teaching action."
}}

Rules:
- confidence must be an integer from 0 to 100.
- severity must be one of:
  "none", "low", "medium", "high".
- has_misconception must be true only when there is
  reasonable evidence of a misconception.
"""

        try:
            result = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.2,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to detect misconception: {exc}"
            ) from exc

        return self._normalize_result(result)

    async def analyze_concept(
        self,
        concept: str,
        student_explanation: str,
        reference_explanation: Optional[str] = None,
        student_level: str = "beginner",
        language: str = "English",
    ) -> Dict[str, Any]:
        """
        Analyze a student's explanation of a concept.

        Useful when the teacher asks:
        "Explain this concept in your own words."
        """

        if not concept or not concept.strip():
            raise ValueError("Concept cannot be empty.")

        if not student_explanation or not student_explanation.strip():
            raise ValueError(
                "Student explanation cannot be empty."
            )

        prompt = f"""
Analyze a student's understanding of a concept.

Concept:
{concept}

Student explanation:
{student_explanation}

Reference explanation:
{reference_explanation or "No reference explanation provided."}

Student level:
{student_level}

Language:
{language}

Determine whether the student understands the concept.

Pay attention to:
- conceptual accuracy,
- incorrect assumptions,
- confusion with related ideas,
- missing essential information,
- incorrect terminology,
- reasoning quality.

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
    "recommended_next_step": "Next teaching step."
}}

understanding_level must be one of:
- "strong"
- "good"
- "partial"
- "weak"
- "insufficient_evidence"

confidence must be an integer from 0 to 100.
"""

        try:
            result = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.2,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to analyze concept understanding: {exc}"
            ) from exc

        return result

    async def suggest_remediation(
        self,
        misconception: Dict[str, Any],
        topic: str,
        student_level: str = "beginner",
        language: str = "English",
    ) -> Dict[str, Any]:
        """
        Generate a targeted remediation strategy for a detected
        misconception.
        """

        prompt = f"""
You are an AI Teacher creating a remediation plan.

Topic:
{topic}

Student level:
{student_level}

Detected misconception:
{misconception}

Language:
{language}

Create a short teaching intervention that helps the student
replace the incorrect mental model with the correct one.

The intervention should:
1. Explain the misconception without embarrassing the student.
2. Rebuild the concept from a simple foundation.
3. Give an intuitive example.
4. Contrast the incorrect and correct ideas.
5. Include one question to verify understanding.
6. Suggest what to teach next.

Return ONLY valid JSON:

{{
    "misconception": "Short description",
    "correction": "Correct understanding.",
    "teaching_strategy": "Recommended strategy.",
    "explanation": "Teacher explanation.",
    "example": "Simple example.",
    "contrast": {{
        "incorrect_idea": "What the student may think.",
        "correct_idea": "What is actually correct."
    }},
    "check_question": "Question to verify understanding.",
    "next_topic": "Suggested next topic."
}}
"""

        try:
            result = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.3,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to generate remediation strategy: {exc}"
            ) from exc

        return result

    async def analyze_history(
        self,
        interactions: List[Dict[str, Any]],
        topic: str,
        student_level: str = "beginner",
        language: str = "English",
    ) -> Dict[str, Any]:
        """
        Analyze multiple previous interactions to identify
        recurring misconceptions.
        """

        if not interactions:
            return {
                "has_recurring_misconceptions": False,
                "recurring_misconceptions": [],
                "recommendations": [],
            }

        prompt = f"""
You are analyzing a student's learning history.

Topic:
{topic}

Student level:
{student_level}

Language:
{language}

Previous interactions:
{interactions}

Identify recurring conceptual problems.

Look for patterns rather than isolated mistakes.

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
        "Recommended teaching action"
    ]
}}

priority must be:
- "low"
- "medium"
- "high"
"""

        try:
            result = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.2,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to analyze learning history: {exc}"
            ) from exc

        return result

    def _normalize_result(
        self,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Normalize the misconception analysis."""

        if not isinstance(result, dict):
            raise ValueError(
                "LLM returned an invalid misconception analysis."
            )

        result.setdefault("has_misconception", False)
        result.setdefault("confidence", 0)
        result.setdefault("severity", "none")
        result.setdefault("misconceptions", [])
        result.setdefault("prerequisite_gaps", [])
        result.setdefault("teacher_action", "")

        try:
            result["confidence"] = int(
                result["confidence"]
            )
        except (TypeError, ValueError):
            result["confidence"] = 0

        result["confidence"] = max(
            0,
            min(100, result["confidence"]),
        )

        valid_severity = {
            "none",
            "low",
            "medium",
            "high",
        }

        if result["severity"] not in valid_severity:
            result["severity"] = "none"

        result["has_misconception"] = bool(
            result["has_misconception"]
        )

        return result


# Default reusable instance
misconception_agent = MisconceptionAgent()