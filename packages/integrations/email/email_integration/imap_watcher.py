from __future__ import annotations

import asyncio
import email
import imaplib
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from email.message import Message
from email.utils import parseaddr


@dataclass(frozen=True)
class InboundMessage:
    sender: str
    subject: str
    body: str
    message_id: str | None
    references: str | None
    in_reply_to: str | None


def sender_allowed(sender: str, allowlist: str) -> bool:
    allowed = [item.strip().lower() for item in allowlist.split(",") if item.strip()]
    if not allowed:
        return False
    _, address = parseaddr(sender)
    address = address.lower()
    domain = address.rsplit("@", 1)[-1] if "@" in address else ""
    return address in allowed or domain in allowed or f"@{domain}" in allowed


def spam_flagged(message: Message) -> bool:
    return message.get("X-Spam-Flag", "").strip().upper() == "YES"


def _plain_body(message: Message) -> str:
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition", "")):
                payload = part.get_payload(decode=True) or b""
                return payload.decode(part.get_content_charset() or "utf-8", errors="replace").strip()
        return ""
    payload = message.get_payload(decode=True) or b""
    return payload.decode(message.get_content_charset() or "utf-8", errors="replace").strip()


def parse_message(raw: bytes) -> InboundMessage | None:
    parsed = email.message_from_bytes(raw)
    if spam_flagged(parsed):
        return None
    return InboundMessage(
        sender=parseaddr(parsed.get("From", ""))[1],
        subject=str(parsed.get("Subject", "")).strip() or "Untitled email task",
        body=_plain_body(parsed),
        message_id=parsed.get("Message-ID"),
        references=parsed.get("References"),
        in_reply_to=parsed.get("In-Reply-To"),
    )


async def watch_inbox(
    host: str,
    port: int,
    username: str,
    password: str,
    allowlist: str,
    callback: Callable[[InboundMessage], Awaitable[None]],
    mailbox: str = "INBOX",
    poll_seconds: float = 30.0,
) -> None:
    seen: set[bytes] = set()

    def poll() -> list[InboundMessage]:
        messages: list[InboundMessage] = []
        with imaplib.IMAP4_SSL(host, port) as client:
            client.login(username, password)
            client.select(mailbox)
            _, data = client.search(None, "UNSEEN")
            for message_id in data[0].split():
                if message_id in seen:
                    continue
                seen.add(message_id)
                _, fetched = client.fetch(message_id, "(RFC822)")
                raw = fetched[0][1] if fetched and isinstance(fetched[0], tuple) else None
                if not isinstance(raw, bytes):
                    continue
                message = parse_message(raw)
                if message and sender_allowed(message.sender, allowlist):
                    messages.append(message)
        return messages

    while True:
        for message in await asyncio.to_thread(poll):
            await callback(message)
        await asyncio.sleep(poll_seconds)
