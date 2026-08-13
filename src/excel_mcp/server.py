from __future__ import annotations
from typing import Any
import pandas as pd
from mcp.server.fastmcp import FastMCP
from .domain import ReadRequest, WorkbookRequest, WritePreviewRequest
from .infrastructure import Audit, PreviewStore, SecurityError, WorkbookStore, Workspace, rows, sha256

mcp = FastMCP("excel-mcp")
workspace, store, previews = Workspace(), None, PreviewStore()
store = WorkbookStore(workspace); audit = Audit(workspace)

def _wb(req: WorkbookRequest):
    p = store.path(req.path); return p, store.load(p)

@mcp.tool()
def excel_inspect(path: str) -> dict[str, Any]:
    p, wb = _wb(WorkbookRequest(path=path)); result = {"path": str(p), "sha256": sha256(p), "sheets": wb.sheetnames, "size": p.stat().st_size}; wb.close(); return result

@mcp.tool()
def excel_list_sheets(path: str) -> list[str]:
    _, wb = _wb(WorkbookRequest(path=path)); result = wb.sheetnames; wb.close(); return result

@mcp.tool()
def excel_schema(path: str, sheet: str) -> dict[str, Any]:
    _, wb = _wb(WorkbookRequest(path=path)); ws = wb[sheet]; result = {"sheet": sheet, "max_row": ws.max_row, "max_column": ws.max_column, "headers": [ws.cell(1,c).value for c in range(1, ws.max_column+1)]}; wb.close(); return result

@mcp.tool()
def excel_read(path: str, sheet: str, range: str | None = None, max_rows: int = 1000) -> list[list[Any]]:
    _, wb = _wb(WorkbookRequest(path=path)); result = rows(wb[sheet], range, max_rows); wb.close(); return result

@mcp.tool()
def excel_search(path: str, query: str, sheet: str | None = None) -> list[dict[str, Any]]:
    _, wb = _wb(WorkbookRequest(path=path)); out=[]
    for ws in wb.worksheets if sheet is None else [wb[sheet]]:
        for row in ws.iter_rows():
            for cell in row:
                if query.lower() in str(cell.value).lower(): out.append({"sheet": ws.title, "cell": cell.coordinate, "value": cell.value})
    wb.close(); return out

@mcp.tool()
def _frame(path: str, sheet: str) -> pd.DataFrame:
    data = excel_read(path, sheet)
    if not data: return pd.DataFrame()
    return pd.DataFrame(data[1:], columns=[str(x) if x is not None else f"column_{i+1}" for i, x in enumerate(data[0])])

def _mask(series: pd.Series, operator: str, value: Any) -> pd.Series:
    if operator == "eq": return series == value
    if operator == "ne": return series != value
    if operator == "gt": return series > value
    if operator == "gte": return series >= value
    if operator == "lt": return series < value
    if operator == "lte": return series <= value
    if operator == "contains": return series.astype(str).str.contains(str(value), case=False, na=False)
    if operator == "in": return series.isin(value)
    raise ValueError("unsupported filter operator")

@mcp.tool()
def excel_filter(path: str, sheet: str, column: int, value: Any, operator: str = "eq") -> list[list[Any]]:
    frame = _frame(path, sheet)
    if frame.empty: return []
    result = frame[_mask(frame.iloc[:, column - 1], operator, value)]
    return [list(frame.columns)] + result.where(pd.notna(result), None).values.tolist()

@mcp.tool()
def excel_aggregate(path: str, sheet: str, column: int, operation: str = "sum") -> float:
    frame = _frame(path, sheet)
    if frame.empty: return 0.0
    values = pd.to_numeric(frame.iloc[:, column - 1], errors="coerce")
    if operation == "sum": return float(values.sum())
    if operation in ("average", "mean"): return float(values.mean()) if values.notna().any() else 0.0
    if operation == "count": return float(values.count())
    if operation == "min": return float(values.min())
    if operation == "max": return float(values.max())
    raise ValueError("operation must be sum, average, mean, min, max, or count")

@mcp.tool()
def excel_group_by(path: str, sheet: str, key_column: int, value_column: int) -> dict[str, float]:
    frame = _frame(path, sheet)
    if frame.empty: return {}
    values = pd.to_numeric(frame.iloc[:, value_column - 1], errors="coerce")
    grouped = values.groupby(frame.iloc[:, key_column - 1]).sum(min_count=1)
    return {str(k): float(v) for k, v in grouped.dropna().items()}

@mcp.tool()
def excel_group_by_advanced(path: str, sheet: str, key_column: int, value_column: int, operation: str = "sum") -> dict[str, float]:
    frame = _frame(path, sheet)
    if frame.empty: return {}
    values = pd.to_numeric(frame.iloc[:, value_column - 1], errors="coerce")
    grouped = values.groupby(frame.iloc[:, key_column - 1])
    if operation == "sum": result = grouped.sum(min_count=1)
    elif operation in ("average", "mean"): result = grouped.mean()
    elif operation == "count": result = grouped.count()
    elif operation == "min": result = grouped.min()
    elif operation == "max": result = grouped.max()
    else: raise ValueError("operation must be sum, average, mean, min, or max")
    return {str(k): float(v) for k, v in result.dropna().items()}

@mcp.tool()
def excel_preview_write(path: str, sheet: str, values: list[list[Any]], cell: str | None = None, range: str | None = None) -> dict[str, Any]:
    if (cell is None) == (range is None): raise ValueError("provide exactly one of cell or range")
    p=store.path(path); wb=store.load(p); wb.close(); pid=previews.put({"path":str(p),"sheet":sheet,"values":values,"cell":cell,"range":range,"sha256":sha256(p)}); return previews.items[pid]

def _apply(wb: Any, item: dict[str,Any]) -> None:
    ws=wb[item["sheet"]]
    if item["cell"]:
        for i,row in enumerate(item["values"]):
            for j,val in enumerate(row): ws.cell(ws[item["cell"]].row+i, ws[item["cell"]].column+j).value=val
    else:
        for row, vals in zip(ws[item["range"]], item["values"]):
            for cell,val in zip(row,vals): cell.value=val

@mcp.tool()
def excel_write_cell(preview_id: str) -> dict[str, Any]: return _commit(preview_id)
@mcp.tool()
def excel_write_range(preview_id: str) -> dict[str, Any]: return _commit(preview_id)
def _commit(pid: str) -> dict[str,Any]:
    item=previews.pop(pid); p=store.path(item["path"]); store.commit(p,item["sha256"],lambda wb:_apply(wb,item)); event={"preview_id":pid,"path":str(p),"sha256":sha256(p)}; audit.write(event); return {"committed":True,**event}

def main() -> None: mcp.run()
