"""eval/webvoyager-100/direct_runner.py — Run WebVoyager eval directly (no gateway).

Uses Playwright + OpenAI API directly, bypassing the gateway entirely.
Each task runs in its own browser context for isolation.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx
import yaml
from playwright.async_api import async_playwright

PLANNER_BACKEND = os.environ.get("PLANNER_BACKEND", "openai")  # openai, anthropic, or kimi
GPT_MODEL = os.environ.get("PLANNER_MODEL", "gpt-5.5")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
KIMI_KEY = os.environ.get("KIMI_API_KEY", "")
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "claude-sonnet-4-6")

SYSTEM_PROMPT = (
    "You are a WebVoyager browser agent. You can navigate websites, click elements, type text, and extract information.\n"
    "\n"
    "## ACTIONS (return exactly one JSON object):\n"
    "- {\"action\": \"open\", \"args\": {\"url\": \"https://...\"}} - Navigate to a URL\n"
    "- {\"action\": \"click\", \"args\": {\"element_id\": \"pw-5\"}} - Click element by id from state.elements\n"
    "- {\"action\": \"type\", \"args\": {\"element_id\": \"pw-3\", \"text\": \"search query\"}} - Type into input field\n"
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


async def plan_next_action(
    client: httpx.AsyncClient,
    task: str,
    state: dict[str, Any],
    previous_steps: list[dict],
) -> dict:
    prompt = {
        "task": task,
        "state": state,
        "previous_steps": previous_steps[-5:],
    }

    if PLANNER_BACKEND == "anthropic":
        # Anthropic planner
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": GPT_MODEL,
                "max_tokens": 8192,
                "messages": [
                    {"role": "user", "content": SYSTEM_PROMPT + "\n\n" + json.dumps(prompt, separators=(",", ":"))},
                ],
            },
            timeout=120,
        )
        resp.raise_for_status()
        content = resp.json()["content"][0]["text"]
    elif PLANNER_BACKEND == "kimi":
        # Kimi/Moonshot planner (OpenAI-compatible)
        resp = await client.post(
            "https://api.moonshot.ai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {KIMI_KEY}",
            },
            json={
                "model": GPT_MODEL,  # e.g. kimi-k2-turbo-preview
                "max_tokens": 8192,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": json.dumps(prompt, separators=(",", ":"))},
                ],
            },
            timeout=120,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
    else:
        # OpenAI planner (default)
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_KEY}",
            },
            json={
                "model": GPT_MODEL,
                "max_completion_tokens": 8192,
                "reasoning_effort": "high",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": json.dumps(prompt, separators=(",", ":"))},
                ],
            },
            timeout=120,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]

    # Parse JSON from response - handle multi-line/thinking output
    candidate = content.strip()
    # Strip thinking tags if present
    import re
    candidate = re.sub(r'<thinking>.*?</thinking>', '', candidate, flags=re.DOTALL)
    candidate = re.sub(r'\x08.*?\x0e', '', candidate, flags=re.DOTALL)
    candidate = candidate.strip()
    # Extract code block
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        start_idx = 1
        end_idx = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
        candidate = "\n".join(lines[start_idx:end_idx]).strip()
    # Extract JSON object
    if not candidate.startswith("{"):
        start = candidate.find("{")
        if start >= 0:
            candidate = candidate[start:]
    # Find matching closing brace
    if candidate.startswith("{"):
        depth = 0
        for i, c in enumerate(candidate):
            if c == "{": depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    candidate = candidate[:i+1]
                    break
    return json.loads(candidate)


async def judge(task_desc: str, criterion: str, response: str) -> bool:
    if not ANTHROPIC_KEY:
        print("  [JUDGE] No ANTHROPIC_API_KEY — returning False")
        return False
    prompt = f"""Judge whether the response satisfies the success criterion.

Task: {task_desc}
Success criterion: {criterion}
Agent response: {response}

Respond with exactly one word: PASS or FAIL."""
    max_retries = 4
    for attempt in range(max_retries):
        try:
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
                if r.status_code == 429:
                    retry_after = int(r.headers.get("retry-after", 10))
                    print(f"  [JUDGE] Rate limited (attempt {attempt+1}/{max_retries}), waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    continue
                if r.status_code != 200:
                    print(f"  [JUDGE] HTTP {r.status_code} on attempt {attempt+1}: {r.text[:120]}")
                    await asyncio.sleep(2 ** attempt)
                    continue
                text = r.json()["content"][0]["text"].strip().upper()
                result = text.startswith("PASS")
                print(f"  [JUDGE] {'PASS' if result else 'FAIL'}")
                return result
        except Exception as exc:
            print(f"  [JUDGE] Exception (attempt {attempt+1}/{max_retries}): {exc}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
    print("  [JUDGE] All retries exhausted — returning False")
    return False


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


async def run_task(task: dict, traces_dir: Path | None) -> dict:
    t0 = time.perf_counter()
    try:
        # Per-task timeout: 600s max (many WV tasks need >300s for multi-page navigation)
        return await asyncio.wait_for(_run_task_inner(task, traces_dir, t0), timeout=600)
    except asyncio.TimeoutError:
        return {
            "id": task["id"],
            "passed": False,
            "error": "Task timed out (600s)",
            "final_answer": "",
            "steps": [],
            "duration_s": round(time.perf_counter() - t0, 2),
        }
    except Exception as e:
        return {
            "id": task["id"],
            "passed": False,
            "error": f"{type(e).__name__}: {e}",
            "duration_s": round(time.perf_counter() - t0, 2),
        }


async def _run_task_inner(task: dict, traces_dir: Path | None, t0: float):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(task["starting_url"], wait_until="domcontentloaded", timeout=15000)
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
                        attrs = raw.get("attributes") if isinstance(raw.get("attributes"), dict) else {}
                        elements.append(
                            {
                                "id": eid,
                                "role": str(raw.get("role") or "unknown"),
                                "text": raw.get("text") if isinstance(raw.get("text"), str) else None,
                                "attributes": {str(k): str(v) for k, v in attrs.items()},
                            }
                        )

                    # Trim to 50 elements
                    priority_roles = {"textbox", "searchbox", "button", "link", "combobox", "option"}
                    elements.sort(key=lambda e: 0 if e.get("role") in priority_roles else 1)
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
                            task=task["description"],
                            state=state,
                            previous_steps=steps,
                        )
                    except Exception as e:
                        action = {"action": "finish", "args": {"final_answer": f"Error planning: {e}"}}

                    # Execute action
                    obs = ""
                    finish_answer = None
                    try:
                        name = action.get("action", "")
                        args = action.get("args", {})
                        if name == "open":
                            url = args.get("url", "")
                            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                            obs = f"Opened {url}"
                        elif name == "click":
                            eid = args.get("element_id") or args.get("id", "")
                            if eid:
                                idx = int(eid.split("-")[1]) if "-" in eid else 0
                                raw = await page.evaluate(ELEMENT_SNAPSHOT_SCRIPT)
                                if idx < len(raw):
                                    sel = raw[idx].get("selector", "")
                                    await page.locator(sel).first.click(timeout=5000)
                                    obs = f"Clicked {eid}"
                                else:
                                    obs = f"Element {eid} not found"
                            else:
                                obs = "click requires element_id"
                        elif name == "type":
                            eid = args.get("element_id") or args.get("id", "")
                            text = args.get("text", "")
                            if eid:
                                idx = int(eid.split("-")[1]) if "-" in eid else 0
                                raw = await page.evaluate(ELEMENT_SNAPSHOT_SCRIPT)
                                if idx < len(raw):
                                    sel = raw[idx].get("selector", "")
                                    await page.locator(sel).first.fill(text, timeout=5000)
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
                            finish_answer = str(args.get("final_answer") or args.get("answer") or "")
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
        }

    passed = await judge(task["description"], task["success_criterion"], final_answer)

    result = {
        "id": task["id"],
        "passed": passed,
        "final_answer": final_answer[:1000],
        "steps": steps,
        "duration_s": round(time.perf_counter() - t0, 2),
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


async def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default="eval/webvoyager-100/tasks.yaml")
    ap.add_argument("--output", default="outputs/v1_1/webvoyager-gpt55-direct.json")
    ap.add_argument("--concurrency", type=int, default=10, help="Parallel browser tasks (default 10)")
    ap.add_argument("--max-retries", type=int, default=2, help="Retry failed tasks up to N times (default 2)")
    ap.add_argument("--retry-failed", type=str, default=None, help="Load prior JSON results and retry only failed tasks")
    ap.add_argument("--traces", action="store_true")
    ap.add_argument("--traces-dir", default=None)
    ap.add_argument("--skip-done", action="store_true", help="Skip tasks with existing trace files")
    args = ap.parse_args()

    with open(args.tasks) as f:
        config = yaml.safe_load(f)
    all_tasks = config["tasks"]

    traces_dir: Path | None = None
    if args.traces:
        traces_dir = Path(args.traces_dir or Path(args.output).parent / "traces")
        traces_dir.mkdir(parents=True, exist_ok=True)

    sem = asyncio.Semaphore(args.concurrency)

    async def run_with_sem(task: dict) -> dict:
        async with sem:
            result = await run_task(task, traces_dir)
            print(f"  {result['id']}: {'PASS' if result['passed'] else 'FAIL'} ({result.get('duration_s', 0):.0f}s)")
            return result

    # Load prior results if retrying
    prior_results: dict[str, dict] = {}
    if args.retry_failed and Path(args.retry_failed).exists():
        prior = json.loads(Path(args.retry_failed).read_text())
        prior_results = {r["id"]: r for r in prior.get("results", [])}
        print(f"Loaded {len(prior_results)} prior results from {args.retry_failed}")

    # Determine tasks to run
    tasks_to_run = []
    for t in all_tasks:
        tid = t["id"]
        # Skip if already passed in prior run
        if tid in prior_results and prior_results[tid].get("passed"):
            continue
        # Skip if trace exists and --skip-done (load trace result)
        if args.skip_done and traces_dir and (traces_dir / f"{tid}.json").exists():
            if tid not in prior_results:
                prior_results[tid] = json.loads((traces_dir / f"{tid}.json").read_text())
            continue
        tasks_to_run.append(t)

    skipped = len(all_tasks) - len(tasks_to_run)
    if skipped:
        print(f"Skipping {skipped} already-passed/done tasks, running {len(tasks_to_run)}")

    # Run with retries
    remaining = list(tasks_to_run)
    all_results: dict[str, dict] = dict(prior_results)

    for attempt in range(1 + args.max_retries):
        if not remaining:
            break
        if attempt > 0:
            print(f"\n=== RETRY ATTEMPT {attempt}/{args.max_retries} ({len(remaining)} tasks) ===")

        results = await asyncio.gather(*[run_with_sem(t) for t in remaining])

        still_failing = []
        for r in results:
            if r["passed"]:
                all_results[r["id"]] = r
            else:
                still_failing.append(next(t for t in remaining if t["id"] == r["id"]))
                all_results[r["id"]] = r  # keep best effort

        remaining = still_failing

    # Merge with prior passed results
    final_results = [all_results[t["id"]] for t in all_tasks if t["id"] in all_results]
    # Any tasks never run (shouldn't happen) get a FAIL stub
    for t in all_tasks:
        if t["id"] not in all_results:
            final_results.append({"id": t["id"], "passed": False, "final_answer": "", "steps": [], "error": "never run"})

    passed = sum(1 for r in final_results if r["passed"])
    total = len(final_results)
    out = {
        "benchmark": "webvoyager",
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": passed / total if total else 0,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": final_results,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=2))
    print(f"WebVoyager: {passed}/{total} = {out['pass_rate']:.2%}")
    sys.exit(0 if out["pass_rate"] >= 0.60 else 1)


if __name__ == "__main__":
    asyncio.run(main())
