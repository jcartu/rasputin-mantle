from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches as DocxInches
from docx.shared import Pt as DocxPt
from docx.shared import RGBColor as DocxRGBColor
from openpyxl import Workbook
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[2]
SLIDE_DIR = ROOT / "packages/skills/slides/templates"
SHEET_DIR = ROOT / "packages/skills/spreadsheet/templates"
DOC_DIR = ROOT / "packages/skills/document/templates"


SLIDE_THEMES = {
    "minimal": {
        "title": "Minimal Template",
        "subtitle": "Clean monochrome presentation system",
        "bg": "FFFFFF",
        "ink": "111827",
        "muted": "6B7280",
        "accent": "111827",
        "accent2": "E5E7EB",
        "soft": "F9FAFB",
    },
    "corporate": {
        "title": "Corporate Template",
        "subtitle": "Navy and teal executive reporting deck",
        "bg": "F8FAFC",
        "ink": "0B1F3A",
        "muted": "475569",
        "accent": "0F766E",
        "accent2": "164E63",
        "soft": "E6FFFA",
    },
    "pitch": {
        "title": "Pitch Template",
        "subtitle": "Warm investor storytelling deck",
        "bg": "FFF7ED",
        "ink": "3B2416",
        "muted": "7C4A2D",
        "accent": "EA580C",
        "accent2": "F59E0B",
        "soft": "FFEDD5",
    },
    "research": {
        "title": "Research Template",
        "subtitle": "Academic blue evidence and methods deck",
        "bg": "F8FBFF",
        "ink": "102A43",
        "muted": "486581",
        "accent": "1D4ED8",
        "accent2": "3B82F6",
        "soft": "DBEAFE",
    },
}


DOC_THEMES = {
    "minimal": {"accent": "111827", "soft": "F9FAFB", "font": "Arial", "title": "Minimal Document Template"},
    "academic": {"accent": "1D4ED8", "soft": "EFF6FF", "font": "Times New Roman", "title": "Academic Report Template"},
    "business": {"accent": "1F4E79", "soft": "EAF3F8", "font": "Aptos", "title": "Business Brief Template"},
}


def _rgb(hex_value: str) -> RGBColor:
    return RGBColor.from_string(hex_value)


def _docx_rgb(hex_value: str) -> DocxRGBColor:
    return DocxRGBColor.from_string(hex_value)


def _blank_slide(prs: Presentation):
    return prs.slides.add_slide(prs.slide_layouts[6])


def _set_slide_background(slide, color: str) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = _rgb(color)


def _add_textbox(slide, text: str, x: float, y: float, w: float, h: float, size: int, color: str, bold: bool = False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.margin_left = 0
    frame.margin_right = 0
    frame.vertical_anchor = MSO_ANCHOR.TOP
    para = frame.paragraphs[0]
    para.text = text
    run = para.runs[0]
    run.font.name = "Inter"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = _rgb(color)
    return box


def _add_label(slide, text: str, x: float, y: float, w: float, h: float, theme: dict[str, str]) -> None:
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = _rgb(theme["soft"])
    shape.line.color.rgb = _rgb(theme["accent"])
    shape.text = text
    para = shape.text_frame.paragraphs[0]
    para.alignment = PP_ALIGN.CENTER
    para.runs[0].font.name = "Inter"
    para.runs[0].font.size = Pt(11)
    para.runs[0].font.bold = True
    para.runs[0].font.color.rgb = _rgb(theme["accent"])


def _add_image_placeholder(
    slide,
    x: float,
    y: float,
    w: float,
    h: float,
    theme: dict[str, str],
    label: str = "Image placeholder",
) -> None:
    rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    rect.fill.solid()
    rect.fill.fore_color.rgb = _rgb(theme["soft"])
    rect.line.color.rgb = _rgb(theme["accent"])
    rect.line.width = Pt(1.5)
    rect.text = label
    para = rect.text_frame.paragraphs[0]
    para.alignment = PP_ALIGN.CENTER
    para.runs[0].font.name = "Inter"
    para.runs[0].font.size = Pt(14)
    para.runs[0].font.color.rgb = _rgb(theme["muted"])


def _add_footer(slide, theme: dict[str, str], label: str) -> None:
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.65), Inches(7.05), Inches(11.05), Inches(0.03))
    line.fill.solid()
    line.fill.fore_color.rgb = _rgb(theme["accent"])
    line.line.fill.background()
    _add_textbox(slide, label, 0.65, 7.12, 5, 0.25, 8, theme["muted"])


def create_slide_templates() -> None:
    SLIDE_DIR.mkdir(parents=True, exist_ok=True)
    for name, theme in SLIDE_THEMES.items():
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

        slide = _blank_slide(prs)
        _set_slide_background(slide, theme["bg"])
        _add_textbox(slide, theme["title"], 0.7, 0.85, 5.7, 0.8, 34, theme["ink"], True)
        _add_textbox(slide, theme["subtitle"], 0.72, 1.72, 5.2, 0.45, 17, theme["muted"])
        _add_label(slide, "Presentation Template", 0.72, 2.35, 2.25, 0.42, theme)
        _add_image_placeholder(slide, 6.7, 0.75, 5.75, 4.6, theme, "Hero image placeholder")
        _add_footer(slide, theme, "Title slide · image + subtitle layout")

        slide = _blank_slide(prs)
        _set_slide_background(slide, theme["accent"])
        _add_textbox(slide, "01", 0.85, 0.85, 1.4, 0.5, 16, "FFFFFF", True)
        _add_textbox(slide, "Section Divider", 0.85, 2.55, 8.4, 0.9, 38, "FFFFFF", True)
        _add_textbox(
            slide,
            "Use this slide to reset context and introduce the next narrative arc.",
            0.9,
            3.52,
            7.4,
            0.55,
            18,
            "FFFFFF",
        )
        band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(10.4), Inches(0), Inches(2.95), Inches(7.5))
        band.fill.solid()
        band.fill.fore_color.rgb = _rgb(theme["accent2"])
        band.line.fill.background()

        slide = _blank_slide(prs)
        _set_slide_background(slide, theme["bg"])
        _add_textbox(slide, "Two-Column Content", 0.65, 0.55, 8, 0.55, 26, theme["ink"], True)
        _add_textbox(slide, "Left narrative", 0.8, 1.45, 4.8, 0.4, 16, theme["accent"], True)
        _add_textbox(
            slide,
            "• Key insight with supporting detail\n• Evidence point or customer quote\n• Decision implication",
            0.8,
            1.95,
            4.9,
            2.5,
            15,
            theme["ink"],
        )
        _add_textbox(slide, "Right narrative", 6.8, 1.45, 4.8, 0.4, 16, theme["accent"], True)
        _add_textbox(
            slide,
            "• Counterpoint or operational risk\n• Quantified metric or benchmark\n• Recommended next action",
            6.8,
            1.95,
            4.9,
            2.5,
            15,
            theme["ink"],
        )
        _add_footer(slide, theme, "Two-column content layout")

        slide = _blank_slide(prs)
        _set_slide_background(slide, theme["bg"])
        _add_textbox(slide, "Chart Placeholder", 0.65, 0.55, 8, 0.55, 26, theme["ink"], True)
        chart = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.85), Inches(1.35), Inches(7.3), Inches(4.8))
        chart.fill.solid()
        chart.fill.fore_color.rgb = _rgb("FFFFFF")
        chart.line.color.rgb = _rgb(theme["accent"])
        chart.text = "Chart / graph placeholder"
        chart.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        for idx, height in enumerate([1.1, 1.9, 2.7, 3.4], start=1):
            bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(1.35 + idx),
                Inches(5.75 - height),
                Inches(0.48),
                Inches(height),
            )
            bar.fill.solid()
            bar.fill.fore_color.rgb = _rgb(theme["accent"] if idx % 2 else theme["accent2"])
            bar.line.fill.background()
        _add_textbox(slide, "Key takeaway", 8.75, 1.45, 3.5, 0.35, 16, theme["accent"], True)
        _add_textbox(
            slide,
            "Summarize the signal in one sentence, then list the implications for the audience.",
            8.75,
            1.95,
            3.4,
            1.4,
            15,
            theme["ink"],
        )
        _add_footer(slide, theme, "Chart placeholder slide")

        slide = _blank_slide(prs)
        _set_slide_background(slide, theme["bg"])
        _add_textbox(slide, "Thank you", 0.85, 1.15, 5.8, 0.75, 38, theme["ink"], True)
        _add_textbox(slide, "Questions, discussion, and next steps", 0.9, 2.02, 5.6, 0.45, 18, theme["muted"])
        _add_image_placeholder(slide, 7.4, 1.0, 4.7, 3.6, theme, "Closing visual placeholder")
        _add_textbox(slide, "contact@example.com  ·  company.com", 0.9, 6.25, 5.2, 0.35, 13, theme["accent"], True)
        _add_footer(slide, theme, "Closing / thanks slide")

        prs.save(SLIDE_DIR / f"{name}.pptx")


def _style_ws(ws, tab_color: str = "1F4E79") -> None:
    header_fill = PatternFill("solid", fgColor=tab_color)
    total_fill = PatternFill("solid", fgColor="E2E8F0")
    thin = Side(style="thin", color="CBD5E1")
    ws.freeze_panes = "A2"
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")
    for row in ws.iter_rows():
        for cell in row:
            cell.border = Border(bottom=thin)
    for cell in ws[ws.max_row]:
        cell.font = Font(bold=True)
        cell.fill = total_fill
    for column in range(1, ws.max_column + 1):
        ws.column_dimensions[get_column_letter(column)].width = 18
    ws.sheet_properties.tabColor = tab_color


def _add_defined_name(wb: Workbook, name: str, ref: str) -> None:
    defined = DefinedName(name, attr_text=ref)
    try:
        wb.defined_names.add(defined)
    except AttributeError:
        wb.defined_names.append(defined)


def create_spreadsheet_templates() -> None:
    SHEET_DIR.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    pnl = wb.active
    pnl.title = "P&L"
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    pnl.append(["Line Item", *months, "Total"])
    rows = [
        ("Revenue", [120000, 132000, 145000, 151000, 164000, 178000]),
        ("Cost of Goods Sold", [-36000, -39800, -43500, -45300, -49200, -53400]),
        ("Gross Profit", ["=B2+B3", "=C2+C3", "=D2+D3", "=E2+E3", "=F2+F3", "=G2+G3"]),
        ("Operating Expenses", [-52000, -54000, -56000, -58500, -60000, -62000]),
        ("Net Income", ["=B4+B5", "=C4+C5", "=D4+D5", "=E4+E5", "=F4+F5", "=G4+G5"]),
    ]
    for idx, (label, values) in enumerate(rows, start=2):
        pnl.append([label, *values, f"=SUM(B{idx}:G{idx})"])
    bs = wb.create_sheet("Balance Sheet")
    bs.append(["Account", "Opening", "Jan", "Feb", "Mar", "Apr", "May", "Jun"])
    balance_sheet_rows = [
        ("Cash", 320000),
        ("Accounts Receivable", 95000),
        ("Inventory", 52000),
        ("Accounts Payable", -48000),
        ("Equity", -419000),
    ]
    for label, opening in balance_sheet_rows:
        bs.append([label, opening, *[f"=B{bs.max_row + 1}+{5000 * i}" for i in range(1, 7)]])
    bs.append(
        [
            "Balance Check",
            "=SUM(B2:B6)",
            "=SUM(C2:C6)",
            "=SUM(D2:D6)",
            "=SUM(E2:E6)",
            "=SUM(F2:F6)",
            "=SUM(G2:G6)",
            "=SUM(H2:H6)",
        ]
    )
    cf = wb.create_sheet("Cash Flow")
    cf.append(["Line Item", *months, "Total"])
    cash_flow_rows = [
        ("Net Income", 31000),
        ("Depreciation", 5000),
        ("Working Capital Change", -12000),
        ("Capital Expenditures", -18000),
        ("Net Cash Flow", "=B2+B3+B4+B5"),
    ]
    for idx, (label, base) in enumerate(cash_flow_rows, start=2):
        if isinstance(base, str):
            values = [base.replace("B", get_column_letter(col)) for col in range(2, 8)]
        else:
            values = [base + 1200 * (col - 2) for col in range(2, 8)]
        cf.append([label, *values, f"=SUM(B{idx}:G{idx})"])
    for ws in wb.worksheets:
        _style_ws(ws, "0F766E" if ws.title == "Cash Flow" else "1F4E79")
    _add_defined_name(wb, "Revenue", "'P&L'!$B$2:$G$2")
    _add_defined_name(wb, "NetIncome", "'P&L'!$B$6:$G$6")
    _add_defined_name(wb, "CashBalance", "'Balance Sheet'!$C$2:$H$2")
    wb.save(SHEET_DIR / "financial-model.xlsx")

    wb = Workbook()
    ws = wb.active
    ws.title = "Comparison Matrix"
    ws.append(
        [
            "Option",
            "Cost",
            "Security",
            "Usability",
            "Support",
            "Implementation",
            "Weighted Score",
            "Recommendation",
        ]
    )
    options = [("Vendor A", 4, 5, 4, 3, 4), ("Vendor B", 5, 3, 5, 4, 3), ("Vendor C", 3, 5, 4, 5, 5)]
    for row, values in enumerate(options, start=2):
        ws.append([*values, f"=AVERAGE(B{row}:F{row})", '=IF(G{0}>=4.2,"Shortlist","Review")'.format(row)])
    ws.append(["Criteria Weight", 0.2, 0.25, 0.2, 0.15, 0.2, "", ""])
    _style_ws(ws, "7C2D12")
    ws.conditional_formatting.add(
        "B2:G4",
        ColorScaleRule(
            start_type="min",
            start_color="FEE2E2",
            mid_type="percentile",
            mid_value=50,
            mid_color="FEF3C7",
            end_type="max",
            end_color="DCFCE7",
        ),
    )
    wb.save(SHEET_DIR / "comparison-matrix.xlsx")

    wb = Workbook()
    raw = wb.active
    raw.title = "Input"
    raw.append(["Customer", "Email", "Spend", "Status", "Duplicate Flag"])
    rows = [
        ("Ada Lovelace", "ada@example.com", "$1,200", "Active", ""),
        ("Ada Lovelace", "ada@example.com", "$1,200", "Active", "Duplicate"),
        ("Lin Chen", "lin@example.com", "900", "Trial", ""),
        ("Maya Singh", "maya@example.com", "$2,450", "Active", ""),
    ]
    for row in rows:
        raw.append(row)
    clean = wb.create_sheet("Cleaned")
    clean.append(["Customer", "Email", "Spend Numeric", "Status", "Included"])
    for row in range(2, 6):
        clean.append(
            [
                f"=Input!A{row}",
                f"=LOWER(Input!B{row})",
                f'=VALUE(SUBSTITUTE(Input!C{row},"$","") )',
                f"=Input!D{row}",
                f'=IF(Input!E{row}="Duplicate","No","Yes")',
            ]
        )
    clean.append(["Total Included Spend", "", '=SUMIF(E2:E5,"Yes",C2:C5)', "", ""])
    for ws in wb.worksheets:
        _style_ws(ws, "334155")
    _add_defined_name(wb, "RawInput", "'Input'!$A$1:$E$5")
    _add_defined_name(wb, "CleanedSpend", "'Cleaned'!$C$2:$C$5")
    wb.save(SHEET_DIR / "data-cleaning.xlsx")


def _set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    tc_pr.append(shading)


def _add_toc(paragraph) -> None:
    run = paragraph.add_run()
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), 'TOC \\o "1-3" \\h \\z \\u')
    run._r.append(fld)


def _configure_doc_styles(doc: Document, name: str, theme: dict[str, str]) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = theme["font"]
    normal.font.size = DocxPt(10.5)
    for level, size in [(1, 20), (2, 15), (3, 12)]:
        style = doc.styles[f"Heading {level}"]
        style.font.name = theme["font"]
        style.font.size = DocxPt(size)
        style.font.bold = True
        style.font.color.rgb = _docx_rgb(theme["accent"] if name != "minimal" else "111827")
    if "Sidebar" not in doc.styles:
        sidebar = doc.styles.add_style("Sidebar", WD_STYLE_TYPE.PARAGRAPH)
        sidebar.font.name = theme["font"]
        sidebar.font.size = DocxPt(9)
        sidebar.font.color.rgb = _docx_rgb("334155")


def _add_cover(doc: Document, name: str, theme: dict[str, str]) -> None:
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_before = DocxPt(150)
    run = title.add_run(theme["title"])
    run.font.name = theme["font"]
    run.font.size = DocxPt(28)
    run.font.bold = True
    run.font.color.rgb = _docx_rgb(theme["accent"] if name != "minimal" else "111827")
    subtitle = doc.add_paragraph("Cover page · table of contents · registered heading styles · section breaks")
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.runs[0].font.size = DocxPt(11)
    doc.add_page_break()


def create_document_templates() -> None:
    DOC_DIR.mkdir(parents=True, exist_ok=True)
    sections = [
        ("Executive Summary", "A concise overview of the artifact purpose, audience, and recommended decision."),
        ("Analysis", "Structured findings belong here, supported by tables, evidence, and clear synthesis."),
        ("Recommendations", "Close with prioritized next steps, owners, timing, and success criteria."),
    ]
    for name, theme in DOC_THEMES.items():
        doc = Document()
        _configure_doc_styles(doc, name, theme)
        _add_cover(doc, name, theme)
        doc.add_heading("Table of Contents", level=1)
        _add_toc(doc.add_paragraph())
        doc.add_section(WD_SECTION.NEW_PAGE)
        if name == "business":
            table = doc.add_table(rows=1, cols=2)
            table.autofit = False
            table.columns[0].width = DocxInches(1.55)
            table.columns[1].width = DocxInches(4.8)
            sidebar, body = table.rows[0].cells
            sidebar.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
            _set_cell_shading(sidebar, theme["soft"])
            sidebar.text = "SIDEBAR\nKey metric\nDecision owner\nDeadline"
            for para in sidebar.paragraphs:
                para.style = doc.styles["Sidebar"]
            container = body
        else:
            container = None
        for idx, (heading, text) in enumerate(sections, start=1):
            display = f"{idx}. {heading}" if name == "academic" else heading
            if container is not None:
                container.add_paragraph(display, style="Heading 1")
                container.add_paragraph(text)
                container.add_paragraph("Evidence Detail", style="Heading 2")
                container.add_paragraph("Add charts, observations, and implications under registered heading levels.")
            else:
                doc.add_heading(display, level=1)
                doc.add_paragraph(text)
                doc.add_heading("Evidence Detail", level=2)
                doc.add_paragraph("Add charts, observations, and implications under registered heading levels.")
                doc.add_heading("Implementation Note", level=3)
                doc.add_paragraph("Use this third-level heading for sub-findings that should appear in the TOC.")
            if idx == 1 and name != "business":
                doc.add_section(WD_SECTION.NEW_PAGE)
        for section in doc.sections:
            section.top_margin = DocxInches(0.75)
            section.bottom_margin = DocxInches(0.75)
            section.left_margin = DocxInches(0.8)
            section.right_margin = DocxInches(0.8)
        doc.save(DOC_DIR / f"{name}.docx")


def main() -> None:
    create_slide_templates()
    create_spreadsheet_templates()
    create_document_templates()


if __name__ == "__main__":
    main()
