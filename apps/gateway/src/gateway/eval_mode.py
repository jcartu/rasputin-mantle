from __future__ import annotations

import os


def is_eval_mode() -> bool:
    """Returns True when MANTLE_EVAL_MODE=1 is set.

    Eval mode disables background work that interferes with benchmark runs:
    - APScheduler background jobs
    - Skill-loader rediscovery
    - Project KB lazy mount on session start
    """
    return os.environ.get("MANTLE_EVAL_MODE", "").lower() in ("1", "true", "yes")
