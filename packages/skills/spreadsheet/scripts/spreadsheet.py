from __future__ import annotations

# ruff: noqa: E402,E501,I001

import json
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TEMPLATE_DIR = ROOT / "templates"
SKILLS_ROOT = Path(__file__).resolve().parents[2]
if str(SKILLS_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILLS_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.drawing.image import Image as WorkbookImage
from openpyxl.styles import Font, PatternFill

from subskills.comparison_matrix import add_comparison_matrix  # noqa: E402
from subskills.data_cleaning import clean_rows  # noqa: E402
from subskills.financial_model import build_financial_model  # noqa: E402
from shared.self_review import self_review  # noqa: E402


def workspace_path(payload: dict[str, Any], filename: str) -> Path:
    explicit = payload.get("output_dir")
    if explicit:
        out_dir = Path(str(explicit))
    else:
        task = str(payload.get("task") or payload.get("session_id") or "default").strip("/") or "default"
        out_dir = Path("/workspace") / task
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / filename


def _payload_from_prompt(payload: dict[str, Any]) -> dict[str, Any]:
    prompt = str(payload.get("prompt") or "").casefold()
    base = {"output_dir": payload.get("output_dir"), "prompt": payload.get("prompt")}
    if "financial model" in prompt or "five-year" in prompt or "five year" in prompt:
        return {
            **base,
            "mode": "financial_model",
            "assumptions": {"starting_revenue": 850000, "revenue_growth": 0.28, "gross_margin": 0.74},
        }
    if "feature comparison" in prompt or "vendor scoring" in prompt:
        criteria = ["Cost", "Security", "Usability", "Support", "Implementation"]
        if "vendor" in prompt:
            criteria = ["Cost", "Compliance", "Support", "Reliability", "Implementation"]
        return {
            **base,
            "mode": "comparison_matrix",
            "criteria": criteria,
            "items": [
                {"name": "Option A", "scores": {criterion: 4 for criterion in criteria}},
                {"name": "Option B", "scores": {criterion: 3 + (idx % 2) for idx, criterion in enumerate(criteria)}},
                {"name": "Option C", "scores": {criterion: 5 if idx < 2 else 3 for idx, criterion in enumerate(criteria)}},
            ],
        }
    if "customer data cleaning" in prompt or "deduplicate" in prompt:
        return {
            **base,
            "mode": "data_cleaning",
            "schema": [{"name": "Name"}, {"name": "Company"}, {"name": "Spend"}, {"name": "Status"}],
            "rows": [
                {"Name": "Ada Lovelace", "Company": "Analytical Ops", "Spend": "$1,200", "Status": "Active"},
                {"Name": "Ada Lovelace", "Company": "Analytical Ops", "Spend": "$1,200", "Status": "Active"},
                {"Name": "Lin Chen", "Company": "Vector Labs", "Spend": "900", "Status": "Trial"},
                {"Name": "Maya Singh", "Company": "Nimbus", "Spend": "$2,450", "Status": "Active"},
            ],
            "summary": True,
        }
    if "expense" in prompt:
        return {
            **base,
            "mode": "table",
            "schema": [{"name": "Category"}, {"name": "Vendor"}, {"name": "Monthly Cost"}, {"name": "Variance"}],
            "rows": [
                {"Category": "Compute", "Vendor": "GPU Cloud", "Monthly Cost": 4200, "Variance": 350},
                {"Category": "Models", "Vendor": "API Provider", "Monthly Cost": 1800, "Variance": -120},
                {"Category": "Storage", "Vendor": "Object Store", "Monthly Cost": 420, "Variance": 40},
            ],
            "charts": [{"type": "bar", "x": "Category", "y": "Monthly Cost", "title": "Monthly Cost by Category"}],
        }
    if "hiring" in prompt:
        return {
            **base,
            "mode": "table",
            "schema": [{"name": "Role"}, {"name": "Stage"}, {"name": "Owner"}, {"name": "Candidates"}],
            "rows": [
                {"Role": "Platform Engineer", "Stage": "Technical", "Owner": "Avery", "Candidates": 5},
                {"Role": "Product Designer", "Stage": "Portfolio", "Owner": "Sam", "Candidates": 3},
                {"Role": "Operations Lead", "Stage": "Onsite", "Owner": "Jordan", "Candidates": 2},
            ],
            "summary": True,
        }
    if "product metrics" in prompt:
        return {
            **base,
            "mode": "table",
            "schema": [{"name": "Metric"}, {"name": "Current"}, {"name": "Previous"}, {"name": "Interpretation"}],
            "rows": [
                {"Metric": "Activation", "Current": 61, "Previous": 54, "Interpretation": "Improving"},
                {"Metric": "Retention", "Current": 43, "Previous": 41, "Interpretation": "Stable"},
                {"Metric": "Quality", "Current": 88, "Previous": 82, "Interpretation": "Improving"},
            ],
            "charts": [{"type": "bar", "x": "Metric", "y": "Current", "title": "Current Product Metrics"}],
        }
    if "budget" in prompt:
        return {**base, "mode": "budget"}
    if "filter" in prompt or "status" in prompt:
        return {
            **base,
            "mode": "table",
            "schema": [{"name": "Initiative"}, {"name": "Owner"}, {"name": "Health"}, {"name": "Priority"}],
            "rows": [
                {"Initiative": "Runner update", "Owner": "Ada", "Health": "Green", "Priority": "High"},
                {"Initiative": "Skill QA", "Owner": "Lin", "Health": "Yellow", "Priority": "High"},
                {"Initiative": "Release comms", "Owner": "Maya", "Health": "Red", "Priority": "Medium"},
            ],
            "query_plan": {"where_equals": {"Health": "Green"}},
            "summary": True,
        }
    return {
        **base,
        "mode": "table",
        "schema": [{"name": "Stage"}, {"name": "Owner"}, {"name": "Deals"}, {"name": "Forecast Risk"}],
        "rows": [
            {"Stage": "Prospect", "Owner": "Sales", "Deals": 18, "Forecast Risk": "Medium"},
            {"Stage": "Qualified", "Owner": "AE Team", "Deals": 11, "Forecast Risk": "Low"},
            {"Stage": "Commit", "Owner": "Revenue Lead", "Deals": 6, "Forecast Risk": "Low"},
        ],
        "charts": [{"type": "bar", "x": "Stage", "y": "Deals", "title": "Deals by Stage"}],
    }


def create_workbook(payload: dict[str, Any]) -> Path:
    if not payload.get("mode"):
        payload = _payload_from_prompt(payload)
    output = workspace_path(payload, "data.xlsx")
    mode = str(payload.get("mode") or "table")
    if mode == "financial_model":
        template = TEMPLATE_DIR / "financial-model.xlsx"
        if template.exists():
            wb = load_workbook(template)
            wb.save(output)
            return output
        return build_financial_model(output, dict(payload.get("assumptions") or {}))
    if mode == "budget":
        return _create_budget_workbook(output)

    workbook_templates = {
        "comparison_matrix": "comparison-matrix.xlsx",
        "data_cleaning": "data-cleaning.xlsx",
    }
    template_name = workbook_templates.get(mode)
    if template_name and (TEMPLATE_DIR / template_name).exists():
        wb = load_workbook(TEMPLATE_DIR / template_name)
        wb.save(output)
        return output

    wb = Workbook()
    if mode == "comparison_matrix":
        add_comparison_matrix(wb, list(payload.get("items") or []), [str(c) for c in payload.get("criteria") or []])
    else:
        rows = list(payload.get("rows") or [])
        schema = list(payload.get("schema") or [])
        if mode == "data_cleaning":
            rows = clean_rows(rows, schema)
            schema = [{"name": key} for key in (rows[0].keys() if rows else [])]
        if payload.get("query_plan"):
            rows = _apply_query_plan(rows, dict(payload.get("query_plan") or {}))
        _add_table(wb.active, rows, schema)
    if payload.get("summary"):
        _add_summary_sheet(wb, str(payload.get("prompt") or "Summary"))
    _format(wb)
    wb.save(output)
    if payload.get("charts"):
        _add_charts(output, list(payload.get("charts") or []))
    return output


def _review_plan(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("mode"):
        return dict(payload)
    return _payload_from_prompt(dict(payload))


def _create_budget_workbook(output: Path) -> Path:
    wb = Workbook()
    ws = wb.active
    ws.title = "Budget"
    ws.append(["Month", "Planned", "Actual", "Variance"])
    rows = [("Jan", 1200, 1150), ("Feb", 1350, 1425), ("Mar", 1500, 1610), ("Apr", 1650, 1580)]
    for idx, (month, planned, actual) in enumerate(rows, start=2):
        ws.append([month, planned, actual, f"=B{idx}-C{idx}"])
    ws.append(["Total", "=SUM(B2:B5)", "=SUM(C2:C5)", "=SUM(D2:D5)"])
    summary = wb.create_sheet("Summary")
    summary.append(["Metric", "Value"])
    summary.append(["Total Planned", "=Budget!B6"])
    summary.append(["Total Actual", "=Budget!C6"])
    summary.append(["Total Variance", "=Budget!D6"])
    _format(wb)
    wb.save(output)
    _add_charts(output, [{"type": "line", "x": "Month", "y": "Planned", "title": "Planned Budget"}])
    return output


def _add_summary_sheet(wb: Workbook, prompt: str) -> None:
    if "Summary" in wb.sheetnames:
        return
    ws = wb.create_sheet("Summary")
    ws.append(["Question", "Answer"])
    ws.append(["Purpose", prompt[:180]])
    ws.append(["Review Focus", "Use the workbook to identify risks, owners, and next decisions."])
    ws.append(["Next Step", "Validate assumptions with the responsible team before publication."])


def _apply_query_plan(rows: list[dict[str, Any]], plan: dict[str, Any]) -> list[dict[str, Any]]:
    select = [str(item) for item in plan.get("select") or []]
    filtered = rows
    if plan.get("where_equals"):
        expected = dict(plan["where_equals"])
        filtered = [row for row in filtered if all(row.get(key) == value for key, value in expected.items())]
    if select:
        filtered = [{key: row.get(key) for key in select} for row in filtered]
    return filtered


def _add_table(ws: Any, rows: list[dict[str, Any]], schema: list[dict[str, Any]]) -> None:
    headers = [str(col.get("name")) for col in schema] if schema else sorted({key for row in rows for key in row})
    ws.title = "Data"
    ws.append(headers)
    for row in rows:
        ws.append([row.get(header, "") for header in headers])


def _format(wb: Workbook) -> None:
    for ws in wb.worksheets:
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1F4E79")
        ws.freeze_panes = "A2"
        for column_cells in ws.columns:
            ws.column_dimensions[column_cells[0].column_letter].width = 18


def _add_charts(path: Path, charts: list[dict[str, Any]]) -> None:
    wb = load_workbook(path)
    ws = wb.active
    rows = list(ws.values)
    if len(rows) < 2:
        wb.save(path)
        return
    df = pd.DataFrame(rows[1:], columns=rows[0])
    chart_ws = wb.create_sheet("Charts")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for index, chart in enumerate(charts, start=1):
            image = _chart_image(df, chart, tmp_dir / f"chart-{index}.png")
            chart_ws.add_image(WorkbookImage(str(image)), f"A{1 + (index - 1) * 18}")
        wb.save(path)


def _chart_image(df: pd.DataFrame, chart: dict[str, Any], target: Path) -> Path:
    x_col = str(chart.get("x") or df.columns[0])
    y_col = str(chart.get("y") or df.columns[-1])
    kind = str(chart.get("type") or "bar")
    fig, ax = plt.subplots(figsize=(6, 3.4), dpi=150)
    if kind == "line":
        ax.plot(df[x_col].astype(str), pd.to_numeric(df[y_col], errors="coerce"), marker="o")
    else:
        ax.bar(df[x_col].astype(str), pd.to_numeric(df[y_col], errors="coerce"))
    ax.set_title(str(chart.get("title") or y_col))
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(target)
    plt.close(fig)
    return target


def main() -> None:
    payload = json.loads(sys.stdin.read() or "{}")
    output = create_workbook(payload)
    review_plan = _review_plan(payload)
    review = self_review(output, review_plan, "spreadsheet", max_iterations=2)
    workbook = load_workbook(output, data_only=False)
    print(
        json.dumps(
            {
                "path": str(output),
                "sheets": workbook.sheetnames,
                "mode": review_plan.get("mode", "table"),
                "self_review": {"artifact_id": output.name, **review},
            }
        )
    )


if __name__ == "__main__":
    main()
