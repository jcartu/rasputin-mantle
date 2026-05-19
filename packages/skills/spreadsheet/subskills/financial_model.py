from __future__ import annotations

from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

YEARS = ["Year 1", "Year 2", "Year 3"]


def build_financial_model(output_path: str | Path, assumptions: dict[str, Any] | None = None) -> Path:
    values = assumptions or {}
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "Assumptions"
    _assumptions(ws, values)
    _profit_and_loss(wb.create_sheet("P&L"))
    _balance_sheet(wb.create_sheet("Balance Sheet"))
    _cash_flow(wb.create_sheet("Cash Flow"))
    _format_workbook(wb)
    wb.save(path)
    return path


def _assumptions(ws: Any, values: dict[str, Any]) -> None:
    rows = [
        ("Starting Revenue", values.get("starting_revenue", 1_000_000)),
        ("Revenue Growth", values.get("revenue_growth", 0.2)),
        ("Gross Margin", values.get("gross_margin", 0.68)),
        ("Operating Expense %", values.get("opex_percent", 0.42)),
        ("Tax Rate", values.get("tax_rate", 0.21)),
        ("Starting Cash", values.get("starting_cash", 250_000)),
        ("Starting Debt", values.get("starting_debt", 100_000)),
        ("Capex % Revenue", values.get("capex_percent", 0.05)),
        ("Depreciation % Revenue", values.get("depreciation_percent", 0.03)),
        ("Working Capital % Revenue", values.get("working_capital_percent", 0.08)),
    ]
    ws.append(["Assumption", "Value"])
    for row in rows:
        ws.append(list(row))


def _profit_and_loss(ws: Any) -> None:
    ws.append(["Line Item", *YEARS])
    labels = [
        "Revenue",
        "COGS",
        "Gross Profit",
        "Operating Expenses",
        "EBITDA",
        "Depreciation",
        "EBIT",
        "Taxes",
        "Net Income",
    ]
    for label in labels:
        ws.append([label, None, None, None])
    ws["B2"] = "=Assumptions!B1"
    ws["C2"] = "=B2*(1+Assumptions!B2)"
    ws["D2"] = "=C2*(1+Assumptions!B2)"
    for col in range(2, 5):
        letter = get_column_letter(col)
        ws[f"{letter}3"] = f"={letter}2*(1-Assumptions!B3)"
        ws[f"{letter}4"] = f"={letter}2-{letter}3"
        ws[f"{letter}5"] = f"={letter}2*Assumptions!B4"
        ws[f"{letter}6"] = f"={letter}4-{letter}5"
        ws[f"{letter}7"] = f"={letter}2*Assumptions!B9"
        ws[f"{letter}8"] = f"={letter}6-{letter}7"
        ws[f"{letter}9"] = f"=MAX(0,{letter}8*Assumptions!B5)"
        ws[f"{letter}10"] = f"={letter}8-{letter}9"


def _balance_sheet(ws: Any) -> None:
    ws.append(["Line Item", *YEARS])
    labels = ["Cash", "Accounts Receivable", "Fixed Assets", "Total Assets", "Debt", "Equity"]
    labels.append("Total Liabilities & Equity")
    for label in labels:
        ws.append([label, None, None, None])
    ws["B2"] = "=Assumptions!B6+'Cash Flow'!B8"
    ws["C2"] = "=B2+'Cash Flow'!C8"
    ws["D2"] = "=C2+'Cash Flow'!D8"
    for col in range(2, 5):
        letter = get_column_letter(col)
        ws[f"{letter}3"] = f"='P&L'!{letter}2*Assumptions!B10"
        ws[f"{letter}4"] = f"='P&L'!{letter}2*Assumptions!B8"
        ws[f"{letter}5"] = f"=SUM({letter}2:{letter}4)"
        ws[f"{letter}6"] = "=Assumptions!B7" if col == 2 else f"={get_column_letter(col - 1)}6"
        ws[f"{letter}7"] = f"={letter}5-{letter}6"
        ws[f"{letter}8"] = f"=SUM({letter}6:{letter}7)"


def _cash_flow(ws: Any) -> None:
    ws.append(["Line Item", *YEARS])
    labels = [
        "Net Income",
        "Depreciation",
        "Change in Working Capital",
        "Operating Cash Flow",
        "Capex",
        "Free Cash Flow",
        "Debt Change",
        "Net Cash Flow",
    ]
    for label in labels:
        ws.append([label, None, None, None])
    for col in range(2, 5):
        letter = get_column_letter(col)
        prior = get_column_letter(col - 1)
        ws[f"{letter}2"] = f"='P&L'!{letter}10"
        ws[f"{letter}3"] = f"='P&L'!{letter}7"
        ws[f"{letter}4"] = (
            f"='P&L'!{letter}2*Assumptions!B10"
            if col == 2
            else f"=('P&L'!{letter}2-'P&L'!{prior}2)*Assumptions!B10"
        )
        ws[f"{letter}5"] = f"={letter}2+{letter}3-{letter}4"
        ws[f"{letter}6"] = f"='P&L'!{letter}2*Assumptions!B8"
        ws[f"{letter}7"] = f"={letter}5-{letter}6"
        ws[f"{letter}8"] = "=0"
        ws[f"{letter}9"] = f"={letter}7+{letter}8"


def _format_workbook(wb: Workbook) -> None:
    fill = PatternFill("solid", fgColor="1F4E79")
    for ws in wb.worksheets:
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = fill
        ws.freeze_panes = "B2"
        for col in range(1, ws.max_column + 1):
            ws.column_dimensions[get_column_letter(col)].width = 22
