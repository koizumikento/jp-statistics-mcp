import json
import sys

import httpx
import pytest
import respx
from mcp import Client, StdioServerParameters
from mcp.types import TextContent

from e_stat_dashboard_mcp import create_server
from e_stat_dashboard_mcp.client import BASE_URL


@pytest.mark.asyncio
async def test_stdio_tools() -> None:
    params = StdioServerParameters(command=sys.executable, args=["-m", "e_stat_dashboard_mcp"])
    async with Client(params, mode="legacy", read_timeout_seconds=10) as client:
        result = await client.list_tools()
    assert {tool.name for tool in result.tools} == {
        "search_indicators",
        "get_indicator_data",
        "search_regions",
        "search_terms",
        "search_social_events",
        "search_surveys",
    }
    assert all(tool.annotations and tool.annotations.read_only_hint for tool in result.tools)


@pytest.mark.asyncio
@respx.mock
async def test_tool_response() -> None:
    route = respx.get(BASE_URL + "getData?IndicatorCode=0201010000000010000&RegionCode=00000").mock(
        return_value=httpx.Response(
            200,
            json=json.loads(
                '{"GET_STATS":{"RESULT":{"status":"0"},"STATISTICAL_DATA":{"DATA_INF":{"DATA_OBJ":[{"VALUE":{"$":"123"}},{"VALUE":{"$":"456"}}]}}}}'
            ),
        )
    )
    async with Client(create_server()) as client:
        result = await client.call_tool(
            "get_indicator_data", {"indicator_code": "0201010000000010000", "limit": 1}
        )
    assert route.called
    assert not result.is_error
    assert isinstance(result.content[0], TextContent)
    payload = json.loads(result.content[0].text)
    assert payload["total"] == 2
    assert payload["observations"] == [{"VALUE": {"$": "123"}}]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool", "path", "envelope", "group", "key", "expected"),
    [
        (
            "search_regions",
            "getRegionInfo",
            "GET_META_REGION_INF",
            {
                "@parentRegionCode": "10000",
                "@name": "親地域",
                "CLASS": [
                    {"@regionCode": "10001", "@name": "一", "@hiragana": "サンプル一"},
                    {"@regionCode": "10002", "@name": "二", "@hiragana": "サンプル二"},
                ],
            },
            "regions",
            {"code": "10001", "parent_code": "10000", "reading": "サンプル一"},
        ),
        (
            "search_terms",
            "getTermInfo",
            "GET_META_TERM_INFO",
            {"CLASS": {"@code": "01", "@name": "サンプル", "@detail": "定義"}},
            "terms",
            {"code": "01", "definition": "定義"},
        ),
        (
            "search_social_events",
            "getSocialEventInfo",
            "GET_META_SOCIAL_INFO",
            {
                "@code": "02",
                "@name": "サンプル",
                "@fromTime": "2025年1月",
                "CLASS": {"@code": "1403", "@name": "災害"},
            },
            "events",
            {"code": "02", "start": "2025年1月", "categories": [{"code": "1403", "name": "災害"}]},
        ),
        (
            "search_surveys",
            "getStatInfo",
            "GET_META_STAT_INFO",
            {"CLASS": {"@code": "03", "@name": "サンプル", "@agency": "総務省"}},
            "surveys",
            {"code": "03", "agency": "総務省"},
        ),
    ],
)
@respx.mock
async def test_metadata_tool(tool, path, envelope, group, key, expected) -> None:
    route = respx.get(BASE_URL + path).respond(
        json={
            envelope: {
                "RESULT": {"status": "0"},
                "METADATA_INF": {"CLASS_INF": {"CLASS_OBJ": group}},
            }
        }
    )
    async with Client(create_server()) as client:
        result = await client.call_tool(tool, {"query": "サンプル", "limit": 1})
        assert not result.is_error
        assert isinstance(result.content[0], TextContent)
        payload = json.loads(result.content[0].text)
        assert len(payload[key]) == 1
        assert all(payload[key][0][field] == value for field, value in expected.items())
        if key == "regions":
            assert payload["total"] == 2
            assert payload["next_offset"] == 1
            result = await client.call_tool(
                tool, {"query": "サンプル", "limit": 1, "offset": payload["next_offset"]}
            )
            assert not result.is_error
            assert isinstance(result.content[0], TextContent)
            payload = json.loads(result.content[0].text)
            assert payload[key][0]["code"] == "10002"
        assert payload["next_offset"] is None
    assert route.called
