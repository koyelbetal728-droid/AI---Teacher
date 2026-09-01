# recommendation_agent.py
"""
Recommendation Agent.

Generates personalized learning recommendations based on a
student's progress, performance, strengths, weaknesses, and
detected misconceptions.

All AI generation is performed through the local LLM service.
"""

from typing import Any, Dict, List, Optional

from app.ai.llm.llm_service import llm_service


class RecommendationAgent:
    """AI agent responsible for personalized learning recommendations."""

    def __init__(self):
        self.llm = llm_service

    async def recommend(
        self,
        student_profile: Optional[Dict[str, Any]] = None,
        progress: Optional[Dict[str, Any]] = None,
        recent_performance: Optional[Dict[str, Any]] = None,
        misconceptions: Optional[List[str]] = None,
        current_topic: Optional[str] = None,
        language: str = "English",
    ) -> Dict[str, Any]:
        """
        Generate personalized learning recommendations.

        Args:
            student_profile: Student preferences and learning information.
            progress: Overall learning progress.
            recent_performance: Recent quiz/interaction performance.
            misconceptions: Known misconceptions or weak areas.
            current_topic: Topic currently being studied.
            language: Recommendation language.

        Returns:
            Structured personalized recommendations.
        """

        profile = student_profile or {}
        progress_data = progress or {}
        performance = recent_performance or {}
        misconception_data = misconceptions or []

        prompt = f"""
You are an AI Teacher responsible for personalized learning
recommendations.

Student profile:
{profile}

Overall progress:
{progress_data}

Recent performance:
{performance}

Known misconceptions or weak areas:
{misconception_data}

Current topic:
{current_topic or "No current topic specified."}

Language:
{language}

Create a practical learning recommendation.

Consider:
1. Topics the student should review.
2. Topics the student is ready to learn next.
3. Weak areas that need attention.
4. Strong areas that can be advanced.
5. Appropriate difficulty.
6. Useful practice activities.
7. Whether the student should continue or revisit a topic.

Do not make recommendations unsupported by the provided
student information.

Return ONLY valid JSON:

{{
    "overall_recommendation": "Short personalized recommendation.",
    "recommended_action": "continue",
    "priority": "medium",
    "next_topic": "Recommended next topic",
    "topics_to_review": [
        "Topic to review"
    ],
    "strengths_to_build_on": [
        "Student strength"
    ],
    "practice_activities": [
        "Recommended activity"
    ],
    "reasoning": "Why these recommendations were selected.",
    "estimated_difficulty": "medium"
}}

recommended_action must be one of:
- "continue"
- "review"
- "practice"
- "advance"
- "take_assessment"

priority must be:
- "low"
- "medium"
- "high"

estimated_difficulty must be:
- "easy"
- "medium"
- "hard"
"""

        try:
            result = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.3,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to generate recommendations: {exc}"
            ) from exc

        return self._normalize_result(result)

    async def recommend_next_topic(
        self,
        completed_topics: List[str],
        weak_topics: Optional[List[str]] = None,
        strong_topics: Optional[List[str]] = None,
        student_level: str = "beginner",
        subject: Optional[str] = None,
        language: str = "English",
    ) -> Dict[str, Any]:
        """
        Recommend what the student should learn next.
        """

        prompt = f"""
You are an AI Teacher selecting the next topic for a student.

Subject:
{subject or "Not specified"}

Student level:
{student_level}

Completed topics:
{completed_topics}

Weak topics:
{weak_topics or []}

Strong topics:
{strong_topics or []}

Language:
{language}

Choose an appropriate next learning topic.

Prioritize:
- prerequisite relationships,
- unresolved weak areas,
- natural progression,
- appropriate difficulty.

Do not recommend a topic that requires knowledge the student
has clearly not developed unless you also recommend the
necessary prerequisite first.

Return ONLY valid JSON:

{{
    "recommended_topic": "Topic name",
    "reason": "Why this topic is appropriate.",
    "prerequisites": [
        "Required prerequisite"
    ],
    "difficulty": "medium",
    "learning_objectives": [
        "Objective 1",
        "Objective 2"
    ],
    "alternative_topics": [
        "Alternative topic"
    ]
}}

difficulty must be:
- "easy"
- "medium"
- "hard"
"""

        try:
            return await self.llm.generate_json(
                prompt=prompt,
                temperature=0.3,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to recommend next topic: {exc}"
            ) from exc

    async def recommend_review(
        self,
        performance_history: List[Dict[str, Any]],
        misconceptions: Optional[List[str]] = None,
        language: str = "English",
    ) -> Dict[str, Any]:
        """
        Identify topics that should be reviewed.
        """

        prompt = f"""
You are an AI Teacher analyzing a student's learning history.

Performance history:
{performance_history}

Known misconceptions:
{misconceptions or []}

Language:
{language}

Identify which topics should be reviewed.

Look for:
- repeated incorrect answers,
- low scores,
- recurring misconceptions,
- concepts that appear to be forgotten,
- prerequisites needed for future topics.

Return ONLY valid JSON:

{{
    "review_required": true,
    "priority_topics": [
        {{
            "topic": "Topic",
            "priority": "high",
            "reason": "Reason for review.",
            "suggested_activity": "Recommended activity."
        }}
    ],
    "review_strategy": "Overall review strategy."
}}

priority must be:
- "low"
- "medium"
- "high"
"""

        try:
            return await self.llm.generate_json(
                prompt=prompt,
                temperature=0.2,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to generate review recommendations: {exc}"
            ) from exc

    async def recommend_practice(
        self,
        topic: str,
        student_level: str = "beginner",
        performance: Optional[Dict[str, Any]] = None,
        language: str = "English",
    ) -> Dict[str, Any]:
        """
        Recommend practice activities for a specific topic.
        """

        prompt = f"""
You are an AI Teacher creating personalized practice.

Topic:
{topic}

Student level:
{student_level}

Recent performance:
{performance or {}}

Language:
{language}

Create practice recommendations appropriate for the
student's current ability.

Include a progression from easier to more challenging tasks.

Return ONLY valid JSON:

{{
    "topic": "{topic}",
    "practice_plan": [
        {{
            "type": "conceptual",
            "difficulty": "easy",
            "instruction": "Practice instruction.",
            "goal": "What the student should learn."
        }}
    ],
    "recommended_count": 3,
    "completion_goal": "What successful practice looks like."
}}

type may be:
- "conceptual"
- "problem_solving"
- "application"
- "recall"
- "mixed"

difficulty must be:
- "easy"
- "medium"
- "hard"
"""

        try:
            return await self.llm.generate_json(
                prompt=prompt,
                temperature=0.3,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to generate practice recommendations: {exc}"
            ) from exc

    async def create_study_plan(
        self,
        goals: List[str],
        available_minutes_per_day: int,
        current_progress: Optional[Dict[str, Any]] = None,
        student_level: str = "beginner",
        language: str = "English",
    ) -> Dict[str, Any]:
        """
        Create a personalized study plan.

        The plan is based only on the student's stated goals,
        available time, and supplied progress information.
        """

        if not goals:
            raise ValueError("At least one learning goal is required.")

        if available_minutes_per_day <= 0:
            raise ValueError(
                "Available study time must be greater than zero."
            )

        prompt = f"""
Create a realistic personalized study plan.

Student level:
{student_level}

Learning goals:
{goals}

Available study time per day:
{available_minutes_per_day} minutes

Current progress:
{current_progress or {}}

Language:
{language}

The plan should:
1. Prioritize the most important goals.
2. Fit within the available daily time.
3. Include learning, practice, and revision.
4. Avoid unrealistic workloads.
5. Include checkpoints for progress.

Return ONLY valid JSON:

{{
    "daily_minutes": {available_minutes_per_day},
    "plan": [
        {{
            "day": 1,
            "focus": "Topic or goal",
            "activities": [
                "Activity 1",
                "Activity 2"
            ],
            "estimated_minutes": 30
        }}
    ],
    "weekly_goal": "Main weekly goal.",
    "success_criteria": [
        "Success criterion"
    ]
}}
"""

        try:
            return await self.llm.generate_json(
                prompt=prompt,
                temperature=0.3,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to create study plan: {exc}"
            ) from exc

    def _normalize_result(
        self,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Normalize the recommendation result."""

        if not isinstance(result, dict):
            raise ValueError(
                "LLM returned an invalid recommendation."
            )

        result.setdefault(
            "overall_recommendation",
            "",
        )
        result.setdefault(
            "recommended_action",
            "continue",
        )
        result.setdefault(
            "priority",
            "medium",
        )
        result.setdefault(
            "next_topic",
            "",
        )
        result.setdefault(
            "topics_to_review",
            [],
        )
        result.setdefault(
            "strengths_to_build_on",
            [],
        )
        result.setdefault(
            "practice_activities",
            [],
        )
        result.setdefault(
            "reasoning",
            "",
        )
        result.setdefault(
            "estimated_difficulty",
            "medium",
        )

        valid_actions = {
            "continue",
            "review",
            "practice",
            "advance",
            "take_assessment",
        }

        valid_priorities = {
            "low",
            "medium",
            "high",
        }

        valid_difficulties = {
            "easy",
            "medium",
            "hard",
        }

        if result["recommended_action"] not in valid_actions:
            result["recommended_action"] = "continue"

        if result["priority"] not in valid_priorities:
            result["priority"] = "medium"

        if result["estimated_difficulty"] not in valid_difficulties:
            result["estimated_difficulty"] = "medium"

        return result


# Default reusable instance
recommendation_agent = RecommendationAgent()