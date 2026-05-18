from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ProjectVisibility = Literal["private", "team", "public"]
ProjectRole = Literal["owner", "editor", "viewer"]
ProjectPlanner = Literal["gpt-5.5", "opus-4-6", "sonnet-4-6", "kimi-k2-6"]


class ProjectSchema(BaseModel):
    id: str
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime
    owner_id: str
    visibility: ProjectVisibility = "private"
    default_planner: ProjectPlanner | None = None
    system_prompt_addendum: str | None = None
    allowed_tools: list[str] = Field(default_factory=list)


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=120, pattern=r"^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$")
    visibility: ProjectVisibility = "private"
    default_planner: ProjectPlanner | None = None
    system_prompt_addendum: str | None = None
    allowed_tools: list[str] = Field(default_factory=list)


class ProjectUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    slug: str | None = Field(
        default=None, min_length=1, max_length=120, pattern=r"^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$"
    )
    visibility: ProjectVisibility | None = None
    default_planner: ProjectPlanner | None = None
    system_prompt_addendum: str | None = None
    allowed_tools: list[str] | None = None


class ProjectMemberSchema(BaseModel):
    project_id: str
    user_id: str
    role: ProjectRole
    added_at: datetime


class ProjectMemberCreateRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=200)
    role: ProjectRole = "viewer"


class KBFileSchema(BaseModel):
    id: int
    project_id: str
    filename: str
    mime_type: str | None = None
    size_bytes: int
    sha256: str
    uploaded_at: datetime
    storage_path: str
