---
name: browser
description: Automate browser interactions with pluggable backends (agent-browser, browser-use). Provides unified API for navigation, element inspection, clicking, typing, and JavaScript evaluation.
version: 1.0.0
author: Mantle
license: MIT
capability: browser_automation
platforms:
  - linux
metadata:
  hermes:
    tags:
      - browser
      - automation
      - web
prerequisites:
  python: ">=3.11"
---

This is a markdown playbook — invoke via bash, not skill_mcp()

## Overview

The `browser` package provides a unified Python API for browser automation with pluggable backend support. It abstracts over multiple browser control implementations (agent-browser, browser-use) and enforces sandbox-on assertion for security.

## Architecture

### BrowserBackend (Abstract Base Class)

The core abstraction for all browser operations:

```python
class BrowserBackend(ABC):
    @abstractmethod
    def open(self, url: str) -> None:
        """Navigate to a URL."""
        ...

    @abstractmethod
    def get_state(self) -> BrowserState:
        """Fetch current page URL and interactive elements.
        
        Returns:
            BrowserState with url (str) and elements (list[BrowserElement])
        """
        ...

    @abstractmethod
    def click(self, element_id: str) -> None:
        """Click an element by ID."""
        ...

    @abstractmethod
    def type(self, element_id: str, text: str) -> None:
        """Type text into an element."""
        ...

    @abstractmethod
    def evaluate(self, script: str) -> Any:
        """Execute JavaScript and return result."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Close the browser."""
        ...
```

### Concrete Implementations

**PlaywrightBackend** (agent-browser CLI wrapper)
- Wraps `agent-browser` command-line tool
- Parses JSON state output
- 30-second command timeout
- Raises `BrowserNotAvailable` if CLI not on PATH

**BrowserUseBackend** (browser-use CLI wrapper)
- Wraps `browser-use` command-line tool
- Parses text-based state output with regex
- 30-second command timeout
- Raises `BrowserNotAvailable` if CLI not on PATH

### Data Types

```python
@dataclass
class BrowserElement:
    id: str                              # Element reference (e.g., "@123")
    role: str                            # Semantic role (button, input, link, etc.)
    text: str | None = None              # Visible text content
    attributes: dict[str, str] = {}      # HTML attributes

@dataclass
class BrowserState:
    url: str                             # Current page URL
    elements: list[BrowserElement]       # Interactive elements on page
```

### Factory

```python
def create_browser_backend(backend: str | None = None) -> BrowserBackend:
    """Create a browser backend instance.
    
    Args:
        backend: "agent-browser" or "browser-use" (default: env MANTLE_BROWSER_BACKEND or "agent-browser")
    
    Returns:
        BrowserBackend instance
    
    Raises:
        BrowserActionError: If backend name is unsupported
    """
```

## Security Assertion

**Sandbox-on is non-negotiable.** The browser package enforces that all browser processes run in isolated sandboxes. No `the unsafe flag` flags are permitted. This is validated at initialization time.

## Example Agent Loop

```python
from browser import create_browser_backend, BrowserActionError

# Create backend (defaults to agent-browser)
backend = create_browser_backend()

try:
    # Navigate
    backend.open("https://example.com")
    
    # Inspect page
    state = backend.get_state()
    print(f"URL: {state.url}")
    for elem in state.elements:
        print(f"  [{elem.id}] {elem.role}: {elem.text}")
    
    # Interact
    backend.click("@42")
    backend.type("@43", "search query")
    
    # Evaluate JavaScript
    result = backend.evaluate("document.title")
    print(f"Title: {result}")
    
finally:
    backend.close()
```

## Error Handling

- `BrowserNotAvailable`: Backend CLI not found on PATH
- `BrowserActionError`: Command execution failed or timed out

## Environment Variables

- `MANTLE_BROWSER_BACKEND`: Default backend name ("agent-browser" or "browser-use")
