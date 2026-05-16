# Rasputin Mantle

Self-hosted, open-source, Manus-equivalent agent platform with a live computer view.

Built on top of:
- `kernel/` — `rasputin-omnitool`, the 28-capability OSS catalog
- `memory/` — `rasputin-memory`, LoCoMo 77.7% backend
- `oh-my-openagent` — Sisyphus + specialist subagents

## Quick Start

```bash
git clone --recursive <repo-url>
cd rasputin-mantle
pnpm i
uv sync
docker compose -f infra/compose.dev.yml up -d
pnpm test
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Security](docs/SECURITY.md)
- [Skill Authoring](docs/SKILL_AUTHORING.md)

## License

MIT
