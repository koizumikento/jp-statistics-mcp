# 日本銀行の時系列統計

## ツール

| ツール | 用途 |
| --- | --- |
| `search_series` | DB内の系列を系列名・系列コードで検索 |
| `get_series_data` | 1件の系列コードと期間で時系列を取得 |
| `get_multiple_series_data` | 同じDB・期種の複数系列を一括取得（最大250コード） |
| `get_series_data_by_layer` | DB・期種・階層を指定し、配下の系列の時系列を取得 |

`search_series` の結果には `SERIES_CODE`、`FREQUENCY`、`LAYER1`〜`LAYER5` が含まれます。階層は `1,2` のように1〜5段をカンマ区切りで指定し、各段に `*` を使えます。期種は `CY`（暦年）、`FY`（年度）、`CH`（暦年半期）、`FH`（年度半期）、`Q`（四半期）、`M`（月次）、`W`（週次）、`D`（日次）で指定します。

期間は年次なら `YYYY`、半期なら `YYYY` に `01`〜`02`、四半期なら `01`〜`04`、月次・週次・日次なら月を付けます。取得結果の `NEXTPOSITION` が数値なら、同じ条件の `start_position` に指定して続きを取得できます。一括取得では系列コードの並び順も維持します。階層は、期種で絞り込む前の対象が1,250系列以内になるように指定してください。


## 出典と利用条件

コードはMIT Licenseです。取得するデータの権利と利用条件は、API提供元と各データ提供機関の定めに従います。[公式API仕様](https://www.stat-search.boj.or.jp/info/api_manual.pdf) · [利用案内](https://www.stat-search.boj.or.jp/info/nme_aphelp.html)
