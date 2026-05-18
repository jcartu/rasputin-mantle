#!/usr/bin/env python3
"""scripts/compute_per_category.py — Compute per-category and per-source breakdowns from WV-300 results."""
from __future__ import annotations
import json
import sys
from collections import defaultdict
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: python compute_per_category.py <results.json> [output_dir]")
        sys.exit(1)

    results_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else results_file.parent

    with open(results_file) as f:
        data = json.load(f)

    results = data.get("results", [])
    total = len(results)
    passed = sum(1 for r in results if r.get("passed"))

    # Per-source
    by_source = defaultdict(lambda: {"passed": 0, "total": 0})
    for r in results:
        src = r.get("source", "original")
        by_source[src]["total"] += 1
        if r.get("passed"):
            by_source[src]["passed"] += 1

    # Per-category
    by_category = defaultdict(lambda: {"passed": 0, "total": 0})
    for r in results:
        cat = r.get("category_hint", "UNCLASSIFIED") or "UNCLASSIFIED"
        by_category[cat]["total"] += 1
        if r.get("passed"):
            by_category[cat]["passed"] += 1

    # Build output
    per_source = {}
    for src, counts in sorted(by_source.items()):
        rate = counts["passed"] / counts["total"] if counts["total"] else 0
        per_source[src] = {
            "passed": counts["passed"],
            "total": counts["total"],
            "rate": round(rate, 4),
        }

    per_category = {}
    for cat, counts in sorted(by_category.items()):
        rate = counts["passed"] / counts["total"] if counts["total"] else 0
        per_category[cat] = {
            "passed": counts["passed"],
            "total": counts["total"],
            "rate": round(rate, 4),
        }

    # Print summary
    print(f"\n=== {results_file.name} ===")
    print(f"Overall: {passed}/{total} = {passed/total:.2%}")
    print(f"\nPer-Source:")
    for src, info in per_source.items():
        print(f"  {src}: {info['passed']}/{info['total']} = {info['rate']:.2%}")
    print(f"\nPer-Category:")
    for cat, info in per_category.items():
        print(f"  {cat}: {info['passed']}/{info['total']} = {info['rate']:.2%}")

    # Write outputs
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "per-source-final.json").write_text(json.dumps(per_source, indent=2))
    (output_dir / "per-category-final.json").write_text(json.dumps(per_category, indent=2))
    print(f"\nWritten to {output_dir}/")


if __name__ == "__main__":
    main()
