# eval/webvoyager-300/runner.py — WebVoyager-300 eval harness.
#
# Multi-planner runner supporting GPT-5.5, Sonnet 4.6, Opus 4.6/4.7, Kimi K2.6.
# Single-attempt per task. No memoization. No best-of-N.
#
# Usage:
#   python runner.py --planner gpt-5.5
#   python runner.py --planner sonnet-4.6

from __future__ import annotations

import argparse
import asyncio
import glob
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import httpx
import yaml
from playwright.async_api import async_playwright

os.environ["MANTLE_EVAL_MODE"] = "1"

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "claude-sonnet-4-6")

PLANNER_MAP = {
    "gpt-5.5": {
        "provider": "openai",
        "model": "gpt-5.5",
        "max_tokens": 8192,
        "reasoning_effort": "high",
    },
    "sonnet-4.6": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-6",
        "max_tokens": 8192,
    },
    "opus-4-6": {
        "provider": "anthropic",
        "model": "claude-opus-4-6",
        "max_tokens": 8192,
    },
    "opus-4.7": {
        "provider": "anthropic",
        "model": "claude-opus-4-7",
        "max_tokens": 8192,
    },
    "kimi-k2.6": {
        "provider": "openai",
        "model": "kimi-k2.6",
        "max_tokens": 8192,
        "reasoning_effort": "high",
    },
}

SYSTEM_PROMPT = (
    "You are a WebVoyager browser agent. You can navigate websites, click elements, "
    "type text, and extract information.\n"
    "\n"
    "## ACTIONS (return exactly one JSON object):\n"
    "- {\"action\": \"open\", \"args\": {\"url\": \"https://...\"}} - Navigate to a URL\n"
    "- {\"action\": \"click\", \"args\": {\"element_id\": \"pw-5\"}} - Click element by id from state.elements\n"
    "- {\"action\": \"type\", \"args\": {\"element_id\": \"pw-3\", "
    "\"text\": \"search query\"}} - Type into input field\n"
    "- {\"action\": \"evaluate\", \"args\": {\"script\": \"document.querySelector(...)\"}} - Run JS\n"
    "- {\"action\": \"finish\", \"args\": {\"final_answer\": \"...\"}} - Submit final answer\n"
    "\n"
    "## RULES:\n"
    "1. NEVER finish on the first step. Always explore the page first.\n"
    "2. Read the current page state carefully. Use elements from state.elements.\n"
    "3. If you need to search, find a search box, type your query, and click search.\n"
    "4. Navigate to relevant pages before extracting answers.\n"
    "5. Only finish when you have found the specific information requested.\n"
    "6. The final_answer must directly answer the task question with specific details.\n"
    "\n"
    "Return ONLY a JSON object, no markdown, no explanation."
)

# ---------------------------------------------------------------------------
# Element snapshot (same as direct_runner)
# ---------------------------------------------------------------------------

ELEMENT_SNAPSHOT_SCRIPT = r"""
() => {
  const interactiveSelector = [
    'a[href]', 'button', 'input', 'textarea', 'select',
    '[role]', '[contenteditable="true"]', '[tabindex]:not([tabindex="-1"])'
  ].join(',');

  function cssEscape(value) {
    if (window.CSS && typeof window.CSS.escape === 'function')
      return window.CSS.escape(value);
    return String(value).replace(/[^a-zA-Z0-9_-]/g, '\\$&');
  }

  function selectorFor(element) {
    if (element.id) return '#' + cssEscape(element.id);
    for (const attr of ['data-testid', 'data-test', 'aria-label', 'name']) {
      const value = element.getAttribute(attr);
      if (value) return element.tagName.toLowerCase() + '[' + attr + '="' + String(value).replace(/"/g, '\\"') + '"]';
    }
    const parts = [];
    let current = element;
    while (current && current.nodeType === Node.ELEMENT_NODE && current !== document.body) {
      const tag = current.tagName.toLowerCase();
      const siblings = Array.from(current.parentElement?.children || []).filter(s => s.tagName === current.tagName);
      const index = siblings.indexOf(current) + 1;
      parts.unshift(siblings.length > 1 ? tag + ':nth-of-type(' + index + ')' : tag);
      current = current.parentElement;
    }
    return parts.length ? parts.join(' > ') : element.tagName.toLowerCase();
  }

  function roleFor(element) {
    const explicitRole = element.getAttribute('role');
    if (explicitRole) return explicitRole;
    const tag = element.tagName.toLowerCase();
    if (tag === 'a') return 'link';
    if (tag === 'button') return 'button';
    if (tag === 'input') return element.getAttribute('type') || 'textbox';
    if (tag === 'textarea') return 'textbox';
    if (tag === 'select') return 'combobox';
    return tag;
  }

  return Array.from(document.querySelectorAll(interactiveSelector)).map((el, i) => {
    const attrs = {};
    for (const attr of ['id', 'name', 'type', 'href', 'aria-label', 'placeholder', 'value', 'data-testid']) {
      const value = el.getAttribute(attr);
      if (value !== null) attrs[attr] = value;
    }
    return {
      id: 'pw-' + i,
      role: roleFor(el),
      text: (el.innerText || el.getAttribute('aria-label') || el.getAttribute('value') || '').trim() || null,
      attributes: attrs,
      selector: selectorFor(el),
    };
  });
}
"""

# ---------------------------------------------------------------------------
# Planner
# ---------------------------------------------------------------------------


async def plan_next_action(
    client: httpx.AsyncClient,
    planner_cfg: dict,
    task: str,
    state: dict[str, Any],
    previous_steps: list[dict],
) -> dict:
    prompt = {
        "task": task,
        "state": state,
        "previous_steps": previous_steps[-5:],
    }

    provider = planner_cfg["provider"]
    if provider == "openai":
        payload = {
            "model": planner_cfg["model"],
            "max_completion_tokens": planner_cfg["max_tokens"],
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(prompt, separators=(",", ":"))},
            ],
        }
        if "reasoning_effort" in planner_cfg:
            payload["reasoning_effort"] = planner_cfg["reasoning_effort"]

        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_KEY}",
            },
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]

    elif provider == "anthropic":
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": planner_cfg["model"],
                "max_tokens": planner_cfg["max_tokens"],
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": json.dumps(prompt, separators=(",", ":"))}],
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        content = "".join(
            part.get("text", "")
            for part in data.get("content", [])
            if isinstance(part, dict) and part.get("type") == "text"
        )

    else:
        raise ValueError(f"Unknown provider: {provider}")

    # Parse JSON from response
    candidate = content.strip()
    candidate = re.sub(r"<thinking>.*?</thinking>", "", candidate, flags=re.DOTALL)
    candidate = re.sub(r"<think>.*?</think>", "", candidate, flags=re.DOTALL)
    candidate = candidate.strip()

    if candidate.startswith("```"):
        lines = candidate.splitlines()
        start_idx = 1
        end_idx = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
        candidate = "\n".join(lines[start_idx:end_idx]).strip()

    if not candidate.startswith("{"):
        start = candidate.find("{")
        if start >= 0:
            candidate = candidate[start:]

    if candidate.startswith("{"):
        depth = 0
        for i, c in enumerate(candidate):
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    candidate = candidate[: i + 1]
                    break

    return json.loads(candidate)


# ---------------------------------------------------------------------------
# Judge
# ---------------------------------------------------------------------------


async def judge(task_desc: str, criterion: str, response: str) -> bool:
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


# ---------------------------------------------------------------------------
# Task runner
# ---------------------------------------------------------------------------


async def run_task(task: dict, planner_cfg: dict, traces_dir: Path | None) -> dict:
    t0 = time.perf_counter()
    try:
        return await asyncio.wait_for(
            _run_task_inner(task, planner_cfg, traces_dir, t0), timeout=180
        )
    except asyncio.TimeoutError:
        return {
            "id": task["id"],
            "passed": False,
            "error": "Task timed out (180s)",
            "duration_s": round(time.perf_counter() - t0, 2),
            "source": task.get("source", "original"),
            "category_hint": task.get("category_hint", ""),
        }
    except Exception as e:
        return {
            "id": task["id"],
            "passed": False,
            "error": f"{type(e).__name__}: {e}",
            "duration_s": round(time.perf_counter() - t0, 2),
            "source": task.get("source", "original"),
            "category_hint": task.get("category_hint", ""),
        }


async def _run_task_inner(
    task: dict, planner_cfg: dict, traces_dir: Path | None, t0: float
):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(
                task["starting_url"], wait_until="domcontentloaded", timeout=15000
            )
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass

            steps = []
            final_answer = ""

            async with httpx.AsyncClient(timeout=120) as client:
                for step_index in range(1, 26):
                    # Get DOM state
                    try:
                        raw_elements = await page.evaluate(ELEMENT_SNAPSHOT_SCRIPT)
                    except Exception:
                        raw_elements = []

                    elements = []
                    for raw in raw_elements:
                        if not isinstance(raw, dict):
                            continue
                        eid = str(raw.get("id") or "")
                        sel = raw.get("selector")
                        if not eid or not isinstance(sel, str):
                            continue
                        attrs = (
                            raw.get("attributes")
                            if isinstance(raw.get("attributes"), dict)
                            else {}
                        )
                        elements.append(
                            {
                                "id": eid,
                                "role": str(raw.get("role") or "unknown"),
                                "text": (
                                    raw.get("text")
                                    if isinstance(raw.get("text"), str)
                                    else None
                                ),
                                "attributes": {
                                    str(k): str(v) for k, v in attrs.items()
                                },
                            }
                        )

                    # Trim to 50 elements
                    priority_roles = {
                        "textbox",
                        "searchbox",
                        "button",
                        "link",
                        "combobox",
                        "option",
                    }
                    elements.sort(
                        key=lambda e: 0 if e.get("role") in priority_roles else 1
                    )
                    elements = elements[:50]

                    state = {
                        "url": page.url,
                        "title": await page.title(),
                        "elements": elements,
                    }

                    # Plan next action
                    try:
                        action = await plan_next_action(
                            client,
                            planner_cfg,
                            task=task["description"],
                            state=state,
                            previous_steps=steps,
                        )
                    except Exception as e:
                        action = {
                            "action": "finish",
                            "args": {"final_answer": f"Error planning: {e}"},
                        }

                    # Execute action
                    obs = ""
                    finish_answer = None
                    try:
                        name = action.get("action", "")
                        args = action.get("args", {})
                        if name == "open":
                            url = args.get("url", "")
                            await page.goto(
                                url, wait_until="domcontentloaded", timeout=15000
                            )
                            obs = f"Opened {url}"
                        elif name == "click":
                            eid = args.get("element_id") or args.get("id", "")
                            if eid:
                                idx = (
                                    int(eid.split("-")[1]) if "-" in eid else 0
                                )
                                raw = await page.evaluate(ELEMENT_SNAPSHOT_SCRIPT)
                                if idx < len(raw):
                                    sel = raw[idx].get("selector", "")
                                    await page.locator(sel).first.click(
                                        timeout=5000
                                    )
                                    obs = f"Clicked {eid}"
                                else:
                                    obs = f"Element {eid} not found"
                            else:
                                obs = "click requires element_id"
                        elif name == "type":
                            eid = args.get("element_id") or args.get("id", "")
                            text = args.get("text", "")
                            if eid:
                                idx = (
                                    int(eid.split("-")[1]) if "-" in eid else 0
                                )
                                raw = await page.evaluate(ELEMENT_SNAPSHOT_SCRIPT)
                                if idx < len(raw):
                                    sel = raw[idx].get("selector", "")
                                    await page.locator(sel).first.fill(
                                        text, timeout=5000
                                    )
                                    obs = f"Typed into {eid}"
                                else:
                                    obs = f"Element {eid} not found"
                            else:
                                obs = "type requires element_id"
                        elif name == "evaluate":
                            script = args.get("script", "")
                            result = await page.evaluate(script)
                            obs = f"Eval: {json.dumps(result, default=str)[:500]}"
                        elif name == "finish":
                            finish_answer = str(
                                args.get("final_answer")
                                or args.get("answer")
                                or ""
                            )
                            obs = "Finished"
                    except Exception as e:
                        obs = f"Action failed: {e}"

                    steps.append(
                        {
                            "step": step_index,
                            "state": state,
                            "action": action,
                            "observation": obs,
                        }
                    )

                    if finish_answer is not None:
                        final_answer = finish_answer
                        break

            await browser.close()

    except Exception as e:
        return {
            "id": task["id"],
            "passed": False,
            "error": f"{type(e).__name__}: {e}",
            "duration_s": round(time.perf_counter() - t0, 2),
            "source": task.get("source", "original"),
            "category_hint": task.get("category_hint", ""),
        }

    passed = await judge(
        task["description"], task["success_criterion"], final_answer
    )

    result = {
        "id": task["id"],
        "passed": passed,
        "final_answer": final_answer[:1000],
        "steps": steps,
        "duration_s": round(time.perf_counter() - t0, 2),
        "source": task.get("source", "original"),
        "category_hint": task.get("category_hint", ""),
    }

    if traces_dir:
        trace = {
            "task_id": result["id"],
            "task_description": task["description"],
            "starting_url": task["starting_url"],
            "passed": result["passed"],
            "final_answer": result.get("final_answer", ""),
            "duration_s": result.get("duration_s", 0),
            "steps": result.get("steps", []),
        }
        (traces_dir / f"{result['id']}.json").write_text(json.dumps(trace, indent=2))

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def batch_output_path(output: str, batch_offset: int, batch_count: int) -> Path:
    output_path = Path(output)
    batch_end = batch_offset + max(batch_count - 1, 0)
    suffix = output_path.suffix or ".json"
    return output_path.with_name(
        f"{output_path.stem}.batch-{batch_offset:03d}-{batch_end:03d}{suffix}"
    )


def aggregate_batch_outputs(output: str, planner_name: str) -> dict[str, Any] | None:
    output_path = Path(output)
    suffix = output_path.suffix or ".json"
    pattern = str(output_path.with_name(f"{output_path.stem}.batch-*{suffix}"))
    batch_files = sorted(glob.glob(pattern))
    if not batch_files:
        return None

    results: list[dict[str, Any]] = []
    for batch_file in batch_files:
        try:
            data = json.loads(Path(batch_file).read_text())
        except (OSError, json.JSONDecodeError) as e:
            print(f"WARN: skipping unreadable batch result {batch_file}: {e}")
            continue
        for result in data.get("results", []):
            if isinstance(result, dict):
                results.append(result)

    results.sort(key=lambda r: str(r.get("id", "")))
    passed = sum(1 for r in results if r.get("passed"))
    total = len(results)
    aggregate = {
        "benchmark": "webvoyager-300",
        "planner": planner_name,
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": passed / total if total else 0,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "batch_files": batch_files,
        "results": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(aggregate, indent=2))
    return aggregate


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--tasks",
        default="eval/webvoyager-300/tasks.yaml",
        help="Path to tasks.yaml",
    )
    ap.add_argument(
        "--planner",
        choices=list(PLANNER_MAP.keys()),
        default="gpt-5.5",
        help="Planner model to use",
    )
    ap.add_argument(
        "--output",
        default=None,
        help="Output JSON path (auto-generated if omitted)",
    )
    ap.add_argument("--concurrency", type=int, default=3)
    ap.add_argument("--traces", action="store_true")
    ap.add_argument("--traces-dir", default=None)
    ap.add_argument("--batch-size", type=int, default=None, help="Run only N tasks")
    ap.add_argument("--batch-offset", type=int, default=0, help="Skip first M tasks")
    ap.add_argument(
        "--batch-cooldown",
        type=float,
        default=30,
        help="Seconds to wait after a batch completes",
    )
    args = ap.parse_args()

    if args.batch_size is not None and args.batch_size <= 0:
        ap.error("--batch-size must be positive")
    if args.batch_offset < 0:
        ap.error("--batch-offset must be non-negative")
    if args.batch_cooldown < 0:
        ap.error("--batch-cooldown must be non-negative")

    # Load tasks
    with open(args.tasks) as f:
        config = yaml.safe_load(f)
    tasks = config["tasks"]
    original_total = len(tasks)

    batch_mode = args.batch_size is not None or args.batch_offset > 0
    if batch_mode:
        start = args.batch_offset
        stop = original_total if args.batch_size is None else start + args.batch_size
        tasks = tasks[start:stop]

    planner_name = args.planner
    planner_cfg = PLANNER_MAP[planner_name]

    # Validate keys
    if planner_cfg["provider"] == "openai" and not OPENAI_KEY:
        print("ERROR: OPENAI_API_KEY not set")
        sys.exit(1)
    if planner_cfg["provider"] == "anthropic" and not ANTHROPIC_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    traces_dir: Path | None = None
    if args.traces:
        traces_dir = Path(
            args.traces_dir or Path(args.output or "outputs/v1_1/traces").parent
        )
        traces_dir.mkdir(parents=True, exist_ok=True)

    output = args.output or f"outputs/v1_1/webvoyager-300-{planner_name}.json"
    batch_output = (
        batch_output_path(output, args.batch_offset, len(tasks)) if batch_mode else Path(output)
    )

    sem = asyncio.Semaphore(args.concurrency)

    async def run_with_sem(task: dict) -> dict:
        async with sem:
            result = await run_task(task, planner_cfg, traces_dir)
            print(
                f"  {result['id']}: {'PASS' if result['passed'] else 'FAIL'} ({result.get('duration_s', 0):.0f}s)"
            )
            return result

    if batch_mode:
        print(
            f"Running WebVoyager-300 with {planner_name} "
            f"(batch offset {args.batch_offset}, {len(tasks)}/{original_total} tasks)..."
        )
    else:
        print(f"Running WebVoyager-300 with {planner_name} ({len(tasks)} tasks)...")
    results = await asyncio.gather(*[run_with_sem(t) for t in tasks])

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    out = {
        "benchmark": "webvoyager-300",
        "planner": planner_name,
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": passed / total if total else 0,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": results,
    }

    batch_output.parent.mkdir(parents=True, exist_ok=True)
    batch_output.write_text(json.dumps(out, indent=2))
    print(f"\nWebVoyager-300 ({planner_name}): {passed}/{total} = {out['pass_rate']:.2%}")
    print(f"Output: {batch_output}")

    if batch_mode:
        aggregate = aggregate_batch_outputs(output, planner_name)
        if aggregate:
            print(
                f"Aggregate: {aggregate['passed']}/{aggregate['total']} = "
                f"{aggregate['pass_rate']:.2%}"
            )
            print(f"Aggregate output: {output}")
        if args.batch_cooldown:
            print(f"Cooling down for {args.batch_cooldown:.0f}s...")
            await asyncio.sleep(args.batch_cooldown)


if __name__ == "__main__":
    asyncio.run(main())
