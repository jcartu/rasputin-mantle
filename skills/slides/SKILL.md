---
name: slides
description: "Generate presentation slides from markdown using Marp, PptxGenJS, and reveal.js."
version: 0.1.0
author: Rasputin Mantle
license: MIT
capability: slides
metadata:
  hermes:
    tags: [slides, presentation, marp, pptx, reveal, deck]
---

# Slides

Generate presentation slides from markdown content. Supports Marp for PDF/HTML output, PptxGenJS for programmatic PPTX, and reveal.js for web-based presentations.

This is a markdown playbook — invoke via bash, not skill_mcp().

## When to use

- User asks to create a presentation or slide deck
- User wants to convert markdown or text into slides
- User needs PPTX, PDF, or HTML slide output

## Stack

| Component | Tool | License | Role |
|-----------|------|---------|------|
| Markdown slides | Marp | MIT | MD to PDF/HTML |
| Programmatic PPTX | PptxGenJS | MIT | JS PPTX generation |
| Web slides | reveal.js | MIT | HTML presentation framework |

## Workflow

1. Extract or generate slide content from user input
2. Choose output format:
   - PDF/HTML → Marp
   - PPTX → PptxGenJS
   - Web presentation → reveal.js
3. Generate slides with proper theming and layout
4. Output to sandbox workspace

## Commands

Generate slides with Marp:
```bash
# Install Marp CLI
npm install -g @marp-team/marp-cli

# Convert markdown to PDF
marp slides.md --pdf --output slides.pdf

# Convert markdown to HTML
marp slides.md --html --output slides.html
```

Generate PPTX with PptxGenJS:
```bash
npm install pptxgenjs
# Run PptxGenJS script in sandbox
node generate-slides.js
```

Create reveal.js presentation:
```bash
# Clone reveal.js template
git clone https://github.com/hakimel/reveal.js
cd reveal.js
# Edit slides in index.html or use markdown plugin
```

## Constraints

- All rendering happens in sandbox
- Confirm before accessing any external URLs for content
- Output files go to sandbox workspace only
