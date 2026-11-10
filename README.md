# jp-statistics-mcp

統計ダッシュボードの指標と、日本銀行の時系列統計を調べるMCPサーバーです。MCP、CLI、Pythonライブラリから同じ機能を使えます。

[準備](#準備) · [MCP登録](#mcpクライアントに登録する) · [CLI](#cliで使う) · [Python](#pythonで使う) · [移行手順](docs/migration.md)

## 準備

Python 3.12以上、[uv](https://docs.astral.sh/uv/)、Gitが必要です。

```sh
git clone https://github.com/koizumikento/jp-statistics-mcp.git
cd jp-statistics-mcp
uv sync --locked
```

APIキーは不要です。

## MCPクライアントに登録する

設定例の `/absolute/path/to/jp-statistics-mcp` をクローン先の絶対パスに置き換えます。Windowsでは `C:/projects/jp-statistics-mcp` のように書けます。

### Codex

```sh
codex mcp add jp-statistics-mcp -- uv --directory "/absolute/path/to/jp-statistics-mcp" run --locked jp-statistics-mcp
codex mcp list
```

新しいセッションで `/mcp` を開いて接続状態を確認します。

### Claude Desktop / Cursor

Claude DesktopはOSに応じて次のファイルに設定します。

- Windowsは `%APPDATA%/Claude/claude_desktop_config.json`
- macOSは `~/Library/Application Support/Claude/claude_desktop_config.json`

Cursorはプロジェクト内の `.cursor/mcp.json` を使います。`mcpServers` に次の項目を追加し、クライアントを再起動してください。

```json
{
  "mcpServers": {
    "jp-statistics-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/jp-statistics-mcp",
        "run",
        "--locked",
        "jp-statistics-mcp"
      ]
    }
  }
}
```

`uv` が見つからない場合は、`command` に実行ファイルの絶対パスを指定してください。

## ツール

データごとの入力条件、結果、出典と利用条件は、表のリンク先に記載しています。

| ツール | データと操作の説明 |
| --- | --- |
| `search_indicators` | [統計ダッシュボード](docs/dashboard.md) |
| `get_indicator_data` | [統計ダッシュボード](docs/dashboard.md) |
| `search_regions` | [統計ダッシュボード](docs/dashboard.md) |
| `search_terms` | [統計ダッシュボード](docs/dashboard.md) |
| `search_social_events` | [統計ダッシュボード](docs/dashboard.md) |
| `search_surveys` | [統計ダッシュボード](docs/dashboard.md) |
| `search_series` | [日本銀行の時系列統計](docs/boj.md) |
| `get_series_data` | [日本銀行の時系列統計](docs/boj.md) |
| `get_multiple_series_data` | [日本銀行の時系列統計](docs/boj.md) |
| `get_series_data_by_layer` | [日本銀行の時系列統計](docs/boj.md) |

## CLIで使う

クローン先で実行します。取得結果はUTF-8のJSONとして標準出力に書き出します。

```sh
uv run jp-statistics-mcp dashboard search-indicators --query 総人口 --limit 3
uv run jp-statistics-mcp boj search-series --database fm08 --query ドル --limit 3
```

引数の説明は、各サブコマンドに `--help` を付けて確認できます。

## Pythonで使う

自分のPythonプロジェクトの依存関係に追加します。

```sh
uv add "git+https://github.com/koizumikento/jp-statistics-mcp.git@main"
```

次のコードを `example.py` に保存し、`uv run python example.py` で実行します。

```python
import asyncio

from jp_statistics_mcp import search_indicators

result = asyncio.run(search_indicators(query="総人口", limit=3))
print(result)
```

ツールと同じ名前の非同期関数を利用できます。すでにイベントループがある場合は、直接 `await` してください。

## 出典と利用条件

コードはMITライセンスです。データは実行時に各提供元から取得します。取得データには、データ別の説明に記載した提供元の利用条件が適用されます。

## 開発

```sh
uv sync --locked
uv run ruff check .
uv run ty check
uv run pytest
uv build
```
