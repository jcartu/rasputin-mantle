---
name: document
description: Create polished DOCX and PDF documents from structured outlines with styles, tables, images, and automatic TOCs.
when_to_use: Invoke when a user needs a downloadable report, memo, proposal, whitepaper, or PDF/DOCX document from an outline.
capability: document
version: 1.0.0
license: MIT
author: Mantle
metadata:
  tags:
    - productivity
    - document
    - docx
    - pdf
---

# Document

Use this skill to generate `.docx`, `.pdf`, or both in `/workspace/<task>/`.

## Input

```json
{
  "task": "session-or-task-name",
  "formats": ["docx", "pdf"],
  "style": "business",
  "outline": {
    "title": "Launch Plan",
    "sections": [
      {"heading": "Summary", "paragraphs": ["One paragraph."], "tables": []}
    ]
  }
}
```

Styles: `minimal`, `academic`, `business`. Documents with more than five sections receive a table of contents.
