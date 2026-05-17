# Security Policy

## Supported versions

Only the latest tagged release (`phase-R6-shipped` / `mantle-v1-released` and any subsequent `v1.x` tags) receives security updates. Older phase tags are immutable historical markers and are **not** patched.

| Version | Supported |
|---|:--:|
| `v1.x` / `mantle-v1-released` | ✅ |
| `phase-R{0..5}-shipped` | ❌ (historical) |

## Threat model

Rasputin Mantle is designed to run **locally**, behind a firewall, with a single operator. The default posture:

- **Gateway** binds `127.0.0.1` unless `MANTLE_PUBLIC=true` is explicitly set.
- **The agent's code execution** happens inside a Docker sandbox (`python:3.12-slim`, non-root, 512 MB, 1 CPU, `no-new-privileges`) — the host filesystem is unreachable from the sandbox.
- **Chromium** runs with the OS sandbox **on**. `--no-sandbox` is forbidden in the tree and enforced by pre-commit hook.
- **URLs** the agent navigates to are validated against an SSRF policy before any request is made.
- **Secrets** (`ANTHROPIC_API_KEY`, `VLLM_API_KEY`, etc.) live only in `.env` and process environment. They are never logged.
- **Cost ceiling** is server-trusted: usage is read from the upstream model response and persisted to `gateway_costs` — clients cannot self-report cost.

### Out of scope

- Running Mantle on a public IP without a reverse proxy / TLS / authentication. If you set `MANTLE_PUBLIC=true`, you are responsible for the perimeter.
- Adversarial LLM input. The agent will refuse to execute on malformed `SKILL.md` files, but defending against prompt injection in the agent's *responses* is a research problem, not a security one.

## Reporting a vulnerability

**Do not open a public issue for security reports.**

Use GitHub's private vulnerability reporting:

➡️  **<https://github.com/jcartu/rasputin-mantle/security/advisories/new>**

Include:

- A description of the issue and its impact
- The affected version (`git rev-parse HEAD`)
- A proof-of-concept or steps to reproduce
- Your suggested remediation, if any
- Whether you wish to be publicly credited in the resulting advisory

### Response timeline

| Stage | Target time |
|---|---|
| First response acknowledging the report | **3 business days** |
| Triage and severity assessment | **7 days** |
| Fix landed + advisory published (low/medium) | **30 days** |
| Fix landed + advisory published (high/critical) | **14 days** |

## Disclosure policy

We follow **coordinated disclosure**. Once a fix is available we will:

1. Publish a GitHub Security Advisory.
2. Issue a CVE if one is warranted.
3. Credit the reporter (unless they prefer anonymity).
4. Publish a release with the fix and a note in `CHANGELOG.md`.

We will **not** disclose the vulnerability publicly before a fix exists.

## Hall of fame

Once we have our first reported vulnerability we will list the discoverer here.

## Cryptographic primitives

Mantle does not implement its own cryptographic primitives. We rely on:

- TLS via `httpx` (uses `certifi` for trust roots)
- Bearer tokens (when configured) for `rasputin-memory`
- Postgres connections (pgcrypto for column-level encryption if you opt in)

If you find a misuse of any of the above (e.g. accidental disabling of TLS verification), report it via the channel above.
