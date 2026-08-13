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

## SDK v2 migration decision

The server currently pins `mcp>=1.20,<2` because the implementation uses the v1 `FastMCP` API. The official SDK v2 line is now stable and changes the minimal server entry point to `MCPServer`; migration should be a separate compatibility change after validating transport behavior and client interoperability. The Excel application and infrastructure layers are intentionally independent of this adapter, so the migration is limited to `server.py`, startup wiring and MCP integration tests.
