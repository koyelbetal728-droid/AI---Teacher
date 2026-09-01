# teaching_service.py
from typing import Any


class TeachingService:
    """
    Coordinates the AI Teacher's teaching flow.

    This service is intentionally kept independent from
    the API layer so that the teacher agent, RAG pipeline,
    assessment system, and personalization system can
    be connected cleanly later.
    """

    def __init__(
        self,
        teacher_agent: Any | None = None,
        rag_pipeline: Any | None = None,
        evaluator_agent: Any | None = None,
        misconception_agent: Any | None = None,
    ):
        self.teacher_agent = teacher_agent
        self.rag_pipeline = rag_pipeline
        self.evaluator_agent = evaluator_agent
        self.misconception_agent = misconception_agent

    # ---------------------------------------------------------
    # Prepare teaching context
    # ---------------------------------------------------------

    async def prepare_context(
        self,
        topic: str,
        question: str | None = None,
        document_id: str | None = None,
        student_profile: dict | None = None,
    ) -> dict:
        """
        Prepare the context required by the AI Teacher.

        RAG retrieval will be connected here later.
        """

        context = {
            "topic": topic,
            "question": question,
            "document_id": document_id,
            "student_profile": student_profile or {},
            "retrieved_context": [],
        }

        if self.rag_pipeline is not None:
            try:
                retrieved_context = await self.rag_pipeline.retrieve(
                    query=question or topic,
                    document_id=document_id,
                )

                context["retrieved_context"] = (
                    retrieved_context or []
                )

            except Exception:
                # Keep teaching available even if retrieval
                # is temporarily unavailable.
                context["retrieved_context"] = []

        return context

    # ---------------------------------------------------------
    # Generate explanation
    # ---------------------------------------------------------

    async def explain(
        self,
        topic: str,
        student_profile: dict | None = None,
        question: str | None = None,
        document_id: str | None = None,
    ) -> dict:
        """
        Generate a teaching explanation for a topic.
        """

        context = await self.prepare_context(
            topic=topic,
            question=question,
            document_id=document_id,
            student_profile=student_profile,
        )

        if self.teacher_agent is None:
            return {
                "success": False,
                "message": (
                    "Teacher Agent is not configured yet."
                ),
                "topic": topic,
                "context": context,
            }

        response = await self.teacher_agent.explain(
            topic=topic,
            context=context,
            student_profile=student_profile or {},
        )

        return {
            "success": True,
            "topic": topic,
            "response": response,
            "context": context,
        }

    # ---------------------------------------------------------
    # Answer student question
    # ---------------------------------------------------------

    async def answer_question(
        self,
        question: str,
        topic: str | None = None,
        student_profile: dict | None = None,
        document_id: str | None = None,
    ) -> dict:
        """
        Answer a student's question using the AI Teacher.
        """

        context = await self.prepare_context(
            topic=topic or "general",
            question=question,
            document_id=document_id,
            student_profile=student_profile,
        )

        if self.teacher_agent is None:
            return {
                "success": False,
                "message": (
                    "Teacher Agent is not configured yet."
                ),
                "question": question,
            }

        response = await self.teacher_agent.answer(
            question=question,
            context=context,
            student_profile=student_profile or {},
        )

        return {
            "success": True,
            "question": question,
            "response": response,
            "context": context,
        }

    # ---------------------------------------------------------
    # Evaluate student answer
    # ---------------------------------------------------------

    async def evaluate_answer(
        self,
        question: str,
        student_answer: str,
        expected_answer: str | None = None,
        context: dict | None = None,
    ) -> dict:
        """
        Evaluate a student's answer.

        The Evaluator Agent will perform the actual AI
        evaluation once it is connected.
        """

        if self.evaluator_agent is None:
            return {
                "success": False,
                "message": (
                    "Evaluator Agent is not configured yet."
                ),
                "question": question,
                "student_answer": student_answer,
            }

        result = await self.evaluator_agent.evaluate(
            question=question,
            student_answer=student_answer,
            expected_answer=expected_answer,
            context=context or {},
        )

        return {
            "success": True,
            "evaluation": result,
        }

    # ---------------------------------------------------------
    # Detect misconception
    # ---------------------------------------------------------

    async def detect_misconception(
        self,
        question: str,
        student_answer: str,
        evaluation: dict | None = None,
    ) -> dict:
        """
        Detect possible misconceptions in a student's answer.
        """

        if self.misconception_agent is None:
            return {
                "success": False,
                "message": (
                    "Misconception Agent is not configured yet."
                ),
                "misconception": None,
            }

        result = await self.misconception_agent.detect(
            question=question,
            student_answer=student_answer,
            evaluation=evaluation or {},
        )

        return {
            "success": True,
            "misconception": result,
        }

    # ---------------------------------------------------------
    # Generate next teaching action
    # ---------------------------------------------------------

    async def next_action(
        self,
        evaluation: dict | None = None,
        misconception: dict | None = None,
        student_profile: dict | None = None,
    ) -> dict:
        """
        Decide what the AI Teacher should do next.

        This is the foundation of adaptive teaching.
        """

        evaluation = evaluation or {}
        misconception = misconception or {}
        student_profile = student_profile or {}

        is_correct = evaluation.get(
            "is_correct"
        )

        has_misconception = bool(
            misconception.get("misconception")
        )

        if has_misconception:
            action = "clarify_misconception"

        elif is_correct is False:
            action = "explain_again"

        elif is_correct is True:
            action = "increase_difficulty"

        else:
            action = "ask_follow_up"

        return {
            "success": True,
            "action": action,
            "evaluation": evaluation,
            "misconception": misconception,
            "student_profile": student_profile,
        }


def get_teaching_service(
    teacher_agent: Any | None = None,
    rag_pipeline: Any | None = None,
    evaluator_agent: Any | None = None,
    misconception_agent: Any | None = None,
) -> TeachingService:
    """
    Create a TeachingService instance.
    """

    return TeachingService(
        teacher_agent=teacher_agent,
        rag_pipeline=rag_pipeline,
        evaluator_agent=evaluator_agent,
        misconception_agent=misconception_agent,
    )