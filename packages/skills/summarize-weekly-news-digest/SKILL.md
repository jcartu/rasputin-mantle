---
name: summarize-weekly-news-digest
description: Build a weekly news digest with themes, notable links, impact, and recommended actions.
when_to_use: Invoke when a user asks to summarize recent news, industry updates, releases, or announcements.
capability: summarize
version: 1.0.0
license: MIT
author: Mantle
metadata:
  tags:
    - summarize
    - news
    - digest
---

# Summarize weekly news digest

This is a markdown playbook — invoke via bash, not skill_mcp()

Use this skill to organize a set of headlines or links into a digest stakeholders can scan quickly.

## Script

`scripts/digest.py` accepts `topic` and `items` and emits a digest skeleton.
