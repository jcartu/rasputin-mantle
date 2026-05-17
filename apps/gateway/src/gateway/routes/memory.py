from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from gateway.memory_client import MemoryClient

router = APIRouter()
memory_client = MemoryClient()


class MemoryStoreRequest(BaseModel):
    key: str | None = None
    value: Any | None = None
    content: str | None = None
    source: str = "gateway"
    importance: float = 0.5


@router.post("/store")
async def memory_store(request: MemoryStoreRequest | None = None, content: str | None = None, source: str = "gateway") -> dict:
    if request is not None:
        key = request.key or request.source
        value = request.value if request.value is not None else request.content
    else:
        key = source
        value = content
    return await memory_client.store(str(key), value)


@router.get("/search")
async def memory_search(query: str, limit: int = 10) -> dict:
    return await memory_client.query(query, k=limit)


@router.post("/reflect")
async def memory_reflect(query: str, limit: int = 10) -> dict:
    return await memory_client.reflect(query, k=limit)


@router.get("/stats")
async def memory_stats() -> dict:
    return await memory_client.stats()
