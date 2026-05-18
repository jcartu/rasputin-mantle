from __future__ import annotations

from dataclasses import asdict
from typing import Any

from codeact.skills_loader import (
    SkillLoaderError,
    discover_skills,
    invoke_skill,
    save_session_as_skill,
    skill_detail,
)
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()
session_router = APIRouter()


class InvokeSkillRequest(BaseModel):
    session_id: str | None = None
    args: dict[str, Any] = Field(default_factory=dict)


class SaveAsSkillRequest(BaseModel):
    name: str
    description: str
    intent_tags: list[str] = Field(default_factory=list)
    publish_publicly: bool = False


@router.get("")
async def list_skills(session_id: str | None = Query(default=None)) -> dict[str, list[dict[str, Any]]]:
    try:
        return {"skills": [asdict(skill) for skill in discover_skills(session_id)]}
    except SkillLoaderError as exc:
        raise HTTPException(status_code=400, detail={"message": str(exc)}) from exc


@router.get("/{name}")
async def get_skill(name: str, session_id: str | None = Query(default=None)) -> dict[str, Any]:
    try:
        return skill_detail(name, session_id)
    except SkillLoaderError as exc:
        raise HTTPException(status_code=404, detail={"message": str(exc)}) from exc


@router.post("/{name}/invoke")
async def invoke_skill_route(name: str, request: InvokeSkillRequest) -> dict[str, Any]:
    try:
        return asdict(invoke_skill(name, request.args, request.session_id))
    except SkillLoaderError as exc:
        raise HTTPException(status_code=404, detail={"message": str(exc)}) from exc


@session_router.post("/{session_id}/save-as-skill")
async def save_as_skill(session_id: str, request: SaveAsSkillRequest) -> dict[str, Any]:
    try:
        skill = save_session_as_skill(
            session_id=session_id,
            name=request.name,
            description=request.description,
            tags=request.intent_tags,
            publish_publicly=request.publish_publicly,
        )
    except SkillLoaderError as exc:
        raise HTTPException(status_code=400, detail={"message": str(exc)}) from exc
    return asdict(skill)
