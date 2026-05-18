---
name: build-internal-dashboard
description: Create an internal dashboard plan with metrics, filters, permissions, and starter layout.
when_to_use: Invoke when a user asks for an operations, analytics, admin, or internal reporting dashboard.
capability: build
version: 1.0.0
license: MIT
author: Mantle
metadata:
  tags:
    - build
    - dashboard
    - internal-tools
---

# Build internal dashboard

This is a markdown playbook — invoke via bash, not skill_mcp()

Use this skill to design dashboard information architecture, KPI cards, table views, filters, and role-aware actions.

## Script

`scripts/dashboard_plan.py` accepts `audience`, `metrics`, and `actions` and emits a dashboard spec.
