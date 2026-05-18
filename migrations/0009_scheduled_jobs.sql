-- 0009_scheduled_jobs.sql (W6-004)
-- Scheduled task definitions (persists across gateway restarts).
CREATE TABLE IF NOT EXISTS scheduled_jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    task_prompt     TEXT NOT NULL,
    cron_expr       TEXT NOT NULL,
    start_date      TIMESTAMPTZ,
    end_date        TIMESTAMPTZ,
    max_runs        INT,
    runs_count      INT NOT NULL DEFAULT 0,
    last_run_at     TIMESTAMPTZ,
    next_run_at     TIMESTAMPTZ,
    paused          BOOLEAN NOT NULL DEFAULT false,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
