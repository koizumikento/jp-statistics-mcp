# 統計ダッシュボード

## ツール

| ツール | 用途 |
| --- | --- |
| `search_indicators` | 指標名から系列コードを検索 |
| `get_indicator_data` | 系列コード、任意の地域・周期で統計値を取得 |
| `search_regions` | 地域名・よみ・コードで検索し、親地域とコードの有効期間を確認 |
| `search_terms` | 統計用語の定義と参照先を検索 |
| `search_social_events` | 社会的な出来事を探し、時期と関連分野を確認 |
| `search_surveys` | 統計調査を探し、実施機関・調査概要・参照先を確認 |

地域別の統計値を調べるときは、`search_indicators` の系列コードと `search_regions` の地域コードを `get_indicator_data` に渡します。地域コードには、先頭のゼロを含めてください。

1回の返却件数は最大100件です。地域・用語・出来事・調査は `query` を省略して一覧を表示できます。結果の `next_offset` が数値なら、同じ条件で次の呼び出しの `offset` に指定します。


## 出典と利用条件

コードはMIT Licenseです。取得するデータの権利と利用条件は、API提供元と各データ提供機関の定めに従います。[公式API仕様](https://dashboard.e-stat.go.jp/static/api) · [利用案内](https://dashboard.e-stat.go.jp/static/api)

このサービスは、統計ダッシュボードのAPI機能を使用していますが、サービスの内容は国によって保証されたものではありません。
