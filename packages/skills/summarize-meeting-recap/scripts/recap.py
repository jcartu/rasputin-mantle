from __future__ import annotations

import json
import sys


def main() -> None:
    data = json.loads(sys.stdin.read() or "{}")
    attendees = data.get("attendees") or []
    notes = str(data.get("notes", "")).strip()
    print("# Meeting recap\n")
    if attendees:
        print("Attendees: " + ", ".join(attendees) + "\n")
    print("## Summary\n" + (notes[:500] if notes else "Add concise meeting summary here."))
    print("\n## Decisions\n- Decision: TBD")
    print("\n## Action items\n| Owner | Task | Due |\n|---|---|---|\n| TBD | TBD | TBD |")
    print("\n## Risks / blockers\n- TBD")


if __name__ == "__main__":
    main()
