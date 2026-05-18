from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from gateway.routes.sessions import SessionCreateRequest, create_session

router = APIRouter()
_writer: Any = None
_scheduler: AsyncIOScheduler | None = None
_memory_tasks: dict[str, "ScheduledTask"] = {}


class ScheduledTaskCreate(BaseModel):
    name: str
    task_prompt: str = Field(alias="query")
    cron: str
    start_date: dt.datetime | None = None
    end_date: dt.datetime | None = None
    max_runs: int | None = None

    model_config = {"populate_by_name": True}


class ScheduledTaskUpdate(BaseModel):
    name: str | None = None
    task_prompt: str | None = Field(default=None, alias="query")
    cron: str | None = None
    start_date: dt.datetime | None = None
    end_date: dt.datetime | None = None
    max_runs: int | None = None
    paused: bool | None = None
    enabled: bool | None = None

    model_config = {"populate_by_name": True}


class ScheduledRun(BaseModel):
    session_id: str
    status: str
    ran_at: dt.datetime


class ScheduledTask(BaseModel):
    id: str
    name: str
    task_prompt: str
    cron: str
    start_date: dt.datetime | None = None
    end_date: dt.datetime | None = None
    max_runs: int | None = None
    runs_count: int = 0
    last_run_at: dt.datetime | None = None
    next_run_at: dt.datetime | None = None
    paused: bool = False
    created_at: dt.datetime
    updated_at: dt.datetime
    run_history: list[ScheduledRun] = Field(default_factory=list)


def set_writer(writer: Any) -> None:
    global _writer
    _writer = writer


def set_scheduler(scheduler: AsyncIOScheduler | None) -> None:
    global _scheduler
    _scheduler = scheduler


async def _pool() -> Any | None:
    if _writer is None or _writer._pool is None:
        return None
    return _writer._pool


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def _cron_trigger(cron: str, start_date: dt.datetime | None = None, end_date: dt.datetime | None = None) -> CronTrigger:
    fields = cron.split()
    if len(fields) != 5:
        raise HTTPException(status_code=400, detail={"error": "invalid_cron", "message": "Cron must have five fields"})
    return CronTrigger(
        minute=fields[0],
        hour=fields[1],
        day=fields[2],
        month=fields[3],
        day_of_week=fields[4],
        start_date=start_date,
        end_date=end_date,
    )


def _row_to_task(row: Any) -> ScheduledTask:
    return ScheduledTask(
        id=str(row["id"]),
        name=row["name"],
        task_prompt=row["task_prompt"],
        cron=row["cron_expr"],
        start_date=row["start_date"],
        end_date=row["end_date"],
        max_runs=row["max_runs"],
        runs_count=row["runs_count"],
        last_run_at=row["last_run_at"],
        next_run_at=row["next_run_at"],
        paused=row["paused"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


async def _schedule_job(task: ScheduledTask) -> None:
    if _scheduler is None:
        return
    try:
        trigger = _cron_trigger(task.cron, task.start_date, task.end_date)
        _scheduler.add_job(
            "gateway.routes.scheduled:run_scheduled_task",
            trigger=trigger,
            args=[task.id],
            id=task.id,
            replace_existing=True,
        )
        if task.paused:
            _scheduler.pause_job(task.id)
        job = _scheduler.get_job(task.id)
        task.next_run_at = job.next_run_time if job else None
    except Exception as exc:
        raise HTTPException(status_code=400, detail={"error": "schedule_failed", "message": str(exc)}) from exc


async def _remove_job(task_id: str) -> None:
    if _scheduler is None:
        return
    try:
        _scheduler.remove_job(task_id)
    except Exception:
        return


async def _persist_next_run(task: ScheduledTask) -> None:
    pool = await _pool()
    if pool is None:
        _memory_tasks[task.id] = task
        return
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE scheduled_jobs SET next_run_at = $1, updated_at = now() WHERE id = $2::uuid",
            task.next_run_at,
            task.id,
        )


async def run_scheduled_task(task_id: str) -> None:
    task = await get_scheduled_task(task_id)
    if task.paused or (task.max_runs is not None and task.runs_count >= task.max_runs):
        return
    session = await create_session(SessionCreateRequest())
    now = _utcnow()
    pool = await _pool()
    if pool is None:
        task.runs_count += 1
        task.last_run_at = now
        task.run_history.insert(0, ScheduledRun(session_id=session.session_id, status="created", ran_at=now))
        _memory_tasks[task.id] = task
        return
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE scheduled_jobs
            SET runs_count = runs_count + 1, last_run_at = $1, updated_at = now()
            WHERE id = $2::uuid
            """,
            now,
            task_id,
        )


@router.get("", response_model=list[ScheduledTask])
async def list_scheduled_tasks() -> list[ScheduledTask]:
    pool = await _pool()
    if pool is None:
        return sorted(_memory_tasks.values(), key=lambda task: task.created_at, reverse=True)
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM scheduled_jobs ORDER BY created_at DESC")
    return [_row_to_task(row) for row in rows]


@router.post("", response_model=ScheduledTask, status_code=status.HTTP_201_CREATED)
async def create_scheduled_task(request: ScheduledTaskCreate) -> ScheduledTask:
    task_id = str(uuid.uuid4())
    now = _utcnow()
    task = ScheduledTask(
        id=task_id,
        name=request.name,
        task_prompt=request.task_prompt,
        cron=request.cron,
        start_date=request.start_date,
        end_date=request.end_date,
        max_runs=request.max_runs,
        created_at=now,
        updated_at=now,
    )
    await _schedule_job(task)
    pool = await _pool()
    if pool is None:
        _memory_tasks[task_id] = task
        return task
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO scheduled_jobs (id, name, task_prompt, cron_expr, start_date, end_date, max_runs, next_run_at)
            VALUES ($1::uuid, $2, $3, $4, $5, $6, $7, $8)
            RETURNING *
            """,
            task.id,
            task.name,
            task.task_prompt,
            task.cron,
            task.start_date,
            task.end_date,
            task.max_runs,
            task.next_run_at,
        )
    return _row_to_task(row)


@router.get("/{task_id}", response_model=ScheduledTask)
async def get_scheduled_task(task_id: str) -> ScheduledTask:
    pool = await _pool()
    if pool is None:
        task = _memory_tasks.get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail={"error": "scheduled_task_not_found"})
        return task
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM scheduled_jobs WHERE id = $1::uuid", task_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"error": "scheduled_task_not_found"})
    return _row_to_task(row)


@router.patch("/{task_id}", response_model=ScheduledTask)
async def update_scheduled_task(task_id: str, request: ScheduledTaskUpdate) -> ScheduledTask:
    task = await get_scheduled_task(task_id)
    updates = request.model_dump(exclude_unset=True, by_alias=False)
    if request.enabled is not None:
        updates["paused"] = not request.enabled
    for field_name in ("name", "task_prompt", "start_date", "end_date", "max_runs", "paused"):
        if field_name in updates:
            setattr(task, field_name, updates[field_name])
    if "cron" in updates and updates["cron"] is not None:
        task.cron = str(updates["cron"])
    task.updated_at = _utcnow()
    await _schedule_job(task)
    await _persist_next_run(task)
    pool = await _pool()
    if pool is None:
        _memory_tasks[task_id] = task
        return task
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            UPDATE scheduled_jobs
            SET name = $2, task_prompt = $3, cron_expr = $4, start_date = $5, end_date = $6,
                max_runs = $7, paused = $8, next_run_at = $9, updated_at = now()
            WHERE id = $1::uuid
            RETURNING *
            """,
            task_id,
            task.name,
            task.task_prompt,
            task.cron,
            task.start_date,
            task.end_date,
            task.max_runs,
            task.paused,
            task.next_run_at,
        )
    return _row_to_task(row)


@router.patch("/{task_id}/pause", response_model=ScheduledTask)
async def pause_scheduled_task(task_id: str) -> ScheduledTask:
    return await update_scheduled_task(task_id, ScheduledTaskUpdate(paused=True))


@router.patch("/{task_id}/resume", response_model=ScheduledTask)
async def resume_scheduled_task(task_id: str) -> ScheduledTask:
    return await update_scheduled_task(task_id, ScheduledTaskUpdate(paused=False))


@router.delete("/{task_id}")
async def delete_scheduled_task(task_id: str) -> dict[str, str]:
    pool = await _pool()
    if pool is None:
        if task_id not in _memory_tasks:
            raise HTTPException(status_code=404, detail={"error": "scheduled_task_not_found"})
        _memory_tasks.pop(task_id, None)
        await _remove_job(task_id)
        return {"deleted": task_id}
    async with pool.acquire() as conn:
        row = await conn.fetchrow("DELETE FROM scheduled_jobs WHERE id = $1::uuid RETURNING id", task_id)
    if row is None:
        raise HTTPException(status_code=404, detail={"error": "scheduled_task_not_found"})
    await _remove_job(task_id)
    return {"deleted": task_id}
