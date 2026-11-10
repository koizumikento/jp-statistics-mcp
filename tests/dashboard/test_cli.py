import json
from unittest.mock import AsyncMock

import pytest

from e_stat_dashboard_mcp import cli


def test_cli_uses_public_function(
    monkeypatch: pytest.MonkeyPatch, capsysbinary: pytest.CaptureFixture[bytes]
) -> None:
    payload = {"name": "日本語"}
    handler = AsyncMock(return_value=payload)
    monkeypatch.setattr(cli, "search_indicators", handler)
    args = ["search-indicators", "--query", "総人口", "--limit", "1"]
    cli.run_cli(args)
    handler.assert_awaited_once_with(**{"query": "総人口", "limit": 1})
    assert json.loads(capsysbinary.readouterr().out) == payload


def test_metadata_cli(
    monkeypatch: pytest.MonkeyPatch, capsysbinary: pytest.CaptureFixture[bytes]
) -> None:
    handler = AsyncMock(return_value={"regions": [{"code": "13000", "name": "東京都"}]})
    monkeypatch.setattr(cli, "search_regions", handler)
    cli.run_cli(["search-regions", "--query", "東京都", "--offset", "2"])
    handler.assert_awaited_once_with(query="東京都", offset=2)
    assert json.loads(capsysbinary.readouterr().out)["regions"][0]["code"] == "13000"
