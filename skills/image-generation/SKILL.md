---
name: image-generation
description: "Generate images from text prompts using FLUX.2, Z-Image-Turbo, and Stable Diffusion models."
version: 0.1.0
author: Rasputin Mantle
license: MIT
capability: image_generation
metadata:
  hermes:
    tags: [image, generation, flux, diffusion, ai-art, text-to-image]
---

# Image Generation

Generate images from text prompts using open-weight models. Supports FLUX.2 for frontier quality, Z-Image-Turbo for fast bilingual generation, and Stable Diffusion 3.5 for mature ecosystem.

This is a markdown playbook — invoke via bash, not skill_mcp().

## When to use

- User asks to generate an image from a description
- User wants to create artwork, illustrations, or designs
- User needs image variations or style transfers

## Stack

| Component | Tool | License | Role |
|-----------|------|---------|------|
| Frontier quality | FLUX.2 dev | FLUX dev NC | 32B image generation |
| Fast bilingual | Z-Image-Turbo | Apache-2.0 | Quick image gen |
| Mature ecosystem | SD 3.5 Large | Stability Community | SD-based generation |
| Open weight | HiDream-I1 | MIT | Alternative generator |

## Workflow

1. Parse user prompt into generation parameters
2. Select model based on quality/speed tradeoff
3. Generate image in sandbox
4. Return image path or base64 output

## Commands

Generate with FLUX.2 (requires GPU):
```bash
# Clone FLUX repo
git clone https://github.com/black-forest-labs/flux
cd flux
# Run generation script
python generate.py --prompt "your prompt here" --output output.png
```

Generate with Z-Image-Turbo:
```bash
git clone https://github.com/QwenLM/Z-Image
cd Z-Image
python generate.py --prompt "your prompt" --output output.png
```

## Constraints

- Image generation requires GPU in sandbox (check availability first)
- FLUX.2 dev has non-commercial license — verify use case
- Output images stay in sandbox workspace
- **confirm: true** — large model downloads require confirmation
- Respect model license terms (NC vs commercial)
