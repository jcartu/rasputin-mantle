from __future__ import annotations

import json
import sys


def main() -> None:
    data = json.loads(sys.stdin.read() or "{}")
    audience = data.get("audience", "operators")
    metrics = data.get("metrics") or ["active users", "conversion", "errors", "latency"]
    actions = data.get("actions") or ["export CSV", "assign owner", "open detail"]
    print(f"# Internal dashboard spec for {audience}\n")
    print("## KPI cards\n" + "\n".join(f"- {metric}" for metric in metrics))
    print("\n## Controls\n- Date range\n- Owner/team filter\n- Status filter")
    print("\n## Row actions\n" + "\n".join(f"- {action}" for action in actions))
    print("\n## Permissions\n- Viewer: read-only\n- Operator: row actions\n- Admin: configuration")


if __name__ == "__main__":
    main()
