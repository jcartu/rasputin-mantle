from __future__ import annotations

import os
import time
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from wide_research.dispatcher import SearchBackendUnavailable, dispatch_research
from wide_research.merger import merge_results

router = APIRouter()


class ResearchRequest(BaseModel):
    query: str
    sources: list[str] | None = None
    max_agents: int = Field(default=5, ge=1, le=10)


class ResearchTask(BaseModel):
    id: str
    query: str
    status: str
    results: list[dict] = Field(default_factory=list)
    merged_markdown: str = ""
    created_at: float = 0.0
    completed_at: float = 0.0


_tasks: dict[str, ResearchTask] = {}


def _has_search_backend() -> bool:
    brave_key = os.environ.get("BRAVE_SEARCH_API_KEY", "").strip()
    exa_key = os.environ.get("EXA_API_KEY", "").strip()
    return bool(brave_key or exa_key)


@router.post("/")
async def start_research(request: ResearchRequest) -> dict:
    if not _has_search_backend():
        raise HTTPException(
            status_code=501,
            detail={"error": "search_backend_unconfigured", "message": "Set BRAVE_SEARCH_API_KEY or EXA_API_KEY."},
        )

    created_at = time.time()
    try:
        results = await dispatch_research(request.query, request.max_agents)
    except SearchBackendUnavailable as exc:
        raise HTTPException(
            status_code=501,
            detail={"error": "search_backend_unconfigured", "message": str(exc)},
        ) from exc

    task = ResearchTask(
        id=str(uuid.uuid4()),
        query=request.query,
        status="completed",
        results=results,
        merged_markdown=merge_results(results),
        created_at=created_at,
        completed_at=time.time(),
    )
    _tasks[task.id] = task
    return task.model_dump()


@router.get("/{task_id}")
async def get_research(task_id: str) -> dict:
    task = _tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail={"error": "research_not_found"})
    return task.model_dump()


@router.get("/")
async def list_research() -> list[dict]:
    return [
        {"id": t.id, "query": t.query, "status": t.status, "created_at": t.created_at}
        for t in _tasks.values()
    ]
