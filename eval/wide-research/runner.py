from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx
import yaml

GATEWAY = os.environ.get("MANTLE_GATEWAY_URL", "http://127.0.0.1:8000")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "claude-sonnet-4-6")


async def judge_response(query: str, response: dict[str, Any]) -> bool:
    if not ANTHROPIC_KEY:
        return bool(response.get("merged_markdown") and response.get("results"))

    prompt = (
        "You judge whether a Wide Research response is useful.\n"
        f"Query: {query}\n"
        f"Response markdown:\n{response.get('merged_markdown', '')[:4000]}\n\n"
        "Pass if it contains relevant cited web results and useful synthesis cues. Reply PASS or FAIL."
    )
    async with httpx.AsyncClient(timeout=45.0) as client:
        result = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={"model": JUDGE_MODEL, "max_tokens": 10, "messages": [{"role": "user", "content": prompt}]},
        )
    if result.status_code != 200:
        return False
    return result.json()["content"][0]["text"].strip().upper().startswith("PASS")


async def run_task(client: httpx.AsyncClient, task: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        response = await client.post(f"{GATEWAY}/api/research/", json={"query": task["query"], "max_agents": 4}, timeout=180.0)
        if response.status_code == 501:
            return {"id": task["id"], "skipped": True, "reason": "search backend unconfigured"}
        if response.status_code != 200:
            return {"id": task["id"], "passed": False, "error": f"gateway {response.status_code}"}
        payload = response.json()
        passed = await judge_response(task["query"], payload)
        return {
            "id": task["id"],
            "passed": passed,
            "result_count": len(payload.get("results", [])),
            "duration_s": round(time.perf_counter() - started, 2),
        }
    except Exception as exc:
        return {"id": task["id"], "passed": False, "error": f"{type(exc).__name__}: {exc}"}


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", default="eval/wide-research/tasks.yaml")
    parser.add_argument("--output", default="outputs/wide-research-eval.json")
    parser.add_argument("--concurrency", type=int, default=3)
    args = parser.parse_args()

    if not (os.environ.get("BRAVE_SEARCH_API_KEY", "").strip() or os.environ.get("EXA_API_KEY", "").strip()):
        out = {
            "benchmark": "wide-research",
            "skipped": True,
            "reason": "BRAVE_SEARCH_API_KEY or EXA_API_KEY not set",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(out, indent=2), encoding="utf-8")
        print("Wide Research eval skipped: search backend unconfigured")
        return 0

    config = yaml.safe_load(Path(args.tasks).read_text(encoding="utf-8"))
    tasks = config["tasks"]
    semaphore = asyncio.Semaphore(args.concurrency)

    async def guarded(task: dict[str, Any]) -> dict[str, Any]:
        async with semaphore:
            return await run_task(client, task)

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*[guarded(task) for task in tasks])

    skipped = sum(1 for result in results if result.get("skipped"))
    judged = [result for result in results if not result.get("skipped")]
    passed = sum(1 for result in judged if result.get("passed"))
    total = len(judged)
    pass_rate = passed / total if total else 0.0
    out = {
        "benchmark": "wide-research",
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "skipped": skipped,
        "pass_rate": pass_rate,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": results,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wide Research: {passed}/{total} = {pass_rate:.2%}; skipped={skipped}")
    return 0 if pass_rate >= 0.70 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
