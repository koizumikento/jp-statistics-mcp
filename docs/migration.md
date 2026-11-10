# 移行手順

## インストールと登録

```sh
uv add "git+https://github.com/koizumikento/jp-statistics-mcp.git@main"
```

MCPクライアントでは `jp-statistics-mcp` を登録します。登録方法は[README](../README.md#mcpクライアントに登録する)を参照してください。

## CLIとPython

このパッケージには次のコマンドとPythonモジュールが含まれます。既存の引数と公開関数を使えます。

| コマンド | Pythonモジュール | 新しいCLIの指定 |
| --- | --- | --- |
| `e-stat-dashboard-mcp` | `e_stat_dashboard_mcp` | `jp-statistics-mcp dashboard ...` |
| `boj-stats-mcp` | `boj_stats_mcp` | `jp-statistics-mcp boj ...` |

Pythonでは統合パッケージからも関数をインポートできます。データの出典、ページ送り、キャッシュ、認証情報の設定は各データの説明を確認してください。
