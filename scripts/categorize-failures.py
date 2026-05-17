#!/usr/bin/env python3
"""scripts/categorize-failures.py — classify WebVoyager failures into the S2 taxonomy.

Reads a WebVoyager run output JSON (with trace data per task) and writes a
failure-taxonomy.json with one categorized entry per failed task.

Categorization uses Sonnet 4.6. The prompt is intentionally generic — it doesn't
mention WebVoyager and doesn't see any expected_answer beyond what's in the task
definition. This keeps the categorizer honest.

Usage:
    python scripts/categorize-failures.py \\
        --run outputs/v1_1/webvoyager-100-baseline.json \\
        --tasks eval/webvoyager-100/tasks.yaml \\
        --output outputs/v1_1/failure-taxonomy.json
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


CATEGORIES = [
    "DOM_FLAKY",
    "VLM_NEEDED",
    "MULTI_HOP_LOST",
    "ANSWER_MALFORMED",
    "TOOL_BROKEN",
    "LOGIN_WALL",
    "CAPTCHA",
    "TIME_SENSITIVE",
    "JUDGE_HARSH",
    "UNCLASSIFIED",
]


CATEGORIZER_PROMPT = """You are categorizing a single failure from a web-browsing agent benchmark.

You see:
- The task the agent was asked to complete
- The expected answer (for reference only)
- The agent's actual final answer
- The last 5 tool calls and their results

Choose ONE category from this list that best explains why the agent failed:

- DOM_FLAKY: element-not-found or stale-element errors that suggest race conditions or timing issues on dynamic pages.
- VLM_NEEDED: the agent could not extract content because the DOM was opaque (canvas, virtual scroll, custom widgets) — a screenshot-reasoning approach would have helped.
- MULTI_HOP_LOST: the agent took a wrong turn during multi-step navigation and couldn't recover. The final answer is plausible but factually wrong because it came from the wrong page.
- ANSWER_MALFORMED: the agent had the right information but expressed it in a format the judge rejected (Unicode encoding, prose wrapping, units).
- TOOL_BROKEN: the agent's tool call returned an error message that looks like a bug in the tool implementation, not in the page.
- LOGIN_WALL: the page required authentication the agent did not have.
- CAPTCHA: the site presented bot-detection (CAPTCHA, rate limit, IP block).
- TIME_SENSITIVE: the task's expected answer depends on a value that changes over time, and the agent's answer is internally consistent but mismatched with the stored expected_answer.
- JUDGE_HARSH: the agent's answer is correct but the judge unreasonably rejected it.
- UNCLASSIFIED: none of the above fit. (Use sparingly; prefer to fit into existing categories.)

Respond with JSON only:

{
  "category": "ONE_OF_THE_ABOVE",
  "evidence": "One sentence pointing at the specific signal in the trace.",
  "fixable_in_phase": "S3" | "S4" | "S5" | "S6" | "not_fixable",
  "estimated_fix_effort": "low" | "medium" | "high"
}

Don't mention specific benchmarks. Just classify what you see in the trace.
"""


async def categorize_one(client: httpx.AsyncClient, task: dict, result: dict) -> dict:
    last_5_steps = result.get("steps", [])[-5:] if isinstance(result.get("steps"), list) else []

    user_msg = f"""Task: {task['description']}
Expected answer: {task.get('expected_answer', task.get('success_criterion', ''))}
Agent's final answer: {result.get('answer', result.get('final_answer', ''))[:500]}

Last tool calls:
{json.dumps(last_5_steps, indent=2)[:2000]}

Categorize this failure.
"""

    resp = await client.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": os.environ.get("ANTHROPIC_API_KEY", ""),
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 400,
            "system": CATEGORIZER_PROMPT,
            "messages": [{"role": "user", "content": user_msg}],
        },
        timeout=60,
    )
    if resp.status_code != 200:
        return {"category": "UNCLASSIFIED", "evidence": f"categorizer HTTP {resp.status_code}",
                "fixable_in_phase": "not_fixable", "estimated_fix_effort": "high"}

    text = resp.json()["content"][0]["text"].strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        verdict = json.loads(text)
        if verdict.get("category") not in CATEGORIES:
            verdict["category"] = "UNCLASSIFIED"
            verdict["evidence"] = f"unknown category returned: {text[:200]}"
        return verdict
    except json.JSONDecodeError:
        return {"category": "UNCLASSIFIED", "evidence": f"non-JSON response: {text[:200]}",
                "fixable_in_phase": "not_fixable", "estimated_fix_effort": "high"}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="Path to webvoyager-*.json run output")
    ap.add_argument("--tasks", required=True, help="Path to tasks.yaml")
    ap.add_argument("--output", required=True, help="Path to write failure-taxonomy.json")
    ap.add_argument("--concurrency", type=int, default=4)
    args = ap.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(2)

    run = json.loads(Path(args.run).read_text())
    tasks_yaml = yaml.safe_load(Path(args.tasks).read_text())
    tasks_by_id = {t["id"]: t for t in tasks_yaml["tasks"]}

    results = run.get("results", run.get("responses", []))
    failures = [r for r in results if not r.get("passed", r.get("success", False))]

    print(f"Run: {args.run}")
    print(f"Total: {len(results)}, failures: {len(failures)}")
    print(f"Categorizing with claude-sonnet-4-6, concurrency={args.concurrency}...")

    sem = asyncio.Semaphore(args.concurrency)

    async def with_sem(client, task, result):
        async with sem:
            return await categorize_one(client, task, result)

    async with httpx.AsyncClient() as client:
        coros = []
        for r in failures:
            task = tasks_by_id.get(r["id"])
            if not task:
                continue
            coros.append((r, task, with_sem(client, task, r)))
        verdicts = await asyncio.gather(*[c[2] for c in coros])

    by_category: dict[str, int] = {c: 0 for c in CATEGORIES}
    out_failures = []
    for (r, task, _coro), v in zip(coros, verdicts):
        by_category[v.get("category", "UNCLASSIFIED")] += 1
        out_failures.append({
            "task_id": r["id"],
            "task_description": task["description"],
            "agent_answer": r.get("answer", r.get("final_answer", ""))[:500],
            "expected_answer": task.get("expected_answer", ""),
            "category": v.get("category", "UNCLASSIFIED"),
            "evidence": v.get("evidence", ""),
            "fixable_in_phase": v.get("fixable_in_phase", ""),
            "estimated_fix_effort": v.get("estimated_fix_effort", ""),
        })

    out = {
        "source_run": args.run,
        "tasks_file": args.tasks,
        "total_failures": len(failures),
        "categorized_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "categorizer_model": "claude-sonnet-4-6",
        "by_category": by_category,
        "failures": out_failures,
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=2))

    print()
    for cat, count in by_category.items():
        if count:
            print(f"  {cat:20s} {count:3d}")
    print()
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
