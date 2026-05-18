from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    bind_host: str = field(
        default_factory=lambda: "127.0.0.1" if os.environ.get("MANTLE_PUBLIC") != "true" else "0.0.0.0"
    )
    bind_port: int = int(os.environ.get("MANTLE_PORT", "8000"))
    skills_dir: str = os.environ.get("MANTLE_SKILLS_DIR", "skills")
    sandbox_backend: str = os.environ.get("MANTLE_SANDBOX_BACKEND", "docker")
    files_root: str = os.environ.get("MANTLE_FILES_ROOT", "/workspace")
    kb_root: str = os.environ.get("MANTLE_KB_ROOT", "/workspace/projects")
    max_cost_dollars: float = float(os.environ.get("MANTLE_MAX_COST", "40.0"))
    max_cost_tokens: int = int(os.environ.get("MANTLE_MAX_TOKENS", "1000000"))
    debug: bool = os.environ.get("MANTLE_DEBUG", "false").lower() == "true"
    rasputin_url: str = os.environ.get("RASPUTIN_URL", "http://127.0.0.1:7777")
    rasputin_token: str = os.environ.get("RASPUTIN_TOKEN", "")
    vllm_base_url: str = os.environ.get("VLLM_BASE_URL", "")
    vllm_model: str = os.environ.get("VLLM_MODEL", "qwen3.6-27b")
    vllm_api_key: str = os.environ.get("VLLM_API_KEY", "")
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")
    database_url: str = os.environ.get("DATABASE_URL", "postgresql://mantle:mantle-dev@postgres:5432/mantle")
    redis_url: str = os.environ.get("MANTLE_REDIS_URL", "redis://127.0.0.1:6379/0")
    slack_client_id: str = os.environ.get("SLACK_CLIENT_ID", "")
    slack_client_secret: str = os.environ.get("SLACK_CLIENT_SECRET", "")
    slack_signing_secret: str = os.environ.get("SLACK_SIGNING_SECRET", "")
    slack_redirect_uri: str = os.environ.get("SLACK_REDIRECT_URI", "")
    mail_imap_host: str = os.environ.get("MAIL_IMAP_HOST", "")
    mail_imap_port: int = int(os.environ.get("MAIL_IMAP_PORT", "993"))
    mail_imap_user: str = os.environ.get("MAIL_IMAP_USER", "")
    mail_imap_password: str = os.environ.get("MAIL_IMAP_PASSWORD", "")
    mail_allowed_senders: str = os.environ.get("MAIL_ALLOWED_SENDERS", "")
    mail_inbox_address: str = os.environ.get("MAIL_INBOX_ADDRESS", "")
    mail_smtp_host: str = os.environ.get("MAIL_SMTP_HOST", "")
    mail_smtp_port: int = int(os.environ.get("MAIL_SMTP_PORT", "587"))
    mail_smtp_user: str = os.environ.get("MAIL_SMTP_USER", "")
    mail_smtp_password: str = os.environ.get("MAIL_SMTP_PASSWORD", "")


settings = Settings()
