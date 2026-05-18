from __future__ import annotations

import argparse
import base64
import io
import json
import os
import textwrap
import urllib.request
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

CANVAS_SIZE = (1200, 630)
DEFAULT_OUTPUT_DIR = Path("outputs/v1_3/og-images")


def fetch_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=15) as response:  # noqa: S310 - operator supplied gateway URL
        return json.loads(response.read().decode("utf-8"))


def payload_data(step: dict[str, Any]) -> dict[str, Any]:
    payload = step.get("payload")
    if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
        return payload["data"]
    return {}


def final_screenshot(steps: list[dict[str, Any]]) -> str | None:
    for step in reversed(steps):
        data = payload_data(step)
        for key in ("src", "screenshot", "screenshot_url", "url"):
            value = data.get(key)
            if isinstance(value, str) and value:
                return value
    return None


def load_image(source: str | None) -> Image.Image:
    if not source:
        return Image.new("RGB", CANVAS_SIZE, (11, 15, 25))
    if source.startswith("data:image"):
        _, encoded = source.split(",", 1)
        return Image.open(io.BytesIO(base64.b64decode(encoded))).convert("RGB")
    if source.startswith("http://") or source.startswith("https://"):
        with urllib.request.urlopen(source, timeout=15) as response:  # noqa: S310 - replay screenshot URL
            return Image.open(io.BytesIO(response.read())).convert("RGB")
    return Image.open(source).convert("RGB")


def caption_from_share(share: dict[str, Any]) -> str:
    final_answer = share.get("final_answer")
    if isinstance(final_answer, str) and final_answer.strip():
        return final_answer.strip().replace("\n", " ")[:80].rstrip(" .")
    return "Rasputin Mantle agent replay"


def fit_cover(image: Image.Image) -> Image.Image:
    width, height = image.size
    scale = max(CANVAS_SIZE[0] / width, CANVAS_SIZE[1] / height)
    resized = image.resize((round(width * scale), round(height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - CANVAS_SIZE[0]) // 2
    top = (resized.height - CANVAS_SIZE[1]) // 2
    return resized.crop((left, top, left + CANVAS_SIZE[0], top + CANVAS_SIZE[1]))


def font(size: int) -> ImageFont.ImageFont:
    font_paths = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    for path in font_paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def composite(screenshot: Image.Image, caption: str) -> Image.Image:
    canvas = fit_cover(screenshot).convert("RGBA")
    overlay = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(CANVAS_SIZE[1]):
        alpha = int(max(0, (y - 280) / (CANVAS_SIZE[1] - 280)) * 225)
        draw.line([(0, y), (CANVAS_SIZE[0], y)], fill=(0, 0, 0, alpha))
    canvas.alpha_composite(overlay)

    draw = ImageDraw.Draw(canvas)
    title_font = font(46)
    small_font = font(28)
    wrapped = "\n".join(textwrap.wrap(caption, width=38)[:2])
    draw.text((48, 470), "Public replay", fill=(220, 225, 235, 210), font=small_font)
    draw.text((48, 510), wrapped, fill=(255, 255, 255, 255), font=title_font, spacing=6)

    logo_x, logo_y = 966, 532
    draw.rounded_rectangle((logo_x, logo_y, 1152, 592), radius=18, fill=(11, 15, 25, 196), outline=(255, 255, 255, 45))
    draw.rounded_rectangle((logo_x + 16, logo_y + 13, logo_x + 50, logo_y + 47), radius=10, fill=(126, 231, 213, 255))
    draw.text((logo_x + 64, logo_y + 14), "Mantle", fill=(255, 255, 255, 255), font=small_font)
    return canvas.convert("RGB")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Mantle replay OG image.")
    parser.add_argument("session_id")
    parser.add_argument("output", nargs="?", help="Output PNG path")
    parser.add_argument("--gateway", default=os.environ.get("MANTLE_GATEWAY_URL", "http://127.0.0.1:8000"))
    args = parser.parse_args()

    output = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR / f"{args.session_id}.png"
    share = fetch_json(f"{args.gateway.rstrip('/')}/api/share/{args.session_id}")
    image = composite(load_image(final_screenshot(share.get("steps", []))), caption_from_share(share))
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, "PNG")
    print(output)


if __name__ == "__main__":
    main()
