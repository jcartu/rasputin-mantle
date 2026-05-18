from __future__ import annotations

# ruff: noqa: E402,I001

import os
from dotenv import load_dotenv
from fastapi import FastAPI

# Load .env from project root (walks up from this file)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".env"))
load_dotenv(os.path.join(os.path.expanduser("~"), ".dev", "rasputin-mantle", ".env"))

from gateway.middleware import cost_ceiling_middleware
from gateway.cost_wall import default_cost_wall
from gateway.routes.absorb import router as absorb_router
from gateway.routes.agent import router as agent_router
from gateway.routes.files import router as files_router
from gateway.routes.mcp import router as mcp_router
from gateway.routes.memory import router as memory_router
from gateway.routes.neko_session import router as neko_session_router
from gateway.routes.research import router as research_router
from gateway.routes.sandbox_files import router as sandbox_files_router
from gateway.routes.sandbox_watch import router as sandbox_watch_router
from gateway.routes.scheduler import router as scheduler_router
from gateway.routes.sessions import router as sessions_router
from gateway.routes.skills import router as skills_router
from gateway.routes.voice import router as voice_router

app = FastAPI(title="Rasputin Mantle Gateway", version="0.1.0")
app.add_middleware(cost_ceiling_middleware)
app.include_router(sessions_router, prefix="/api/sessions")
app.include_router(skills_router, prefix="/api/skills")
app.include_router(files_router, prefix="/api/files")
app.include_router(memory_router, prefix="/api/memory")
app.include_router(research_router, prefix="/api/research")
app.include_router(scheduler_router, prefix="/api/scheduler")
app.include_router(voice_router, prefix="/api/voice")
app.include_router(mcp_router, prefix="/api/mcp")
app.include_router(absorb_router, prefix="/api/absorb")
app.include_router(agent_router, prefix="/api/agent")
app.include_router(sandbox_files_router)
app.include_router(sandbox_watch_router)
app.include_router(neko_session_router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


@app.on_event("shutdown")
async def close_cost_wall() -> None:
    await default_cost_wall.close()
