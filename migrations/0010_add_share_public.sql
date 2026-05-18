-- 0010_add_share_public.sql (W3)
-- Owner-facing public replay toggle mirrored from share_tokens.
ALTER TABLE sessions
  ADD COLUMN IF NOT EXISTS share_public BOOLEAN NOT NULL DEFAULT false;

CREATE INDEX IF NOT EXISTS idx_sessions_share_public
  ON sessions (share_public)
  WHERE share_public = true;
