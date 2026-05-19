---
name: slides
description: Create real PowerPoint presentations with templates, speaker notes, images, and charts.
when_to_use: Invoke when a user needs a downloadable slide deck, pitch deck, research presentation, or meeting presentation from an outline.
capability: presentation
version: 1.0.0
license: MIT
author: Mantle
metadata:
  tags:
    - productivity
    - presentation
    - pptx
---

# Slides

Use this skill to turn a structured outline into `/workspace/<task>/slides.pptx`.

## Input

`scripts/slides.py` reads JSON from stdin:

```json
{
  "task": "session-or-task-name",
  "template": "minimal",
  "outline": {
    "title": "Quarterly Plan",
    "sections": [
      {"title": "Goals", "bullets": ["Ship W7", "Measure productivity"], "notes": "Emphasize outcomes."}
    ]
  }
}
```

Templates: `minimal`, `corporate`, `pitch`, `research`.

Sections may include `bullets`, `notes`, `images` (URL or sandbox file path), and `chart` definitions. Chart data is rendered with matplotlib and embedded as an image.

## Output

The script emits JSON including the generated `path`, `slide_count`, and selected `template`.
