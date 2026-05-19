from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

try:
    from gateway.eval_mode import is_eval_mode
except ModuleNotFoundError:  # pragma: no cover - codeact can run without gateway on sys.path

    def is_eval_mode() -> bool:
        return os.environ.get("MANTLE_EVAL_MODE", "").lower() in ("1", "true", "yes")


NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
MAX_SKILL_MD_CHARS = 100_000
MAX_DESCRIPTION_CHARS = 1024
REQUIRED_FRONTMATTER = ("name", "description", "when_to_use", "capability", "version", "license")


class SkillLoaderError(Exception):
    pass


class SkillValidationError(SkillLoaderError):
    pass


class SkillNotFoundError(SkillLoaderError):
    pass


@dataclass(frozen=True)
class DiscoveredSkill:
    name: str
    description: str
    when_to_use: str
    capability: str
    version: str
    license: str
    author: str
    tags: list[str]
    path: str
    source: str
    sha256: str
    readme: str = ""


@dataclass(frozen=True)
class SkillInvocationResult:
    skill: str
    script: str | None
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int
    estimated_cost_usd: float = 0.0
    cost_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class _SessionCache:
    signature: str
    skills: dict[str, DiscoveredSkill] = field(default_factory=dict)


_CACHE: dict[str, _SessionCache] = {}


def default_search_paths(session_id: str | None = None) -> list[Path]:
    project_root = Path(__file__).resolve().parents[3]
    paths = [project_root / "packages" / "skills"]
    if session_id:
        paths.append(Path("/workspace") / session_id / "_skills")
    paths.append(Path.home() / ".mantle" / "skills")
    return paths


def discover_skills(session_id: str | None = None, search_paths: list[Path] | None = None) -> list[DiscoveredSkill]:
    paths = search_paths or default_search_paths(session_id)
    cache_key = session_id or "__global__"
    cached = _CACHE.get(cache_key)
    if is_eval_mode() and cached:
        return sorted(cached.skills.values(), key=lambda skill: skill.name)

    signature = _signature(paths, session_id)
    if cached and cached.signature == signature:
        return sorted(cached.skills.values(), key=lambda skill: skill.name)

    discovered: dict[str, DiscoveredSkill] = {}
    for root in paths:
        for skill_md in _skill_files(root):
            skill = _read_skill(skill_md, _source_for(root))
            discovered[skill.name] = skill

    _CACHE[cache_key] = _SessionCache(signature=signature, skills=discovered)
    return sorted(discovered.values(), key=lambda skill: skill.name)


def get_skill(name: str, session_id: str | None = None) -> DiscoveredSkill:
    for skill in discover_skills(session_id):
        if skill.name == name:
            return skill
    raise SkillNotFoundError(f"Skill not found: {name}")


def skill_detail(name: str, session_id: str | None = None) -> dict[str, Any]:
    skill = get_skill(name, session_id)
    root = Path(skill.path).parent
    scripts = sorted(str(path.relative_to(root)) for path in (root / "scripts").glob("*") if path.is_file())
    templates = sorted(str(path.relative_to(root)) for path in (root / "templates").glob("*") if path.is_file())
    examples = sorted(str(path.relative_to(root)) for path in (root / "examples").glob("*") if path.is_file())
    return {**asdict(skill), "scripts": scripts, "templates": templates, "examples": examples}


def invoke_skill(name: str, args: dict[str, Any] | None = None, session_id: str | None = None) -> SkillInvocationResult:
    payload = dict(args or {})
    requested_script = payload.pop("script", None)
    timeout_seconds = int(payload.pop("timeout_seconds", 30))
    skill = get_skill(name, session_id)
    skill_dir = Path(skill.path).parent
    script_path = _select_script(skill_dir, requested_script)
    if script_path is None:
        cost = _estimated_skill_cost(skill, 0)
        return SkillInvocationResult(name, None, skill.readme, "", 0, 0, cost, _cost_metadata(skill, cost))

    started = time.perf_counter()
    command = _command_for_script(script_path)
    completed = subprocess.run(
        command,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        cwd=str(skill_dir),
        check=False,
    )
    duration_ms = int((time.perf_counter() - started) * 1000)
    cost = _estimated_skill_cost(skill, duration_ms)
    return SkillInvocationResult(
        skill=name,
        script=str(script_path.relative_to(skill_dir)),
        stdout=completed.stdout,
        stderr=completed.stderr,
        exit_code=completed.returncode,
        duration_ms=duration_ms,
        estimated_cost_usd=cost,
        cost_metadata=_cost_metadata(skill, cost),
    )


def save_session_as_skill(
    session_id: str,
    name: str,
    description: str,
    tags: list[str] | None = None,
    publish_publicly: bool = False,
) -> DiscoveredSkill:
    if not NAME_PATTERN.fullmatch(name):
        raise SkillValidationError("Skill name must be lowercase, hyphenated, and no more than 64 characters")
    target_root = Path.cwd() / "packages" / "skills" if publish_publicly else Path.home() / ".mantle" / "skills"
    target_dir = target_root / name
    scripts_dir = target_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    tag_values = tags or ["saved-session"]
    tag_yaml = "\n".join(f"    - {tag}" for tag in tag_values)
    skill_md = f"""---
name: {name}
description: {description}
when_to_use: Invoke when a user wants to repeat the successful workflow from session {session_id}.
capability: saved_workflow
version: 1.0.0
license: MIT
metadata:
  tags:
{tag_yaml}
---

# {name}

Saved from session `{session_id}`.

## Workflow

1. Review the user's goal and confirm it matches the saved workflow intent.
2. Reconstruct the plan from the prior session trace when available.
3. Execute the bundled script to produce a starter checklist.
"""
    (target_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    (scripts_dir / "run.py").write_text(
        "from __future__ import annotations\n\n"
        "import json\nimport sys\n\n"
        "data = json.loads(sys.stdin.read() or '{}')\n"
        "print(json.dumps({'status': 'ready', 'input': data}, indent=2))\n",
        encoding="utf-8",
    )
    invalidate_session_cache(session_id)
    return _read_skill(target_dir / "SKILL.md", "user")


def invalidate_session_cache(session_id: str | None = None) -> None:
    if session_id is None:
        _CACHE.clear()
    else:
        _CACHE.pop(session_id, None)


def _skill_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.glob("*/SKILL.md") if path.is_file())


def _read_skill(skill_md: Path, source: str) -> DiscoveredSkill:
    content = skill_md.read_text(encoding="utf-8")
    if len(content) > MAX_SKILL_MD_CHARS:
        raise SkillValidationError(f"{skill_md} exceeds {MAX_SKILL_MD_CHARS} characters")
    frontmatter, body = _split_frontmatter(content)
    raw = yaml.safe_load(frontmatter) or {}
    if not isinstance(raw, dict):
        raise SkillValidationError(f"{skill_md} frontmatter must be a mapping")

    values = {key: _required_string(raw, key, skill_md) for key in REQUIRED_FRONTMATTER}
    if not NAME_PATTERN.fullmatch(values["name"]):
        raise SkillValidationError(f"{skill_md} name must be lowercase, hyphenated, and no more than 64 characters")
    if len(values["description"]) > MAX_DESCRIPTION_CHARS:
        raise SkillValidationError(f"{skill_md} description exceeds 1024 characters")

    return DiscoveredSkill(
        name=values["name"],
        description=values["description"],
        when_to_use=values["when_to_use"],
        capability=values["capability"],
        version=values["version"],
        license=values["license"],
        author=str(raw.get("author") or "Mantle"),
        tags=_tags(raw),
        path=str(skill_md),
        source=source,
        sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        readme=body.strip(),
    )


def _split_frontmatter(content: str) -> tuple[str, str]:
    if not content.startswith("---\n"):
        raise SkillValidationError("SKILL.md must start with YAML frontmatter delimiter")
    parts = content.split("\n---\n", 1)
    if len(parts) != 2:
        raise SkillValidationError("SKILL.md frontmatter missing closing delimiter")
    return parts[0][4:], parts[1]


def _required_string(raw: dict[Any, Any], key: str, skill_md: Path) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SkillValidationError(f"{skill_md} missing required string field: {key}")
    return value.strip()


def _tags(raw: dict[Any, Any]) -> list[str]:
    metadata = raw.get("metadata") or {}
    if not isinstance(metadata, dict):
        return []
    values = metadata.get("tags") or metadata.get("intent_tags") or []
    if not isinstance(values, list):
        return []
    return [str(value) for value in values if str(value).strip()]


def _select_script(skill_dir: Path, requested_script: Any) -> Path | None:
    scripts_dir = skill_dir / "scripts"
    if requested_script:
        candidate = (scripts_dir / str(requested_script)).resolve()
        if scripts_dir.resolve() not in candidate.parents or not candidate.is_file():
            raise SkillNotFoundError(f"Script not found: {requested_script}")
        return candidate
    scripts = sorted(path for path in scripts_dir.glob("*") if path.is_file())
    return scripts[0] if scripts else None


def _command_for_script(script_path: Path) -> list[str]:
    if script_path.suffix == ".py":
        return [sys.executable, str(script_path)]
    if script_path.suffix in {".sh", ".bash"}:
        return ["bash", str(script_path)]
    return [str(script_path)]


def _estimated_skill_cost(skill: DiscoveredSkill, duration_ms: int) -> float:
    floor_by_capability = {
        "presentation": 0.01,
        "spreadsheet": 0.02,
        "document": 0.05,
    }
    floor = floor_by_capability.get(skill.capability, 0.001)
    runtime_component = min(duration_ms / 1_000_000, 0.01)
    return round(floor + runtime_component, 4)


def _cost_metadata(skill: DiscoveredSkill, estimated_cost_usd: float) -> dict[str, Any]:
    return {
        "meter": "skill-invocation",
        "skill": skill.name,
        "capability": skill.capability,
        "estimated_cost_usd": estimated_cost_usd,
    }


def _signature(paths: list[Path], session_id: str | None) -> str:
    parts = [session_id or ""]
    for root in paths:
        if not root.exists():
            parts.append(f"{root}:missing")
            continue
        for skill_md in _skill_files(root):
            stat = skill_md.stat()
            parts.append(f"{skill_md}:{stat.st_mtime_ns}:{stat.st_size}")
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def _source_for(root: Path) -> str:
    expanded = root.expanduser()
    if str(expanded).startswith("/workspace"):
        return "session"
    if expanded == Path.home() / ".mantle" / "skills":
        return "user"
    return "bundled"


def _main() -> None:
    parser = argparse.ArgumentParser(description="Discover Mantle agent skills")
    parser.add_argument("--list", action="store_true", help="print discovered skills as JSON")
    parser.add_argument("--session-id", default=os.environ.get("MANTLE_SESSION_ID"))
    args = parser.parse_args()
    if args.list:
        print(json.dumps([asdict(skill) for skill in discover_skills(args.session_id)], indent=2))


if __name__ == "__main__":
    _main()
