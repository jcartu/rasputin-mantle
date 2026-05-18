---
name: build-landing-page
description: Generate a conversion-focused landing page brief and starter HTML sections.
when_to_use: Invoke when a user wants to build, rewrite, or prototype a marketing landing page.
capability: build
version: 1.0.0
license: MIT
author: Mantle
metadata:
  tags:
    - build
    - landing-page
    - marketing
---

# Build landing page

This is a markdown playbook — invoke via bash, not skill_mcp()

Use this skill to create a hero, value propositions, social proof, pricing CTA, FAQ, and implementation checklist.

## Script

`scripts/scaffold.py` accepts `product`, `audience`, and `cta` and returns starter markup.
