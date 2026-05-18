# Phase W4 — Projects with Knowledge Base

Completion checklist:

- [x] Verified migrations 0004-0007 match the W4 data model.
- [x] Added persistent project CRUD routes under `/api/projects`.
- [x] Added project member list/add/remove routes.
- [x] Added project KB upload/list/delete routes with 50-file and 100MB caps; 100MB violations return HTTP 413.
- [x] Stored KB files under `/workspace/projects/<project_id>/kb/` by default, configurable via `MANTLE_KB_ROOT`.
- [x] Extended session creation to accept `project_id`, inherit default planner, prompt addendum, allowed tools, and mount KB files read-only.
- [x] Added project metadata to shared session schemas.
- [x] Replaced the left pane with a project sidebar including Personal, collapsible projects, recent sessions, and New project.
- [x] Added project page tabs for Sessions, Knowledge base, and Settings.
- [x] Added project new-session route that inherits project settings.
- [x] Added project UI components: switcher, sidebar, KB uploader, KB file list, settings form.
- [x] Updated README with Projects and KB bullets.

Verification performed in-session:

- LSP diagnostics run on changed backend/frontend files.
- Build/type checks run where available.
