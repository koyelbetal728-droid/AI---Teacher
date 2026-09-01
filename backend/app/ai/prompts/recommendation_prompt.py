# recommendation_prompt.py
"""
Prompts for the Recommendation Agent.

This module contains reusable prompts for:

- Recommending the next topic
- Recommending revision topics
- Recommending practice activities
- Creating personalized study plans
- Adapting recommendations based on student performance
"""

from typing import Any, Dict, List, Optional


RECOMMENDATION_SYSTEM_PROMPT = """
You are an expert AI Teacher responsible for creating
personalized learning recommendations.

Your recommendations must be:

1. Based on the student's actual learning evidence.
2. Appropriate for the student's current level.
3. Focused on learning progress rather than speed.
4. Personalized to strengths, weaknesses, and misconceptions.
5. Practical and achievable.
6. Ordered by learning priority.
7. Respectful and encouraging.

Important rules:

- Do not recommend advanced topics before required prerequisites.
- Do not repeatedly recommend topics the student has already mastered.
- If the student has a misconception, prioritize correcting it.
- If evidence is insufficient, clearly state that.
- Never invent student performance data.

When structured JSON is requested, return valid JSON only.
"""


def build_recommendation_prompt(
    student_profile: Dict[str, Any],
    current_topic: Optional[str] = None,
    recent_performance: Optional[List[Dict[str, Any]]] = None,
    completed_topics: Optional[List[str]] = None,
    weak_topics: Optional[List[str]] = None,
    misconceptions: Optional[List[Dict[str, Any]]] = None,
    available_topics: Optional[List[str]] = None,
    student_level: str = "beginner",
    language: str = "English",
) -> str:
    """
    Build a personalized learning recommendation prompt.
    """

    return f"""
Create a personalized learning recommendation for the student.

STUDENT PROFILE
{student_profile}

CURRENT TOPIC
{current_topic or "Not specified."}

RECENT PERFORMANCE
{recent_performance or "No recent performance data provided."}

COMPLETED TOPICS
{completed_topics or "No completed-topic information provided."}

WEAK TOPICS
{weak_topics or "No weak-topic information provided."}

KNOWN MISCONCEPTIONS
{misconceptions or "No known misconceptions provided."}

AVAILABLE TOPICS
{available_topics or "No topic list provided."}

STUDENT LEVEL
{student_level}

LANGUAGE
{language}

RECOMMENDATION RULES

Consider:

1. Current understanding.
2. Recent performance.
3. Weak areas.
4. Known misconceptions.
5. Prerequisite relationships.
6. Topics already completed.
7. The student's current learning level.

Choose the most useful next learning action.

Possible actions include:

- Learn a new topic.
- Review a previous topic.
- Practice a weak concept.
- Correct a misconception.
- Study a prerequisite.
- Take an assessment.
- Continue the current lesson.

Return ONLY valid JSON:

{{
    "recommendation_type": "new_topic",
    "priority": "high",
    "topic": "Recommended topic",
    "reason": "Why this is recommended.",
    "learning_objectives": [
        "Objective 1",
        "Objective 2"
    ],
    "suggested_activity": "Recommended learning activity.",
    "estimated_difficulty": "beginner",
    "prerequisites": [],
    "confidence": 0
}}

RECOMMENDATION TYPE

Must be one of:

- "new_topic"
- "review"
- "practice"
- "misconception_correction"
- "prerequisite"
- "assessment"
- "continue"

PRIORITY

Must be one of:

- "low"
- "medium"
- "high"

CONFIDENCE
Must be an integer from 0 to 100.
"""


def build_next_topic_prompt(
    current_topic: str,
    completed_topics: List[str],
    performance: Optional[Dict[str, Any]] = None,
    misconceptions: Optional[List[Dict[str, Any]]] = None,
    available_topics: Optional[List[str]] = None,
    student_level: str = "beginner",
    language: str = "English",
) -> str:
    """
    Build a prompt for selecting the next topic in a learning path.
    """

    return f"""
Select the most appropriate next topic for the student.

CURRENT TOPIC
{current_topic}

COMPLETED TOPICS
{completed_topics}

PERFORMANCE
{performance or "No performance data provided."}

MISCONCEPTIONS
{misconceptions or "No misconceptions provided."}

AVAILABLE TOPICS
{available_topics or "No topic list provided."}

STUDENT LEVEL
{student_level}

LANGUAGE
{language}

The next topic should:

1. Build naturally on what the student already knows.
2. Respect prerequisite relationships.
3. Avoid unnecessary repetition.
4. Address important weaknesses when appropriate.
5. Match the student's current level.
6. Be achievable as the next learning step.

If the current topic is not sufficiently understood,
recommend review or practice instead of a new topic.

Return ONLY valid JSON:

{{
    "action": "learn_new_topic",
    "recommended_topic": "Topic name",
    "reason": "Why this should be next.",
    "prerequisites_satisfied": true,
    "missing_prerequisites": [],
    "learning_objectives": [],
    "confidence": 0
}}

ACTION

Must be one of:

- "learn_new_topic"
- "review_current_topic"
- "practice_current_topic"
- "learn_prerequisite"

CONFIDENCE
Must be an integer from 0 to 100.
"""


def build_review_recommendation_prompt(
    weak_topics: List[str],
    misconceptions: Optional[List[Dict[str, Any]]] = None,
    performance_history: Optional[List[Dict[str, Any]]] = None,
    student_level: str = "beginner",
    language: str = "English",
) -> str:
    """
    Build a prompt for identifying topics that should be reviewed.
    """

    return f"""
Create a personalized revision recommendation.

WEAK TOPICS
{weak_topics}

MISCONCEPTIONS
{misconceptions or "None provided."}

PERFORMANCE HISTORY
{performance_history or "No history provided."}

STUDENT LEVEL
{student_level}

LANGUAGE
{language}

Determine:

1. Which topic should be reviewed first.
2. Why it needs review.
3. What type of review would be most effective.
4. Whether a prerequisite should be reviewed first.

Possible review activities:

- Concept explanation
- Worked example
- Practice questions
- Flashcards
- Mini quiz
- Comparison
- Visual explanation

Return ONLY valid JSON:

{{
    "review_priority": [
        {{
            "topic": "Topic",
            "priority": "high",
            "reason": "Reason for review.",
            "activity": "Recommended activity.",
            "focus_areas": []
        }}
    ],

    "recommended_order": [],

    "study_tip": "Personalized study advice."
}}
"""


def build_practice_recommendation_prompt(
    topic: str,
    performance: Optional[Dict[str, Any]] = None,
    mistakes: Optional[List[str]] = None,
    misconceptions: Optional[List[Dict[str, Any]]] = None,
    student_level: str = "beginner",
    language: str = "English",
) -> str:
    """
    Build a prompt for recommending targeted practice.
    """

    return f"""
Create a targeted practice recommendation.

TOPIC
{topic}

PERFORMANCE
{performance or "No performance data provided."}

RECENT MISTAKES
{mistakes or "No mistakes provided."}

MISCONCEPTIONS
{misconceptions or "No misconceptions provided."}

STUDENT LEVEL
{student_level}

LANGUAGE
{language}

The practice should focus on the student's actual weaknesses.

Determine:

1. What skill needs practice.
2. What difficulty level is appropriate.
3. What type of questions should be used.
4. How many practice questions are appropriate.
5. What should indicate readiness to move forward.

Return ONLY valid JSON:

{{
    "topic": "{topic}",
    "skill_to_practice": "Skill",
    "difficulty": "easy",
    "question_count": 5,
    "practice_type": "conceptual",
    "focus_areas": [],
    "success_criteria": [
        "Criterion 1"
    ],
    "recommended_activity": "Practice activity.",
    "confidence": 0
}}

DIFFICULTY

Must be one of:

- "easy"
- "medium"
- "hard"
- "adaptive"

PRACTICE TYPE

Must be one of:

- "conceptual"
- "calculation"
- "application"
- "mixed"
- "problem_solving"

CONFIDENCE
Must be an integer from 0 to 100.
"""


def build_study_plan_prompt(
    goal: str,
    available_topics: List[str],
    student_profile: Dict[str, Any],
    completed_topics: Optional[List[str]] = None,
    weak_topics: Optional[List[str]] = None,
    available_minutes_per_day: int = 30,
    days: int = 7,
    student_level: str = "beginner",
    language: str = "English",
) -> str:
    """
    Build a personalized multi-day study plan.
    """

    return f"""
Create a personalized study plan.

LEARNING GOAL
{goal}

AVAILABLE TOPICS
{available_topics}

STUDENT PROFILE
{student_profile}

COMPLETED TOPICS
{completed_topics or "None provided."}

WEAK TOPICS
{weak_topics or "None provided."}

AVAILABLE TIME PER DAY
{available_minutes_per_day} minutes

PLAN LENGTH
{days} days

STUDENT LEVEL
{student_level}

LANGUAGE
{language}

PLAN REQUIREMENTS

The plan should:

1. Start from the student's current level.
2. Respect topic prerequisites.
3. Include revision where appropriate.
4. Include practice and assessment.
5. Prioritize weak areas.
6. Avoid unrealistic workloads.
7. Fit within the available daily time.
8. Progress gradually toward the learning goal.

Return ONLY valid JSON:

{{
    "goal": "{goal}",
    "duration_days": {days},
    "daily_minutes": {available_minutes_per_day},

    "plan": [
        {{
            "day": 1,
            "focus": "Topic",
            "activities": [
                "Activity 1",
                "Activity 2"
            ],
            "minutes": {available_minutes_per_day},
            "objective": "Learning objective."
        }}
    ],

    "milestones": [
        "Milestone 1"
    ],

    "final_assessment": "Description of final assessment."
}}
"""


def build_adaptive_recommendation_prompt(
    student_state: Dict[str, Any],
    latest_interaction: Dict[str, Any],
    current_lesson: Optional[str] = None,
    language: str = "English",
) -> str:
    """
    Build a prompt for deciding what the teacher should do next
    based on the student's latest interaction.
    """

    return f"""
Decide the student's next best learning action based on the
latest interaction.

STUDENT STATE
{student_state}

LATEST INTERACTION
{latest_interaction}

CURRENT LESSON
{current_lesson or "No current lesson provided."}

LANGUAGE
{language}

Choose the action that best supports learning.

Possible actions:

- Continue explanation
- Simplify explanation
- Give an example
- Ask a question
- Give a hint
- Practice
- Review
- Correct misconception
- Move to next concept
- Take a quiz

Return ONLY valid JSON:

{{
    "next_action": "continue_explanation",
    "reason": "Why this action is appropriate.",
    "instruction": "What the teacher should do.",
    "difficulty_change": "same",
    "topic_change": false,
    "confidence": 0
}}

DIFFICULTY CHANGE

Must be one of:

- "increase"
- "decrease"
- "same"

CONFIDENCE
Must be an integer from 0 to 100.
"""