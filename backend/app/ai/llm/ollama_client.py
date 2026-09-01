# ollama_client.py
import json
from typing import Any

import httpx

from app.config import settings


class OllamaClient:
    """
    Lightweight client for communicating with a local
    Ollama server.

    Ollama runs locally, so the AI Teacher can work without
    paid LLM APIs.
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 120.0,
    ):
        self.base_url = (
            base_url or settings.ollama_base_url
        ).rstrip("/")

        self.model = (
            model or settings.ollama_model
        )

        self.timeout = timeout

    # ---------------------------------------------------------
    # Health check
    # ---------------------------------------------------------

    async def health_check(self) -> bool:
        """
        Check whether Ollama is running.
        """

        try:
            async with httpx.AsyncClient(
                timeout=10.0
            ) as client:
                response = await client.get(
                    f"{self.base_url}/api/tags"
                )

                return response.status_code == 200

        except (
            httpx.HTTPError,
            OSError,
        ):
            return False

    # ---------------------------------------------------------
    # List models
    # ---------------------------------------------------------

    async def list_models(self) -> list[str]:
        """
        Return locally available Ollama models.
        """

        try:
            async with httpx.AsyncClient(
                timeout=10.0
            ) as client:
                response = await client.get(
                    f"{self.base_url}/api/tags"
                )

                response.raise_for_status()

                data = response.json()

                models = data.get(
                    "models",
                    [],
                )

                return [
                    model.get("name")
                    for model in models
                    if model.get("name")
                ]

        except (
            httpx.HTTPError,
            ValueError,
        ):
            return []

    # ---------------------------------------------------------
    # Generate response
    # ---------------------------------------------------------

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        stream: bool = False,
    ) -> str:
        """
        Generate a response using the local Ollama model.
        """

        if not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
            },
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )

                response.raise_for_status()

                data = response.json()

                return data.get(
                    "response",
                    "",
                ).strip()

        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "Ollama request timed out."
            ) from exc

        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Unable to communicate with Ollama: {exc}"
            ) from exc

    # ---------------------------------------------------------
    # Chat
    # ---------------------------------------------------------

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        stream: bool = False,
    ) -> str:
        """
        Send a conversation to Ollama.
        """

        if not messages:
            raise ValueError(
                "Messages cannot be empty."
            )

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
            },
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                )

                response.raise_for_status()

                data = response.json()

                message = data.get(
                    "message",
                    {},
                )

                return message.get(
                    "content",
                    "",
                ).strip()

        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "Ollama chat request timed out."
            ) from exc

        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Unable to communicate with Ollama: {exc}"
            ) from exc

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
        Ask Ollama to return structured JSON.

        Useful for:
        - Lesson plans
        - Quizzes
        - Evaluations
        - Recommendations
        """

        json_instruction = (
            "\n\nReturn ONLY valid JSON. "
            "Do not include markdown code fences, "
            "explanations, or extra text."
        )

        response = await self.generate(
            prompt=prompt + json_instruction,
            system_prompt=system_prompt,
            temperature=temperature,
            stream=False,
        )

        cleaned = response.strip()

        # Handle accidental markdown fences.
        if cleaned.startswith(
            "```json"
        ):
            cleaned = cleaned[
                len("```json"):
            ].strip()

        elif cleaned.startswith("```"):
            cleaned = cleaned[
                len("```"):
            ].strip()

        if cleaned.endswith("```"):
            cleaned = cleaned[
                :-len("```")
            ].strip()

        try:
            return json.loads(cleaned)

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Ollama returned invalid JSON."
            ) from exc


# -------------------------------------------------------------
# Default client
# -------------------------------------------------------------

ollama_client = OllamaClient()