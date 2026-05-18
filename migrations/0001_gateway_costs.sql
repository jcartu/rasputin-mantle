-- 0001_gateway_costs.sql
-- Retroactive: gateway_costs table already created by cost_wall.py inline SQL.
-- This migration ensures the version table tracks it.
CREATE TABLE IF NOT EXISTS gateway_costs(
    workspace_id TEXT NOT NULL,
    model TEXT NOT NULL,
    ts TIMESTAMP NOT NULL,
    input_tokens INT NOT NULL,
    output_tokens INT NOT NULL,
    cost_usd NUMERIC NOT NULL
);
