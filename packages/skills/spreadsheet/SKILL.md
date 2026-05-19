---
name: spreadsheet
description: Create real Excel workbooks with tables, formulas, charts, financial models, comparison matrices, and cleaned data.
when_to_use: Invoke when a user needs a downloadable spreadsheet, analysis workbook, financial model, comparison matrix, or cleaned tabular data.
capability: spreadsheet
version: 1.0.0
license: MIT
author: Mantle
metadata:
  tags:
    - productivity
    - spreadsheet
    - xlsx
---

# Spreadsheet

Use this skill to create `/workspace/<task>/data.xlsx` from either explicit rows or a workbook plan.

## Scripts

- `scripts/spreadsheet.py` creates workbooks from `schema` + `rows`, `query_plan`, or `mode`.
- `subskills/financial_model.py` creates P&L, balance sheet, and cash-flow tabs with openpyxl formulas.
- `subskills/comparison_matrix.py` creates multi-dimensional feature comparisons.
- `subskills/data_cleaning.py` dedupes, normalizes headers, and type-coerces rows.

## Input

```json
{
  "task": "session-or-task-name",
  "mode": "table",
  "schema": [{"name": "Metric"}, {"name": "Value", "type": "number"}],
  "rows": [{"Metric": "Revenue", "Value": 1200}],
  "charts": [{"type": "bar", "title": "Revenue", "x": "Metric", "y": "Value"}]
}
```

Modes: `table`, `financial_model`, `comparison_matrix`, `data_cleaning`.
