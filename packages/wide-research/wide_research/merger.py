from __future__ import annotations

from collections import OrderedDict
from typing import Any


def _score(row: dict[str, Any]) -> float:
    rank = int(row.get("rank") or 99)
    snippet_len = len(str(row.get("snippet", "")))
    title_len = len(str(row.get("title", "")))
    return (100 - rank * 10) + min(snippet_len, 500) / 50 + min(title_len, 120) / 120


def merge_results(results: list[dict[str, Any]]) -> str:
    """Deduplicate search rows by URL, rank them, and format markdown."""

    deduped: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for row in results:
        url = str(row.get("url", "")).strip()
        if not url:
            continue
        current = deduped.get(url)
        if current is None or _score(row) > _score(current):
            deduped[url] = row

    ranked = sorted(deduped.values(), key=_score, reverse=True)
    if not ranked:
        return "## Wide Research Results\n\nNo search results were returned."

    lines = ["## Wide Research Results", ""]
    for index, row in enumerate(ranked, start=1):
        title = str(row.get("title") or "Untitled").strip()
        url = str(row.get("url") or "").strip()
        snippet = str(row.get("snippet") or "").strip()
        agent_id = row.get("agent_id", "?")
        sub_query = str(row.get("sub_query") or "").strip()
        lines.append(f"{index}. [{title}]({url})")
        lines.append(f"   - Agent: {agent_id}; query: `{sub_query}`")
        if snippet:
            lines.append(f"   - {snippet}")
    return "\n".join(lines)
