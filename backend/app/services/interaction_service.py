# interaction_service.py
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.question import Question
from app.services.teaching_service import TeachingService


class InteractionService:
    """
    Handles the interaction between the student and
    the AI Teacher.
    """

    def __init__(
        self,
        db: Session,
        teaching_service: TeachingService,
    ):
        self.db = db
        self.teaching_service = teaching_service

    # ---------------------------------------------------------
    # Ask AI Teacher
    # ---------------------------------------------------------

    async def ask_teacher(
        self,
        question: str,
        topic: str | None = None,
        student_id: int | None = None,
        lesson_id: int | None = None,
        document_id: str | None = None,
        student_profile: dict | None = None,
    ) -> dict:
        """
        Send a student's question to the AI Teacher.
        """

        result = await self.teaching_service.answer_question(
            question=question,
            topic=topic,
            student_profile=student_profile,
            document_id=document_id,
        )

        return {
            "success": result.get("success", False),
            "question": question,
            "topic": topic,
            "student_id": student_id,
            "lesson_id": lesson_id,
            "response": result.get("response"),
            "context": result.get("context", {}),
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }

    # ---------------------------------------------------------
    # Evaluate answer
    # ---------------------------------------------------------

    async def submit_answer(
        self,
        question_id: str,
        student_answer: str,
    ) -> dict:
        """
        Evaluate a student's answer to an existing question.
        """

        question = (
            self.db.query(Question)
            .filter(
                Question.question_id == question_id
            )
            .first()
        )

        if question is None:
            return {
                "success": False,
                "message": "Question not found.",
            }

        evaluation = await self.teaching_service.evaluate_answer(
            question=question.question_text,
            student_answer=student_answer,
            expected_answer=question.correct_answer,
        )

        evaluation_data = evaluation.get(
            "evaluation",
            {},
        )

        if isinstance(evaluation_data, dict):
            question.student_answer = student_answer

            question.is_correct = (
                1
                if evaluation_data.get("is_correct") is True
                else 0
                if evaluation_data.get("is_correct") is False
                else None
            )

            question.score = evaluation_data.get(
                "score"
            )

            question.feedback = evaluation_data.get(
                "feedback"
            )

            self.db.commit()
            self.db.refresh(question)

        misconception = (
            await self.teaching_service.detect_misconception(
                question=question.question_text,
                student_answer=student_answer,
                evaluation=evaluation_data,
            )
        )

        misconception_data = misconception.get(
            "misconception"
        )

        if misconception_data:
            question.misconception = str(
                misconception_data
            )

            self.db.commit()
            self.db.refresh(question)

        next_action = (
            await self.teaching_service.next_action(
                evaluation=evaluation_data,
                misconception={
                    "misconception": misconception_data
                },
            )
        )

        return {
            "success": True,
            "question_id": question.question_id,
            "student_answer": student_answer,
            "evaluation": evaluation_data,
            "misconception": misconception_data,
            "next_action": next_action.get(
                "action"
            ),
            "feedback": question.feedback,
            "score": question.score,
        }

    # ---------------------------------------------------------
    # Get question
    # ---------------------------------------------------------

    def get_question(
        self,
        question_id: str,
    ) -> Question | None:
        """
        Retrieve a question by its public question ID.
        """

        return (
            self.db.query(Question)
            .filter(
                Question.question_id == question_id
            )
            .first()
        )

    # ---------------------------------------------------------
    # Get student questions
    # ---------------------------------------------------------

    def get_student_questions(
        self,
        student_id: int,
        lesson_id: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Question]:
        """
        Return questions answered or attempted by a student.
        """

        query = (
            self.db.query(Question)
            .filter(
                Question.student_id == student_id
            )
        )

        if lesson_id is not None:
            query = query.filter(
                Question.lesson_id == lesson_id
            )

        return (
            query
            .order_by(
                Question.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )


def get_interaction_service(
    db: Session,
    teaching_service: TeachingService,
) -> InteractionService:
    """
    Create an InteractionService instance.
    """

    return InteractionService(
        db=db,
        teaching_service=teaching_service,
    )