# Security Checklist

Each item below is a CI-enforced gate. PRs that violate them block merge.

## Gateway

- [x] Gateway binds to `127.0.0.1` unless `MANTLE_PUBLIC=true` is explicitly set. (Phase 3)
- [ ] CORS allowlist is explicit, not `*`. (Phase 3)

## Sandbox

- [ ] Sandbox containers run as a non-root UID. (Phase 1)
- [ ] No `--no-sandbox` on Chromium ever. If a sandbox image needs it to function, the image is broken — fix the image. (Phase 2)
- [ ] Neko/VNC is gated by short-lived signed tokens issued by the gateway. URL fragment, not query string. Expires in 5 minutes; auto-renews while the session is active. (Phase 4)

## State

- [ ] No world-writable state directories. `umask 077` in every Dockerfile. (Phase 1)

## Secrets

- [ ] Secrets via env or sops; never committed; never logged in Langfuse spans. (Phase 0)

## Network

- [ ] Every external network call from inside a sandbox is logged with destination host and byte count, surfaced in the live computer view's "network" tab. (Phase 4)

## Prompt Injection

- [ ] Prompt-injection canaries in every skill — a tripwire string the model is told to never repeat. If it appears in a tool call, the session is killed and an alert fires. (Phase 2)

## Phase 0/1 Status

| Item | Status |
|---|---|
| Gateway binding | Deferred (Phase 3) |
| CORS | Deferred (Phase 3) |
| Non-root sandbox | Enforced in `infra/compose.dev.yml` |
| `--no-sandbox` Chromium | N/A (no browser in Phase 0/1) |
| Neko/VNC tokens | Deferred (Phase 4) |
| `umask 077` | Enforced in sandbox Dockerfile |
| Secrets via env | Enforced by `.gitignore` |
| Network logging | Deferred (Phase 4) |
| Prompt canaries | Deferred (Phase 2) |
