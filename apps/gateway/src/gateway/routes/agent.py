from __future__ import annotations

import asyncio
import ipaddress
import json
import socket
from dataclasses import asdict
from typing import Any, Literal
from urllib.parse import urlparse

import httpx
from browser.playwright_backend import PlaywrightBackend
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sandbox.backend import create_backend

from gateway.config import settings
from gateway.cost_wall import CostCeilingExceeded, default_cost_wall
from gateway import model_client
from gateway.model_client import ModelCallError
from gateway.sessions import broker
router = APIRouter()

AgentActionName = Literal["open", "click", "type", "evaluate", "finish"]
EVALUATE_SCRIPT_MAX_CHARS = 4_000
TYPE_TEXT_MAX_CHARS = 8_000
VLLM_TIMEOUT = httpx.Timeout(timeout=120.0, connect=5.0, read=120.0, write=10.0, pool=5.0)
BLOCKED_HOSTNAMES = {"localhost"}
BLOCKED_EVALUATE_TOKENS = (
    "fetch(",
    "xmlhttprequest",
    "websocket",
    "navigator.sendbeacon",
    "document.cookie",
    "localstorage",
    "sessionstorage",
)


class AgentRunRequest(BaseModel):
    task: str = Field(min_length=1)
    starting_url: str = Field(min_length=1)
    max_steps: int = Field(default=10, ge=1, le=50)
    headless: bool = False
    planner: str | None = None  # e.g. "gpt-5.5" to use OpenAI instead of vLLM


class AgentStep(BaseModel):
    step: int
    state: dict[str, Any]
    action: dict[str, Any]
    observation: str


class AgentRunResponse(BaseModel):
    final_answer: str
    steps: list[AgentStep]
    success: bool


class AgentAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: AgentActionName
    args: dict[str, Any] = Field(default_factory=dict)


@router.post("/run", response_model=AgentRunResponse)
async def run_agent(request: AgentRunRequest) -> AgentRunResponse:
    if not settings.vllm_base_url and not request.planner:
        raise HTTPException(
            status_code=500,
            detail={"error": "no_planner_configured", "message": "VLLM_BASE_URL is not set and no planner specified"},
        )

    starting_url = await _validated_http_url(request.starting_url)
    sandbox = create_backend(settings.sandbox_backend)
    sandbox_id: str | None = None
    browser = PlaywrightBackend()
    steps: list[AgentStep] = []
    final_answer = ""
    success = False

    try:
        async with asyncio.timeout(_run_timeout_seconds(request.max_steps)):
            sandbox_id = await asyncio.to_thread(sandbox.create)
            await browser._open(starting_url)  # noqa: SLF001

            for step_index in range(1, request.max_steps + 1):
                    state = _state_for_model(await browser._get_state())  # noqa: SLF001
                    await _validated_http_url(str(state.get("url") or ""))
                    action = await _plan_next_action(
                        task=request.task,
                        state=state,
                        previous_steps=steps,
                        planner=request.planner,
                    )
                    observation, finish_answer = await _execute_action(browser, action)

                    steps.append(
                        AgentStep(
                            step=step_index,
                            state=state,
                            action=action.model_dump(),
                            observation=observation,
                        )
                    )
                    if finish_answer is not None:
                        final_answer = finish_answer
                        success = True
                        break

        if not final_answer:
            final_answer = "Reached max_steps before the agent returned a finish action."
        return AgentRunResponse(final_answer=final_answer, steps=steps, success=success)
    except TimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail={"error": "agent_run_timeout", "message": "Agent run exceeded the allowed wall-clock time"},
        ) from exc
    finally:
        await asyncio.shield(_cleanup(browser, sandbox, sandbox_id))


async def _plan_next_action(
    *,
    task: str,
    state: dict[str, Any],
    previous_steps: list[AgentStep],
    planner: str | None = None,
) -> AgentAction:
    prompt = {
        "task": task,
        "state": state,
        "previous_steps": [
            {"step": step.step, "action": step.action, "observation": step.observation}
            for step in previous_steps[-5:]
        ],
    }
    messages = [
        {
            "role": "system",
            "content": (
                "You are a WebVoyager browser agent. Return exactly one JSON object with shape "
                '{"action":"open|click|type|evaluate|finish","args":{...}}. '
                "Use element ids from state.elements for click/type. "
                "For finish, put the answer in args.final_answer."
            ),
        },
        {"role": "user", "content": json.dumps(prompt, separators=(",", ":"))},
    ]
    if planner:
        return await _plan_openai(messages=messages, planner=planner)
    return await _plan_vllm(messages=messages)


async def _plan_vllm(*, messages: list[dict[str, Any]]) -> AgentAction:
    try:
        result = await model_client.vllm_chat(
            model=settings.vllm_model,
            messages=messages,
            max_tokens=4096,
            workspace_id="default",
            temperature=0,
        )
    except ModelCallError as exc:
        raise HTTPException(
            status_code=502,
            detail={"error": "vllm_call_failed", "message": str(exc)},
        ) from exc
    await _enforce_cost(result)
    return _parse_action(result["content"])


async def _plan_openai(
    *,
    messages: list[dict[str, Any]],
    planner: str,
) -> AgentAction:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=500,
            detail={"error": "openai_not_configured", "message": "OPENAI_API_KEY is not set"},
        )
    try:
        result = await model_client.openai_chat(
            model=planner,
            messages=messages,
            max_tokens=8192,
            workspace_id="default",
            temperature=0,
            thinking_enabled=True,
            thinking_budget_tokens=16384,
        )
    except ModelCallError as exc:
        raise HTTPException(
            status_code=502,
            detail={"error": "openai_call_failed", "message": str(exc)},
        ) from exc
    await _enforce_cost(result)
    return _parse_action(result["content"])


async def _enforce_cost(result: dict[str, Any]) -> None:
    """Check cost wall and update session cost tracking after each LLM call."""
    try:
        await default_cost_wall.check_and_record(
            workspace_id="default",
            model=result["model"],
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            cost_usd=result["cost_usd"],
        )
    except CostCeilingExceeded as exc:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "cost_ceiling_exceeded",
                "message": "Session cost ceiling exceeded",
                "cost_dollars": round(exc.attempted_total_usd, 4),
                "max_cost_dollars": exc.max_cost_dollars,
            },
        ) from exc

async def _execute_action(browser: PlaywrightBackend, action: AgentAction) -> tuple[str, str | None]:
    name = action.action
    args = action.args

    try:
        if name == "open":
            url = await _validated_http_url(_required_arg(args, "url"))
            await browser._open(url)  # noqa: SLF001
            return f"Opened {url}", None
        if name == "click":
            element_id = str(args.get("element_id") or args.get("id") or "")
            if not element_id:
                raise ValueError("click requires args.element_id")
            strategy = await browser._click(element_id)  # noqa: SLF001
            return f"Clicked {element_id} (strategy: {strategy})", None
        if name == "type":
            element_id = str(args.get("element_id") or args.get("id") or "")
            text = str(args.get("text") or "")
            if not element_id:
                raise ValueError("type requires args.element_id")
            if len(text) > TYPE_TEXT_MAX_CHARS:
                raise ValueError(f"type text exceeds {TYPE_TEXT_MAX_CHARS} characters")
            strategy = await browser._type_text(element_id, text)  # noqa: SLF001
            return f"Typed into {element_id} (strategy: {strategy})", None
        if name == "evaluate":
            script = _required_arg(args, "script")
            _validate_evaluate_script(script)
            result = await browser._evaluate(script)  # noqa: SLF001
            return f"Evaluated script: {json.dumps(result, default=str)[:1000]}", None
        if name == "finish":
            answer = str(args.get("final_answer") or args.get("answer") or "")
            return "Finished", answer
    except Exception as exc:  # Let the model observe and recover from browser/action errors.
        return f"Action failed: {exc}", None

    return f"Unsupported action: {name}", None


def _state_for_model(state: Any, max_elements: int = 50) -> dict[str, Any]:
    data = asdict(state)
    screenshot = data.pop("screenshot_b64", None)
    data["has_screenshot"] = bool(screenshot)
    # Trim elements to top-N most relevant (inputs, buttons, links first)
    elements = data.get("elements", [])
    if len(elements) > max_elements:
        priority_roles = {"textbox", "searchbox", "button", "link", "combobox", "option"}
        prioritized = sorted(elements, key=lambda e: 0 if e.get("role") in priority_roles else 1)
        data["elements"] = prioritized[:max_elements]
    return data


def _parse_action(content: str) -> AgentAction:
    candidate = content.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        candidate = "\n".join(lines[1:-1]).strip()
    if not candidate.startswith("{"):
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start >= 0 and end > start:
            candidate = candidate[start : end + 1]
    try:
        action = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502,
            detail={"error": "invalid_action_json", "message": "Planner did not return parseable action JSON"},
        ) from exc

    if not isinstance(action, dict) or action.get("action") not in {
        "open",
        "click",
        "type",
        "evaluate",
        "finish",
    }:
        raise HTTPException(
            status_code=502,
            detail={"error": "invalid_action", "message": "Action must be one of open, click, type, evaluate, finish"},
        )
    if not isinstance(action.get("args"), dict):
        action["args"] = {}
    try:
        return AgentAction.model_validate(action)
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail={"error": "invalid_action", "message": "Invalid action shape"},
        ) from exc


def _required_arg(args: dict[str, Any], key: str) -> str:
    value = args.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"args.{key} is required")
    return value


def _chat_completions_url(base_url: str) -> str:
    trimmed = base_url.rstrip("/")
    if trimmed.endswith("/v1"):
        return f"{trimmed}/chat/completions"
    return f"{trimmed}/v1/chat/completions"


def _vllm_headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if settings.vllm_api_key:
        headers["Authorization"] = f"Bearer {settings.vllm_api_key}"
    return headers


async def _validated_http_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise HTTPException(
            status_code=400,
            detail={"error": "invalid_url", "message": "Only http and https URLs with hostnames are allowed"},
        )
    hostname = parsed.hostname.lower()
    if hostname in BLOCKED_HOSTNAMES:
        raise HTTPException(
            status_code=400,
            detail={"error": "blocked_url", "message": "URL host is not allowed"},
        )
    await asyncio.to_thread(_ensure_public_hostname, hostname, parsed.port)
    return url


def _ensure_public_hostname(hostname: str, port: int | None) -> None:
    try:
        infos = socket.getaddrinfo(hostname, port or 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise HTTPException(
            status_code=400,
            detail={"error": "invalid_url", "message": "URL hostname cannot resolve"},
        ) from exc

    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (
            ip.is_loopback
            or ip.is_private
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise HTTPException(
                status_code=400, detail={"error": "blocked_url", "message": "URL host is not allowed"}
            )


def _validate_evaluate_script(script: str) -> None:
    normalized = script.lower().replace(" ", "")
    if len(script) > EVALUATE_SCRIPT_MAX_CHARS:
        raise ValueError(f"evaluate script exceeds {EVALUATE_SCRIPT_MAX_CHARS} characters")
    if any(token in normalized for token in BLOCKED_EVALUATE_TOKENS):
        raise ValueError("evaluate script contains a blocked browser API")


def _run_timeout_seconds(max_steps: int) -> float:
    return min(600.0, 30.0 + (max_steps * 75.0))


async def _cleanup(browser: PlaywrightBackend, sandbox: Any, sandbox_id: str | None) -> None:
    await browser._close()  # noqa: SLF001
    if sandbox_id is not None:
        await asyncio.to_thread(sandbox.destroy, sandbox_id)
