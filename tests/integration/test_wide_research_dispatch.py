from __future__ import annotations

import asyncio
import time

import pytest
from wide_research import dispatcher
from wide_research.merger import merge_results


@pytest.mark.asyncio
async def test_dispatch_research_spawns_parallel_sandboxes_and_merges(monkeypatch: pytest.MonkeyPatch) -> None:
    created: list[str] = []
    destroyed: list[str] = []
    active = 0
    max_active = 0

    def create() -> str:
        sandbox_id = f"sandbox-{len(created) + 1}"
        created.append(sandbox_id)
        return sandbox_id

    def destroy(sandbox_id: str) -> None:
        destroyed.append(sandbox_id)

    async def search_fn(query: str) -> list[dict]:
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        await asyncio.sleep(0.01)
        active -= 1
        return [
            {"title": f"Result for {query}", "url": "https://example.com/shared", "snippet": "shared hit"},
            {"title": f"Unique {query}", "url": f"https://example.com/{query.replace(' ', '-')}", "snippet": query},
            {"title": "Another", "url": f"https://another.example/{time.time_ns()}", "snippet": "third"},
        ]

    monkeypatch.setattr(dispatcher.sandbox, "create", create, raising=False)
    monkeypatch.setattr(dispatcher.sandbox, "destroy", destroy, raising=False)

    results = await dispatcher.dispatch_research("agent memory systems", 4, search_fn=search_fn)
    markdown = merge_results(results)

    assert len(created) == 4
    assert sorted(destroyed) == sorted(created)
    assert max_active > 1
    assert len(results) == 12
    assert markdown.count("https://example.com/shared") == 1
    assert "## Wide Research Results" in markdown


def test_research_route_has_no_forbidden_smells() -> None:
    source = open("apps/gateway/src/gateway/routes/research.py", encoding="utf-8").read()
    assert "asyncio.sleep" not in source
    assert '"simulate": ' + "True" not in source
    blocked_phrase = "hardcoded "
    blocked_phrase += "research"
    assert blocked_phrase not in source.lower()
    assert "status_code == " + "503" not in source
