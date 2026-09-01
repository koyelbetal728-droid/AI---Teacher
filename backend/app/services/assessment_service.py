# assessment_service.py
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.question import Question
from app.schemas.assessment import (
    AssessmentAnswer,
    AssessmentCreate,
    AssessmentQuestion,
    AssessmentResult,
)
from app.services.teaching_service import TeachingService


class AssessmentService:
    """
    Handles assessment generation, answer submission,
    evaluation, and result calculation.
    """

    def __init__(
        self,
        db: Session,
        teaching_service: TeachingService | None = None,
    ):
        self.db = db
        self.teaching_service = teaching_service

    # ---------------------------------------------------------
    # Generate assessment
    # ---------------------------------------------------------

    async def create_assessment(
        self,
        assessment_data: AssessmentCreate,
    ) -> dict:
        """
        Generate an assessment for a topic.

        If the Teacher Agent is connected, AI-generated
        questions are used. Otherwise, a clear configuration
        error is returned.
        """

        if self.teaching_service is None:
            return {
                "success": False,
                "message": (
                    "Teaching service is not configured."
                ),
                "questions": [],
            }

        if self.teaching_service.teacher_agent is None:
            return {
                "success": False,
                "message": (
                    "Teacher Agent is not configured yet."
                ),
                "questions": [],
            }

        prompt = (
            f"Create {assessment_data.number_of_questions} "
            f"assessment questions about "
            f"'{assessment_data.topic}'. "
            f"Difficulty: {assessment_data.difficulty}. "
            f"Language: {assessment_data.language}. "
            "Return structured questions with question text, "
            "question type, options when applicable, and "
            "correct answers."
        )

        try:
            generated = await self.teaching_service.teacher_agent.generate_assessment(
                topic=assessment_data.topic,
                number_of_questions=(
                    assessment_data.number_of_questions
                ),
                difficulty=assessment_data.difficulty,
                language=assessment_data.language,
                prompt=prompt,
            )
        except AttributeError:
            return {
                "success": False,
                "message": (
                    "Teacher Agent does not yet support "
                    "assessment generation."
                ),
                "questions": [],
            }

        questions = self._normalize_questions(
            generated
        )

        assessment_id = str(uuid4())

        # Save generated questions.
        for item in questions:
            question = Question(
                question_id=item["question_id"],
                lesson_id=assessment_data.lesson_id,
                student_id=assessment_data.student_id,
                question_text=item["question"],
                question_type=item[
                    "question_type"
                ],
                difficulty=item[
                    "difficulty"
                ],
                options=self._serialize_options(
                    item.get("options")
                ),
                correct_answer=item.get(
                    "correct_answer"
                ),
            )

            self.db.add(question)

        self.db.commit()

        public_questions = [
            AssessmentQuestion(
                question_id=item["question_id"],
                question=item["question"],
                question_type=item[
                    "question_type"
                ],
                options=item.get("options"),
                difficulty=item["difficulty"],
            )
            for item in questions
        ]

        return {
            "success": True,
            "assessment_id": assessment_id,
            "topic": assessment_data.topic,
            "questions": public_questions,
        }

    # ---------------------------------------------------------
    # Submit assessment
    # ---------------------------------------------------------

    async def submit_assessment(
        self,
        answers: list[AssessmentAnswer],
    ) -> AssessmentResult:
        """
        Evaluate all submitted answers and calculate
        the final assessment result.
        """

        total = len(answers)

        if total == 0:
            return AssessmentResult(
                score=0,
                total_questions=0,
                correct_answers=0,
                incorrect_answers=0,
                feedback="No answers were submitted.",
            )

        correct = 0
        scores: list[int] = []
        feedback_list: list[str] = []
        misconceptions: list[str] = []

        for answer in answers:
            question = (
                self.db.query(Question)
                .filter(
                    Question.question_id
                    == answer.question_id
                )
                .first()
            )

            if question is None:
                continue

            evaluation = await self._evaluate_answer(
                question=question,
                student_answer=answer.answer,
            )

            is_correct = evaluation.get(
                "is_correct"
            )

            score = evaluation.get(
                "score"
            )

            if isinstance(score, int):
                score = max(
                    0,
                    min(score, 100),
                )
                scores.append(score)

            if is_correct is True:
                correct += 1
                question.is_correct = 1

            elif is_correct is False:
                question.is_correct = 0

            else:
                question.is_correct = None

            question.student_answer = answer.answer
            question.score = score
            question.feedback = evaluation.get(
                "feedback"
            )

            misconception = evaluation.get(
                "misconception"
            )

            if misconception:
                question.misconception = str(
                    misconception
                )
                misconceptions.append(
                    str(misconception)
                )

            feedback = evaluation.get(
                "feedback"
            )

            if feedback:
                feedback_list.append(
                    str(feedback)
                )

        self.db.commit()

        score = self._calculate_score(
            correct=correct,
            total=total,
            individual_scores=scores,
        )

        strengths = []

        if score >= 80:
            strengths.append(
                "Strong understanding of the topic."
            )

        elif score >= 60:
            strengths.append(
                "Good basic understanding."
            )

        weaknesses = []

        if score < 60:
            weaknesses.append(
                "Needs additional practice."
            )

        recommended_topics = []

        if score < 80:
            recommended_topics.append(
                "Review the concepts covered in this assessment."
            )

        feedback = self._build_feedback(
            score=score,
            feedback_list=feedback_list,
        )

        return AssessmentResult(
            score=score,
            total_questions=total,
            correct_answers=correct,
            incorrect_answers=total - correct,
            feedback=feedback,
            strengths=strengths,
            weaknesses=weaknesses,
            misconceptions=list(
                dict.fromkeys(misconceptions)
            ),
            recommended_topics=recommended_topics,
        )

    # ---------------------------------------------------------
    # Evaluate single answer
    # ---------------------------------------------------------

    async def _evaluate_answer(
        self,
        question: Question,
        student_answer: str,
    ) -> dict:
        """
        Evaluate one answer using the AI evaluator when
        available.

        Multiple-choice questions can also be checked
        directly against the stored correct answer.
        """

        expected = (
            question.correct_answer or ""
        ).strip()

        submitted = student_answer.strip()

        # Direct comparison for objective questions.
        if (
            expected
            and question.question_type
            in {
                "multiple_choice",
                "true_false",
            }
        ):
            is_correct = (
                submitted.lower()
                == expected.lower()
            )

            return {
                "is_correct": is_correct,
                "score": 100 if is_correct else 0,
                "feedback": (
                    "Correct answer."
                    if is_correct
                    else "Incorrect answer."
                ),
                "misconception": (
                    None
                    if is_correct
                    else "The submitted answer does not match the expected answer."
                ),
            }

        # AI evaluation for open-ended answers.
        if (
            self.teaching_service is not None
            and self.teaching_service.evaluator_agent
            is not None
        ):
            result = await (
                self.teaching_service.evaluator_agent.evaluate(
                    question=question.question_text,
                    student_answer=student_answer,
                    expected_answer=question.correct_answer,
                    context={},
                )
            )

            if isinstance(result, dict):
                return result

        # Safe fallback when no evaluator is available.
        return {
            "is_correct": None,
            "score": None,
            "feedback": (
                "This answer requires AI evaluation."
            ),
            "misconception": None,
        }

    # ---------------------------------------------------------
    # Normalize generated questions
    # ---------------------------------------------------------

    def _normalize_questions(
        self,
        generated: Any,
    ) -> list[dict]:
        """
        Convert different possible LLM output formats
        into one predictable internal structure.
        """

        if isinstance(generated, dict):
            generated = generated.get(
                "questions",
                [],
            )

        if not isinstance(generated, list):
            return []

        normalized = []

        for item in generated:
            if not isinstance(item, dict):
                continue

            question_text = (
                item.get("question")
                or item.get("question_text")
            )

            if not question_text:
                continue

            normalized.append(
                {
                    "question_id": (
                        item.get("question_id")
                        or str(uuid4())
                    ),
                    "question": str(
                        question_text
                    ),
                    "question_type": str(
                        item.get(
                            "question_type",
                            "multiple_choice",
                        )
                    ),
                    "options": item.get(
                        "options"
                    ),
                    "difficulty": str(
                        item.get(
                            "difficulty",
                            "medium",
                        )
                    ),
                    "correct_answer": (
                        item.get(
                            "correct_answer"
                        )
                        or item.get(
                            "answer"
                        )
                    ),
                }
            )

        return normalized

    # ---------------------------------------------------------
    # Serialize options
    # ---------------------------------------------------------

    @staticmethod
    def _serialize_options(
        options: Any,
    ) -> str | None:
        """
        Store options as JSON text in the database.
        """

        if options is None:
            return None

        import json

        try:
            return json.dumps(
                options,
                ensure_ascii=False,
            )
        except (TypeError, ValueError):
            return str(options)

    # ---------------------------------------------------------
    # Calculate final score
    # ---------------------------------------------------------

    @staticmethod
    def _calculate_score(
        correct: int,
        total: int,
        individual_scores: list[int],
    ) -> int:
        """
        Calculate final assessment score.
        """

        if individual_scores:
            return round(
                sum(individual_scores)
                / len(individual_scores)
            )

        if total == 0:
            return 0

        return round(
            (correct / total) * 100
        )

    # ---------------------------------------------------------
    # Build feedback
    # ---------------------------------------------------------

    @staticmethod
    def _build_feedback(
        score: int,
        feedback_list: list[str],
    ) -> str:
        """
        Generate a simple summary of assessment feedback.
        """

        if score >= 80:
            summary = (
                "Excellent work! You have a strong "
                "understanding of this topic."
            )

        elif score >= 60:
            summary = (
                "Good work! Review a few concepts "
                "to improve your understanding."
            )

        else:
            summary = (
                "Keep practicing. Let's review the "
                "important concepts again."
            )

        if feedback_list:
            details = " ".join(
                feedback_list[:3]
            )
            return f"{summary} {details}"

        return summary


def get_assessment_service(
    db: Session,
    teaching_service: TeachingService | None = None,
) -> AssessmentService:
    """
    Create an AssessmentService instance.
    """

    return AssessmentService(
        db=db,
        teaching_service=teaching_service,
    )