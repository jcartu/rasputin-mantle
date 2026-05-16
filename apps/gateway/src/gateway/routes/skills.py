from __future__ import annotations

from fastapi import APIRouter
from skills.manifest import generate_manifest
from skills.registry import SkillRegistry

from gateway.config import settings

router = APIRouter()


@router.get("")
async def list_skills() -> dict[str, list[dict[str, str]]]:
    registry = SkillRegistry(settings.skills_dir)
    return generate_manifest(registry)
