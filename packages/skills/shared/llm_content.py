from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

DEFAULT_VLLM_BASE_URL = "http://127.0.0.1:11435"
DEFAULT_VLLM_MODEL = "qwen3.6-27b"


def generate_content(prompt: str, format_type: str, schema: dict[str, Any]) -> dict[str, Any]:
    """Generate a structured artifact plan from a user prompt and schema.

    The productivity skills call this before falling back to their legacy keyword
    plans. The return value is intentionally generic: each skill normalizes it to
    its own outline/payload shape.
    """
    system_prompt = f"""You are a content generator for {format_type} artifacts.
Given a user prompt and structural schema, generate the content structure.
Use the concrete facts from the prompt. Do not invent unrelated companies or placeholder content.
Return JSON only."""

    shape_instructions = "\n".join(
        [
            '- slides: {"title": string, "subtitle": string, "template": string, '
            '"sections": [{"title": string, "bullets": [string], "notes": string, '
            '"chart": optional {"type": "bar"|"line"|"pie", "title": string, '
            '"labels": [string], "values": [number]}}]}',
            '- document: {"title": string, "style": string, "formats": ["docx"|"pdf"], '
            '"sections": [{"heading": string, "paragraphs": [string], '
            '"tables": optional [{"headers": [string], "rows": [[string|number]]}]}]}',
            '- spreadsheet: {"mode": "table"|"financial_model"|"comparison_matrix"|'
            '"data_cleaning"|"budget", "schema": [{"name": string}], "rows": [object], '
            '"charts": optional [{"type": "bar"|"line", "x": string, "y": string, '
            '"title": string}], "summary": boolean}',
        ]
    )

    user_prompt = f"""Prompt:
{prompt}

Schema:
{json.dumps(schema or {}, indent=2)}

Required JSON shape by artifact type:
{shape_instructions}

Generate the content structure as JSON."""

    try:
        base_url = (
            os.environ.get("MANTLE_CONTENT_VLLM_BASE_URL") or os.environ.get("VLLM_BASE_URL") or DEFAULT_VLLM_BASE_URL
        )
        model = os.environ.get("MANTLE_CONTENT_VLLM_MODEL") or DEFAULT_VLLM_MODEL
        request_body = json.dumps(
            {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0,
                "max_tokens": 4000,
                "chat_template_kwargs": {"enable_thinking": False},
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            f"{base_url.rstrip('/')}/v1/chat/completions",
            data=request_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=20) as response:  # noqa: S310 - local/self-hosted model endpoint
            response_payload = json.loads(response.read().decode("utf-8"))
        message = response_payload["choices"][0]["message"]
        content = message.get("content") or message.get("reasoning") or ""
        parsed = _parse_json_object(str(content))
        return parsed if isinstance(parsed, dict) else _empty_structure()
    except Exception:
        return _empty_structure()


def _parse_json_object(content: str) -> Any:
    content = _strip_thinking(content).strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.IGNORECASE)
        content = re.sub(r"\s*```$", "", content).strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        parsed_objects: list[Any] = []
        for match in re.finditer(r"\{", content):
            try:
                parsed, _ = decoder.raw_decode(content[match.start() :])
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                parsed_objects.append(parsed)
        if parsed_objects:
            combined = _combine_sheet_fragments(parsed_objects)
            if combined is not None:
                return combined
            return max(parsed_objects, key=lambda item: len(json.dumps(item)))
        raise


def _strip_thinking(content: str) -> str:
    return re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE)


def _combine_sheet_fragments(objects: list[dict[str, Any]]) -> dict[str, Any] | None:
    largest = max(objects, key=lambda item: len(json.dumps(item)))
    if any(key in largest for key in ("mode", "rows", "sheets", "sections")):
        return None

    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in objects:
        sheet = item.get("sheet") or item.get("sheet_name")
        if not sheet:
            continue
        row = item.get("data") or item.get("cells") or item.get("cell_data")
        if not isinstance(row, dict):
            row = {
                key: value
                for key, value in item.items()
                if key not in {"sheet", "sheet_name", "row_id", "row_type", "notes", "formula_type", "formulas_used"}
            }
        if row:
            grouped.setdefault(str(sheet), []).append(row)
    if sum(len(rows) for rows in grouped.values()) < 2:
        return None
    return {"rows": [{"sheet": name, "data": rows} for name, rows in grouped.items()]}


def _empty_structure() -> dict[str, Any]:
    return {"slides": [], "sheets": [], "sections": []}
