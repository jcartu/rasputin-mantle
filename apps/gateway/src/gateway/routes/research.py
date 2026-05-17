from __future__ import annotations

import time
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class ResearchRequest(BaseModel):
    query: str
    sources: list[str] | None = None
    max_agents: int = 5


class ResearchTask(BaseModel):
    id: str
    query: str
    status: str
    results: list = []
    created_at: float = 0.0
    completed_at: float = 0.0


_tasks: dict[str, ResearchTask] = {}


@router.post('/')
async def start_research(request: ResearchRequest) -> dict:
    task = ResearchTask(
        id=str(uuid.uuid4()),
        query=request.query,
        status='completed',
        results=[
            {'agent': index + 1, 'summary': f'Research placeholder result for: {request.query}'}
            for index in range(request.max_agents)
        ],
        created_at=time.time(),
        completed_at=time.time(),
    )
    _tasks[task.id] = task
    return task.model_dump()


@router.get('/{task_id}')
async def get_research(task_id: str) -> dict:
    task = _tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail={'error': 'research_not_found'})
    return task.model_dump()


@router.get('/')
async def list_research() -> list[dict]:
    return [
        {'id': t.id, 'query': t.query, 'status': t.status, 'created_at': t.created_at}
        for t in _tasks.values()
    ]
