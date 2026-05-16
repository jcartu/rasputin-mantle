from __future__ import annotations

import json
import subprocess
from typing import Any

from browser.errors import BrowserActionError, BrowserNotAvailable
from browser.types import BrowserBackend, BrowserElement, BrowserState

COMMAND_TIMEOUT_SECONDS = 30


def _run_agent_browser(args: list[str]) -> subprocess.CompletedProcess[str]:
    command = ["agent-browser", *args]
    try:
        result = subprocess.run(command, capture_output=True, check=False, text=True, timeout=COMMAND_TIMEOUT_SECONDS)
    except FileNotFoundError as exc:
        raise BrowserNotAvailable("agent-browser CLI is not available on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise BrowserActionError(f"agent-browser {' '.join(args)} timed out after 30s") from exc

    if result.returncode != 0:
        output = result.stderr or result.stdout or f"agent-browser exited with code {result.returncode}"
        raise BrowserActionError(output.strip())
    return result


def _string_field(value: dict[str, Any], keys: list[str]) -> str | None:
    for key in keys:
        field = value.get(key)
        if isinstance(field, str) and field:
            return field
    return None


def _attributes(value: dict[str, Any]) -> dict[str, str]:
    raw = value.get("attributes")
    if not isinstance(raw, dict):
        return {}
    return {str(key): attr_value for key, attr_value in raw.items() if isinstance(attr_value, str)}


def _collect_elements(value: Any, elements: list[BrowserElement], seen: set[str]) -> None:
    if isinstance(value, list):
        for item in value:
            _collect_elements(item, elements, seen)
        return
    if not isinstance(value, dict):
        return

    element_id = _string_field(value, ["ref", "id"])
    if element_id and element_id.startswith("@") and element_id not in seen:
        seen.add(element_id)
        elements.append(
            BrowserElement(
                id=element_id,
                role=_string_field(value, ["role", "type", "tag"]) or "unknown",
                text=_string_field(value, ["text", "name", "label", "value"]),
                attributes=_attributes(value),
            )
        )

    for child in value.values():
        _collect_elements(child, elements, seen)


def _read_url(value: Any) -> str:
    if isinstance(value, list):
        for item in value:
            url = _read_url(item)
            if url:
                return url
        return ""
    if not isinstance(value, dict):
        return ""

    url = _string_field(value, ["url", "currentUrl", "pageUrl"])
    if url:
        return url
    for child in value.values():
        child_url = _read_url(child)
        if child_url:
            return child_url
    return ""


def _parse_snapshot(stdout: str) -> BrowserState:
    payload = json.loads(stdout)
    elements: list[BrowserElement] = []
    _collect_elements(payload, elements, set())
    return BrowserState(url=_read_url(payload), elements=elements)


def _parse_eval(stdout: str) -> Any:
    trimmed = stdout.strip()
    if not trimmed:
        return None
    try:
        return json.loads(trimmed)
    except json.JSONDecodeError:
        return trimmed


class AgentBrowserBackend(BrowserBackend):
    def open(self, url: str) -> None:
        _run_agent_browser(["open", url])

    def get_state(self) -> BrowserState:
        result = _run_agent_browser(["snapshot", "-i", "--json"])
        try:
            return _parse_snapshot(result.stdout)
        except json.JSONDecodeError as exc:
            raise BrowserActionError(f"Failed to parse agent-browser snapshot: {exc}") from exc

    def click(self, element_id: str) -> None:
        _run_agent_browser(["click", element_id])

    def type(self, element_id: str, text: str) -> None:
        _run_agent_browser(["fill", element_id, text])

    def evaluate(self, script: str) -> Any:
        result = _run_agent_browser(["eval", script])
        return _parse_eval(result.stdout)

    def close(self) -> None:
        _run_agent_browser(["close"])
