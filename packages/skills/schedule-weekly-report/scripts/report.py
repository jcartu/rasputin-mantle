from __future__ import annotations

import json
import sys


def main() -> None:
    data = json.loads(sys.stdin.read() or "{}")
    audience = data.get("audience", "stakeholders")
    weekday = data.get("weekday", "Friday")
    metrics = data.get("metrics") or ["progress", "risks", "next milestones"]
    print(f"# Weekly report routine for {audience}\n")
    print(f"Cadence: every {weekday}\n")
    print("## Sections\n- Executive summary\n- Progress since last report\n- Metrics\n- Risks and asks\n- Next week")
    print("\n## Metrics\n" + "\n".join(f"- {metric}" for metric in metrics))


if __name__ == "__main__":
    main()
