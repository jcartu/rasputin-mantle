from __future__ import annotations

import json
from pathlib import Path

from codeact.skills_loader import invoke_skill
from pptx import Presentation


def test_slides_skill_round_trip(tmp_path: Path) -> None:
    result = invoke_skill(
        "slides",
        {
            "output_dir": str(tmp_path),
            "template": "research",
            "outline": {
                "title": "W7 Research Deck",
                "sections": [
                    {"title": "Method", "bullets": ["Create deck", "Open deck"], "notes": "Explain method."},
                    {
                        "title": "Results",
                        "bullets": ["PPTX opens"],
                        "chart": {"labels": ["Pass", "Fail"], "values": [1, 0]},
                    },
                ],
            },
        },
    )
    assert result.exit_code == 0, result.stderr
    payload = json.loads(result.stdout)
    deck = Path(payload["path"])
    assert deck.exists()
    presentation = Presentation(deck)
    assert len(presentation.slides) == 3
