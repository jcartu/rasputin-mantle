#!/usr/bin/env python3
"""scripts/convert-baseline.py — convert v1.0 baseline to categorizer-compatible format.

The v1.0 baseline stores `steps` as an integer and `success` as the pass/fail flag.
The categorizer expects `steps` as a list of dicts and `passed` as the flag.

Usage:
    python scripts/convert-baseline.py \\
        --input outputs/multi-model/gpt-5-5.json \\
        --output outputs/v1_1/webvoyager-100-baseline.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to v1.0 baseline JSON")
    ap.add_argument("--output", required=True, help="Path to write converted baseline")
    args = ap.parse_args()

    raw = json.loads(Path(args.input).read_text())
    results = raw.get("results", raw.get("responses", []))

    converted = []
    for r in results:
        converted.append({
            "id": r["id"],
            "passed": r.get("success", r.get("passed", False)),
            "final_answer": r.get("answer", r.get("final_answer", "")),
            "agent_response": r.get("answer", r.get("final_answer", "")),
            "error": r.get("error", ""),
            "steps": [],  # v1.0 has no step-level traces
            "duration_s": r.get("duration_s", 0),
        })

    out = {
        "benchmark": "webvoyager",
        "total": raw.get("total", len(results)),
        "passed": raw.get("passed", sum(1 for r in converted if r["passed"])),
        "failed": raw.get("total", len(results)) - raw.get("passed", sum(1 for r in converted if r["passed"])),
        "pass_rate": raw.get("pass_rate", 0),
        "model": raw.get("model", ""),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_baseline": args.input,
        "note": "Converted from v1.0 baseline. steps=[] — no trace data available. Re-run with --traces for full traces.",
        "results": converted,
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=2))
    print(f"Wrote {args.output} ({len(converted)} results)")


if __name__ == "__main__":
    main()
