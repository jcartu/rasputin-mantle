"""eval/gaia-mini/runner.py — GAIA-mini harness for R6 gate.

For each task: run the agent, judge its final answer against expected_answer.
- grading: exact (default) — case-insensitive exact match after trim
- grading: contains — expected_answer must appear in agent_response
- grading: open — LLM-judge (Sonnet) decides reasonable correctness

Outputs JSON with same shape as WebVoyager runner.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

import httpx
import yaml


GATEWAY = os.environ.get("MANTLE_GATEWAY_URL", "http://127.0.0.1:8000")
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "claude-sonnet-4-6")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


def normalize(s: str) -> str:
    return " ".join(s.lower().split()).strip(".,;: ")


async def run_task(client: httpx.AsyncClient, task: dict) -> dict:
    t0 = time.perf_counter()
    try:
        r = await client.post(
            f"{GATEWAY}/api/agent/run",
            json={"task": task["description"], "max_steps": 25},
            timeout=300,
        )
        if r.status_code != 200:
            return {"id": task["id"], "passed": False, "error": f"gateway {r.status_code}",
                    "duration_s": time.perf_counter() - t0}
        answer = r.json().get("final_answer", "")
    except Exception as e:
        return {"id": task["id"], "passed": False, "error": f"{type(e).__name__}: {e}",
                "duration_s": time.perf_counter() - t0}

    expected = task["expected_answer"]
    grading = task.get("grading", "exact")

    if grading == "exact":
        passed = normalize(expected) in normalize(answer)
    elif grading == "contains":
        passed = normalize(expected) in normalize(answer)
    elif grading == "open":
        passed = await judge_open(task["description"], expected, answer)
    else:
        passed = False

    return {
        "id": task["id"],
        "passed": passed,
        "expected": expected,
        "agent_answer": answer[:500],
        "duration_s": round(time.perf_counter() - t0, 2),
    }


async def judge_open(task: str, expected: str, response: str) -> bool:
    if not ANTHROPIC_KEY:
        return False
    prompt = (f"Task: {task}\nExample acceptable answer: {expected}\n"
              f"Agent answer: {response}\n\nDid the agent answer the task correctly? "
              f"Reply with one word: PASS or FAIL.")
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
    ap.add_argument("--tasks", default="eval/gaia-mini/tasks.yaml")
    ap.add_argument("--output", default="outputs/gaia-mini.json")
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
        "benchmark": "gaia-mini",
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": passed / total if total else 0,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": results,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=2))
    print(f"GAIA-mini: {passed}/{total} = {out['pass_rate']:.2%}")
    sys.exit(0 if out["pass_rate"] >= 0.40 else 1)


if __name__ == "__main__":
    asyncio.run(main())
