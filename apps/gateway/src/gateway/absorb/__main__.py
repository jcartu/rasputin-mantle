from __future__ import annotations

import argparse
import json
import pathlib
import re
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

FEEDS = [
    {"name": "GitHub trending ai-agent", "url": "https://api.github.com/search/repositories?q=topic:ai-agent&sort=stars&per_page=25"},
    {"name": "GitHub trending mcp", "url": "https://api.github.com/search/repositories?q=topic:mcp&sort=stars&per_page=25"},
    {"name": "GitHub trending browser-agent", "url": "https://api.github.com/search/repositories?q=topic:browser-agent&sort=stars&per_page=25"},
    {"name": "GitHub trending codeact", "url": "https://api.github.com/search/repositories?q=topic:codeact&sort=stars&per_page=25"},
    {"name": "GitHub trending computer-use", "url": "https://api.github.com/search/repositories?q=topic:computer-use&sort=stars&per_page=25"},
]

CAPABILITY_BUCKETS = [
    "sandbox", "browser", "memory", "codeact", "voice", "research",
    "image-gen", "data-analysis", "document", "mcp", "skills",
    "scheduler", "auth", "frontend", "observability", "evals",
]

LICENSE_GREEN = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "MPL-2.0"}
LICENSE_YELLOW = {"GPL-3.0", "AGPL-3.0", "LGPL-3.0", "EPL-2.0"}


def fetch_feed(feed: dict) -> list[dict]:
    try:
        req = urllib.request.Request(feed["url"], headers={"Accept": "application/vnd.github.v3+json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get("items", [])
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        print(f"  WARN: failed to fetch {feed['name']}: {exc}")
        return []


def classify_repo(repo: dict) -> list[str]:
    topics = set(repo.get("topics", []))
    desc = (repo.get("description") or "").lower()
    buckets = []
    topic_map = {
        "sandbox": {"sandbox", "e2b", "daytona", "firecracker"},
        "browser": {"browser", "browser-use", "playwright", "puppeteer", "chromium"},
        "memory": {"memory", "memory-store", "vector-db", "knowledge-graph"},
        "codeact": {"codeact", "code-interpreter", "agent-code"},
        "voice": {"voice", "tts", "stt", "whisper", "speech"},
        "research": {"research", "deep-research", "web-search", "crawl4ai"},
        "image-gen": {"image-generation", "flux", "stable-diffusion", "comfyui"},
        "data-analysis": {"data-analysis", "pandas", "duckdb", "plotly"},
        "document": {"document", "docling", "pdf", "ocr"},
        "mcp": {"mcp", "model-context-protocol"},
        "skills": {"agent-skills", "skill", "agent-skill"},
        "scheduler": {"scheduler", "cron", "airflow", "kestra"},
        "auth": {"auth", "authentication", "oauth", "sso"},
        "frontend": {"frontend", "ui", "react", "nextjs"},
        "observability": {"observability", "tracing", "langfuse", "opentelemetry"},
        "evals": {"eval", "benchmark", "promptfoo", "webvoyager"},
    }
    for bucket, keywords in topic_map.items():
        if topics & keywords or any(k in desc for k in keywords):
            buckets.append(bucket)
    return buckets or ["other"]


def check_license(repo: dict) -> str:
    license_info = repo.get("license", {})
    spdx = (license_info.get("spdx_id") or "").strip()
    if not spdx:
        return "unknown"
    if spdx in LICENSE_GREEN:
        return "green"
    if spdx in LICENSE_YELLOW:
        return "yellow"
    return "review"


def run_scan(output_dir: pathlib.Path, max_repos: int) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()

    all_repos = []
    seen_ids = set()

    for feed in FEEDS:
        print(f"Scanning {feed['name']}...")
        repos = fetch_feed(feed)
        for repo in repos[:max_repos]:
            if repo["id"] not in seen_ids:
                seen_ids.add(repo["id"])
                all_repos.append(repo)

    print(f"Found {len(all_repos)} unique repos")

    records = []
    for repo in all_repos:
        buckets = classify_repo(repo)
        license_status = check_license(repo)
        records.append({
            "name": repo["full_name"],
            "url": repo["html_url"],
            "stars": repo.get("stargazers_count", 0),
            "description": repo.get("description", "")[:200],
            "language": repo.get("language", ""),
            "license": repo.get("license", {}).get("spdx_id", "unknown"),
            "license_status": license_status,
            "buckets": buckets,
            "updated_at": repo.get("updated_at", ""),
            "created_at": repo.get("created_at", ""),
        })

    records.sort(key=lambda r: r["stars"], reverse=True)

    # Generate capability delta
    delta_lines = [
        "# Capability Delta",
        f"> Generated {timestamp} by absorb-nightly",
        "",
        "## Summary",
        f"- **Repos scanned:** {len(records)}",
        f"- **Green license:** {sum(1 for r in records if r['license_status'] == 'green')}",
        f"- **Yellow license:** {sum(1 for r in records if r['license_status'] == 'yellow')}",
        f"- **Needs review:** {sum(1 for r in records if r['license_status'] == 'review')}",
        "",
        "## Top New Repos",
        "",
        "| Repo | Stars | License | Buckets |",
        "|---|---|---|---|",
    ]
    for r in records[:20]:
        buckets_str = ", ".join(r["buckets"])
        delta_lines.append(f"| [{r['name']}]({r['url']}) | {r['stars']} | {r['license']} ({r['license_status']}) | {buckets_str} |")

    delta_lines.extend([
        "",
        "## Full Data",
        "",
        "See  for the complete dataset.",
        "",
    ])

    delta_path = output_dir / "CAPABILITY_DELTA.md"
    delta_path.write_text("
".join(delta_lines) + "
")

    data_path = output_dir / "absorb-data.json"
    data_path.write_text(json.dumps({"timestamp": timestamp, "records": records}, indent=2))

    return {"total": len(records), "delta": str(delta_path), "data": str(data_path)}


def main():
    parser = argparse.ArgumentParser(description="mantle-absorb: capability scan")
    parser.add_argument("--output-dir", default="outputs/absorb")
    parser.add_argument("--max-repos", type=int, default=50)
    args = parser.parse_args()

    print("mantle-absorb: scanning feeds...")
    result = run_scan(pathlib.Path(args.output_dir), args.max_repos)
    print(f"Done: {result['total']} repos scanned")
    print(f"Delta: {result['delta']}")
    print(f"Data: {result['data']}")


if __name__ == "__main__":
    main()
