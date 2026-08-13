# excel-mcp

An MCP server for safe `.xlsx` inspection and controlled workbook writes.

## Status

This is an MVP. It supports workbook inspection, sheet/schema discovery, reads, search, simple filtering and numeric aggregation, plus preview-based writes. Writes are guarded by workspace confinement, SHA-256 compare-and-swap, a per-workbook lock, backup, temporary-file save, re-open verification, atomic replacement and JSONL audit logging.

Macro-enabled workbooks, external links, charts, formatting operations and non-`.xlsx` files are intentionally out of scope.

## Run

```sh
uv sync --extra dev
EXCEL_MCP_WORKSPACE=/path/to/workspace uv run excel-mcp
```

The MCP server uses the official Python SDK's `FastMCP` and `@mcp.tool()` API.

