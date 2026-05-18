# Phase W6 Done

## Completion checklist

- [x] Slack OAuth install/callback routes added under `/api/slack`.
- [x] Slack slash command and event webhook handlers verify Slack signatures.
- [x] Slack installation tokens persist in `slack_installations` via env-provided secrets only.
- [x] Email inbound task creation route and allowlist/spam controls added under `/api/mail`.
- [x] SMTP threaded reply helper sends summaries with session links via env-provided SMTP config.
- [x] Scheduled tasks CRUD added under `/api/scheduled` using `scheduled_jobs` and APScheduler when available.
- [x] APScheduler lifecycle wired into gateway startup/shutdown with Redis jobstore config.
- [x] Scheduled tasks UI added at `/scheduled` with create/edit/delete/pause/resume controls.
- [x] Integrations settings UI added at `/settings/integrations` with Slack and Mail cards.
- [x] Integration packages added for Slack and Email.

## Notes

- Migrations `0008_slack_tokens.sql` and `0009_scheduled_jobs.sql` already existed and are used by the implementation.
- Gateway routes gracefully degrade when database or Redis are unavailable for local unit tests.
