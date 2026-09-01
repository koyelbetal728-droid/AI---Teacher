# progress_service.py
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.progress import Progress


class ProgressService:
    """
    Handles student learning progress, scores,
    completed lessons, and performance summaries.
    """

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------
    # Create progress record
    # ---------------------------------------------------------

    def create_progress(
        self,
        student_id: int,
        lesson_id: int | None = None,
        topic: str | None = None,
        score: int | None = None,
        completed: bool = False,
    ) -> Progress:
        """
        Create a new learning-progress record.
        """

        progress = Progress(
            student_id=student_id,
            lesson_id=lesson_id,
            topic=topic,
            score=score,
            completed=completed,
        )

        self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)

        return progress

    # ---------------------------------------------------------
    # Get progress by ID
    # ---------------------------------------------------------

    def get_progress(
        self,
        progress_id: int,
    ) -> Progress | None:
        """
        Return one progress record.
        """

        return (
            self.db.query(Progress)
            .filter(
                Progress.id == progress_id
            )
            .first()
        )

    # ---------------------------------------------------------
    # Get student progress
    # ---------------------------------------------------------

    def get_student_progress(
        self,
        student_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Progress]:
        """
        Return the learning history of a student.
        """

        return (
            self.db.query(Progress)
            .filter(
                Progress.student_id == student_id
            )
            .order_by(
                Progress.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    # ---------------------------------------------------------
    # Get lesson progress
    # ---------------------------------------------------------

    def get_lesson_progress(
        self,
        lesson_id: int,
    ) -> list[Progress]:
        """
        Return progress records belonging to a lesson.
        """

        return (
            self.db.query(Progress)
            .filter(
                Progress.lesson_id == lesson_id
            )
            .order_by(
                Progress.created_at.asc()
            )
            .all()
        )

    # ---------------------------------------------------------
    # Update progress
    # ---------------------------------------------------------

    def update_progress(
        self,
        progress_id: int,
        score: int | None = None,
        completed: bool | None = None,
        topic: str | None = None,
    ) -> Progress | None:
        """
        Update an existing progress record.
        """

        progress = self.get_progress(
            progress_id
        )

        if progress is None:
            return None

        if score is not None:
            progress.score = max(
                0,
                min(score, 100),
            )

        if completed is not None:
            progress.completed = completed

        if topic is not None:
            progress.topic = topic

        progress.updated_at = datetime.now(
            timezone.utc
        )

        self.db.commit()
        self.db.refresh(progress)

        return progress

    # ---------------------------------------------------------
    # Record lesson completion
    # ---------------------------------------------------------

    def record_lesson_completion(
        self,
        student_id: int,
        lesson_id: int,
        topic: str | None = None,
        score: int | None = None,
    ) -> Progress:
        """
        Record that a student completed a lesson.
        """

        progress = Progress(
            student_id=student_id,
            lesson_id=lesson_id,
            topic=topic,
            score=(
                max(0, min(score, 100))
                if score is not None
                else None
            ),
            completed=True,
        )

        self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)

        return progress

    # ---------------------------------------------------------
    # Calculate student statistics
    # ---------------------------------------------------------

    def get_student_statistics(
        self,
        student_id: int,
    ) -> dict[str, Any]:
        """
        Calculate a student's overall learning statistics.
        """

        records = self.get_student_progress(
            student_id=student_id,
            skip=0,
            limit=10000,
        )

        if not records:
            return {
                "student_id": student_id,
                "total_lessons": 0,
                "completed_lessons": 0,
                "average_score": None,
                "best_score": None,
                "lowest_score": None,
                "completion_rate": 0,
                "total_topics": 0,
            }

        scores = [
            record.score
            for record in records
            if isinstance(
                record.score,
                (int, float),
            )
        ]

        completed_lessons = sum(
            1
            for record in records
            if record.completed
        )

        topics = {
            record.topic
            for record in records
            if record.topic
        }

        average_score = (
            sum(scores) / len(scores)
            if scores
            else None
        )

        completion_rate = (
            completed_lessons
            / len(records)
            * 100
        )

        return {
            "student_id": student_id,
            "total_lessons": len(records),
            "completed_lessons": completed_lessons,
            "average_score": (
                round(average_score, 2)
                if average_score is not None
                else None
            ),
            "best_score": (
                max(scores)
                if scores
                else None
            ),
            "lowest_score": (
                min(scores)
                if scores
                else None
            ),
            "completion_rate": round(
                completion_rate,
                2,
            ),
            "total_topics": len(topics),
        }

    # ---------------------------------------------------------
    # Topic performance
    # ---------------------------------------------------------

    def get_topic_performance(
        self,
        student_id: int,
    ) -> list[dict[str, Any]]:
        """
        Calculate performance separately for each topic.
        """

        records = self.get_student_progress(
            student_id=student_id,
            skip=0,
            limit=10000,
        )

        topic_data: dict[str, list[int]] = {}

        for record in records:
            if (
                not record.topic
                or not isinstance(
                    record.score,
                    (int, float),
                )
            ):
                continue

            topic_data.setdefault(
                record.topic,
                [],
            ).append(
                int(record.score)
            )

        result = []

        for topic, scores in topic_data.items():
            average = (
                sum(scores) / len(scores)
            )

            result.append(
                {
                    "topic": topic,
                    "attempts": len(scores),
                    "average_score": round(
                        average,
                        2,
                    ),
                    "best_score": max(scores),
                    "lowest_score": min(scores),
                }
            )

        result.sort(
            key=lambda item: item[
                "average_score"
            ],
            reverse=True,
        )

        return result

    # ---------------------------------------------------------
    # Identify weak topics
    # ---------------------------------------------------------

    def get_weak_topics(
        self,
        student_id: int,
        threshold: int = 60,
    ) -> list[str]:
        """
        Return topics where the student's average score
        is below the specified threshold.
        """

        performance = self.get_topic_performance(
            student_id
        )

        return [
            item["topic"]
            for item in performance
            if item["average_score"] < threshold
        ]

    # ---------------------------------------------------------
    # Identify strong topics
    # ---------------------------------------------------------

    def get_strong_topics(
        self,
        student_id: int,
        threshold: int = 80,
    ) -> list[str]:
        """
        Return topics where the student's average score
        is above the specified threshold.
        """

        performance = self.get_topic_performance(
            student_id
        )

        return [
            item["topic"]
            for item in performance
            if item["average_score"] >= threshold
        ]

    # ---------------------------------------------------------
    # Learning summary
    # ---------------------------------------------------------

    def get_learning_summary(
        self,
        student_id: int,
    ) -> dict[str, Any]:
        """
        Build a complete learning summary that can be
        consumed by the personalization system.
        """

        statistics = self.get_student_statistics(
            student_id
        )

        topic_performance = (
            self.get_topic_performance(
                student_id
            )
        )

        weak_topics = self.get_weak_topics(
            student_id
        )

        strong_topics = self.get_strong_topics(
            student_id
        )

        return {
            "student_id": student_id,
            "statistics": statistics,
            "topic_performance": topic_performance,
            "strong_topics": strong_topics,
            "weak_topics": weak_topics,
        }

    # ---------------------------------------------------------
    # Delete progress
    # ---------------------------------------------------------

    def delete_progress(
        self,
        progress_id: int,
    ) -> bool:
        """
        Delete a progress record.
        """

        progress = self.get_progress(
            progress_id
        )

        if progress is None:
            return False

        self.db.delete(progress)
        self.db.commit()

        return True


def get_progress_service(
    db: Session,
) -> ProgressService:
    """
    Create a ProgressService instance.
    """

    return ProgressService(db)