# evaluator_agent.py
"""
Evaluator Agent.

Evaluates a student's answer and provides structured feedback.

The agent determines whether the answer is correct, partially
correct, or incorrect, explains the reasoning, identifies weak
areas, and suggests what the student should do next.

All AI generation is performed through the local LLM service.
"""

from typing import Any, Dict, List, Optional

from app.ai.llm.llm_service import llm_service


class EvaluatorAgent:
    """AI agent responsible for evaluating student answers."""

    def __init__(self):
        self.llm = llm_service

    async def evaluate(
        self,
        question: str,
        student_answer: str,
        expected_answer: Optional[str] = None,
        context: Optional[str] = None,
        student_level: str = "beginner",
        language: str = "English",
    ) -> Dict[str, Any]:
        """
        Evaluate a student's answer.

        Args:
            question: Question asked to the student.
            student_answer: Student's submitted answer.
            expected_answer: Optional expected/reference answer.
            context: Relevant lesson or RAG context.
            student_level: Student's current level.
            language: Feedback language.

        Returns:
            Structured evaluation result.
        """

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        if not student_answer or not student_answer.strip():
            raise ValueError("Student answer cannot be empty.")

        prompt = f"""
You are an AI Teacher evaluating a student's answer.

Question:
{question}

Student answer:
{student_answer}

Expected/reference answer:
{expected_answer or "No exact reference answer was provided."}

Learning context:
{context or "No additional context provided."}

Student level:
{student_level}

Feedback language:
{language}

Evaluate the answer fairly.

Consider:
1. Whether the answer is correct.
2. Whether the important concepts are present.
3. Whether the reasoning is logically sound.
4. Whether there are factual or conceptual errors.
5. Whether the answer is appropriate for the student's level.

Do NOT mark an answer incorrect simply because it is worded
differently from the reference answer.

If there is insufficient information to determine correctness,
say so clearly.

Return ONLY valid JSON:

{{
    "status": "correct",
    "score": 0,
    "max_score": 100,
    "is_correct": true,
    "feedback": "Helpful feedback for the student.",
    "explanation": "Why the answer received this evaluation.",
    "strengths": [
        "Strength 1"
    ],
    "mistakes": [
        "Mistake 1"
    ],
    "missing_concepts": [
        "Missing concept"
    ],
    "corrected_answer": "A better or corrected answer.",
    "next_step": "What the student should do next."
}}

The status MUST be one of:
- "correct"
- "partially_correct"
- "incorrect"
- "uncertain"

The score must be an integer between 0 and 100.
"""

        try:
            result = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.2,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to evaluate student answer: {exc}"
            ) from exc

        return self._normalize_result(result)

    async def evaluate_quiz(
        self,
        questions: List[Dict[str, Any]],
        answers: List[Dict[str, Any]],
        context: Optional[str] = None,
        student_level: str = "beginner",
        language: str = "English",
    ) -> Dict[str, Any]:
        """
        Evaluate multiple quiz answers.

        Each question should contain at least:
            question

        Each answer should contain:
            answer

        An optional question ID can be used to match questions
        and answers.
        """

        if not questions:
            raise ValueError("Quiz must contain at least one question.")

        if not answers:
            raise ValueError("Quiz must contain student answers.")

        evaluations = []

        answer_map = {}

        for index, answer_data in enumerate(answers):
            question_id = answer_data.get("question_id", index)
            answer_map[question_id] = answer_data.get("answer", "")

        for index, question_data in enumerate(questions):
            question_id = question_data.get("id", index)

            student_answer = answer_map.get(question_id, "")

            evaluation = await self.evaluate(
                question=question_data.get("question", ""),
                student_answer=student_answer,
                expected_answer=question_data.get("answer"),
                context=context,
                student_level=student_level,
                language=language,
            )

            evaluations.append(
                {
                    "question_id": question_id,
                    "question": question_data.get("question", ""),
                    "student_answer": student_answer,
                    "evaluation": evaluation,
                }
            )

        correct_count = sum(
            1
            for item in evaluations
            if item["evaluation"].get("is_correct") is True
        )

        total_questions = len(evaluations)

        score = round(
            (correct_count / total_questions) * 100
        ) if total_questions else 0

        return {
            "total_questions": total_questions,
            "correct_answers": correct_count,
            "score": score,
            "evaluations": evaluations,
            "summary": self._build_quiz_summary(
                score,
                correct_count,
                total_questions,
            ),
        }

    async def compare_answer(
        self,
        question: str,
        student_answer: str,
        reference_answer: str,
        language: str = "English",
    ) -> Dict[str, Any]:
        """
        Compare a student's answer with a reference answer.

        This is useful for short-answer questions where an exact
        string match would not be appropriate.
        """

        prompt = f"""
Compare a student's answer with the reference answer.

Question:
{question}

Student answer:
{student_answer}

Reference answer:
{reference_answer}

Language:
{language}

Focus on meaning rather than exact wording.

Return ONLY valid JSON:

{{
    "is_equivalent": true,
    "similarity_score": 0,
    "missing_information": [],
    "incorrect_information": [],
    "feedback": "Feedback for the student."
}}

similarity_score must be an integer from 0 to 100.
"""

        try:
            result = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.2,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to compare answers: {exc}"
            ) from exc

        return result

    async def generate_feedback(
        self,
        question: str,
        student_answer: str,
        evaluation: Optional[Dict[str, Any]] = None,
        language: str = "English",
    ) -> str:
        """
        Generate a natural-language feedback message.
        """

        evaluation = evaluation or {}

        prompt = f"""
You are a supportive AI Teacher.

Question:
{question}

Student answer:
{student_answer}

Evaluation:
{evaluation}

Write concise, constructive feedback in {language}.

The feedback should:
- acknowledge what the student did well,
- explain what needs improvement,
- avoid discouraging language,
- give one clear next step.

Do not unnecessarily repeat the entire answer.
"""

        try:
            return await self.llm.generate(
                prompt=prompt,
                temperature=0.3,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to generate feedback: {exc}"
            ) from exc

    def _normalize_result(
        self,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Normalize and validate the LLM evaluation result.
        """

        if not isinstance(result, dict):
            raise ValueError("LLM returned an invalid evaluation.")

        result.setdefault("status", "uncertain")
        result.setdefault("score", 0)
        result.setdefault("max_score", 100)
        result.setdefault("is_correct", False)
        result.setdefault("feedback", "")
        result.setdefault("explanation", "")
        result.setdefault("strengths", [])
        result.setdefault("mistakes", [])
        result.setdefault("missing_concepts", [])
        result.setdefault("corrected_answer", "")
        result.setdefault("next_step", "")

        valid_statuses = {
            "correct",
            "partially_correct",
            "incorrect",
            "uncertain",
        }

        if result["status"] not in valid_statuses:
            result["status"] = "uncertain"

        try:
            result["score"] = int(result["score"])
        except (TypeError, ValueError):
            result["score"] = 0

        result["score"] = max(
            0,
            min(100, result["score"]),
        )

        result["is_correct"] = bool(
            result["is_correct"]
        )

        return result

    @staticmethod
    def _build_quiz_summary(
        score: int,
        correct_count: int,
        total_questions: int,
    ) -> str:
        """Create a simple human-readable quiz summary."""

        if total_questions == 0:
            return "No questions were evaluated."

        if score >= 90:
            return (
                f"Excellent work! You answered "
                f"{correct_count} out of {total_questions} correctly."
            )

        if score >= 70:
            return (
                f"Good work! You answered "
                f"{correct_count} out of {total_questions} correctly. "
                f"Review the questions you missed."
            )

        if score >= 50:
            return (
                f"You answered {correct_count} out of "
                f"{total_questions} correctly. "
                f"Let's review the weaker areas together."
            )

        return (
            f"You answered {correct_count} out of "
            f"{total_questions} correctly. "
            f"Don't worry—let's revisit the fundamentals "
            f"and try again."
        )


# Default reusable instance
evaluator_agent = EvaluatorAgent()