from __future__ import annotations

from fastapi import FastAPI

from gateway.middleware import cost_ceiling_middleware
from gateway.routes.files import router as files_router
from gateway.routes.memory import router as memory_router
from gateway.routes.mcp import router as mcp_router
from gateway.routes.research import router as research_router
from gateway.routes.scheduler import router as scheduler_router
from gateway.routes.sessions import router as sessions_router
from gateway.routes.skills import router as skills_router
from gateway.routes.voice import router as voice_router
from gateway.routes.absorb import router as absorb_router

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


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}
