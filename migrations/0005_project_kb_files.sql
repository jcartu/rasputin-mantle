-- 0005_project_kb_files.sql (W4-001)
-- Knowledge base files per project.
CREATE TABLE IF NOT EXISTS project_kb_files (
    id          BIGSERIAL PRIMARY KEY,
    project_id  UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    filename    TEXT NOT NULL,
    mime_type   TEXT,
    size_bytes  BIGINT NOT NULL DEFAULT 0,
    sha256      TEXT NOT NULL,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    storage_path TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_kb_files_project
  ON project_kb_files (project_id);
