-- 0002_session_events.sql (W3-000)
-- Persistent session trace storage for replay + share.
CREATE TABLE IF NOT EXISTS session_events (
    id          BIGSERIAL PRIMARY KEY,
    session_id  UUID NOT NULL,
    seq         INTEGER NOT NULL,         -- monotonic within session
    ts          TIMESTAMPTZ NOT NULL DEFAULT now(),
    event_type  TEXT NOT NULL,            -- 'tool_call', 'reasoning', 'file_touch', 'screenshot', 'error', 'completion'
    payload     JSONB NOT NULL,           -- full event body
    UNIQUE (session_id, seq)
);

CREATE INDEX IF NOT EXISTS idx_session_events_session_seq
  ON session_events (session_id, seq);

CREATE INDEX IF NOT EXISTS idx_session_events_session_ts
  ON session_events (session_id, ts);
