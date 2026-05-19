from __future__ import annotations

import os
from typing import Any
from urllib.parse import parse_qs, urlparse

from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

try:
    from gateway.eval_mode import is_eval_mode
except ModuleNotFoundError:  # pragma: no cover - scheduler can run without gateway on sys.path

    def is_eval_mode() -> bool:
        return os.environ.get("MANTLE_EVAL_MODE", "").lower() in ("1", "true", "yes")


async def noop_job() -> None:
    """Serializable no-op job target for persistence tests and smoke checks."""


def _redis_jobstore(redis_url: str) -> RedisJobStore:
    parsed = urlparse(redis_url)
    query = parse_qs(parsed.query)
    db = int((parsed.path or "/0").strip("/") or "0")
    connect_args: dict[str, Any] = {
        "host": parsed.hostname or "127.0.0.1",
        "port": parsed.port or 6379,
        "db": db,
        "jobs_key": query.get("jobs_key", [os.environ.get("MANTLE_SCHEDULER_JOBS_KEY", "apscheduler.jobs")])[0],
        "run_times_key": query.get(
            "run_times_key", [os.environ.get("MANTLE_SCHEDULER_RUN_TIMES_KEY", "apscheduler.run_times")]
        )[0],
    }
    if parsed.password:
        connect_args["password"] = parsed.password
    return RedisJobStore(**connect_args)


def init_scheduler(redis_url: str = "redis://127.0.0.1:6379/0") -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(jobstores={"default": _redis_jobstore(redis_url)})
    if not is_eval_mode():
        scheduler.start(paused=True)
    return scheduler


async def add_job(scheduler: AsyncIOScheduler, func_path: str, trigger: str, **kwargs: Any):
    if not scheduler.running and not is_eval_mode():
        scheduler.start(paused=True)
    job_id = kwargs.pop("id", None)
    replace_existing = kwargs.pop("replace_existing", True)
    return scheduler.add_job(func_path, trigger=trigger, id=job_id, replace_existing=replace_existing, **kwargs)


def shutdown_scheduler(scheduler: AsyncIOScheduler) -> None:
    if scheduler.running:
        scheduler.shutdown(wait=True)
