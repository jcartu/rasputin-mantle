---
name: data-analysis
description: "Analyze data with DuckDB, Jupyter notebooks, Evidence reports, and Apache Superset dashboards."
version: 0.1.0
author: Rasputin Mantle
license: MIT
capability: data_analysis
metadata:
  hermes:
    tags: [data, analysis, duckdb, jupyter, evidence, superset, sql, charts]
---

# Data Analysis

Analyze datasets, generate reports, and build dashboards. Uses DuckDB for embedded analytics, Jupyter for notebooks, Evidence for SQL+Markdown BI reports, and Apache Superset for dashboards.

This is a markdown playbook — invoke via bash, not skill_mcp().

## When to use

- User asks to analyze a dataset, CSV, or database
- User wants charts, statistics, or data visualizations
- User needs a BI report or dashboard

## Stack

| Component | Tool | License | Role |
|-----------|------|---------|------|
| Analytics DB | DuckDB | MIT | Embedded columnar DB |
| Notebooks | JupyterLab | BSD-3-Clause | Interactive notebooks |
| BI reports | Evidence | MIT | SQL+Markdown reports |
| Dashboards | Apache Superset | Apache-2.0 | BI dashboard platform |

## Workflow

1. Load data into DuckDB (CSV, Parquet, JSON, or SQL)
2. Explore with SQL queries or Python/pandas
3. Generate visualizations (matplotlib, seaborn, plotly)
4. Build report (Evidence for SQL+MD, Jupyter for notebooks)
5. Deploy dashboard if needed (Superset)

## Commands

Quick analysis with DuckDB:
```bash
# Install DuckDB CLI
pip install duckdb

# Query a CSV directly
duckdb -c "SELECT * FROM read_csv_auto('data.csv') LIMIT 10"

# Full analysis
duckdb analysis.duckdb <<'SQL'
CREATE TABLE data AS SELECT * FROM read_csv_auto('data.csv');
SELECT category, COUNT(*), AVG(value) FROM data GROUP BY category;
SQL
```

Jupyter notebook:
```bash
jupyter lab --ip=127.0.0.1 --port=8888 --no-browser
```

Evidence report:
```bash
# Clone Evidence
git clone https://github.com/evidence-dev/evidence
cd evidence
# Create queries and markdown in evidence project
```

## Constraints

- All data processing in sandbox
- Never expose raw data outside sandbox without confirmation
- DuckDB files stay in workspace
