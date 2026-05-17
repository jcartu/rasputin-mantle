from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class MemoryClient:
    _stub_store: dict[str, Any] = {}
    _logged_fallback = False

    def __init__(self, memory_url: str | None = None, token: str | None = None, timeout: float = 10.0) -> None:
        self.memory_url = memory_url if memory_url is not None else os.environ.get("RASPUTIN_MEMORY_URL", "").strip()
        self.token = token if token is not None else os.environ.get("RASPUTIN_TOKEN", "").strip()
        self.timeout = timeout
        self.memory_url = memory_url if memory_url is not None else os.environ.get("RASPUTIN_MEMORY_URL", "").strip()
        self.timeout = timeout

    def _fallback(self, reason: str) -> None:
        if not MemoryClient._logged_fallback:
            logger.warning("Using in-process MemoryClient fallback: %s", reason)
            MemoryClient._logged_fallback = True

    async def store(self, key: str, value: Any) -> dict[str, Any]:
        if self.memory_url:
            try:
                headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
                async with httpx.AsyncClient(base_url=self.memory_url, timeout=self.timeout) as client:
                    response = await client.post(
                        "/commit",
                        json={"text": str(value), "source": key, "importance": 60},
                        headers=headers,
                    )
                    if 200 <= response.status_code < 300:
                        payload = response.json()
                        if isinstance(payload, dict):
                            payload.setdefault("backend", "rasputin-memory")
                            return payload
            except (httpx.HTTPError, ValueError) as exc:
                self._fallback(f"rasputin-memory unavailable at {self.memory_url}: {exc}")
        else:
            self._fallback("RASPUTIN_MEMORY_URL is not set")

        MemoryClient._stub_store[key] = value
        return {"stored": key, "backend": "local_stub"}

    async def query(self, query: str, k: int = 5) -> dict[str, Any]:
        if self.memory_url:
            try:
                headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
                async with httpx.AsyncClient(base_url=self.memory_url, timeout=self.timeout) as client:
                    response = await client.get("/search", params={"q": query, "limit": k}, headers=headers)
                    if 200 <= response.status_code < 300:
                        payload = response.json()
                        if isinstance(payload, dict):
                            payload.setdefault("backend", "rasputin-memory")
                            return payload
            except (httpx.HTTPError, ValueError) as exc:
                self._fallback(f"rasputin-memory unavailable at {self.memory_url}: {exc}")
        else:
            self._fallback("RASPUTIN_MEMORY_URL is not set")

        needle = query.lower()
        ranked = []
        for key, value in MemoryClient._stub_store.items():
            text = f"{key} {value}".lower()
            if needle in text:
                score = 1.0
            else:
                score = sum(1 for token in needle.split() if token and token in text) / max(1, len(needle.split()))
            if score > 0:
                ranked.append({"key": key, "value": value, "score": score})
        ranked.sort(key=lambda item: item["score"], reverse=True)
        return {"results": ranked[:k], "backend": "local_stub"}

    async def stats(self) -> dict[str, Any]:
        if self.memory_url:
            try:
                headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
                async with httpx.AsyncClient(base_url=self.memory_url, timeout=self.timeout) as client:
                    response = await client.get("/stats", headers=headers)
                    if 200 <= response.status_code < 300:
                        payload = response.json()
                        if isinstance(payload, dict):
                            payload.setdefault("backend", "rasputin-memory")
                            return payload
            except (httpx.HTTPError, ValueError) as exc:
                self._fallback(f"rasputin-memory unavailable at {self.memory_url}: {exc}")
        else:
            self._fallback("RASPUTIN_MEMORY_URL is not set")

        return {"backend": "local_stub", "count": len(MemoryClient._stub_store)}
        return {"backend": "local_stub", "count": len(MemoryClient._stub_store)}

    async def reflect(self, query: str, k: int = 5) -> dict[str, Any]:
        if self.memory_url:
            try:
                headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
                async with httpx.AsyncClient(base_url=self.memory_url, timeout=self.timeout) as client:
                    response = await client.post("/reflect", json={"q": query, "limit": k}, headers=headers)
                    if 200 <= response.status_code < 300:
                        payload = response.json()
                        if isinstance(payload, dict):
                            payload.setdefault("backend", "rasputin-memory")
                            return payload
            except (httpx.HTTPError, ValueError) as exc:
                self._fallback(f"rasputin-memory unavailable at {self.memory_url}: {exc}")
        else:
            self._fallback("RASPUTIN_MEMORY_URL is not set")

        results = await self.query(query, k=k)
        return {"reflection": results.get("results", []), "backend": results.get("backend", "local_stub")}
        results = await self.query(query, k=k)
        return {"reflection": results.get("results", []), "backend": results.get("backend", "local_stub")}
