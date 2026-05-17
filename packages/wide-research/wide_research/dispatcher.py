from __future__ import annotations

import asyncio
import inspect
import os
from collections.abc import Awaitable, Callable, Sequence
from typing import Any

import httpx
import sandbox

SearchFn = Callable[[str], Awaitable[Sequence[dict[str, Any]]] | Sequence[dict[str, Any]]]


class SearchBackendUnavailable(RuntimeError):
    """Raised when no configured search backend can be used."""


def _split_query(query: str, n_agents: int) -> list[str]:
    base = " ".join(query.split())
    if not base:
        raise ValueError("query must not be empty")

    variations = [
        base,
        f"{base} overview",
        f"{base} latest evidence",
        f"{base} primary sources",
        f"{base} technical analysis",
        f"{base} risks limitations",
        f"{base} comparison alternatives",
        f"{base} expert commentary",
        f"{base} recent developments",
        f"{base} implementation details",
    ]
    if n_agents > len(variations):
        variations.extend(f"{base} research angle {i + 1}" for i in range(len(variations), n_agents))
    return variations[:n_agents]


def _get_search_credentials() -> tuple[str, str]:
    brave_key = os.environ.get("BRAVE_SEARCH_API_KEY", "").strip()
    exa_key = os.environ.get("EXA_API_KEY", "").strip()
    if brave_key:
        return "brave", brave_key
    if exa_key:
        return "exa", exa_key
    raise SearchBackendUnavailable("Set BRAVE_SEARCH_API_KEY or EXA_API_KEY to enable Wide Research.")


async def _search_brave(client: httpx.AsyncClient, query: str, api_key: str) -> list[dict[str, Any]]:
    response = await client.get(
        "https://api.search.brave.com/res/v1/web/search",
        params={"q": query, "count": 3, "search_lang": "en"},
        headers={"Accept": "application/json", "X-Subscription-Token": api_key},
    )
    response.raise_for_status()
    payload = response.json()
    rows = payload.get("web", {}).get("results", [])[:3]
    return [
        {
            "title": row.get("title", "Untitled"),
            "url": row.get("url", ""),
            "snippet": row.get("description") or row.get("snippet") or "",
            "source": "brave",
        }
        for row in rows
        if row.get("url")
    ]


async def _search_exa(client: httpx.AsyncClient, query: str, api_key: str) -> list[dict[str, Any]]:
    response = await client.post(
        "https://api.exa.ai/search",
        headers={"Content-Type": "application/json", "x-api-key": api_key},
        json={"query": query, "numResults": 3, "contents": {"text": {"maxCharacters": 600}}},
    )
    response.raise_for_status()
    payload = response.json()
    rows = payload.get("results", [])[:3]
    return [
        {
            "title": row.get("title", "Untitled"),
            "url": row.get("url", ""),
            "snippet": row.get("text") or row.get("snippet") or row.get("summary") or "",
            "source": "exa",
        }
        for row in rows
        if row.get("url")
    ]


async def _default_search(query: str) -> list[dict[str, Any]]:
    backend, api_key = _get_search_credentials()
    async with httpx.AsyncClient(timeout=30.0) as client:
        if backend == "brave":
            return await _search_brave(client, query, api_key)
        return await _search_exa(client, query, api_key)


def _create_sandbox() -> tuple[Any | None, str]:
    create = getattr(sandbox, "create", None)
    if callable(create):
        return None, str(create())
    backend = sandbox.create_backend(os.environ.get("MANTLE_SANDBOX_BACKEND", "docker"))
    return backend, str(backend.create())


def _destroy_sandbox(backend: Any | None, sandbox_id: str) -> None:
    if backend is not None:
        backend.destroy(sandbox_id)
        return
    destroy = getattr(sandbox, "destroy", None)
    if callable(destroy):
        destroy(sandbox_id)


async def _call_search(search_fn: SearchFn, query: str) -> list[dict[str, Any]]:
    value = search_fn(query)
    if inspect.isawaitable(value):
        value = await value
    return [dict(item) for item in value]


async def _run_subagent(agent_id: int, sub_query: str, search_fn: SearchFn) -> list[dict[str, Any]]:
    backend: Any | None = None
    sandbox_id = ""
    try:
        backend, sandbox_id = await asyncio.to_thread(_create_sandbox)
        rows = await _call_search(search_fn, sub_query)
        enriched: list[dict[str, Any]] = []
        for rank, row in enumerate(rows[:3], start=1):
            enriched.append(
                {
                    "agent_id": agent_id,
                    "sub_query": sub_query,
                    "sandbox_id": sandbox_id,
                    "rank": rank,
                    "title": row.get("title", "Untitled"),
                    "url": row.get("url", ""),
                    "snippet": row.get("snippet", ""),
                    "source": row.get("source", "search"),
                }
            )
        return enriched
    finally:
        if sandbox_id:
            await asyncio.to_thread(_destroy_sandbox, backend, sandbox_id)


async def dispatch_research(query: str, n_agents: int, search_fn: SearchFn | None = None) -> list[dict[str, Any]]:
    """Dispatch N sandboxed research workers and return their top search results."""

    agent_count = max(1, min(int(n_agents), 10))
    sub_queries = _split_query(query, agent_count)
    backend_search = search_fn or _default_search
    batches = await asyncio.gather(
        *[_run_subagent(agent_id, sub_query, backend_search) for agent_id, sub_query in enumerate(sub_queries, start=1)]
    )
    return [result for batch in batches for result in batch]
