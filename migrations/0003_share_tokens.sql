-- 0003_share_public.sql (W3-001)
-- Share tokens for public replay links.
CREATE TABLE IF NOT EXISTS share_tokens (
    id          TEXT PRIMARY KEY,
    session_id  UUID NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at  TIMESTAMPTZ,              -- NULL = never expires
    public      BOOLEAN NOT NULL DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_share_tokens_session
  ON share_tokens (session_id);

CREATE INDEX IF NOT EXISTS idx_share_tokens_expires
  ON share_tokens (expires_at) WHERE expires_at IS NOT NULL;
