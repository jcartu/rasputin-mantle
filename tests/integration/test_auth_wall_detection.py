"""tests/integration/test_auth_wall_detection.py — Verify LoginWallDetector covers LOGIN_WALL failures.

Tests the 9 LOGIN_WALL sites from V1.1 failure report:
LinkedIn, X/Twitter, Pinterest, Medium, Booking.com, Khan Academy.
"""
from __future__ import annotations

from browser.auth import LoginWallDetector
from browser.types import BrowserElement


def _elements(*items: tuple[str, str | None]) -> list[BrowserElement]:
    """Helper: create BrowserElement list from (role, text) tuples."""
    return [
        BrowserElement(id=f"el-{i}", role=role, text=text)
        for i, (role, text) in enumerate(items)
    ]


class TestLoginWallDetection:
    """Test LoginWallDetector against real LOGIN_WALL patterns."""

    def test_linkedin_login_redirect(self) -> None:
        """LinkedIn redirects to login — URL pattern + DOM text."""
        detector = LoginWallDetector()
        signal = detector.detect(
            url="https://www.linkedin.com/login?session_redirect=https%3A%2F%2Fwww.linkedin.com%2Fcompany%2Fmicrosoft",
            title="Sign in to LinkedIn",
            elements=_elements(
                ("textbox", "Email or phone"),
                ("textbox", "Password"),
                ("button", "Sign in"),
                ("link", "Forgot password?"),
                ("link", "Join now"),
            ),
        )
        assert signal is not None
        assert signal.wall_type == "login_form"
        assert signal.confidence >= 0.6

    def test_x_twitter_auth_wall(self) -> None:
        """X (Twitter) blocks public content behind login."""
        detector = LoginWallDetector()
        signal = detector.detect(
            url="https://x.com/login?redirect_after_login=%2FOpenAI",
            title="Sign in to X",
            elements=_elements(
                ("textbox", "Phone, email, or username"),
                ("textbox", "Password"),
                ("button", "Log in"),
                ("button", "Sign up"),
                ("link", "Forgot password"),
            ),
        )
        assert signal is not None
        assert signal.wall_type == "login_form"

    def test_pinterest_auth_required(self) -> None:
        """Pinterest requires login to browse boards."""
        detector = LoginWallDetector()
        signal = detector.detect(
            url="https://www.pinterest.com/login/?next=/boards/minimalist-home-office",
            title="Log in - Pinterest",
            elements=_elements(
                ("textbox", "Email"),
                ("textbox", "Password"),
                ("button", "Log in"),
                ("link", "Sign up"),
                ("link", "Forgot email or password?"),
            ),
        )
        assert signal is not None
        assert signal.wall_type == "login_form"

    def test_medium_paywall(self) -> None:
        """Medium paywall blocks article content."""
        detector = LoginWallDetector()
        signal = detector.detect(
            url="https://medium.com/@author/machine-learning-article-abc123",
            title="Machine Learning Article — Medium",
            elements=_elements(
                ("heading", "Start writing. Connect with your audience."),
                ("button", "Subscribe"),
                ("button", "Sign up for Medium"),
                ("text", "This article is locked for non-members"),
                ("text", "Get unlimited access to the best of Medium"),
            ),
        )
        assert signal is not None
        assert signal.wall_type == "paywall"

    def test_booking_com_bot_detection(self) -> None:
        """Booking.com shows bot detection / CAPTCHA."""
        detector = LoginWallDetector()
        signal = detector.detect(
            url="https://www.booking.com/security/challenge/verify",
            title="Please verify you are human",
            elements=_elements(
                ("text", "Please verify you are human before continuing"),
                ("text", "Security check"),
                ("button", "Verify"),
            ),
        )
        assert signal is not None
        assert signal.wall_type == "bot_detection"

    def test_khan_academy_account_required(self) -> None:
        """Khan Academy blocks content behind account wall."""
        detector = LoginWallDetector()
        signal = detector.detect(
            url="https://www.khanacademy.org/login?next=/math/sat",
            title="Log in | Khan Academy",
            elements=_elements(
                ("textbox", "Email address"),
                ("textbox", "Password"),
                ("button", "Log in"),
                ("link", "Create an account"),
                ("link", "Forgot password?"),
            ),
        )
        assert signal is not None
        assert signal.wall_type == "login_form"

    def test_no_auth_wall_on_normal_page(self) -> None:
        """Normal pages should NOT trigger auth wall detection."""
        detector = LoginWallDetector()
        signal = detector.detect(
            url="https://en.wikipedia.org/wiki/Tokyo",
            title="Tokyo - Wikipedia",
            elements=_elements(
                ("link", "Main page"),
                ("link", "Contents"),
                ("link", "History"),
                ("link", "Geography"),
                ("heading", "Tokyo"),
                ("text", "Tokyo is the capital of Japan"),
            ),
        )
        assert signal is None

    def test_no_auth_wall_on_reddit(self) -> None:
        """Reddit browsing page should NOT trigger auth wall."""
        detector = LoginWallDetector()
        signal = detector.detect(
            url="https://www.reddit.com/r/python/",
            title="Python Programming - Reddit",
            elements=_elements(
                ("link", "Python Programming"),
                ("link", "Post 1"),
                ("link", "Post 2"),
                ("button", "Create Post"),
                ("link", "Top"),
                ("link", "New"),
            ),
        )
        assert signal is None

    def test_url_only_login_pattern(self) -> None:
        """URL alone can trigger detection (e.g., redirect-after-login)."""
        detector = LoginWallDetector(threshold=0.3)
        signal = detector.detect(
            url="https://example.com/login?next=/dashboard",
            title="Login",
            elements=[],
        )
        assert signal is not None
        assert signal.wall_type == "login_form"

    def test_bot_detection_text_only(self) -> None:
        """Bot detection text in DOM triggers detection."""
        detector = LoginWallDetector()
        signal = detector.detect(
            url="https://example.com/page",
            title="Checking your browser",
            elements=_elements(
                ("text", "Checking your browser before accessing"),
                ("text", "This process is automatic. Your browser will redirect"),
                ("text", "Please stand by"),
            ),
        )
        assert signal is not None
        assert signal.wall_type == "bot_detection"

    def test_paywall_text_patterns(self) -> None:
        """Paywall text patterns trigger detection."""
        detector = LoginWallDetector()
        signal = detector.detect(
            url="https://example.com/article/123",
            title="Premium Article",
            elements=_elements(
                ("heading", "This article has 2 stories remaining"),
                ("button", "Subscribe now"),
                ("text", "Premium member content"),
            ),
        )
        assert signal is not None
        assert signal.wall_type == "paywall"

    def test_account_required_text(self) -> None:
        """Account required text triggers detection."""
        detector = LoginWallDetector()
        signal = detector.detect(
            url="https://example.com/restricted",
            title="Access Restricted",
            elements=_elements(
                ("text", "You must be logged in to view this content"),
                ("button", "Sign in to continue"),
                ("link", "Create an account to access"),
            ),
        )
        assert signal is not None
        assert signal.wall_type in ("account_required", "login_form")

    def test_low_threshold_allows_weak_signals(self) -> None:
        """Lowering threshold allows weaker signals to pass."""
        detector = LoginWallDetector(threshold=0.2)
        signal = detector.detect(
            url="https://example.com/page",
            title="Page",
            elements=_elements(
                ("button", "Sign in"),
            ),
        )
        # Single login button should pass at low threshold
        assert signal is not None

    def test_high_threshold_blocks_weak_signals(self) -> None:
        """High threshold blocks weak signals."""
        detector = LoginWallDetector(threshold=0.9)
        signal = detector.detect(
            url="https://example.com/page",
            title="Page",
            elements=_elements(
                ("button", "Sign in"),
            ),
        )
        assert signal is None

    def test_evidence_contains_description(self) -> None:
        """AuthWallSignal.evidence contains human-readable explanation."""
        detector = LoginWallDetector()
        signal = detector.detect(
            url="https://www.linkedin.com/login",
            title="Sign in to LinkedIn",
            elements=_elements(
                ("textbox", "Email or phone"),
                ("textbox", "Password"),
                ("button", "Sign in"),
            ),
        )
        assert signal is not None
        assert len(signal.evidence) > 0
        assert "login" in signal.evidence.lower() or "pattern" in signal.evidence.lower()
