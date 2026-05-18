from __future__ import annotations

import json
import sys


def main() -> None:
    data = json.loads(sys.stdin.read() or "{}")
    team = data.get("team", "the team")
    time = data.get("time", "09:30")
    timezone = data.get("timezone", "local time")
    print(f"# Daily standup routine for {team}\n")
    print(f"Schedule: every weekday at {time} {timezone}\n")
    print("## Agenda\n1. Yesterday\n2. Today\n3. Blockers\n4. Help needed")
    print("\n## Reminder\nPlease post your standup before the meeting: yesterday, today, blockers.")


if __name__ == "__main__":
    main()
