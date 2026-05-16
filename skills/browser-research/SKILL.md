---
name: browser-research
description: "Browse the web, extract content, and synthesize research using CDP-based browser automation."
version: 0.1.0
author: Rasputin Mantle
license: MIT
capability: wide_research
metadata:
  hermes:
    tags: [browser, research, web, crawl, extract, cdp, automation]
---

# Browser Research

Browse the web, extract structured data, and synthesize research findings. Uses CDP-based browser automation (agent-browser or browser-use) through the Mantle sandbox.

This is a markdown playbook — invoke via bash, not skill_mcp().

## When to use

- User asks to research a topic on the web
- User needs to extract data from websites
- User wants to compare products, prices, or information
- User needs multi-source fact-checking

## Stack

| Component | Tool | License | Role |
|-----------|------|---------|------|
| Browser automation | agent-browser | Apache-2.0 | Token-efficient CDP control |
| Browser automation | browser-use | MIT | Index-based browser control |

## Workflow

1. Define research query and scope
2. Navigate to target URLs via browser backend
3. Extract page content (text, structured data, tables)
4. Synthesize findings across sources
5. Return structured research report

## Commands

Using agent-browser (default):
```bash
# Open a URL
agent-browser open "https://example.com"

# Get accessible snapshot
agent-browser snapshot -i --json

# Click element by ref
agent-browser click @e1

# Fill form field
agent-browser fill @e2 "search query"
```

Using browser-use:
```bash
# Open a URL
browser-use open "https://example.com"

# Get interactive state
browser-use state

# Click by index
browser-use click 0

# Type into field
browser-use input 1 "search query"
```

## Research patterns

**Multi-source comparison:**
1. Open source A, extract key data
2. Open source B, extract key data
3. Compare and synthesize

**Deep dive:**
1. Start with search results page
2. Click through top 3-5 results
3. Extract relevant sections from each
4. Synthesize into coherent answer

## Constraints

- **No `--no-sandbox` on Chromium. Ever.**
- All browsing happens in sandbox
- Respect robots.txt and rate limits
- Confirm before submitting any forms or clicking "buy"/"subscribe"
- Timeout: 30s per browser command
