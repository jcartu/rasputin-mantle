from __future__ import annotations


class BrowserNotAvailable(Exception):
    pass


class BrowserActionError(Exception):
    pass


class ElementNotFoundError(BrowserActionError):
    pass
