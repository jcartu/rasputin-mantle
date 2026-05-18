---
name: research-literature-review
description: Plan and synthesize a literature review with themes, methods, evidence quality, and citations.
when_to_use: Invoke when a user asks for academic, technical, policy, or scientific literature review support.
capability: research
version: 1.0.0
license: MIT
author: Mantle
metadata:
  tags:
    - research
    - literature-review
    - synthesis
---

# Research literature review

This is a markdown playbook — invoke via bash, not skill_mcp()

Use this skill to turn a research question into search strings, inclusion criteria, extraction fields, and a synthesis outline.

## Script

`scripts/review.py` accepts `question`, `domains`, and `years` and returns a review plan.
