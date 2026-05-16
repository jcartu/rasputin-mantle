from __future__ import annotations

import time
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class ScheduleCreate(BaseModel):
    name: str
    cron: str
    query: str


class ScheduleUpdate(BaseModel):
    enabled: bool | None = None


class Schedule(BaseModel):
    id: str
    name: str
    cron: str
    query: str
    enabled: bool
    last_run: float = 0.0
    next_run: float = 0.0
    created_at: float = 0.0


_schedules: dict[str, Schedule] = {}


def _parse_next_run(cron: str) -> float:
    return time.time() + 3600


@router.post('/')
async def create_schedule(request: ScheduleCreate) -> dict:
    schedule_id = str(uuid.uuid4())
    schedule = Schedule(
        id=schedule_id,
        name=request.name,
        cron=request.cron,
        query=request.query,
        enabled=True,
        next_run=_parse_next_run(request.cron),
        created_at=time.time(),
    )
    _schedules[schedule_id] = schedule
    return schedule.model_dump()


@router.get('/')
async def list_schedules() -> list[dict]:
    return [s.model_dump() for s in _schedules.values()]


@router.get('/{schedule_id}')
async def get_schedule(schedule_id: str) -> dict:
    schedule = _schedules.get(schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail={'error': 'schedule_not_found'})
    return schedule.model_dump()


@router.delete('/{schedule_id}')
async def delete_schedule(schedule_id: str) -> dict:
    if schedule_id not in _schedules:
        raise HTTPException(status_code=404, detail={'error': 'schedule_not_found'})
    del _schedules[schedule_id]
    return {'deleted': schedule_id}


@router.patch('/{schedule_id}')
async def update_schedule(schedule_id: str, request: ScheduleUpdate) -> dict:
    schedule = _schedules.get(schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail={'error': 'schedule_not_found'})
    if request.enabled is not None:
        schedule.enabled = request.enabled
        schedule.next_run = _parse_next_run(schedule.cron) if request.enabled else 0.0
    return schedule.model_dump()
