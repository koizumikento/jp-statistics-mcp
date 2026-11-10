import subprocess
import sys

import pytest
from mcp import Client, StdioServerParameters

from boj_stats_mcp import cli as boj_cli
from boj_stats_mcp.server import create_server as boj_server
from e_stat_dashboard_mcp import cli as dashboard_cli
from e_stat_dashboard_mcp.server import create_server as dashboard_server
from jp_statistics_mcp import create_server
from jp_statistics_mcp.cli import run_cli


@pytest.mark.asyncio
async def test_combined_tools_preserve_source_schemas() -> None:
    expected = []
    for factory in (
        dashboard_server,
        boj_server,
    ):
        expected.extend(await factory().list_tools())
    actual = await create_server().list_tools()
    assert len(actual) == 10
    assert len({tool.name for tool in actual}) == len(actual)
    assert {tool.name: tool.model_dump(exclude_none=True) for tool in actual} == {
        tool.name: tool.model_dump(exclude_none=True) for tool in expected
    }


@pytest.mark.asyncio
async def test_combined_stdio_lists_all_tools() -> None:
    params = StdioServerParameters(command=sys.executable, args=["-m", "jp_statistics_mcp"])
    async with Client(params, mode="legacy", read_timeout_seconds=10) as client:
        result = await client.list_tools()
    assert len(result.tools) == 10
    assert all(tool.annotations and tool.annotations.read_only_hint for tool in result.tools)


@pytest.mark.parametrize("group, module", [("dashboard", dashboard_cli), ("boj", boj_cli)])
def test_cli_dispatches_without_changing_arguments(monkeypatch, group, module) -> None:
    calls = []
    monkeypatch.setattr(module, "run_cli", lambda args: calls.append(list(args)))
    from jp_statistics_mcp import cli

    monkeypatch.setattr(cli, group.replace("-", "_") + "_cli", module.run_cli)
    run_cli([group, "query", "--limit", "2"])
    assert calls == [["query", "--limit", "2"]]


def test_command_help() -> None:
    for group in ["dashboard", "boj"]:
        result = subprocess.run(
            [sys.executable, "-m", "jp_statistics_mcp", group, "--help"],
            capture_output=True,
            check=True,
        )
        assert b"usage:" in result.stdout
