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

## GitHubから直接使う（推奨）

このリポジトリをcloneしたり、Pythonの依存パッケージを手動でインストールしたりする必要はありません。[uv](https://docs.astral.sh/uv/getting-started/installation/)を一度だけインストールし、MCPクライアントからGitHubのURLを指定して起動できます。

起動コマンド：

```sh
uvx --from git+https://github.com/Matsu132/excel-mcp.git excel-mcp
```

設定が必要なのは、Excelファイルを置くローカルフォルダだけです。

```text
EXCEL_MCP_WORKSPACE=/Users/your-name/Documents/Excel
```

Excelファイルは利用者のPCから外へ送信されません。GitHubから取得するのはMCPサーバー本体と依存関係だけです。

## 開発者向けインストール

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
EXCEL_MCP_WORKSPACE="/Users/your-name/Documents/Excel" uvx --from git+https://github.com/Matsu132/excel-mcp.git excel-mcp
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
      "command": "uvx",
      "args": ["--from", "git+https://github.com/Matsu132/excel-mcp.git", "excel-mcp"],
      "env": {
        "EXCEL_MCP_WORKSPACE": "/Users/your-name/Documents/Excel"
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
  "command": "uvx",
  "args": ["--from", "git+https://github.com/Matsu132/excel-mcp.git", "excel-mcp"],
  "env": {
    "EXCEL_MCP_WORKSPACE": "/Users/your-name/Documents/Excel"
  }
}
```

製品ごとに設定項目名は異なりますが、`command`、`args`、`env`をローカルMCP / stdioサーバーの設定へ対応付けてください。リモートMCPエンドポイントにしか対応していないクライアントで利用する場合は、HTTP transportでのデプロイが別途必要です。

## その他のMCPクライアント

Cursor、VS CodeのMCP拡張、Cline、Windsurfなど、多くのMCPクライアントは同じstdio設定を利用できます。

```text
Command: uvx
Arguments: --from git+https://github.com/Matsu132/excel-mcp.git excel-mcp
Environment: EXCEL_MCP_WORKSPACE=/Users/your-name/Documents/Excel
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

## MCP SDKについて

本プロジェクトは公式MCP Python SDK v2を使用しています。サーバーは`MCPServer`と`@mcp.tool()`で構成され、ローカルMCPクライアント向けの標準transportはstdioです。詳しくは[公式v2ドキュメント](https://py.sdk.modelcontextprotocol.io/)を参照してください。
