-- 0004_projects.sql (W4-001)
-- Persistent project workspaces with knowledge base.
CREATE TABLE IF NOT EXISTS projects (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                    TEXT NOT NULL,
    slug                    TEXT NOT NULL UNIQUE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    owner_id                TEXT NOT NULL,
    visibility              TEXT NOT NULL DEFAULT 'private' CHECK (visibility IN ('private', 'team', 'public')),
    default_planner         TEXT,
    system_prompt_addendum  TEXT,
    allowed_tools           JSONB DEFAULT '[]'::jsonb
);
