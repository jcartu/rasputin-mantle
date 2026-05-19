from __future__ import annotations

import json
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Inches, Pt
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

STYLE_FONTS = {
    "minimal": {"font": "Arial", "accent": colors.HexColor("#2E3440")},
    "academic": {"font": "Times New Roman", "accent": colors.HexColor("#4B5563")},
    "business": {"font": "Aptos", "accent": colors.HexColor("#1F4E79")},
}


def workspace_dir(payload: dict[str, Any]) -> Path:
    explicit = payload.get("output_dir")
    if explicit:
        out_dir = Path(str(explicit))
    else:
        task = str(payload.get("task") or payload.get("session_id") or "default").strip("/") or "default"
        out_dir = Path("/workspace") / task
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def _image_path(ref: str, tmp_dir: Path) -> Path:
    if ref.startswith(("http://", "https://")):
        target = tmp_dir / (Path(ref.split("?", 1)[0]).name or "image")
        with urllib.request.urlopen(ref, timeout=15) as response:  # noqa: S310 - user-provided skill input
            target.write_bytes(response.read())
        return target
    return Path(ref)


def create_documents(payload: dict[str, Any]) -> list[Path]:
    formats = [str(item).lower() for item in payload.get("formats") or ["docx", "pdf"]]
    outline = dict(payload.get("outline") or payload)
    out_dir = workspace_dir(payload)
    outputs: list[Path] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        if "docx" in formats:
            outputs.append(
                _create_docx(out_dir / "document.docx", outline, str(payload.get("style") or "minimal"), tmp_dir)
            )
        if "pdf" in formats:
            outputs.append(
                _create_pdf(out_dir / "document.pdf", outline, str(payload.get("style") or "minimal"), tmp_dir)
            )
    return outputs


def _create_docx(path: Path, outline: dict[str, Any], style_name: str, tmp_dir: Path) -> Path:
    doc = Document()
    _apply_docx_style(doc, style_name)
    doc.add_heading(str(outline.get("title") or "Document"), 0)
    sections = list(outline.get("sections") or [])
    if len(sections) > 5:
        doc.add_heading("Table of Contents", 1)
        for idx, section in enumerate(sections, start=1):
            doc.add_paragraph(f"{idx}. {section.get('heading') or section.get('title')}")
        doc.add_page_break()
    for section in sections:
        doc.add_heading(str(section.get("heading") or section.get("title") or "Section"), 1)
        for paragraph in section.get("paragraphs") or section.get("body") or []:
            doc.add_paragraph(str(paragraph))
        for table in section.get("tables") or []:
            _add_docx_table(doc, table)
        for image in section.get("images") or []:
            image_path = _image_path(str(image), tmp_dir)
            if image_path.exists():
                doc.add_picture(str(image_path), width=Inches(5.8))
    doc.save(path)
    return path


def _apply_docx_style(doc: Document, style_name: str) -> None:
    font_name = STYLE_FONTS.get(style_name, STYLE_FONTS["minimal"])["font"]
    normal = doc.styles["Normal"]
    normal.font.name = str(font_name)
    normal.font.size = Pt(11)
    for name in ("Heading 1", "Heading 2"):
        style = doc.styles[name]
        style.font.name = str(font_name)
        style.font.bold = True
    if "Mantle Table" not in [style.name for style in doc.styles if style.type == WD_STYLE_TYPE.TABLE]:
        doc.styles.add_style("Mantle Table", WD_STYLE_TYPE.TABLE)


def _add_docx_table(doc: Document, spec: dict[str, Any]) -> None:
    headers = [str(item) for item in spec.get("headers") or []]
    rows = list(spec.get("rows") or [])
    table = doc.add_table(rows=1, cols=max(1, len(headers)))
    table.style = "Table Grid"
    for idx, header in enumerate(headers):
        table.rows[0].cells[idx].text = header
    for row in rows:
        cells = table.add_row().cells
        values = row if isinstance(row, list) else [row.get(header, "") for header in headers]
        for idx, value in enumerate(values[: len(cells)]):
            cells[idx].text = str(value)


def _create_pdf(path: Path, outline: dict[str, Any], style_name: str, tmp_dir: Path) -> Path:
    doc = SimpleDocTemplate(str(path), pagesize=LETTER, title=str(outline.get("title") or "Document"))
    styles = getSampleStyleSheet()
    accent = STYLE_FONTS.get(style_name, STYLE_FONTS["minimal"])["accent"]
    story: list[Any] = [Paragraph(str(outline.get("title") or "Document"), styles["Title"]), Spacer(1, 18)]
    sections = list(outline.get("sections") or [])
    if len(sections) > 5:
        story.append(Paragraph("Table of Contents", styles["Heading1"]))
        for idx, section in enumerate(sections, start=1):
            heading = section.get("heading") or section.get("title")
            story.append(Paragraph(f"{idx}. {heading}", styles["BodyText"]))
        story.append(PageBreak())
    for section in sections:
        story.append(Paragraph(str(section.get("heading") or section.get("title") or "Section"), styles["Heading1"]))
        for paragraph in section.get("paragraphs") or section.get("body") or []:
            story.append(Paragraph(str(paragraph), styles["BodyText"]))
            story.append(Spacer(1, 8))
        for table in section.get("tables") or []:
            story.append(_pdf_table(table, accent))
            story.append(Spacer(1, 10))
        for image in section.get("images") or []:
            image_path = _image_path(str(image), tmp_dir)
            if image_path.exists():
                story.append(Image(str(image_path), width=360, height=220, kind="proportional"))
    doc.build(story)
    return path


def _pdf_table(spec: dict[str, Any], accent: Any) -> Table:
    headers = [str(item) for item in spec.get("headers") or []]
    rows = list(spec.get("rows") or [])
    data = [headers] if headers else []
    data.extend(row if isinstance(row, list) else [row.get(header, "") for header in headers] for row in rows)
    table = Table(data or [[""]])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), accent),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    return table


def main() -> None:
    payload = json.loads(sys.stdin.read() or "{}")
    outputs = create_documents(payload)
    print(
        json.dumps(
            {"paths": [str(path) for path in outputs], "formats": [path.suffix.lstrip(".") for path in outputs]}
        )
    )


if __name__ == "__main__":
    main()
