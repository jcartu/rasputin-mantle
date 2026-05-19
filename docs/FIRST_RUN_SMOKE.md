# First-Run Smoke Checklist

Walk through each category as a fresh user after `docker compose -f docker-compose.dev.yml up`.
Check off each item. Log issues in the FINDINGS section below.

## Checklist

### Onboarding (W2)
- [ ] First visit shows three-step onboarding flow
- [ ] Can pick a template and run a task
- [ ] No console errors during onboarding

### Session View (P0-P3)
- [ ] Three panes render (chat, files, shell)
- [ ] Multi-tab browser works
- [ ] Take-control mode activates

### Project Creation (W4)
- [ ] Can create a project
- [ ] Can upload a KB file
- [ ] Can create a session within a project
- [ ] KB file is mounted in the session

### Skills Marketplace (W5)
- [ ] Can browse seed skills
- [ ] Can install a skill
- [ ] Installed skill is invokable from chat

### Replay (W3)
- [ ] Finished session shows replay timeline
- [ ] Can scrub through the timeline
- [ ] Can share publicly (generates link)
- [ ] Shared link works without auth

### Playbook Gallery (W2)
- [ ] Can browse seed playbooks
- [ ] Can save own playbook

### Scheduled Tasks (W6)
- [ ] Can create a scheduled task
- [ ] Task persists (refresh page, still there)

### Integrations (W6)
- [ ] Slack OAuth flow initiates (with placeholder credentials)
- [ ] Email settings page renders

### Productivity Skills (W7)
- [ ] Slides skill produces .pptx from chat
- [ ] Spreadsheet skill produces .xlsx from chat
- [ ] Document skill produces .docx from chat
- [ ] Self-review runs (check logs for iterations_used)

### Cost Gutter
- [ ] Cost numbers appear in chat margin
- [ ] Costs accumulate across turns

### Voice (R5)
- [ ] STT input works (if Whisper running)
- [ ] Kokoro TTS output works (if Kokoro running)

## FINDINGS

### Issue 1: <one-line summary>
Severity: blocker | major | minor
Steps: ...
Expected: ...
Actual: ...
File:line if known: ...
