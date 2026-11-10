import asyncio
import json
import sys
from argparse import SUPPRESS, ArgumentParser
from collections.abc import Sequence

import httpx

from .client import (
    get_indicator_data,
    search_indicators,
    search_regions,
    search_social_events,
    search_surveys,
    search_terms,
)


def run_cli(argv: Sequence[str]) -> None:
    parser = ArgumentParser(prog="e-stat-dashboard-mcp")
    commands = parser.add_subparsers(required=True)

    command = commands.add_parser(
        "search-indicators", help="Find indicator codes by name.", argument_default=SUPPRESS
    )
    command.add_argument("--query", required=True)
    command.add_argument("--limit", type=int)
    command.add_argument("--offset", type=int)
    command.set_defaults(handler=search_indicators)

    command = commands.add_parser(
        "get-indicator-data", help="Get statistics for an indicator.", argument_default=SUPPRESS
    )
    command.add_argument("--indicator-code", required=True)
    command.add_argument("--region-code")
    command.add_argument("--cycle", choices=("1", "2", "3", "4"))
    command.add_argument("--limit", type=int)
    command.add_argument("--offset", type=int)
    command.set_defaults(handler=get_indicator_data)

    for name, help_text, handler in (
        ("search-regions", "Find region codes.", search_regions),
        ("search-terms", "Find statistical terms.", search_terms),
        ("search-social-events", "Find social events.", search_social_events),
        ("search-surveys", "Find statistical surveys.", search_surveys),
    ):
        command = commands.add_parser(name, help=help_text, argument_default=SUPPRESS)
        command.add_argument("--query")
        command.add_argument("--limit", type=int)
        command.add_argument("--offset", type=int)
        command.set_defaults(handler=handler)

    arguments = vars(parser.parse_args(argv))
    handler = arguments.pop("handler")
    try:
        result = asyncio.run(handler(**arguments))
        payload = result
    except (ValueError, OSError, httpx.HTTPError) as exc:
        parser.exit(1, f"{parser.prog}: {exc}\n")
    sys.stdout.buffer.write((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
