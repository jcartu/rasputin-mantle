from __future__ import annotations

import pytest
from gateway.memory_client import MemoryClient


@pytest.mark.asyncio
async def test_memory_client_stub_round_trip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RASPUTIN_MEMORY_URL", raising=False)
    MemoryClient._stub_store.clear()
    MemoryClient._logged_fallback = False

    client = MemoryClient(memory_url="")
    stored = await client.store("r5-memory", {"fact": "wide research dispatch uses sandboxes"})
    result = await client.query("wide research", k=5)

    assert stored["backend"] == "local_stub"
    assert result["backend"] == "local_stub"
    assert result["results"]
    assert result["results"][0]["key"] == "r5-memory"


@pytest.mark.asyncio
async def test_memory_routes_use_client_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    from gateway.routes.memory import memory_client

    monkeypatch.setattr(memory_client, "memory_url", "")
    MemoryClient._stub_store.clear()

    await memory_client.store("route-key", "route fallback value")
    result = await memory_client.query("fallback", k=3)

    assert result["backend"] == "local_stub"
    assert any(item["key"] == "route-key" for item in result["results"])
