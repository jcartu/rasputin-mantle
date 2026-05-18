from __future__ import annotations

import json
import sys


def main() -> None:
    data = json.loads(sys.stdin.read() or "{}")
    question = data.get("question", "the research question")
    domains = data.get("domains") or ["scholarly databases", "preprints", "standards bodies"]
    years = data.get("years", "last 5 years")
    print(f"# Literature review plan\n\nQuestion: {question}\n\nScope: {years}\n")
    print("## Sources\n" + "\n".join(f"- {domain}" for domain in domains))
    print("\n## Extraction fields\n- citation\n- method\n- dataset\n- findings\n- limitations\n- evidence quality")
    print("\n## Synthesis outline\n1. Background\n2. Thematic findings\n3. Methodological disagreements\n4. Gaps and future work")


if __name__ == "__main__":
    main()
