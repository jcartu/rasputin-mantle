---
name: webapp-builder
description: "Build full-stack web applications from prompts using bolt.diy, Puck, Supabase, and PocketBase backends."
version: 0.1.0
author: Rasputin Mantle
license: MIT
capability: webapp_builder
metadata:
  hermes:
    tags: [webapp, fullstack, bolt, puck, supabase, pocketbase, frontend, backend]
---

# Webapp Builder

Build full-stack web applications from natural language prompts. Uses bolt.diy for prompt-to-app generation, Puck for visual editing, and Supabase/PocketBase for backend services.

This is a markdown playbook — invoke via bash, not skill_mcp().

## When to use

- User asks to build a web app, landing page, dashboard, or full-stack application
- User needs a backend with auth, database, and API
- User wants visual page editing capabilities

## Stack

| Component | Tool | License | Role |
|-----------|------|---------|------|
| App generator | bolt.diy | MIT | Prompt-to-full-stack |
| Visual editor | Puck | MIT | React page editor |
| Backend | Supabase | Apache-2.0 | Auth, DB, API |
| Lightweight backend | PocketBase | MIT | Small app backend |
| Hosting | Coolify | Apache-2.0 | Self-host PaaS |

## Workflow

1. Parse user requirements into app spec
2. Scaffold with bolt.diy (prompt-to-app)
3. Add visual editing with Puck if needed
4. Wire backend (Supabase for scale, PocketBase for simplicity)
5. Deploy via Coolify or static hosting

## Commands

Scaffold a new app:
```bash
# Clone bolt.diy and configure
git clone https://github.com/stackblitz-labs/bolt.diy
cd bolt.diy
# Follow bolt.diy setup instructions
```

Add Puck editor:
```bash
npm install @measured/puck
```

Initialize Supabase backend:
```bash
docker run --rm -it -p 5432:5432 -p 8000:8000 supabase/launcher
```

## Constraints

- Always run in sandbox for bolt.diy builds
- Confirm before deploying to any backend
- License review required before adding non-MIT/Apache-2.0 deps
