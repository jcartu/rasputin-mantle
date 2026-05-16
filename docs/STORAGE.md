# Storage layer

## The QNAP's role

The QNAP is **file storage** and optionally the host for **long-running support services**. Nothing more.

It is **not**:
- The host for OpenCode (that lives on your dev machine, wherever you run the Desktop app or terminal)
- The host for Sisyphus or any custom subagent (those live inside OpenCode)
- The host for vLLM (that lives on your cloud GPU box)
- The host for any "orchestrator" daemon (there is no orchestrator daemon — Sisyphus drives the loop interactively)

It **is**:
- Where you store the bootstrap tarball before unzipping it
- Optionally, where you `docker compose up` the support services (`infra/compose.dev.yml`) so they're always reachable even when your dev machine is asleep
- Optionally, where the rasputin-mantle git repo lives if you keep your dev workflow on QNAP-backed storage (SSH from your dev box, or a synced folder)

## Where things actually run

```
                                                       cloud
                                                       ────────
                                                       vLLM (your GPU box)
                                                       Anthropic API
                                                          ▲
                                                          │ HTTPS
                                                          │
   dev machine                          (LAN/VPN)         │
   ──────────────                                         │
   OpenCode Desktop ────────────────────────────────────┼──┐
     ├── Sisyphus                                       │  │
     ├── @mantle-planner   ──→  HTTP  ──→  vLLM ────────┘  │
     ├── @mantle-executor  ──→  HTTP  ──→  vLLM ───────────┤
     ├── @mantle-frontend  ──→  HTTPS ──→  Anthropic ──────┤
     └── @mantle-auditor   ──→  HTTPS ──→  Anthropic ──────┘
                          │
                          │ local git, local file ops
                          ▼
                   ~/dev/rasputin-mantle/    ← repo on dev machine
                          │
                          │ optional sync (rsync / SMB / NFS)
                          ▼
                   /share/Public/...         ← backup or shared access on QNAP


                              QNAP                         (optional)
                              ────────
                              docker compose up:
                                postgres   :5432
                                redis      :6379
                                neko       :8080 (live computer view)
                                whisper    :8803 (R6 voice STT)
                                kokoro     :8804 (R6 voice TTS)
                                memory     :7777 (R5 rasputin-memory)
                              
                              Reached by the gateway and the agent
                              over LAN. Saves your dev machine from
                              hosting all of this. But: the build
                              works fine without the QNAP — just
                              docker compose up on the dev box.
```

## Setup

If you want support services on the QNAP:

```bash
# On the QNAP, in Container Station's SSH shell or via SSH from your dev box
ssh admin@qnap.local
mkdir -p ~/mantle-support
cd ~/mantle-support
# Copy the support compose file from the bootstrap:
scp dev-box:~/dev/rasputin-mantle/infra/compose.dev.yml .
scp dev-box:~/dev/rasputin-mantle/infra/dockerfiles ./dockerfiles -r
scp dev-box:~/dev/rasputin-mantle/.env .env  # the same .env from the dev box
docker compose -f compose.dev.yml up -d
```

Then on the dev machine, set in `.env`:

```bash
# Point at the QNAP's LAN address instead of localhost
POSTGRES_HOST=qnap.local
REDIS_HOST=qnap.local
NEKO_URL=http://qnap.local:8080
WHISPER_URL=http://qnap.local:8803
KOKORO_URL=http://qnap.local:8804
RASPUTIN_MEMORY_URL=http://qnap.local:7777
```

If you don't want to bother: skip all of the above. `docker compose -f infra/compose.dev.yml up -d` on the dev machine works identically; the only cost is your dev machine has to stay on (or you accept the services going down when it sleeps).

## What previously suggested QNAP deployment (v2)

An earlier draft put an "orchestrator container" on the QNAP that ran a Python daemon driving the build loop. That design was wrong. The loop is driven by Sisyphus inside OpenCode on your dev machine; there's no daemon to host anywhere. v2's `UNATTENDED.sh`, `Dockerfile.orchestrator`, and `mantle-orchestrator` container are removed in v3.
