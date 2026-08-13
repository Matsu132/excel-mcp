from __future__ import annotations
from typing import Any
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
def excel_filter(path: str, sheet: str, column: int, value: Any) -> list[list[Any]]:
    data = excel_read(path, sheet); return [r for r in data if len(r) >= column and r[column-1] == value]

@mcp.tool()
def excel_aggregate(path: str, sheet: str, column: int, operation: str = "sum") -> float:
    vals=[r[column-1] for r in excel_read(path,sheet) if len(r)>=column and isinstance(r[column-1],(int,float))]
    if operation == "sum": return float(sum(vals))
    if operation == "average": return float(sum(vals)/len(vals)) if vals else 0.0
    if operation == "count": return float(len(vals))
    raise ValueError("operation must be sum, average, or count")

@mcp.tool()
def excel_group_by(path: str, sheet: str, key_column: int, value_column: int) -> dict[str, float]:
    result: dict[str,float]={}
    for r in excel_read(path,sheet):
        if len(r)>max(key_column,value_column)-1 and isinstance(r[value_column-1],(int,float)): result[str(r[key_column-1])] = result.get(str(r[key_column-1]),0)+r[value_column-1]
    return result

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

