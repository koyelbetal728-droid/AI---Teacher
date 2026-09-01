# personalization_service.py
from typing import Any


class PersonalizationService:
    """
    Handles student-specific learning decisions.

    This service uses the student's previous performance,
    learning preferences, misconceptions, and progress to
    customize the teaching experience.
    """

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # Build student profile
    # ---------------------------------------------------------

    def build_learning_profile(
        self,
        student: Any | None = None,
        progress: list[Any] | None = None,
        assessment_results: list[Any] | None = None,
    ) -> dict:
        """
        Build a normalized learning profile that can be
        passed to the AI Teacher and other AI agents.
        """

        profile = {
            "student_id": getattr(
                student,
                "id",
                None,
            ),
            "name": getattr(
                student,
                "name",
                None,
            ),
            "learning_level": getattr(
                student,
                "learning_level",
                "beginner",
            ),
            "preferred_language": getattr(
                student,
                "preferred_language",
                "english",
            ),
            "learning_style": getattr(
                student,
                "learning_style",
                None,
            ),
            "progress": [],
            "assessment_results": [],
            "strengths": [],
            "weaknesses": [],
            "misconceptions": [],
        }

        if progress:
            profile["progress"] = [
                self._serialize_item(item)
                for item in progress
            ]

        if assessment_results:
            profile["assessment_results"] = [
                self._serialize_item(item)
                for item in assessment_results
            ]

        profile.update(
            self._analyze_performance(
                profile["progress"],
                profile["assessment_results"],
            )
        )

        return profile

    # ---------------------------------------------------------
    # Analyze performance
    # ---------------------------------------------------------

    def _analyze_performance(
        self,
        progress: list[dict],
        assessment_results: list[dict],
    ) -> dict:
        """
        Analyze previous learning performance.
        """

        strengths: list[str] = []
        weaknesses: list[str] = []
        misconceptions: list[str] = []

        scores = []

        for result in assessment_results:
            score = result.get("score")

            if isinstance(score, (int, float)):
                scores.append(float(score))

            result_misconceptions = result.get(
                "misconceptions",
                [],
            )

            if isinstance(
                result_misconceptions,
                list,
            ):
                misconceptions.extend(
                    str(item)
                    for item in result_misconceptions
                )

        average_score = (
            sum(scores) / len(scores)
            if scores
            else None
        )

        if average_score is not None:
            if average_score >= 80:
                strengths.append(
                    "Strong overall academic performance."
                )

            elif average_score >= 60:
                strengths.append(
                    "Moderate understanding with room for improvement."
                )

            else:
                weaknesses.append(
                    "Needs additional revision and guided practice."
                )

        topics_with_progress = {}

        for item in progress:
            topic = item.get("topic")

            if not topic:
                continue

            topics_with_progress.setdefault(
                topic,
                [],
            ).append(item)

        for topic, records in topics_with_progress.items():
            topic_scores = [
                record.get("score")
                for record in records
                if isinstance(
                    record.get("score"),
                    (int, float),
                )
            ]

            if not topic_scores:
                continue

            topic_average = (
                sum(topic_scores)
                / len(topic_scores)
            )

            if topic_average >= 80:
                strengths.append(
                    f"Good understanding of {topic}."
                )

            elif topic_average < 60:
                weaknesses.append(
                    f"Needs more practice in {topic}."
                )

        return {
            "average_score": (
                round(average_score, 2)
                if average_score is not None
                else None
            ),
            "strengths": list(
                dict.fromkeys(strengths)
            ),
            "weaknesses": list(
                dict.fromkeys(weaknesses)
            ),
            "misconceptions": list(
                dict.fromkeys(misconceptions)
            ),
        }

    # ---------------------------------------------------------
    # Recommend difficulty
    # ---------------------------------------------------------

    def recommend_difficulty(
        self,
        recent_scores: list[int | float] | None = None,
        current_level: str = "beginner",
    ) -> str:
        """
        Recommend the next difficulty level.
        """

        if not recent_scores:
            return current_level

        average = (
            sum(recent_scores)
            / len(recent_scores)
        )

        levels = [
            "beginner",
            "intermediate",
            "advanced",
        ]

        current_level = (
            current_level.lower()
        )

        if current_level not in levels:
            current_level = "beginner"

        index = levels.index(
            current_level
        )

        if average >= 85:
            index = min(
                index + 1,
                len(levels) - 1,
            )

        elif average < 50:
            index = max(
                index - 1,
                0,
            )

        return levels[index]

    # ---------------------------------------------------------
    # Recommend learning approach
    # ---------------------------------------------------------

    def recommend_teaching_strategy(
        self,
        profile: dict,
    ) -> dict:
        """
        Decide how the AI Teacher should teach the student.
        """

        weaknesses = profile.get(
            "weaknesses",
            [],
        )

        misconceptions = profile.get(
            "misconceptions",
            [],
        )

        learning_style = profile.get(
            "learning_style"
        )

        strategy = {
            "explanation_depth": "normal",
            "use_examples": True,
            "use_visuals": True,
            "ask_follow_up_questions": True,
            "repeat_concepts": False,
            "pace": "normal",
        }

        if misconceptions:
            strategy["explanation_depth"] = (
                "detailed"
            )
            strategy["repeat_concepts"] = True
            strategy["pace"] = "slow"

        elif len(weaknesses) >= 3:
            strategy["explanation_depth"] = (
                "detailed"
            )
            strategy["pace"] = "slow"

        average_score = profile.get(
            "average_score"
        )

        if (
            isinstance(average_score, (int, float))
            and average_score >= 85
        ):
            strategy["explanation_depth"] = (
                "concise"
            )
            strategy["pace"] = "fast"

        if learning_style:
            learning_style = (
                str(learning_style)
                .lower()
            )

            if learning_style == "visual":
                strategy["use_visuals"] = True

            elif learning_style == "reading":
                strategy["use_visuals"] = False

            elif learning_style == "practical":
                strategy["use_examples"] = True

        return strategy

    # ---------------------------------------------------------
    # Recommend topics
    # ---------------------------------------------------------

    def recommend_topics(
        self,
        profile: dict,
        available_topics: list[str],
    ) -> list[str]:
        """
        Recommend topics based on weaknesses and
        previously detected misconceptions.
        """

        if not available_topics:
            return []

        weaknesses = " ".join(
            str(item)
            for item in profile.get(
                "weaknesses",
                [],
            )
        ).lower()

        misconceptions = " ".join(
            str(item)
            for item in profile.get(
                "misconceptions",
                [],
            )
        ).lower()

        recommendations = []

        for topic in available_topics:
            topic_text = topic.lower()

            if (
                topic_text in weaknesses
                or topic_text in misconceptions
            ):
                recommendations.append(
                    topic
                )

        # If no direct match exists, return a small
        # selection for exploration.
        if not recommendations:
            recommendations = available_topics[:3]

        return list(
            dict.fromkeys(recommendations)
        )

    # ---------------------------------------------------------
    # Create AI context
    # ---------------------------------------------------------

    def create_ai_context(
        self,
        profile: dict,
    ) -> dict:
        """
        Convert the learning profile into a compact context
        object for AI agents.
        """

        return {
            "student_level": profile.get(
                "learning_level",
                "beginner",
            ),
            "language": profile.get(
                "preferred_language",
                "english",
            ),
            "learning_style": profile.get(
                "learning_style"
            ),
            "average_score": profile.get(
                "average_score"
            ),
            "strengths": profile.get(
                "strengths",
                [],
            ),
            "weaknesses": profile.get(
                "weaknesses",
                [],
            ),
            "misconceptions": profile.get(
                "misconceptions",
                [],
            ),
            "teaching_strategy": (
                self.recommend_teaching_strategy(
                    profile
                )
            ),
        }

    # ---------------------------------------------------------
    # Serialize database objects
    # ---------------------------------------------------------

    @staticmethod
    def _serialize_item(
        item: Any,
    ) -> dict:
        """
        Convert a SQLAlchemy/Pydantic object or dictionary
        into a simple dictionary.
        """

        if isinstance(item, dict):
            return item.copy()

        if hasattr(
            item,
            "model_dump",
        ):
            return item.model_dump()

        if hasattr(
            item,
            "__dict__",
        ):
            return {
                key: value
                for key, value in item.__dict__.items()
                if not key.startswith("_")
            }

        return {
            "value": item
        }


def get_personalization_service() -> PersonalizationService:
    """
    Create a PersonalizationService instance.
    """

    return PersonalizationService()