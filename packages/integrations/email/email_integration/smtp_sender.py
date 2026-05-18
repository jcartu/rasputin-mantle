from __future__ import annotations

import smtplib
from dataclasses import dataclass
from email.mime.text import MIMEText


@dataclass(frozen=True)
class SmtpConfig:
    host: str
    port: int
    username: str
    password: str
    from_address: str
    use_tls: bool = True


def send_thread_reply(
    config: SmtpConfig,
    to_address: str,
    subject: str,
    body: str,
    in_reply_to: str | None = None,
    references: str | None = None,
) -> None:
    message = MIMEText(body, "plain", "utf-8")
    message["From"] = config.from_address
    message["To"] = to_address
    message["Subject"] = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    if in_reply_to:
        message["In-Reply-To"] = in_reply_to
    if references:
        message["References"] = references

    with smtplib.SMTP(config.host, config.port, timeout=15.0) as client:
        if config.use_tls:
            client.starttls()
        if config.username or config.password:
            client.login(config.username, config.password)
        client.sendmail(config.from_address, [to_address], message.as_string())
