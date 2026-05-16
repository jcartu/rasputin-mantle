---
name: mail-agent
description: "Read, compose, and send emails via IMAP/SMTP using Himalaya terminal client."
version: 0.1.0
author: Rasputin Mantle
license: MIT
capability: mail_agent
metadata:
  hermes:
    tags: [mail, email, imap, smtp, himalaya]
---

# Mail Agent

Read, compose, and send emails using the Himalaya terminal IMAP/SMTP client. Fully sandboxed — no direct host mail access.

This is a markdown playbook — invoke via bash, not skill_mcp().

## When to use

- User asks to read emails, check inbox, or summarize messages
- User wants to compose and send an email
- User needs email automation or filtering

## Stack

| Component | Tool | License | Role |
|-----------|------|---------|------|
| IMAP/SMTP client | Himalaya | MIT | Terminal email client |

## Workflow

1. Configure Himalaya with IMAP/SMTP credentials (via env vars)
2. Read inbox, list messages, search by criteria
3. Compose email content
4. Send via SMTP (requires confirmation)

## Commands

Configure Himalaya:
```bash
# Install Himalaya
cargo install himalaya

# Configure via env vars (never hardcode credentials)
export HIMALAYA_ACCOUNT_DEFAULT_IMAP_HOST=imap.example.com
export HIMALAYA_ACCOUNT_DEFAULT_IMAP_PORT=993
export HIMALAYA_ACCOUNT_DEFAULT_SMTP_HOST=smtp.example.com
export HIMALAYA_ACCOUNT_DEFAULT_SMTP_PORT=587
```

Read inbox:
```bash
himalaya inbox --limit 20
```

Read a specific message:
```bash
himalaya read --uid <uid>
```

Search emails:
```bash
himalaya search --query "from:support@example.com"
```

Send email (requires confirmation):
```bash
himalaya send --to "recipient@example.com" --subject "Subject" --body "Message body"
```

## Constraints

- **confirm: true** — sending emails requires explicit user confirmation
- Credentials passed via environment variables only
- All email operations happen in sandbox
- Never store credentials in SKILL.md or config files
