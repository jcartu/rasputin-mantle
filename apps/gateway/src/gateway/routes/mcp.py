from __future__ import annotations

import httpx
import time
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class McpServerCreate(BaseModel):
    name: str
    url: str
    transport: str = 'streamable-http'


class McpServerUpdate(BaseModel):
    enabled: bool | None = None


class McpServer(BaseModel):
    id: str
    name: str
    url: str
    transport: str = 'streamable-http'
    enabled: bool = True
    health: str = 'unknown'
    tools: list[str] = []
    last_check: float = 0.0
    created_at: float = 0.0


_servers: dict[str, McpServer] = {}


@router.post('/')
async def register_server(request: McpServerCreate) -> dict:
    server_id = str(uuid.uuid4())
    server = McpServer(
        id=server_id,
        name=request.name,
        url=request.url,
        transport=request.transport,
        enabled=True,
        created_at=time.time(),
    )
    _servers[server_id] = server
    return server.model_dump()


@router.get('/')
async def list_servers() -> list[dict]:
    return [s.model_dump() for s in _servers.values()]


@router.get('/{server_id}')
async def get_server(server_id: str) -> dict:
    server = _servers.get(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail={'error': 'mcp_server_not_found'})
    return server.model_dump()


@router.delete('/{server_id}')
async def unregister_server(server_id: str) -> dict:
    if server_id not in _servers:
        raise HTTPException(status_code=404, detail={'error': 'mcp_server_not_found'})
    del _servers[server_id]
    return {'deleted': server_id}


@router.patch('/{server_id}')
async def update_server(server_id: str, request: McpServerUpdate) -> dict:
    server = _servers.get(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail={'error': 'mcp_server_not_found'})
    if request.enabled is not None:
        server.enabled = request.enabled
    return server.model_dump()


@router.post('/{server_id}/health')
async def check_server_health(server_id: str) -> dict:
    server = _servers.get(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail={'error': 'mcp_server_not_found'})

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(f'{server.url}/health')
            server.health = 'healthy' if resp.status_code == 200 else 'unhealthy'
            server.last_check = time.time()
            try:
                tools_resp = await client.get(f'{server.url}/tools')
                if tools_resp.status_code == 200:
                    try:
                        tools_data = tools_resp.json()
                        server.tools = [t.get('name', t) if isinstance(t, dict) else t for t in tools_data.get('tools', [])]
                    except Exception:
                        pass
            except httpx.RequestError:
                pass
        except httpx.RequestError:
            server.health = 'unreachable'
            server.last_check = time.time()

    return server.model_dump()


@router.post('/health-all')
async def check_all_health() -> list[dict]:
    results = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        for server in _servers.values():
            try:
                resp = await client.get(f'{server.url}/health')
                server.health = 'healthy' if resp.status_code == 200 else 'unhealthy'
            except httpx.RequestError:
                server.health = 'unreachable'
            server.last_check = time.time()
            results.append(server.model_dump())
    return results
