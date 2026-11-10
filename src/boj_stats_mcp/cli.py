import asyncio
import json
import sys
from argparse import SUPPRESS, ArgumentParser
from collections.abc import Sequence
from typing import get_args

import httpx

from .client import (
    Frequency,
    get_multiple_series_data,
    get_series_data,
    get_series_data_by_layer,
    search_series,
)


def run_cli(argv: Sequence[str]) -> None:
    parser = ArgumentParser(prog="boj-stats-mcp")
    commands = parser.add_subparsers(required=True)

    command = commands.add_parser(
        "search-series", help="Search series within a BOJ database.", argument_default=SUPPRESS
    )
    command.add_argument("--database", required=True)
    command.add_argument("--query", required=True)
    command.add_argument("--limit", type=int)
    command.add_argument("--offset", type=int)
    command.set_defaults(handler=search_series)

    command = commands.add_parser(
        "get-series-data", help="Get observations for a BOJ series.", argument_default=SUPPRESS
    )
    command.add_argument("--database", required=True)
    command.add_argument("--series-code", required=True)
    command.add_argument("--start-period", required=True)
    command.add_argument("--end-period", required=True)
    command.add_argument("--start-position", type=int)
    command.set_defaults(handler=get_series_data)

    command = commands.add_parser(
        "get-multiple-series-data",
        help="Get observations for multiple codes with the same frequency.",
        argument_default=SUPPRESS,
    )
    command.add_argument("--database", required=True)
    command.add_argument("--series-code", action="append", dest="series_codes", required=True)
    command.add_argument("--start-period", required=True)
    command.add_argument("--end-period", required=True)
    command.add_argument("--start-position", type=int)
    command.set_defaults(handler=get_multiple_series_data)

    command = commands.add_parser(
        "get-series-data-by-layer",
        help="Get observations for a frequency and layer path.",
        argument_default=SUPPRESS,
    )
    command.add_argument("--database", required=True)
    command.add_argument("--frequency", choices=get_args(Frequency), required=True)
    command.add_argument("--layer", required=True, help="Comma-separated path, e.g. 1,2,*.")
    command.add_argument("--start-period", required=True)
    command.add_argument("--end-period", required=True)
    command.add_argument("--start-position", type=int)
    command.set_defaults(handler=get_series_data_by_layer)

    arguments = vars(parser.parse_args(argv))
    handler = arguments.pop("handler")
    try:
        result = asyncio.run(handler(**arguments))
        payload = result
    except (ValueError, OSError, httpx.HTTPError) as exc:
        parser.exit(1, f"{parser.prog}: {exc}\n")
    sys.stdout.buffer.write((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
