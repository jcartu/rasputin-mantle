from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs


@dataclass(frozen=True)
class SlackCommand:
    team_id: str
    channel_id: str
    user_id: str
    text: str
    response_url: str | None = None


def verify_slack_signature(body: bytes, timestamp: str | None, signature: str | None, signing_secret: str) -> bool:
    if not timestamp or not signature or not signing_secret:
        return False
    try:
        request_ts = int(timestamp)
    except ValueError:
        return False
    if abs(time.time() - request_ts) > 300:
        return False
    base = b"v0:" + timestamp.encode("utf-8") + b":" + body
    digest = hmac.new(signing_secret.encode("utf-8"), base, hashlib.sha256).hexdigest()
    expected = f"v0={digest}"
    return hmac.compare_digest(expected, signature)


def parse_slash_command(body: bytes) -> SlackCommand:
    parsed = parse_qs(body.decode("utf-8"))
    return SlackCommand(
        team_id=parsed.get("team_id", [""])[0],
        channel_id=parsed.get("channel_id", [""])[0],
        user_id=parsed.get("user_id", [""])[0],
        text=parsed.get("text", [""])[0].strip(),
        response_url=parsed.get("response_url", [None])[0],
    )


def command_from_app_mention(payload: dict[str, Any]) -> SlackCommand | None:
    event = payload.get("event")
    if not isinstance(event, dict) or event.get("type") != "app_mention":
        return None
    return SlackCommand(
        team_id=str(payload.get("team_id", "")),
        channel_id=str(event.get("channel", "")),
        user_id=str(event.get("user", "")),
        text=str(event.get("text", "")).strip(),
    )
