from __future__ import annotations

from datetime import datetime
from typing import Any


def clean_rows(rows: list[dict[str, Any]], schema: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    seen: set[tuple[tuple[str, str], ...]] = set()
    cleaned: list[dict[str, Any]] = []
    type_map = {str(col.get("name")): str(col.get("type") or "text") for col in schema or []}
    for row in rows:
        normalized = {_normalize_key(key): _coerce(value, type_map.get(str(key), "text")) for key, value in row.items()}
        signature = tuple(sorted((key, str(value)) for key, value in normalized.items()))
        if signature in seen:
            continue
        seen.add(signature)
        cleaned.append(normalized)
    return cleaned


def _normalize_key(key: Any) -> str:
    return str(key).strip().lower().replace(" ", "_").replace("-", "_")


def _coerce(value: Any, value_type: str) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
    if value_type in {"number", "float", "currency", "percent"}:
        try:
            return float(str(value).replace(",", "").replace("$", "").replace("%", ""))
        except ValueError:
            return value
    if value_type in {"integer", "int"}:
        try:
            return int(float(str(value).replace(",", "")))
        except ValueError:
            return value
    if value_type in {"date", "datetime"}:
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d %b %Y"):
            try:
                return datetime.strptime(str(value), fmt).date().isoformat()
            except ValueError:
                continue
    return value
