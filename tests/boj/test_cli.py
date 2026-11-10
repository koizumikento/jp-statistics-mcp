import json
from unittest.mock import AsyncMock

import pytest

from boj_stats_mcp import cli


def test_cli_uses_public_function(
    monkeypatch: pytest.MonkeyPatch, capsysbinary: pytest.CaptureFixture[bytes]
) -> None:
    payload = {"name": "日本語"}
    handler = AsyncMock(return_value=payload)
    monkeypatch.setattr(cli, "search_series", handler)
    args = ["search-series", "--database", "FM08", "--query", "ドル", "--limit", "1"]
    cli.run_cli(args)
    handler.assert_awaited_once_with(**{"database": "FM08", "query": "ドル", "limit": 1})
    assert json.loads(capsysbinary.readouterr().out) == payload


def test_batch_cli(
    monkeypatch: pytest.MonkeyPatch, capsysbinary: pytest.CaptureFixture[bytes]
) -> None:
    handler = AsyncMock(return_value={"STATUS": 200})
    monkeypatch.setattr(cli, "get_multiple_series_data", handler)
    cli.run_cli(
        [
            "get-multiple-series-data",
            "--database",
            "FM01",
            "--series-code",
            "STRDCLUCON",
            "--series-code",
            "STRDCLUCONH",
            "--start-period",
            "202501",
            "--end-period",
            "202501",
        ]
    )
    handler.assert_awaited_once_with(
        database="FM01",
        series_codes=["STRDCLUCON", "STRDCLUCONH"],
        start_period="202501",
        end_period="202501",
    )
    assert json.loads(capsysbinary.readouterr().out) == {"STATUS": 200}
