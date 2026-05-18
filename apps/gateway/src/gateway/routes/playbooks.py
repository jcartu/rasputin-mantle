from __future__ import annotations

import uuid
from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from shared.schemas import Playbook

router = APIRouter()

# In-memory store for user-saved playbooks
_user_playbooks: dict[str, Playbook] = {}

def load_seed_playbooks() -> list[Playbook]:
    seed_file = Path(__file__).parent.parent.parent.parent.parent / "data" / "seed-playbooks.yaml"
    if not seed_file.exists():
        return []
    with open(seed_file, "r") as f:
        data = yaml.safe_load(f)
    return [Playbook(**item) for item in data] if data else []

@router.get("", response_model=list[Playbook])
async def list_playbooks() -> list[Playbook]:
    seeds = load_seed_playbooks()
    return seeds + list(_user_playbooks.values())

class SavePlaybookRequest(BaseModel):
    session_id: str
    title: str
    description: str

@router.post("", response_model=Playbook)
async def save_playbook(request: SavePlaybookRequest) -> Playbook:
    # In a real implementation, we would extract the prompt from the session trace.
    # For now, we'll just use a placeholder prompt.
    playbook = Playbook(
        id=str(uuid.uuid4()),
        title=request.title,
        description=request.description,
        intent="Custom",
        prompt_template="Custom prompt from session " + request.session_id,
        created_by="you",
        created_at="2026-05-19T00:00:00Z",
    )
    _user_playbooks[playbook.id] = playbook
    return playbook

@router.get("/{playbook_id}", response_model=Playbook)
async def get_playbook(playbook_id: str) -> Playbook:
    seeds = load_seed_playbooks()
    for seed in seeds:
        if seed.id == playbook_id:
            return seed
    if playbook_id in _user_playbooks:
        return _user_playbooks[playbook_id]
    raise HTTPException(status_code=404, detail="Playbook not found")
