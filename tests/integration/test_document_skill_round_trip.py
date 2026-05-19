from __future__ import annotations

import json
from pathlib import Path

from codeact.skills_loader import invoke_skill
from docx import Document


def test_document_skill_round_trip(tmp_path: Path) -> None:
    result = invoke_skill(
        "document",
        {
            "output_dir": str(tmp_path),
            "style": "business",
            "formats": ["docx", "pdf"],
            "outline": {
                "title": "W7 Document",
                "sections": [
                    {"heading": "Summary", "paragraphs": ["The document skill creates files."]},
                    {"heading": "Data", "tables": [{"headers": ["Name", "Value"], "rows": [["A", 1]]}]},
                ],
            },
        },
    )
    assert result.exit_code == 0, result.stderr
    payload = json.loads(result.stdout)
    paths = [Path(path) for path in payload["paths"]]
    assert {path.suffix for path in paths} == {".docx", ".pdf"}
    for path in paths:
        assert path.exists()
    document = Document(next(path for path in paths if path.suffix == ".docx"))
    assert any(paragraph.text == "Summary" for paragraph in document.paragraphs)
