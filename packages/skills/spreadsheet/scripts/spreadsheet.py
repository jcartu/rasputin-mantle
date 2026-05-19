from __future__ import annotations

# ruff: noqa: E402,I001

import json
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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


def workspace_path(payload: dict[str, Any], filename: str) -> Path:
    explicit = payload.get("output_dir")
    if explicit:
        out_dir = Path(str(explicit))
    else:
        task = str(payload.get("task") or payload.get("session_id") or "default").strip("/") or "default"
        out_dir = Path("/workspace") / task
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / filename


def create_workbook(payload: dict[str, Any]) -> Path:
    output = workspace_path(payload, "data.xlsx")
    mode = str(payload.get("mode") or "table")
    if mode == "financial_model":
        return build_financial_model(output, dict(payload.get("assumptions") or {}))

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
    _format(wb)
    wb.save(output)
    if payload.get("charts"):
        _add_charts(output, list(payload.get("charts") or []))
    return output


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
    workbook = load_workbook(output, data_only=False)
    print(json.dumps({"path": str(output), "sheets": workbook.sheetnames, "mode": payload.get("mode", "table")}))


if __name__ == "__main__":
    main()
