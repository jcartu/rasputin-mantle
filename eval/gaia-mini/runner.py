from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Any

import httpx
import yaml

try:
    from gateway.model_client import ModelCallError, anthropic_chat
except ImportError:  # pragma: no cover - allows this file to show skip status outside PYTHONPATH setup
    ModelCallError = RuntimeError
    anthropic_chat = None  # type: ignore[assignment]

DEFAULT_GATEWAY_URL = "http://127.0.0.1:8000"
DEFAULT_STARTING_URL = "https://www.google.com/search?q=Rasputin+Mantle+GAIA+mini"


async def run_eval(tasks_path: Path, gateway_url: str) -> dict[str, Any]:
    tasks = _load_tasks(tasks_path)
    results: list[dict[str, Any]] = []
    for task in tasks:
        agent_result = await _run_agent(gateway_url, task["question"])
        judge_result = await _judge_answer(task, agent_result.get("final_answer", ""))
        results.append({"task_id": task["id"], "agent": agent_result, "judge": judge_result})

    judged = [item for item in results if item["judge"].get("judged")]
    passed = [item for item in judged if item["judge"].get("correct")]
    return {
        "tasks": len(tasks),
        "judged": len(judged),
        "passed": len(passed),
        "pass_rate": round(len(passed) / len(judged), 3) if judged else None,
        "judge_skipped": not bool(judged),
        "results": results,
    }


def _load_tasks(path: Path) -> list[dict[str, str]]:
    data = yaml.safe_load(path.read_text())
    tasks = data.get("tasks", []) if isinstance(data, dict) else []
    if not isinstance(tasks, list) or len(tasks) != 20:
        raise ValueError("tasks.yaml must contain exactly 20 tasks")
    return tasks


async def _run_agent(gateway_url: str, question: str) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{gateway_url.rstrip('/')}/api/agent/run",
                json={"task": question, "starting_url": DEFAULT_STARTING_URL, "max_steps": 8},
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        return {"success": False, "final_answer": "", "error": f"gateway_unavailable: {exc}"}


async def _judge_answer(task: dict[str, str], final_answer: str) -> dict[str, Any]:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return {"judged": False, "reason": "ANTHROPIC_API_KEY is not set"}
    if anthropic_chat is None:
        return {"judged": False, "reason": "gateway.model_client is not importable"}

    prompt = {
        "question": task["question"],
        "answer_hint": task.get("answer_hint", ""),
        "candidate_answer": final_answer,
        "instruction": "Return JSON only: {\"correct\": boolean, \"reason\": string}.",
    }
    try:
        response = await anthropic_chat(
            "claude-sonnet-4-5-20250929",
            [{"role": "user", "content": json.dumps(prompt)}],
            max_tokens=256,
            temperature=0,
        )
        data = json.loads(response["content"])
        return {"judged": True, "correct": bool(data.get("correct")), "reason": str(data.get("reason", ""))}
    except (ModelCallError, json.JSONDecodeError, KeyError, TypeError) as exc:
        return {"judged": False, "reason": f"judge_unavailable: {exc}"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run 20 GAIA-mini web-search tasks against the Mantle gateway.")
    parser.add_argument("--tasks", type=Path, default=Path(__file__).with_name("tasks.yaml"))
    parser.add_argument("--gateway-url", default=os.environ.get("GATEWAY_URL", DEFAULT_GATEWAY_URL))
    parser.add_argument("--output", default=None, help="Write results to JSON file")
    args = parser.parse_args()
    results = asyncio.run(run_eval(args.tasks, args.gateway_url))
    output_json = json.dumps(results, indent=2, sort_keys=True)
    print(output_json)
    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            f.write(output_json)


if __name__ == "__main__":
    main()
