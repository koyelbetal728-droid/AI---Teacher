# lesson_service.py
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.lesson import Lesson
from app.schemas.lesson import LessonCreate, LessonUpdate


class LessonService:
    """
    Handles lesson creation, retrieval, updating,
    and lesson lifecycle management.
    """

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------
    # Create lesson
    # ---------------------------------------------------------

    def create_lesson(
        self,
        lesson_data: LessonCreate,
    ) -> Lesson:
        """
        Create a new personalized lesson.

        The actual AI-generated lesson plan will be added
        later by the Lesson Planner Agent.
        """

        lesson = Lesson(
            lesson_id=str(uuid4()),
            student_id=lesson_data.student_id,
            document_id=lesson_data.document_id,
            topic=lesson_data.topic,
            learner_level=lesson_data.learner_level,
            language=lesson_data.language,
            learning_goal=lesson_data.learning_goal,
            available_time=lesson_data.available_time,
            teaching_style=lesson_data.teaching_style,
            status="created",
            current_step=0,
        )

        self.db.add(lesson)
        self.db.commit()
        self.db.refresh(lesson)

        return lesson

    # ---------------------------------------------------------
    # Get lesson
    # ---------------------------------------------------------

    def get_lesson(
        self,
        lesson_id: str,
    ) -> Lesson | None:
        """
        Find a lesson using its public lesson ID.
        """

        return (
            self.db.query(Lesson)
            .filter(
                Lesson.lesson_id == lesson_id
            )
            .first()
        )

    # ---------------------------------------------------------
    # Get lessons for student
    # ---------------------------------------------------------

    def get_student_lessons(
        self,
        student_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Lesson]:
        """
        Return lessons belonging to a student.
        """

        return (
            self.db.query(Lesson)
            .filter(
                Lesson.student_id == student_id
            )
            .order_by(
                Lesson.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    # ---------------------------------------------------------
    # Update lesson
    # ---------------------------------------------------------

    def update_lesson(
        self,
        lesson_id: str,
        lesson_data: LessonUpdate,
    ) -> Lesson | None:
        """
        Update an existing lesson.
        """

        lesson = self.get_lesson(
            lesson_id
        )

        if lesson is None:
            return None

        update_data = lesson_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(
                lesson,
                field,
                value,
            )

        self.db.commit()
        self.db.refresh(lesson)

        return lesson

    # ---------------------------------------------------------
    # Update lesson plan
    # ---------------------------------------------------------

    def save_lesson_plan(
        self,
        lesson_id: str,
        lesson_plan: str,
    ) -> Lesson | None:
        """
        Save an AI-generated lesson plan.
        """

        lesson = self.get_lesson(
            lesson_id
        )

        if lesson is None:
            return None

        lesson.lesson_plan = lesson_plan
        lesson.status = "ready"

        self.db.commit()
        self.db.refresh(lesson)

        return lesson

    # ---------------------------------------------------------
    # Move lesson to next step
    # ---------------------------------------------------------

    def next_step(
        self,
        lesson_id: str,
    ) -> Lesson | None:
        """
        Move the student to the next lesson step.
        """

        lesson = self.get_lesson(
            lesson_id
        )

        if lesson is None:
            return None

        lesson.current_step += 1

        self.db.commit()
        self.db.refresh(lesson)

        return lesson

    # ---------------------------------------------------------
    # Start lesson
    # ---------------------------------------------------------

    def start_lesson(
        self,
        lesson_id: str,
    ) -> Lesson | None:
        """
        Mark a lesson as in progress.
        """

        lesson = self.get_lesson(
            lesson_id
        )

        if lesson is None:
            return None

        lesson.status = "in_progress"

        self.db.commit()
        self.db.refresh(lesson)

        return lesson

    # ---------------------------------------------------------
    # Complete lesson
    # ---------------------------------------------------------

    def complete_lesson(
        self,
        lesson_id: str,
        score: int | None = None,
    ) -> Lesson | None:
        """
        Mark a lesson as completed.
        """

        lesson = self.get_lesson(
            lesson_id
        )

        if lesson is None:
            return None

        lesson.status = "completed"

        if score is not None:
            lesson.score = max(
                0,
                min(score, 100),
            )

        self.db.commit()
        self.db.refresh(lesson)

        return lesson

    # ---------------------------------------------------------
    # Delete lesson
    # ---------------------------------------------------------

    def delete_lesson(
        self,
        lesson_id: str,
    ) -> bool:
        """
        Delete a lesson.
        """

        lesson = self.get_lesson(
            lesson_id
        )

        if lesson is None:
            return False

        self.db.delete(lesson)
        self.db.commit()

        return True


def get_lesson_service(
    db: Session,
) -> LessonService:
    """
    Create a LessonService instance.
    """

    return LessonService(db)