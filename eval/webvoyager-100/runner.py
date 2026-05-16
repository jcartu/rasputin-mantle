"""eval/webvoyager-100/runner.py — WebVoyager harness for R2 gate.

For each task: spawn a sandbox, drive the browser via the gateway's /api/agent
endpoint, ask the agent to complete the task, judge the response against
success_criterion (LLM-as-judge with Sonnet).

Outputs JSON with shape:
  {"total": N, "passed": K, "pass_rate": K/N, "results": [...]}
"""
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
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "claude-sonnet-4-6")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


async def run_task(client: httpx.AsyncClient, task: dict) -> dict:
    """Run one WebVoyager task. Returns result dict."""
    t0 = time.perf_counter()
    try:
        r = await client.post(
            f"{GATEWAY}/api/agent/run",
            json={
                "starting_url": task["starting_url"],
                "task": task["description"],
                "max_steps": 25,
                "headless": True,
            },
            timeout=300,
        )
        if r.status_code != 200:
            return {"id": task["id"], "passed": False, "error": f"gateway {r.status_code}",
                    "duration_s": time.perf_counter() - t0}
        agent_response = r.json().get("final_answer", "")
    except Exception as e:
        return {"id": task["id"], "passed": False, "error": f"{type(e).__name__}: {e}",
                "duration_s": time.perf_counter() - t0}

    passed = await judge(task["description"], task["success_criterion"], agent_response)

    return {
        "id": task["id"],
        "passed": passed,
        "agent_response": agent_response[:1000],
        "duration_s": round(time.perf_counter() - t0, 2),
    }


async def judge(task_desc: str, criterion: str, response: str) -> bool:
    """LLM judge: does response satisfy criterion?"""
    if not ANTHROPIC_KEY:
        return False
    prompt = f"""Judge whether the response satisfies the success criterion.

Task: {task_desc}
Success criterion: {criterion}
Agent response: {response}

Respond with exactly one word: PASS or FAIL."""

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": JUDGE_MODEL,
                "max_tokens": 10,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        if r.status_code != 200:
            return False
        text = r.json()["content"][0]["text"].strip().upper()
        return text.startswith("PASS")


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default="eval/webvoyager-100/tasks.yaml")
    ap.add_argument("--output", default="outputs/webvoyager-100.json")
    ap.add_argument("--concurrency", type=int, default=4)
    args = ap.parse_args()

    with open(args.tasks) as f:
        config = yaml.safe_load(f)
    tasks = config["tasks"]

    sem = asyncio.Semaphore(args.concurrency)

    async def run_with_sem(client, task):
        async with sem:
            return await run_task(client, task)

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*[run_with_sem(client, t) for t in tasks])

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    out = {
        "benchmark": "webvoyager",
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": passed / total if total else 0,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": results,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=2))
    print(f"WebVoyager: {passed}/{total} = {out['pass_rate']:.2%}")
    sys.exit(0 if out["pass_rate"] >= 0.60 else 1)


if __name__ == "__main__":
    asyncio.run(main())
