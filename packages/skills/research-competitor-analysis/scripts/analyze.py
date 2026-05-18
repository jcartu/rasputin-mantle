from __future__ import annotations

import json
import sys


def main() -> None:
    data = json.loads(sys.stdin.read() or "{}")
    topic = data.get("topic", "the target market")
    competitors = data.get("competitors") or ["Competitor A", "Competitor B", "Competitor C"]
    criteria = data.get("criteria") or ["positioning", "features", "pricing", "distribution", "risks"]
    print(f"# Competitor analysis: {topic}\n")
    print("| Competitor | " + " | ".join(criteria) + " |")
    print("|---" * (len(criteria) + 1) + "|")
    for competitor in competitors:
        print(f"| {competitor} | " + " | ".join("TBD" for _ in criteria) + " |")
    print("\n## Differentiation hypotheses\n- Identify underserved use cases.\n- Compare switching costs.\n- Validate pricing gaps.")


if __name__ == "__main__":
    main()
