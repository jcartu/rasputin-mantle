"""packages/browser/browser/vision.py — VLM screenshot reasoning fallback.

Uses Claude Sonnet 4.6 vision to extract information from screenshots when
DOM-based extraction fails (canvas, virtual scroll, custom widgets, charts).

Features:
- Per-task budget cap (default 3 calls)
- Result caching by hash(screenshot + prompt)
- Cost telemetry tracking
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any

import httpx


@dataclass
class VisionCall:
    """Record of a single vision API call."""

    timestamp: float
    model: str
    input_tokens_est: int
    output_tokens_est: int
    cost_usd: float
    prompt_type: str
    cached: bool = False


class VisionBudgetExceeded(Exception):
    """Raised when vision call budget is exceeded."""

    pass


class VisionAssist:
    """Vision-language model fallback for opaque DOM pages.

    Uses Claude Sonnet 4.6 vision to extract information from screenshots
    when DOM-based extraction fails.

    Features:
    - Per-task budget cap (default 3 calls)
    - Result caching by hash(screenshot + question)
    - Cost telemetry tracking
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-6",
        max_calls_per_task: int = 3,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.max_calls_per_task = max_calls_per_task
        self._call_count: int = 0
        self._cache: dict[str, dict] = {}
        self._calls: list[VisionCall] = []

    def reset_task(self) -> None:
        """Reset call count and cache for a new task."""
        self._call_count = 0
        self._cache.clear()

    @property
    def calls_made(self) -> int:
        return self._call_count

    @property
    def remaining_budget(self) -> int:
        return max(0, self.max_calls_per_task - self._call_count)

    def get_cost_report(self) -> dict:
        """Return cost telemetry for all vision calls."""
        total_cost = sum(c.cost_usd for c in self._calls)
        cached_hits = sum(1 for c in self._calls if c.cached)
        return {
            "total_calls": len(self._calls),
            "cached_hits": cached_hits,
            "unique_calls": len(self._calls) - cached_hits,
            "total_cost_usd": round(total_cost, 4),
            "calls": [
                {
                    "timestamp": c.timestamp,
                    "model": c.model,
                    "input_tokens_est": c.input_tokens_est,
                    "output_tokens_est": c.output_tokens_est,
                    "cost_usd": round(c.cost_usd, 6),
                    "prompt_type": c.prompt_type,
                    "cached": c.cached,
                }
                for c in self._calls
            ],
        }

    def _cache_key(self, screenshot: bytes, prompt: str) -> str:
        """Generate cache key from screenshot and prompt."""
        content = hashlib.sha256(screenshot + prompt.encode()).hexdigest()
        return content

    def _estimate_image_tokens(self, screenshot: bytes) -> int:
        """Estimate input tokens for a screenshot."""
        return 1400  # conservative estimate for typical screenshots

    async def _call_vision(self, screenshot: bytes, prompt: str, prompt_type: str) -> dict:
        """Make a vision API call to Claude Sonnet 4.6."""
        cache_key = self._cache_key(screenshot, prompt)

        # Check cache first
        if cache_key in self._cache:
            cached_result = self._cache[cache_key]
            tokens = self._estimate_image_tokens(screenshot)
            self._calls.append(
                VisionCall(
                    timestamp=time.time(),
                    model=self.model,
                    input_tokens_est=tokens,
                    output_tokens_est=0,
                    cost_usd=0,
                    prompt_type=prompt_type,
                    cached=True,
                )
            )
            return cached_result

        # Check budget
        if self._call_count >= self.max_calls_per_task:
            raise VisionBudgetExceeded(
                f"Vision budget exceeded ({self.max_calls_per_task} calls per task)"
            )

        # Encode screenshot
        img_b64 = base64.b64encode(screenshot).decode("ascii")
        tokens = self._estimate_image_tokens(screenshot)

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": 1024,
                    "system": "You are a vision assistant that extracts precise information from screenshots. Return JSON only.",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": img_b64,
                                    },
                                },
                                {"type": "text", "text": prompt},
                            ],
                        }
                    ],
                },
            )

        if resp.status_code != 200:
            raise Exception(f"Vision API error: {resp.status_code} {resp.text[:200]}")

        data = resp.json()
        text = data["content"][0]["text"].strip()
        usage = data.get("usage", {})
        output_tokens = usage.get("output_tokens", len(text) // 4)

        # Cost: Sonnet 4.6 ~ $3/1M input, $15/1M output
        cost = (tokens / 1_000_000 * 3) + (output_tokens / 1_000_000 * 15)

        self._call_count += 1
        self._calls.append(
            VisionCall(
                timestamp=time.time(),
                model=self.model,
                input_tokens_est=tokens,
                output_tokens_est=output_tokens,
                cost_usd=cost,
                prompt_type=prompt_type,
                cached=False,
            )
        )

        # Parse JSON from response
        try:
            result = self._parse_json_response(text)
        except json.JSONDecodeError:
            result = {"raw_text": text}

        # Cache result
        self._cache[cache_key] = result

        return result

    def _parse_json_response(self, text: str) -> dict:
        """Extract JSON from vision response text."""
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1]).strip()
        if not text.startswith("{"):
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                text = text[start : end + 1]
        return json.loads(text)

    async def find_element_bbox(
        self, screenshot: bytes, description: str
    ) -> dict | None:
        """Find element bounding box in screenshot.

        Args:
            screenshot: PNG bytes of the page screenshot.
            description: Natural language description of the element to find.

        Returns:
            Dict with {x, y, w, h} or None if not found.
        """
        prompt = (
            f"Find the element described as: '{description}'. "
            "Return ONLY a JSON object with keys: x, y, w, h (pixel coordinates and dimensions). "
            "If the element is not visible in the screenshot, return null."
        )
        result = await self._call_vision(screenshot, prompt, "find_element")
        if result is None or result.get("raw_text"):
            return None
        return result

    async def extract_text_from_region(
        self, screenshot: bytes, bbox: dict | None = None
    ) -> str:
        """Extract visible text from screenshot.

        Args:
            screenshot: PNG bytes of the page screenshot.
            bbox: Optional {x, y, w, h} region to focus on.

        Returns:
            Extracted text string.
        """
        region_hint = ""
        if bbox:
            region_hint = f" Focus on the region at x={bbox['x']}, y={bbox['y']}, w={bbox['w']}, h={bbox['h']}."

        prompt = (
            f"Extract all visible text from this screenshot.{region_hint} "
            "Return ONLY a JSON object with key 'text' containing the extracted text."
        )
        result = await self._call_vision(screenshot, prompt, "extract_text")
        return result.get("text", "")

    async def answer_question_about_page(
        self, screenshot: bytes, question: str
    ) -> str:
        """Answer a question about the page content.

        Args:
            screenshot: PNG bytes of the page screenshot.
            question: The question to answer based on visual content.

        Returns:
            Answer string.
        """
        prompt = (
            f"Look at this screenshot and answer: '{question}'. "
            "Return ONLY a JSON object with key 'answer' containing your response."
        )
        result = await self._call_vision(screenshot, prompt, "answer_question")
        return result.get("answer", "")
