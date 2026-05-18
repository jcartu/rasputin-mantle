---
name: schedule-weekly-report
description: Create a recurring weekly report cadence with sections, owners, metrics, and delivery plan.
when_to_use: Invoke when a user wants to schedule weekly status reports, executive updates, or metric digests.
capability: schedule
version: 1.0.0
license: MIT
author: Mantle
metadata:
  tags:
    - schedule
    - weekly-report
    - status-update
---

# Schedule weekly report

This is a markdown playbook — invoke via bash, not skill_mcp()

Use this skill to define report cadence, sections, owners, data sources, and reminder text.

## Script

`scripts/report.py` accepts `audience`, `weekday`, and `metrics` and emits a weekly report routine.
