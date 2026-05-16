"""Executor agent for task execution using local vLLM via OpenAI-compatible API."""

from __future__ import annotations

from typing import Any

import httpx


class ExecutorError(Exception):
    """Exception raised by Executor on API errors."""

    pass


class Executor:
    """Executor agent that calls local vLLM via OpenAI-compatible /v1/chat/completions endpoint.

    Uses direct HTTP calls to vLLM without the OpenAI SDK or LiteLLM.
    """

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str = "EMPTY",
        timeout: float = 600.0,
    ) -> None:
        """Initialize the Executor agent.

        Args:
            base_url: Base URL for vLLM API (e.g., http://localhost:8000/v1).
            model: Model name to use for execution.
            api_key: API key for authorization (default: "EMPTY").
            timeout: Request timeout in seconds (default: 600.0).
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def ping(self) -> bool:
        """Send a minimal request to verify connectivity.

        Returns:
            True if the API is reachable (200 response), False otherwise.
        """
        try:
            response = self.client.get(f"{self.base_url}/v1/models")
            return response.status_code == 200
        except Exception:
            return False

    def execute(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 16384,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        """Send an execution request to vLLM's OpenAI-compatible API.

        Args:
            system_prompt: System prompt for the execution task.
            user_message: User message describing the task to execute.
            max_tokens: Maximum tokens in response (default: 16384).
            temperature: Sampling temperature (default: 0.1).

        Returns:
            Dictionary with keys:
                - text: The response text from the model.
                - raw: The full response JSON from the API.

        Raises:
            ExecutorError: If the API returns a non-200 status code.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        }

        response = self.client.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
        )

        if response.status_code != 200:
            raise ExecutorError(
                f"API returned status {response.status_code}: {response.text}"
            )

        response_data = response.json()
        text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")

        return {
            "text": text,
            "raw": response_data,
        }
