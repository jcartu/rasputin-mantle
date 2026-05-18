---
name: schedule-daily-standup
description: Prepare a recurring daily standup schedule, prompt, agenda, and reminders.
when_to_use: Invoke when a user wants to schedule, automate, or standardize daily team standups.
capability: schedule
version: 1.0.0
license: MIT
author: Mantle
metadata:
  tags:
    - schedule
    - standup
    - team-ritual
---

# Schedule daily standup

This is a markdown playbook — invoke via bash, not skill_mcp()

Use this skill to generate a daily standup routine with participants, time, agenda, and reminder copy.

## Script

`scripts/standup.py` accepts `team`, `time`, and `timezone` and emits a routine spec.
