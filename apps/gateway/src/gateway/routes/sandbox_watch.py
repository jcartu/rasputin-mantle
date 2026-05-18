from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from gateway.routes.sandbox_files import _sandbox_root

router = APIRouter()


@router.get("/api/sandbox/{session_id}/watch")
async def watch_sandbox(session_id: str) -> StreamingResponse:
    try:
        root = _sandbox_root(session_id)
    except HTTPException:
        raise

    async def event_generator():  # type: ignore[no-untyped-def]
        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[dict[str, object]] = asyncio.Queue(maxsize=256)
        observer = Observer()
        observer.schedule(_SandboxEventHandler(root, loop, queue), str(root), recursive=True)
        observer.start()
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"event: file_changed\ndata: {json.dumps(event, separators=(',', ':'))}\n\n"
                except asyncio.TimeoutError:
                    yield "event: heartbeat\ndata: {}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            observer.stop()
            await asyncio.to_thread(observer.join, 5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


class _SandboxEventHandler(FileSystemEventHandler):
    def __init__(self, root: Path, loop: asyncio.AbstractEventLoop, queue: asyncio.Queue[dict[str, object]]) -> None:
        self._root = root
        self._loop = loop
        self._queue = queue

    def on_modified(self, event: FileSystemEvent) -> None:
        self._publish(event)

    def on_created(self, event: FileSystemEvent) -> None:
        self._publish(event)

    def on_deleted(self, event: FileSystemEvent) -> None:
        self._publish(event)

    def on_moved(self, event: FileSystemEvent) -> None:
        self._publish(event)

    def _publish(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = Path(str(event.src_path))
        try:
            relative_path = f"/{path.resolve().relative_to(self._root).as_posix()}"
        except ValueError:
            relative_path = f"/{path.name}"
        payload = {"type": "file_changed", "path": relative_path, "timestamp": time.time()}
        self._loop.call_soon_threadsafe(_put_nowait, self._queue, payload)


def _put_nowait(queue: asyncio.Queue[dict[str, object]], payload: dict[str, object]) -> None:
    if not queue.full():
        queue.put_nowait(payload)
