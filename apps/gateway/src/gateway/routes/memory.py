from __future__ import annotations

import httpx

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post('/store')
async def memory_store(content: str, source: str = 'gateway', importance: float = 0.5) -> dict:
    async with httpx.AsyncClient(base_url='http://127.0.0.1:7777', timeout=60.0) as client:
        try:
            resp = await client.post('/commit', json={'text': content, 'source': source, 'importance': importance})
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail={'error': 'memory_store_failed'})
            return resp.json()
        except httpx.ConnectError as exc:
            raise HTTPException(status_code=503, detail={'error': 'memory_unavailable'}) from exc


@router.get('/search')
async def memory_search(query: str, limit: int = 10) -> dict:
    async with httpx.AsyncClient(base_url='http://127.0.0.1:7777', timeout=60.0) as client:
        try:
            resp = await client.get('/search', params={'q': query, 'limit': limit})
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail={'error': 'memory_search_failed'})
            return resp.json()
        except httpx.ConnectError as exc:
            raise HTTPException(status_code=503, detail={'error': 'memory_unavailable'}) from exc


@router.post('/reflect')
async def memory_reflect(query: str, limit: int = 10) -> dict:
    async with httpx.AsyncClient(base_url='http://127.0.0.1:7777', timeout=60.0) as client:
        try:
            resp = await client.post('/reflect', json={'q': query, 'limit': limit})
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail={'error': 'memory_reflect_failed'})
            return resp.json()
        except httpx.ConnectError as exc:
            raise HTTPException(status_code=503, detail={'error': 'memory_unavailable'}) from exc


@router.get('/stats')
async def memory_stats() -> dict:
    async with httpx.AsyncClient(base_url='http://127.0.0.1:7777', timeout=60.0) as client:
        try:
            resp = await client.get('/stats')
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail={'error': 'memory_stats_failed'})
            return resp.json()
        except httpx.ConnectError as exc:
            raise HTTPException(status_code=503, detail={'error': 'memory_unavailable'}) from exc
