from __future__ import annotations

import json
import sys


def main() -> None:
    data = json.loads(sys.stdin.read() or "{}")
    topic = data.get("topic", "weekly news")
    items = data.get("items") or []
    print(f"# Weekly digest: {topic}\n")
    print("## Top themes\n- Theme 1\n- Theme 2\n- Theme 3\n")
    print("## Notable items")
    if items:
        for item in items:
            print(f"- {item}")
    else:
        print("- Add headline, source, impact, and link.")
    print("\n## Why it matters\n- Summarize stakeholder impact.\n\n## Recommended actions\n- Monitor follow-up coverage.")


if __name__ == "__main__":
    main()
