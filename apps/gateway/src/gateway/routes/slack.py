from __future__ import annotations

import json
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from slack_integration.events import command_from_app_mention, parse_slash_command, verify_slack_signature
from slack_integration.oauth import SlackOAuthConfig, build_authorize_url, exchange_code

from gateway.config import settings
from gateway.routes.sessions import SessionCreateRequest, create_session

router = APIRouter()
_writer: Any = None


class SlackStatus(BaseModel):
    configured: bool
    connected: bool
    team_name: str | None = None


def set_writer(writer: Any) -> None:
    global _writer
    _writer = writer


async def _pool() -> Any | None:
    if _writer is None or _writer._pool is None:
        return None
    return _writer._pool


def _oauth_config(request: Request) -> SlackOAuthConfig:
    redirect_uri = settings.slack_redirect_uri or str(request.url_for("slack_callback"))
    return SlackOAuthConfig(
        client_id=settings.slack_client_id,
        client_secret=settings.slack_client_secret,
        redirect_uri=redirect_uri,
    )


async def _installation(team_id: str) -> dict[str, Any] | None:
    pool = await _pool()
    if pool is None:
        return None
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT team_id, team_name, bot_token, signing_secret
            FROM slack_installations
            WHERE team_id = $1
            ORDER BY installed_at DESC
            LIMIT 1
            """,
            team_id,
        )
    return dict(row) if row else None


async def _signing_secret(team_id: str | None) -> str:
    if team_id:
        installation = await _installation(team_id)
        if installation and installation.get("signing_secret"):
            return str(installation["signing_secret"])
    return settings.slack_signing_secret


async def _verify_request(request: Request, body: bytes, team_id: str | None) -> None:
    secret = await _signing_secret(team_id)
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    signature = request.headers.get("X-Slack-Signature")
    if not verify_slack_signature(body, timestamp, signature, secret):
        raise HTTPException(status_code=401, detail={"error": "invalid_slack_signature"})


async def _post_working_message(team_id: str, channel_id: str, response_url: str | None, text: str) -> None:
    payload = {"text": text}
    async with httpx.AsyncClient(timeout=10.0) as client:
        if response_url:
            await client.post(response_url, json={**payload, "response_type": "ephemeral"})
            return
        installation = await _installation(team_id)
        token = installation.get("bot_token") if installation else None
        if token and channel_id:
            await client.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {token}"},
                json={**payload, "channel": channel_id},
            )


async def _start_slack_task(
    team_id: str,
    channel_id: str,
    task: str,
    response_url: str | None = None,
) -> dict[str, str]:
    session = await create_session(SessionCreateRequest())
    await _post_working_message(
        team_id,
        channel_id,
        response_url,
        f"Working on it… session {session.session_id}: {task or 'Slack task'}",
    )
    return {"session_id": session.session_id, "text": "Working on it…"}


@router.get("/status", response_model=SlackStatus)
async def slack_status() -> SlackStatus:
    connected = False
    team_name: str | None = None
    pool = await _pool()
    if pool is not None:
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT team_name FROM slack_installations ORDER BY installed_at DESC LIMIT 1")
        connected = row is not None
        team_name = str(row["team_name"]) if row and row["team_name"] else None
    return SlackStatus(
        configured=bool(settings.slack_client_id and settings.slack_signing_secret),
        connected=connected,
        team_name=team_name,
    )


@router.delete("/disconnect")
async def disconnect_slack() -> dict[str, bool]:
    pool = await _pool()
    if pool is not None:
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM slack_installations")
    return {"disconnected": True}


@router.get("/install")
async def install_slack(request: Request) -> RedirectResponse:
    if not settings.slack_client_id or not settings.slack_client_secret:
        raise HTTPException(status_code=501, detail={"error": "slack_unconfigured"})
    return RedirectResponse(build_authorize_url(_oauth_config(request)))


@router.get("/callback", name="slack_callback")
async def slack_callback(request: Request, code: str | None = None, error: str | None = None) -> dict[str, Any]:
    if error:
        raise HTTPException(status_code=400, detail={"error": error})
    if not code:
        raise HTTPException(status_code=400, detail={"error": "missing_code"})
    payload = await exchange_code(_oauth_config(request), code)
    team = payload.get("team") or {}
    access_token = payload.get("access_token") or (payload.get("authed_user") or {}).get("access_token")
    if not isinstance(team, dict) or not team.get("id") or not access_token:
        raise HTTPException(status_code=502, detail={"error": "slack_oauth_incomplete"})
    pool = await _pool()
    if pool is None:
        raise HTTPException(status_code=503, detail={"error": "persistence_unavailable"})
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM slack_installations WHERE team_id = $1", team["id"])
        await conn.execute(
            """
            INSERT INTO slack_installations (team_id, team_name, bot_token, signing_secret)
            VALUES ($1, $2, $3, $4)
            """,
            str(team["id"]),
            str(team.get("name", "")),
            str(access_token),
            settings.slack_signing_secret,
        )
    return {"ok": True, "team_id": str(team["id"]), "team_name": str(team.get("name", ""))}


@router.post("/command")
async def slack_command(request: Request) -> dict[str, str]:
    body = await request.body()
    command = parse_slash_command(body)
    await _verify_request(request, body, command.team_id)
    return await _start_slack_task(command.team_id, command.channel_id, command.text, command.response_url)


@router.post("/events")
async def slack_events(request: Request) -> dict[str, Any]:
    body = await request.body()
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail={"error": "invalid_json"}) from exc
    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge", "")}
    team_id = str(payload.get("team_id", "")) or None
    await _verify_request(request, body, team_id)
    command = command_from_app_mention(payload)
    if command is None:
        return {"ok": True, "ignored": True}
    result = await _start_slack_task(command.team_id, command.channel_id, command.text)
    return {"ok": True, **result}
