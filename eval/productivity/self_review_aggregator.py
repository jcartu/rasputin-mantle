from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "outputs" / "v1_3_2" / "self-review-stats.json"


def aggregate_stdout(text: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        records.extend(_extract_reviews(payload))
    return records


def write_stats(records: list[dict[str, Any]], output_path: Path = DEFAULT_OUTPUT) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def _extract_reviews(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [record for item in payload for record in _extract_reviews(item)]
    if not isinstance(payload, dict):
        return []

    reviews: list[dict[str, Any]] = []
    review = payload.get("self_review")
    if isinstance(review, list):
        reviews.extend(_normalize_review(item, payload) for item in review if isinstance(item, dict))
    elif isinstance(review, dict):
        reviews.append(_normalize_review(review, payload))

    for value in payload.values():
        if isinstance(value, (dict, list)):
            reviews.extend(_extract_reviews(value))
    return reviews


def _normalize_review(review: dict[str, Any], parent: dict[str, Any]) -> dict[str, Any]:
    artifact_id = (
        review.get("artifact_id") or parent.get("id") or parent.get("path") or parent.get("paths") or "artifact"
    )
    if isinstance(artifact_id, list):
        artifact_id = artifact_id[0] if artifact_id else "artifact"
    return {
        "artifact_id": str(artifact_id),
        "iterations_used": int(review.get("iterations_used") or 0),
        "issues_found": int(review.get("issues_found") or 0),
        "issues_resolved": int(review.get("issues_resolved") or 0),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate productivity self-review telemetry from task stdout.")
    parser.add_argument("inputs", nargs="*", help="Files containing task stdout JSON lines. Reads stdin when omitted.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    chunks = [Path(path).read_text(encoding="utf-8") for path in args.inputs] if args.inputs else [sys.stdin.read()]
    records = [record for chunk in chunks for record in aggregate_stdout(chunk)]
    write_stats(records, Path(args.output))
    print(json.dumps({"count": len(records), "output": str(Path(args.output))}))


if __name__ == "__main__":
    main()
