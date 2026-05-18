from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx


@dataclass(frozen=True)
class SlackOAuthConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: tuple[str, ...] = ("commands", "chat:write", "app_mentions:read")


def build_authorize_url(config: SlackOAuthConfig, state: str | None = None) -> str:
    params = {
        "client_id": config.client_id,
        "scope": ",".join(config.scopes),
        "redirect_uri": config.redirect_uri,
    }
    if state:
        params["state"] = state
    return f"https://slack.com/oauth/v2/authorize?{urlencode(params)}"


async def exchange_code(config: SlackOAuthConfig, code: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            "https://slack.com/api/oauth.v2.access",
            data={
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "code": code,
                "redirect_uri": config.redirect_uri,
            },
        )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        error = str(payload.get("error", "oauth_failed"))
        raise ValueError(error)
    return payload
