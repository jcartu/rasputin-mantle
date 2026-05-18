from __future__ import annotations

from typing import Any

from email_integration.imap_watcher import InboundMessage, sender_allowed
from email_integration.smtp_sender import SmtpConfig, send_thread_reply
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from gateway.config import settings
from gateway.routes.sessions import SessionCreateRequest, create_session

router = APIRouter()


class MailStatus(BaseModel):
    inbound_configured: bool
    outbound_configured: bool
    allowed_senders: list[str]


class InboundMailRequest(BaseModel):
    sender: str
    subject: str
    body: str
    message_id: str | None = None
    references: str | None = None
    in_reply_to: str | None = None
    spam: bool = False


class OutboundReplyRequest(BaseModel):
    to: str
    subject: str
    summary: str
    session_id: str
    in_reply_to: str | None = None
    references: str | None = None


def _smtp_config() -> SmtpConfig:
    if not settings.mail_smtp_host:
        raise HTTPException(status_code=501, detail={"error": "smtp_unconfigured"})
    return SmtpConfig(
        host=settings.mail_smtp_host,
        port=settings.mail_smtp_port,
        username=settings.mail_smtp_user,
        password=settings.mail_smtp_password,
        from_address=settings.mail_inbox_address or settings.mail_smtp_user,
    )


def _session_link(session_id: str) -> str:
    return f"/sessions/{session_id}"


async def create_session_from_message(message: InboundMessage) -> dict[str, str]:
    if not sender_allowed(message.sender, settings.mail_allowed_senders):
        raise HTTPException(status_code=403, detail={"error": "sender_not_allowed"})
    session = await create_session(SessionCreateRequest())
    return {"session_id": session.session_id, "title": message.subject, "prompt": message.body}


@router.get("/status", response_model=MailStatus)
async def mail_status() -> MailStatus:
    allowed = [item.strip() for item in settings.mail_allowed_senders.split(",") if item.strip()]
    return MailStatus(
        inbound_configured=bool(settings.mail_imap_host and settings.mail_imap_user and settings.mail_allowed_senders),
        outbound_configured=bool(settings.mail_smtp_host and settings.mail_inbox_address),
        allowed_senders=allowed,
    )


@router.post("/inbound")
async def inbound_mail(request: InboundMailRequest) -> dict[str, str]:
    if request.spam:
        return {"status": "skipped_spam"}
    message = InboundMessage(
        sender=str(request.sender),
        subject=request.subject,
        body=request.body,
        message_id=request.message_id,
        references=request.references,
        in_reply_to=request.in_reply_to,
    )
    return await create_session_from_message(message)


@router.post("/reply")
async def outbound_reply(request: OutboundReplyRequest) -> dict[str, Any]:
    body = f"{request.summary}\n\nSession: {_session_link(request.session_id)}"
    send_thread_reply(
        _smtp_config(),
        to_address=str(request.to),
        subject=request.subject,
        body=body,
        in_reply_to=request.in_reply_to,
        references=request.references,
    )
    return {"sent": True, "session_link": _session_link(request.session_id)}
