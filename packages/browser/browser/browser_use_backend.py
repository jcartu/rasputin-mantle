from __future__ import annotations

import json
import re
import subprocess
from typing import Any

from browser.errors import BrowserActionError, BrowserNotAvailable
from browser.types import BrowserBackend, BrowserElement, BrowserState

COMMAND_TIMEOUT_SECONDS = 30
ELEMENT_LINE_RE = re.compile(r'^\s*\[(\d+)]\s+([^\s]+)(?:\s+"([^"]*)")?')
URL_LINE_RE = re.compile(r"^\s*(?:url|current url|page url):\s*(\S+)", re.IGNORECASE)


def _run_browser_use(args: list[str]) -> subprocess.CompletedProcess[str]:
    command = ["browser-use", *args]
    try:
        result = subprocess.run(command, capture_output=True, check=False, text=True, timeout=COMMAND_TIMEOUT_SECONDS)
    except FileNotFoundError as exc:
        raise BrowserNotAvailable("browser-use CLI is not available on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise BrowserActionError(f"browser-use {' '.join(args)} timed out after 30s") from exc

    if result.returncode != 0:
        output = result.stderr or result.stdout or f"browser-use exited with code {result.returncode}"
        raise BrowserActionError(output.strip())
    return result


def _parse_state(stdout: str) -> BrowserState:
    elements: list[BrowserElement] = []
    url = ""
    for line in stdout.splitlines():
        url_match = URL_LINE_RE.match(line)
        if url_match:
            url = url_match.group(1)
            continue

        match = ELEMENT_LINE_RE.match(line)
        if not match:
            continue
        elements.append(BrowserElement(id=match.group(1), role=match.group(2), text=match.group(3)))
    return BrowserState(url=url, elements=elements)


def _parse_eval(stdout: str) -> Any:
    trimmed = stdout.strip()
    if not trimmed:
        return None
    try:
        return json.loads(trimmed)
    except json.JSONDecodeError:
        return trimmed


class BrowserUseBackend(BrowserBackend):
    def open(self, url: str) -> None:
        _run_browser_use(["open", "--", url])

    def get_state(self) -> BrowserState:
        result = _run_browser_use(["state"])
        try:
            return _parse_state(result.stdout)
        except (ValueError, TypeError, AttributeError) as exc:
            raise BrowserActionError(f"Failed to parse browser-use state: {exc}") from exc

    def click(self, element_id: str) -> None:
        _run_browser_use(["click", "--", element_id])

    def type(self, element_id: str, text: str) -> None:
        _run_browser_use(["input", "--", element_id, text])

    def evaluate(self, script: str) -> Any:
        result = _run_browser_use(["eval", "--", script])
        return _parse_eval(result.stdout)

    def close(self) -> None:
        _run_browser_use(["close"])

    def wait_for_selector(self, selector: str, state: str = "visible", timeout: int = 5000) -> bool:
        raise BrowserActionError("wait_for_selector not supported by browser-use")

    def capture_screenshot(self, path: str | None = None) -> bytes:
        raise BrowserActionError("capture_screenshot not supported by browser-use")

    def save_storage_state(self, path: str) -> None:
        raise BrowserActionError("save_storage_state not supported by browser-use")

    def scroll_to(self, element_id: str) -> None:
        raise BrowserActionError("scroll_to not supported by browser-use")
