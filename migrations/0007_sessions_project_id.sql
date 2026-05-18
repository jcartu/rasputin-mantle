-- 0007_sessions_project_id.sql (W4-001)
-- Link sessions to projects (nullable — null = personal scratch).
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'sessions' AND column_name = 'project_id'
    ) THEN
        -- sessions table is in-memory only (SessionStore), no DB table exists yet.
        -- This migration is a no-op placeholder. When sessions get DB persistence,
        -- add: ALTER TABLE sessions ADD COLUMN project_id UUID REFERENCES projects(id);
        RAISE NOTICE 'sessions table does not exist in DB yet — skipping project_id column';
    END IF;
END $$;
