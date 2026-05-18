---
name: research-competitor-analysis
description: Compare competitors, positioning, pricing, strengths, weaknesses, and market gaps.
when_to_use: Invoke when a user asks for competitor research, market mapping, feature comparison, or positioning strategy.
capability: research
version: 1.0.0
license: MIT
author: Mantle
metadata:
  tags:
    - research
    - competitor-analysis
    - market-strategy
---

# Research competitor analysis

This is a markdown playbook — invoke via bash, not skill_mcp()

Use this skill to structure a competitive landscape review. Provide a `topic`, optional `competitors`, and optional `criteria`.

## Output

- competitor matrix
- differentiation notes
- risks and opportunities
- recommended next research steps

## Script

`scripts/analyze.py` reads JSON on stdin and emits a markdown analysis scaffold.
