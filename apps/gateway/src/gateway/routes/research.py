from __future__ import annotations

import asyncio
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
    task_id = str(uuid.uuid4())
    task = ResearchTask(
        id=task_id,
        query=request.query,
        status='running',
        created_at=time.time(),
    )
    _tasks[task_id] = task

    source_list = request.sources or ['web_search', 'arxiv', 'github', 'news', 'discussions']
    agents = source_list[:request.max_agents]

    async def _agent(source: str) -> dict:
        await asyncio.sleep(0.1)
        return {
            'source': source,
            'status': 'completed',
            'items': [{
                'title': f'{source} result for: {request.query}',
                'url': f'https://{source}.example.com/search?q={request.query}',
                'snippet': f'Simulated result from {source}',
            }],
        }

    results = await asyncio.gather(*[_agent(s) for s in agents], return_exceptions=True)

    completed = []
    for r in results:
        if isinstance(r, Exception):
            completed.append({'source': 'unknown', 'status': 'error', 'error': str(r)})
        else:
            completed.append(r)

    task.status = 'completed'
    task.results = completed
    task.completed_at = time.time()

    return {
        'id': task_id,
        'query': request.query,
        'status': task.status,
        'agents_used': len(agents),
        'results': completed,
        'elapsed_ms': int((task.completed_at - task.created_at) * 1000),
    }


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
