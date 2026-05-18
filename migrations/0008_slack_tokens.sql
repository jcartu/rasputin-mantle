-- 0008_slack_tokens.sql (W6-001)
-- Slack OAuth installation tokens.
CREATE TABLE IF NOT EXISTS slack_installations (
    id              BIGSERIAL PRIMARY KEY,
    team_id         TEXT NOT NULL,
    team_name       TEXT,
    bot_token       TEXT NOT NULL,
    signing_secret  TEXT NOT NULL,
    installed_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
