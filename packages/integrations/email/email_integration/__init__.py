from __future__ import annotations

from email_integration.imap_watcher import InboundMessage, parse_message, sender_allowed, spam_flagged
from email_integration.smtp_sender import SmtpConfig, send_thread_reply

__all__ = ["InboundMessage", "SmtpConfig", "parse_message", "sender_allowed", "send_thread_reply", "spam_flagged"]
