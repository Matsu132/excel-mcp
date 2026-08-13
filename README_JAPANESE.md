# excel-mcp

安全な`.xlsx`の調査・読み取り・集計・書き込みをMCP経由で提供するサーバーです。

## 対応範囲

以下の機能を提供します。

- Workbook / Sheet / Schemaの確認
- セル範囲の読み取り
- 検索
- フィルター
- 集計・グループ集計
- Preview IDを使った安全な書き込み

書き込み時は、Workspace制限、SHA-256確認、Workbookロック、バックアップ、テンポラリファイル、再オープン検証、atomic replace、監査ログを使用します。

MVPでは`.xlsx`のみ対応しています。`.xlsm`、外部リンク、チャート、書式変更、その他の非`.xlsx`ファイルは対象外です。

## インストール

```sh
uv sync
```

サーバーがアクセスできるExcelファイルのディレクトリを指定します。

```sh
export EXCEL_MCP_WORKSPACE="/absolute/path/to/workbooks"
```

Workspace外のファイルにはアクセスできません。相対パスはWorkspaceを基準に解決されます。

## サーバーの起動

本サーバーはMCPのstdio transportを使用します。基本的な起動コマンドは次のとおりです。

```sh
EXCEL_MCP_WORKSPACE="/absolute/path/to/workbooks" uv run excel-mcp
```

通常はMCPクライアント側にこのコマンドを登録します。クライアントがプロセスを自動起動・管理します。

## Claude Desktop

Claude DesktopのMCP設定ファイルに、以下を追加します。パスは実際の環境に合わせて絶対パスへ変更してください。

macOSの設定ファイル：

```text
~/Library/Application Support/Claude/claude_desktop_config.json
```

設定例：

```json
{
  "mcpServers": {
    "excel-mcp": {
      "command": "/absolute/path/to/project/.venv/bin/python",
      "args": ["-m", "excel_mcp.server"],
      "env": {
        "EXCEL_MCP_WORKSPACE": "/absolute/path/to/workbooks",
        "PYTHONPATH": "/absolute/path/to/project/src"
      }
    }
  }
}
```

保存後にClaude Desktopを再起動してください。`excel_*`ツールが表示されれば接続成功です。

## OpenAI向けクライアント

OpenAIアプリケーション、Agent SDK、またはローカルMCP stdioサーバーに対応したOpenAI系クライアントでは、次の定義を登録します。

```json
{
  "name": "excel-mcp",
  "command": "/absolute/path/to/project/.venv/bin/python",
  "args": ["-m", "excel_mcp.server"],
  "env": {
    "EXCEL_MCP_WORKSPACE": "/absolute/path/to/workbooks",
    "PYTHONPATH": "/absolute/path/to/project/src"
  }
}
```

製品ごとに設定項目名は異なりますが、`command`、`args`、`env`をローカルMCP / stdioサーバーの設定へ対応付けてください。リモートMCPエンドポイントにしか対応していないクライアントで利用する場合は、HTTP transportでのデプロイが別途必要です。

## その他のMCPクライアント

Cursor、VS CodeのMCP拡張、Cline、Windsurfなど、多くのMCPクライアントは同じstdio設定を利用できます。

```text
Command: /absolute/path/to/project/.venv/bin/python
Arguments: -m excel_mcp.server
Environment: EXCEL_MCP_WORKSPACE=/absolute/path/to/workbooks
             PYTHONPATH=/absolute/path/to/project/src
```

MCP Inspectorで確認する場合：

```sh
EXCEL_MCP_WORKSPACE="/absolute/path/to/workbooks" uv run mcp dev src/excel_mcp/server.py
```

## 開発用チェック

```sh
uv sync --extra dev
uv run pytest -q
uv run ruff check .
uv run mypy src
```

## SDKについて

現在は公式MCP Python SDKのv1系APIである`FastMCP`と`@mcp.tool()`を使用し、`mcp>=1.28,<2`に固定しています。SDK v2への移行は、MCPクライアントとの互換性とtransportの動作を確認したうえで行う予定です。
