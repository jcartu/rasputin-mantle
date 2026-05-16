from __future__ import annotations

from fastapi import FastAPI

from gateway.middleware import cost_ceiling_middleware
from gateway.routes.files import router as files_router
from gateway.routes.sessions import router as sessions_router
from gateway.routes.skills import router as skills_router

app = FastAPI(title="Rasputin Mantle Gateway", version="0.1.0")
app.add_middleware(cost_ceiling_middleware)
app.include_router(sessions_router, prefix="/api/sessions")
app.include_router(skills_router, prefix="/api/skills")
app.include_router(files_router, prefix="/api/files")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}
