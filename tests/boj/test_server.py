import json
import sys

import httpx
import pytest
import respx
from mcp import Client, StdioServerParameters
from mcp.types import TextContent

from boj_stats_mcp import create_server
from boj_stats_mcp.client import BASE_URL


@pytest.mark.asyncio
async def test_stdio_tools() -> None:
    params = StdioServerParameters(command=sys.executable, args=["-m", "boj_stats_mcp"])
    async with Client(params, mode="legacy", read_timeout_seconds=10) as client:
        result = await client.list_tools()
    assert {tool.name for tool in result.tools} == {
        "search_series",
        "get_series_data",
        "get_multiple_series_data",
        "get_series_data_by_layer",
    }
    assert all(tool.annotations and tool.annotations.read_only_hint for tool in result.tools)


@pytest.mark.asyncio
@respx.mock
async def test_tool_response() -> None:
    route = respx.get(
        BASE_URL
        + "getDataCode?db=FM08&code=FXERD04&startDate=202501&endDate=202501&startPosition=1"
    ).mock(
        return_value=httpx.Response(
            200,
            json=json.loads(
                '{"STATUS":200,"RESULTSET":[{"SERIES_CODE":"FXERD04","VALUES":{"VALUES":[null,157.67]}}]}'
            ),
        )
    )
    async with Client(create_server()) as client:
        result = await client.call_tool(
            "get_series_data",
            {
                "database": "FM08",
                "series_code": "FXERD04",
                "start_period": "202501",
                "end_period": "202501",
            },
        )
    assert route.called
    assert not result.is_error
    assert isinstance(result.content[0], TextContent)
    payload = json.loads(result.content[0].text)
    assert payload["RESULTSET"][0]["VALUES"]["VALUES"] == [None, 157.67]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool", "params", "endpoint", "query"),
    [
        (
            "get_multiple_series_data",
            {"series_codes": ["STRDCLUCON", "STRDCLUCONH"]},
            "getDataCode",
            {"code": "STRDCLUCON,STRDCLUCONH"},
        ),
        (
            "get_series_data_by_layer",
            {"frequency": "D", "layer": "1,*"},
            "getDataLayer",
            {"frequency": "D", "layer": "1,*"},
        ),
    ],
)
@respx.mock
async def test_new_data_tools(
    tool: str, params: dict[str, object], endpoint: str, query: dict[str, str]
) -> None:
    response = {"STATUS": 200, "NEXTPOSITION": 7, "RESULTSET": [{"SERIES_CODE": "STRDCLUCON"}]}
    route = respx.get(
        BASE_URL + endpoint,
        params={
            "db": "FM01",
            **query,
            "startDate": "202501",
            "endDate": "202501",
            "startPosition": "2",
        },
    ).respond(json=response)
    async with Client(create_server()) as client:
        result = await client.call_tool(
            tool,
            {
                "database": "FM01",
                **params,
                "start_period": "202501",
                "end_period": "202501",
                "start_position": 2,
            },
        )
    assert route.called
    assert not result.is_error
    assert isinstance(result.content[0], TextContent)
    assert json.loads(result.content[0].text) == response


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("frequency", "period"),
    [("CY", "202501"), ("CH", "202503"), ("Q", "202505"), ("M", "2025")],
)
async def test_layer_rejects_period_for_wrong_frequency(frequency, period) -> None:
    async with Client(create_server()) as client:
        result = await client.call_tool(
            "get_series_data_by_layer",
            {
                "database": "FM01",
                "frequency": frequency,
                "layer": "1",
                "start_period": period,
                "end_period": period,
            },
        )
    assert result.is_error
