from __future__ import annotations

import subprocess
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from scheduler.jobs import add_job, init_scheduler, shutdown_scheduler


def redis_available() -> bool:
    try:
        result = subprocess.run(["redis-cli", "-h", "127.0.0.1", "-p", "6379", "ping"], capture_output=True, timeout=5)
        return result.returncode == 0 and b"PONG" in result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


@pytest.mark.skipif(not redis_available(), reason="Redis is not available at 127.0.0.1:6379")
@pytest.mark.asyncio
async def test_scheduler_job_persists_across_restart() -> None:
    suffix = uuid.uuid4().hex
    redis_url = f"redis://127.0.0.1:6379/0?jobs_key=r5.jobs.{suffix}&run_times_key=r5.run_times.{suffix}"
    job_id = f"r5-{suffix}"

    first = init_scheduler(redis_url)
    try:
        await add_job(
            first,
            "scheduler.jobs:noop_job",
            "date",
            id=job_id,
            run_date=datetime.now(timezone.utc) + timedelta(days=1),
        )
        assert first.get_job(job_id) is not None
    finally:
        shutdown_scheduler(first)

    second = init_scheduler(redis_url)
    try:
        loaded = second.get_job(job_id)
        assert loaded is not None
        assert loaded.id == job_id
        assert loaded.func_ref == "scheduler.jobs:noop_job"
    finally:
        shutdown_scheduler(second)
