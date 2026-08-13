# excel-mcp

An MCP server for safe `.xlsx` inspection and controlled workbook writes.

## Status

This is an MVP. It supports workbook inspection, sheet/schema discovery, reads, search, simple filtering and numeric aggregation, plus preview-based writes. Writes are guarded by workspace confinement, SHA-256 compare-and-swap, a per-workbook lock, backup, temporary-file save, re-open verification, atomic replacement and JSONL audit logging.

Macro-enabled workbooks, external links, charts, formatting operations and non-`.xlsx` files are intentionally out of scope.

## Quick start from GitHub

You do not need to clone this repository. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) once, then configure your MCP client to run the latest version directly from GitHub.

The command is:

```sh
uvx --from git+https://github.com/Matsu132/excel-mcp.git excel-mcp
```

The only local setting you need is the folder containing the Excel files:

```text
EXCEL_MCP_WORKSPACE=/Users/your-name/Documents/Excel
```

This keeps Excel data on your computer. The public GitHub repository provides the server code and dependencies; it does not upload your workbooks.

## Developer installation

```sh
uv sync
```

Set the workbook directory that the server is allowed to access:

```sh
export EXCEL_MCP_WORKSPACE="/absolute/path/to/workbooks"
```

The server accepts only `.xlsx` files inside this directory. Relative paths are resolved from this workspace.

## Starting the server

This server uses MCP over stdio. The command to register in an MCP client is:

```sh
uvx --from git+https://github.com/Matsu132/excel-mcp.git excel-mcp
```

For a direct local check:

```sh
EXCEL_MCP_WORKSPACE="/absolute/path/to/workbooks" uv run excel-mcp
```

Keep the process running when the client starts it; MCP clients normally manage the process lifecycle automatically.

## Claude Desktop

Add the following entry to Claude Desktop's MCP configuration file. Replace the paths with absolute paths on your machine.

macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "excel-mcp": {
  "command": "uvx",
      "args": ["--from", "git+https://github.com/Matsu132/excel-mcp.git", "excel-mcp"],
      "env": {
        "EXCEL_MCP_WORKSPACE": "/Users/your-name/Documents/Excel"
      }
    }
  }
}
```

Restart Claude Desktop after saving the file. The `excel_*` tools should then appear in the MCP tools list.

## OpenAI-compatible clients

For an OpenAI application, Agent SDK, or other client that supports local MCP stdio servers, register the same command as a local MCP server:

```json
{
  "name": "excel-mcp",
  "command": "uvx",
  "args": ["--from", "git+https://github.com/Matsu132/excel-mcp.git", "excel-mcp"],
  "env": {
    "EXCEL_MCP_WORKSPACE": "/Users/your-name/Documents/Excel"
  }
}
```

The exact configuration key varies by product. Use the product's local MCP or stdio server setting and map it to `command`, `args`, and `env` above. If the client only supports remote MCP endpoints, this repository needs an HTTP transport deployment before it can be used directly.

## Other MCP clients

Clients such as Cursor, VS Code MCP extensions, Cline, Windsurf, and MCP Inspector generally accept the same stdio definition. Use:

```text
Command: uvx
Arguments: --from git+https://github.com/Matsu132/excel-mcp.git excel-mcp
Environment: EXCEL_MCP_WORKSPACE=/Users/your-name/Documents/Excel
```

For MCP Inspector, run:

```sh
EXCEL_MCP_WORKSPACE="/absolute/path/to/workbooks" uv run mcp dev src/excel_mcp/server.py
```

## Japanese documentation

日本語のセットアップ手順は [README_JAPANESE.md](README_JAPANESE.md) を参照してください。

## MCP SDK

This project uses the official MCP Python SDK v2 with `MCPServer` and `@mcp.tool()`. The default transport is stdio for local MCP clients. See the [official v2 documentation](https://py.sdk.modelcontextprotocol.io/) for the SDK API and transport details.
