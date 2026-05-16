"""Auditor agent for strict audit verdicts using Anthropic's API."""

from __future__ import annotations

import json
import re
from typing import Any

import httpx


class AuditorError(Exception):
    """Exception raised by Auditor on API errors."""

    pass


class Auditor:
    """Auditor agent that calls Anthropic's API for strict audit verdicts.

    Uses direct HTTP calls to Anthropic's API without the SDK or LiteLLM.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-opus-4",
        base_url: str = "https://api.anthropic.com",
        timeout: float = 120.0,
    ) -> None:
        """Initialize the Auditor agent.

        Args:
            api_key: Anthropic API key.
            model: Model name (default: claude-opus-4).
            base_url: Base URL for Anthropic API (default: https://api.anthropic.com).
            timeout: Request timeout in seconds (default: 120.0).
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def ping(self) -> bool:
        """Send a minimal request to verify connectivity.

        Returns:
            True if the API is reachable (200 response), False otherwise.
        """
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            response = self.client.post(
                f"{self.base_url}/v1/messages",
                headers=headers,
                json={
                    "model": self.model,
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "ping"}],
                },
            )
            return response.status_code == 200
        except Exception:
            return False

    def audit(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Send an audit request to Anthropic's API.

        Args:
            system_prompt: System prompt for the audit.
            user_message: User message to audit.
            max_tokens: Maximum tokens in response (default: 4096).

        Returns:
            Dictionary with keys:
                - verdict: "PASS" or "FAIL" (parsed from response text)
                - reasoning: Extracted reasoning from response
                - raw_text: Full response text

        Raises:
            AuditorError: If the API returns a non-200 status code.
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_message}],
        }

        response = self.client.post(
            f"{self.base_url}/v1/messages",
            headers=headers,
            json=payload,
        )

        if response.status_code != 200:
            raise AuditorError(
                f"API returned status {response.status_code}: {response.text}"
            )

        response_data = response.json()
        raw_text = response_data.get("content", [{}])[0].get("text", "")

        # Parse verdict from response text (case-insensitive)
        verdict_match = re.search(r"\b(PASS|FAIL)\b", raw_text, re.IGNORECASE)
        verdict = verdict_match.group(1).upper() if verdict_match else "FAIL"

        return {
            "verdict": verdict,
            "reasoning": raw_text,
            "raw_text": raw_text,
        }
