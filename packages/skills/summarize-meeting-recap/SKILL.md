---
name: summarize-meeting-recap
description: Convert notes or transcripts into decisions, action items, owners, risks, and follow-ups.
when_to_use: Invoke when a user supplies meeting notes, call transcripts, or rough discussion bullets to summarize.
capability: summarize
version: 1.0.0
license: MIT
author: Mantle
metadata:
  tags:
    - summarize
    - meeting
    - action-items
---

# Summarize meeting recap

This is a markdown playbook — invoke via bash, not skill_mcp()

Use this skill to produce crisp meeting summaries with decisions and accountable next steps.

## Script

`scripts/recap.py` accepts `notes` and optional `attendees` and emits a recap template.
