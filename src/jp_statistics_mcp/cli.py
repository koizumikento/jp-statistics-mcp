from argparse import ArgumentParser
from collections.abc import Sequence

from boj_stats_mcp.cli import run_cli as boj_cli
from e_stat_dashboard_mcp.cli import run_cli as dashboard_cli


def run_cli(argv: Sequence[str]) -> None:
    parser = ArgumentParser(prog="jp-statistics-mcp")
    commands = parser.add_subparsers(required=True)
    commands.add_parser("dashboard", help="統計ダッシュボード", add_help=False).set_defaults(
        handler=dashboard_cli
    )
    commands.add_parser("boj", help="日本銀行の時系列統計", add_help=False).set_defaults(
        handler=boj_cli
    )
    arguments, remaining = parser.parse_known_args(argv)
    arguments.handler(remaining)
