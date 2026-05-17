"""packages/browser/browser/auth.py — Login wall detection.

Detects when a page is behind an authentication wall so the agent can
decide to skip, report, or attempt login rather than wasting steps.

Covers: LinkedIn, X/Twitter, Pinterest, Medium, Booking.com, Khan Academy.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from browser.types import BrowserElement

AuthWallType = Literal[
    "login_form",
    "signup_modal",
    "paywall",
    "bot_detection",
    "account_required",
]


@dataclass
class AuthWallSignal:
    """Detected authentication wall."""

    wall_type: AuthWallType
    confidence: float  # 0.0–1.0
    evidence: str  # short human-readable explanation


# Patterns that indicate a login wall
LOGIN_URL_PATTERNS = [
    re.compile(r"/signin", re.I),
    re.compile(r"/login", re.I),
    re.compile(r"/auth", re.I),
    re.compile(r"/account/access", re.I),
    re.compile(r"/session/new", re.I),
    re.compile(r"\?next=", re.I),  # redirect-after-login pattern
]

BOT_DETECTION_URL_PATTERNS = [
    re.compile(r"verify|captcha|robot|bot-detect", re.I),
    re.compile(r"/security/challenge", re.I),
]

# DOM text patterns
LOGIN_TEXT_PATTERNS = [
    re.compile(r"sign\s*in", re.I),
    re.compile(r"log\s*in", re.I),
    re.compile(r"sign\s*up", re.I),
    re.compile(r"create\s*account", re.I),
    re.compile(r"register", re.I),
    re.compile(r"email\s*address", re.I),
    re.compile(r"password", re.I),
    re.compile(r"forgot\s*password", re.I),
    re.compile(r"don't\s*have\s*an\s*account", re.I),
    re.compile(r"already\s*have\s*an\s*account", re.I),
]

PAYWALL_TEXT_PATTERNS = [
    re.compile(r"subscribe", re.I),
    re.compile(r"subscription", re.I),
    re.compile(r"premium\s*member", re.I),
    re.compile(r"membership\s*required", re.I),
    re.compile(r"paywall", re.I),
    re.compile(r"this\s*article\s*has", re.I),
    re.compile(r"stories\s*remaining", re.I),
    re.compile(r"locked\s*for", re.I),
    re.compile(r"limited\s*free", re.I),
]

BOT_DETECTION_TEXT_PATTERNS = [
    re.compile(r"verify\s*you\s*are\s*human", re.I),
    re.compile(r"captcha", re.I),
    re.compile(r"security\s*check", re.I),
    re.compile(r"unusual\s*traffic", re.I),
    re.compile(r"please\s*stand\s*by", re.I),
    re.compile(r"checking\s*your\s*browser", re.I),
]

ACCOUNT_REQUIRED_TEXT_PATTERNS = [
    re.compile(r"account\s*required", re.I),
    re.compile(r"you\s*must\s*be\s*logged\s*in", re.I),
    re.compile(r"please\s*log\s*in\s*to\s*continue", re.I),
    re.compile(r"sign\s*in\s*to\s*continue", re.I),
    re.compile(r"create\s*an\s*account\s*to\s*access", re.I),
    re.compile(r"only\s*for\s*members", re.I),
]


class LoginWallDetector:
    """Detects authentication walls from URL and DOM elements."""

    def __init__(self, threshold: float = 0.6) -> None:
        self.threshold = threshold

    def detect(
        self,
        url: str,
        title: str,
        elements: list[BrowserElement],
    ) -> AuthWallSignal | None:
        """Check if the current page is behind an auth wall.

        Returns AuthWallSignal if confidence >= threshold, else None.
        """
        scores: dict[AuthWallType, tuple[float, str]] = {}

        # URL-based signals
        url_signals = self._check_url(url)
        for stype, evidence in url_signals:
            scores.setdefault(stype, (0.0, ""))
            scores[stype] = (scores[stype][0] + 0.3, evidence)

        # DOM-based signals
        dom_signals = self._check_dom(title, elements)
        for stype, score, evidence in dom_signals:
            scores.setdefault(stype, (0.0, ""))
            scores[stype] = (scores[stype][0] + score, evidence)

        # Pick highest confidence
        if not scores:
            return None

        best_type, (best_score, best_evidence) = max(
            scores.items(), key=lambda x: x[1][0]
        )

        if best_score >= self.threshold:
            return AuthWallSignal(
                wall_type=best_type,
                confidence=min(best_score, 1.0),
                evidence=best_evidence,
            )

        return None

    def _check_url(self, url: str) -> list[tuple[AuthWallType, str]]:
        signals: list[tuple[AuthWallType, str]] = []

        for pattern in LOGIN_URL_PATTERNS:
            if pattern.search(url):
                signals.append(
                    ("login_form", f"URL matches login pattern: {pattern.pattern}")
                )
                break

        for pattern in BOT_DETECTION_URL_PATTERNS:
            if pattern.search(url):
                signals.append(
                    (
                        "bot_detection",
                        f"URL matches bot detection pattern: {pattern.pattern}",
                    )
                )
                break

        return signals

    def _check_dom(
        self, title: str, elements: list[BrowserElement]
    ) -> list[tuple[AuthWallType, float, str]]:
        signals: list[tuple[AuthWallType, float, str]] = []

        # Collect all text from elements
        all_text_parts: list[str] = []
        for el in elements:
            if el.text:
                all_text_parts.append(el.text)
        all_text = " ".join(all_text_parts)

        # Count matching patterns for each category
        login_matches = sum(1 for p in LOGIN_TEXT_PATTERNS if p.search(all_text))
        if login_matches >= 2:
            signals.append(
                (
                    "login_form",
                    0.4 * min(login_matches / 3, 1.0),
                    f"{login_matches} login-related text patterns found in DOM",
                )
            )

        paywall_matches = sum(1 for p in PAYWALL_TEXT_PATTERNS if p.search(all_text))
        if paywall_matches >= 1:
            signals.append(
                (
                    "paywall",
                    0.6 * min(paywall_matches / 2, 1.0),
                    f"{paywall_matches} paywall-related text patterns found in DOM",
                )
            )

        bot_matches = sum(1 for p in BOT_DETECTION_TEXT_PATTERNS if p.search(all_text))
        if bot_matches >= 1:
            signals.append(
                (
                    "bot_detection",
                    0.6 * min(bot_matches / 2, 1.0),
                    f"{bot_matches} bot detection text patterns found in DOM",
                )
            )

        account_matches = sum(
            1 for p in ACCOUNT_REQUIRED_TEXT_PATTERNS if p.search(all_text)
        )
        if account_matches >= 1:
            signals.append(
                (
                    "account_required",
                    0.6 * min(account_matches / 2, 1.0),
                    f"{account_matches} account-required text patterns found in DOM",
                )
            )

        # Check for input fields that suggest a login form
        input_roles = [
            el for el in elements if el.role in ("textbox", "password", "combobox")
        ]
        if len(input_roles) >= 2 and login_matches >= 1:
            signals.append(
                (
                    "login_form",
                    0.3,
                    f"Found {len(input_roles)} input fields alongside login text",
                )
            )

        # Check for submit buttons with login text
        login_buttons = [
            el
            for el in elements
            if el.role == "button"
            and el.text
            and any(p.search(el.text) for p in LOGIN_TEXT_PATTERNS)
        ]
        if login_buttons:
            signals.append(
                (
                    "login_form",
                    0.3,
                    f"Found {len(login_buttons)} login-related button(s)",
                )
            )

        return signals
