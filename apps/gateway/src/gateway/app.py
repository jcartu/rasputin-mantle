from __future__ import annotations

# ruff: noqa: E402,I001

import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI

# Load .env from project root (walks up from this file)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".env"))
load_dotenv(os.path.join(os.path.expanduser("~"), ".dev", "rasputin-mantle", ".env"))

from gateway.config import settings
from gateway.eval_mode import is_eval_mode
from gateway.middleware import cost_ceiling_middleware
from gateway.cost_wall import default_cost_wall
from gateway.session_persistence import SessionEventWriter
from gateway.routes.absorb import router as absorb_router
from gateway.routes.agent import router as agent_router
from gateway.routes.files import router as files_router
from gateway.routes.mail import router as mail_router
from gateway.routes.mcp import router as mcp_router
from gateway.routes.memory import router as memory_router
from gateway.routes.neko_session import router as neko_session_router
from gateway.routes.playbooks import router as playbooks_router
from gateway.routes.project_kb import router as project_kb_router, set_writer as set_project_kb_writer
from gateway.routes.projects import router as projects_router, set_writer as set_projects_writer
from gateway.routes.research import router as research_router
from gateway.routes.sandbox_files import router as sandbox_files_router
from gateway.routes.sandbox_watch import router as sandbox_watch_router
from gateway.routes.scheduler import router as scheduler_router
from gateway.routes.scheduled import router as scheduled_router, set_scheduler as set_scheduled_scheduler
from gateway.routes.scheduled import set_writer as set_scheduled_writer
from gateway.routes.sessions import router as sessions_router, set_writer as set_sessions_writer
from gateway.routes.session_events import router as session_events_router, set_writer
from gateway.routes.share import router as share_router, set_writer as set_share_writer
from gateway.routes.skills import router as skills_router, session_router as session_skills_router
from gateway.routes.slack import router as slack_router, set_writer as set_slack_writer
from gateway.routes.voice import router as voice_router
from scheduler.jobs import init_scheduler, shutdown_scheduler

app = FastAPI(title="Rasputin Mantle Gateway", version="0.1.0")
app.add_middleware(cost_ceiling_middleware)
logger = logging.getLogger(__name__)

# Initialize session event writer
_event_writer = SessionEventWriter(settings.database_url)
_scheduler = None


def _start_scheduler_if_enabled(redis_url: str):
    if is_eval_mode():
        return None
    try:
        scheduler = init_scheduler(redis_url)
        scheduler.resume()
        return scheduler
    except Exception as exc:
        logger.warning("APScheduler unavailable: %s", exc)
        return None


@app.on_event("startup")
async def startup_event_writer() -> None:
    global _scheduler
    await _event_writer.initialize()
    set_writer(_event_writer)
    set_share_writer(_event_writer)
    set_sessions_writer(_event_writer)
    set_projects_writer(_event_writer)
    set_project_kb_writer(_event_writer)
    set_slack_writer(_event_writer)
    set_scheduled_writer(_event_writer)
    _scheduler = _start_scheduler_if_enabled(settings.redis_url)
    set_scheduled_scheduler(_scheduler)


app.include_router(sessions_router, prefix="/api/sessions")
app.include_router(session_skills_router, prefix="/api/sessions")
app.include_router(session_events_router, prefix="/api/sessions")
app.include_router(share_router, prefix="/api/share")
app.include_router(skills_router, prefix="/api/skills")
app.include_router(files_router, prefix="/api/files")
app.include_router(memory_router, prefix="/api/memory")
app.include_router(research_router, prefix="/api/research")
app.include_router(scheduler_router, prefix="/api/scheduler")
app.include_router(scheduled_router, prefix="/api/scheduled")
app.include_router(voice_router, prefix="/api/voice")
app.include_router(slack_router, prefix="/api/slack")
app.include_router(mail_router, prefix="/api/mail")
app.include_router(mcp_router, prefix="/api/mcp")
app.include_router(absorb_router, prefix="/api/absorb")
app.include_router(agent_router, prefix="/api/agent")
app.include_router(sandbox_files_router)
app.include_router(sandbox_watch_router)
app.include_router(neko_session_router)
app.include_router(playbooks_router, prefix="/api/playbooks")
app.include_router(projects_router, prefix="/api/projects")
app.include_router(project_kb_router, prefix="/api/projects")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await _event_writer.close()
    await default_cost_wall.close()
    if _scheduler is not None:
        shutdown_scheduler(_scheduler)
