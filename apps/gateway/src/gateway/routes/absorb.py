from __future__ import annotations

import json
import pathlib

from fastapi import APIRouter, HTTPException

router = APIRouter()

_OUTPUTS_DIR = pathlib.Path('outputs/absorb')


@router.get('/feed')
async def get_absorb_feed(limit: int = 20) -> dict:
    data_path = _OUTPUTS_DIR / 'absorb-data.json'
    if not data_path.exists():
        return {'timestamp': None, 'records': [], 'message': 'No absorb data yet — wait for nightly run'}
    try:
        data = json.loads(data_path.read_text())
    except (json.JSONDecodeError, OSError):
        raise HTTPException(status_code=500, detail={'error': 'absorb_data_corrupt'})
    records = data.get('records', [])[:limit]
    return {
        'timestamp': data.get('timestamp'),
        'total': len(data.get('records', [])),
        'records': records,
    }


@router.get('/delta')
async def get_capability_delta() -> str:
    delta_path = _OUTPUTS_DIR / 'CAPABILITY_DELTA.md'
    if not delta_path.exists():
        return '# Capability Delta\n\nNo data yet — wait for nightly run.'
    try:
        return delta_path.read_text()
    except OSError:
        raise HTTPException(status_code=500, detail={'error': 'absorb_delta_unreadable'})
