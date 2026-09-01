# llm_service.py
from typing import Any

from app.ai.llm.ollama_client import OllamaClient


class LLMService:
    """
    High-level AI service used by the different AI agents.

    This class keeps the agents independent from the actual
    LLM provider. Currently it uses Ollama, which allows the
    AI Teacher to run with a local/free model.
    """

    def __init__(
        self,
        client: OllamaClient | None = None,
    ):
        self.client = client or OllamaClient()

    # ---------------------------------------------------------
    # Generate text
    # ---------------------------------------------------------

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
    ) -> str:
        """
        Generate a normal text response.
        """

        return await self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
        )

    # ---------------------------------------------------------
    # Chat
    # ---------------------------------------------------------

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
    ) -> str:
        """
        Generate a response from a conversation.
        """

        return await self.client.chat(
            messages=messages,
            temperature=temperature,
        )

    # ---------------------------------------------------------
    # Generate JSON
    # ---------------------------------------------------------

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
    ) -> dict[str, Any] | list[Any]:
        """
        Generate structured JSON output.

        Used for:
        - Lesson plans
        - Questions
        - Evaluations
        - Recommendations
        - Learning analysis
        """

        return await self.client.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
        )

    # ---------------------------------------------------------
    # Explain concept
    # ---------------------------------------------------------

    async def explain(
        self,
        concept: str,
        context: str | None = None,
        student_level: str = "beginner",
        language: str = "english",
    ) -> str:
        """
        Generate a student-friendly explanation.
        """

        prompt = f"""
Explain the following concept to a student.

Concept:
{concept}

Student level:
{student_level}

Language:
{language}

Additional context:
{context or "No additional context provided."}

Requirements:
- Explain clearly.
- Use simple language.
- Start with the basic idea.
- Give a practical example.
- Avoid unnecessary complexity.
- Break difficult ideas into smaller parts.
"""

        system_prompt = """
You are a patient and helpful AI teacher.

Your goal is to help students understand concepts,
not simply provide answers.

Adapt explanations to the student's level.
"""

        return await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
        )

    # ---------------------------------------------------------
    # Ask question
    # ---------------------------------------------------------

    async def answer(
        self,
        question: str,
        context: str | None = None,
        student_level: str = "beginner",
        language: str = "english",
    ) -> str:
        """
        Answer a student's question using the supplied context.
        """

        prompt = f"""
Answer the student's question.

Question:
{question}

Student level:
{student_level}

Language:
{language}

Relevant learning material:
{context or "No external learning material was provided."}

Instructions:
- Give a direct answer first.
- Explain why the answer is correct.
- Use examples when useful.
- If the supplied material does not contain enough
  information, clearly say so.
- Do not invent facts from the learning material.
"""

        system_prompt = """
You are an AI teaching assistant.

Teach step-by-step and make the answer understandable
for the student's current level.
"""

        return await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2,
        )

    # ---------------------------------------------------------
    # Generate lesson
    # ---------------------------------------------------------

    async def generate_lesson(
        self,
        topic: str,
        student_level: str = "beginner",
        language: str = "english",
        duration_minutes: int = 30,
        context: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Generate a structured lesson plan.
        """

        prompt = f"""
Create a lesson plan for:

Topic:
{topic}

Student level:
{student_level}

Language:
{language}

Duration:
{duration_minutes} minutes

Learning material:
{context or "No additional material provided."}

Return JSON with this structure:

{{
    "title": "...",
    "objective": "...",
    "introduction": "...",
    "sections": [
        {{
            "title": "...",
            "explanation": "...",
            "example": "...",
            "activity": "..."
        }}
    ],
    "practice_questions": [
        {{
            "question": "...",
            "answer": "..."
        }}
    ],
    "summary": "...",
    "homework": "..."
}}
"""

        system_prompt = """
You are an expert lesson planner.

Create structured, educational and age-appropriate
lessons. Use the supplied learning material when it
is available.
"""

        return await self.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
        )

    # ---------------------------------------------------------
    # Evaluate answer
    # ---------------------------------------------------------

    async def evaluate(
        self,
        question: str,
        student_answer: str,
        expected_answer: str | None = None,
        context: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Evaluate a student's answer.
        """

        prompt = f"""
Evaluate the student's answer.

Question:
{question}

Student answer:
{student_answer}

Expected answer:
{expected_answer or "Not provided"}

Relevant context:
{context or "No additional context provided."}

Return JSON:

{{
    "is_correct": true,
    "score": 0,
    "feedback": "...",
    "strengths": [],
    "weaknesses": [],
    "misconception": null
}}

Scoring:
- 90-100: Excellent
- 75-89: Very good
- 60-74: Partially correct
- 40-59: Weak understanding
- 0-39: Incorrect or very limited

Be fair. A student's answer can be correct even if
it uses different wording from the expected answer.
"""

        system_prompt = """
You are an educational evaluator.

Evaluate answers fairly and provide constructive
feedback. Do not penalize students simply because
their wording differs from the expected answer.
"""

        return await self.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1,
        )

    # ---------------------------------------------------------
    # Detect misconception
    # ---------------------------------------------------------

    async def detect_misconception(
        self,
        question: str,
        student_answer: str,
        correct_answer: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Identify possible misconceptions in a student's answer.
        """

        prompt = f"""
Analyze the student's answer for conceptual misconceptions.

Question:
{question}

Student answer:
{student_answer}

Correct answer:
{correct_answer or "Not provided"}

Return JSON:

{{
    "has_misconception": false,
    "misconception": null,
    "explanation": "...",
    "recommended_correction": "..."
}}
"""

        system_prompt = """
You are a diagnostic AI teacher.

Your job is to identify why a student may have
misunderstood a concept and suggest a clear correction.
"""

        return await self.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1,
        )

    # ---------------------------------------------------------
    # Recommend next action
    # ---------------------------------------------------------

    async def recommend_next_action(
        self,
        score: int | float | None,
        misconception: str | None = None,
        topic: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Decide what the student should do next.
        """

        prompt = f"""
Determine the best next learning action for a student.

Topic:
{topic or "Unknown"}

Score:
{score if score is not None else "Unknown"}

Misconception:
{misconception or "None detected"}

Return JSON:

{{
    "action": "review",
    "reason": "...",
    "difficulty": "beginner",
    "recommended_activity": "..."
}}

Possible actions:
- continue
- review
- practice
- retry
- advance
"""

        system_prompt = """
You are an adaptive learning assistant.

Choose the next activity based on the student's
actual performance. Do not make the student advance
when important concepts are still misunderstood.
"""

        return await self.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2,
        )

    # ---------------------------------------------------------
    # Health check
    # ---------------------------------------------------------

    async def health_check(self) -> bool:
        """
        Check whether the underlying LLM is available.
        """

        return await self.client.health_check()

    # ---------------------------------------------------------
    # Available models
    # ---------------------------------------------------------

    async def available_models(self) -> list[str]:
        """
        Return models available in Ollama.
        """

        return await self.client.list_models()


# -------------------------------------------------------------
# Default service
# -------------------------------------------------------------

llm_service = LLMService()