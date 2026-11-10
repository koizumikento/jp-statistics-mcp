from __future__ import annotations

from typing import Annotated, Any, Literal

import httpx
from pydantic import Field, validate_call

BASE_URL = "https://dashboard.e-stat.go.jp/api/1.0/Json/"
Query = Annotated[str, Field(min_length=1, max_length=200, pattern=r"\S")]
Limit = Annotated[int, Field(ge=1, le=100)]
Offset = Annotated[int, Field(ge=0, le=10000)]
IndicatorCode = Annotated[str, Field(pattern=r"^\d{19}$")]
RegionCode = Annotated[str, Field(pattern=r"^(?:[0-9]{3}|[0-9]{5})$")]
Cycle = Literal["1", "2", "3", "4"]


def dashboard_result(result: dict[str, Any]) -> dict[str, Any]:
    status = result["RESULT"]["status"]
    if status not in {"0", "1"}:
        raise ValueError(f"Statistics Dashboard returned status {status}.")
    return result


async def get_response(path: str, **params: str | int | None) -> httpx.Response:
    query = {key: value for key, value in params.items() if value is not None}
    try:
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=20.0) as client:
            response = await client.get(path, params=query)
            response.raise_for_status()
            return response
    except httpx.HTTPStatusError as exc:
        raise ValueError(f"Upstream HTTP error {exc.response.status_code}.") from exc
    except httpx.RequestError as exc:
        raise ValueError("Could not reach the upstream API.") from exc


async def get_json(path: str, **params: str | int | None) -> dict[str, Any]:
    response = await get_response(path, **params)
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("Upstream response was not a JSON object.")
    return data


@validate_call
async def search_indicators(query: Query, limit: Limit = 10, offset: Offset = 0) -> dict[str, Any]:
    """Find indicator codes by Japanese or English text in the indicator name."""
    data = await get_json("getIndicatorInfo")
    result = dashboard_result(data["GET_META_INDICATOR_INF"])
    metadata = result.get("METADATA_INF", {})
    items = metadata.get("CLASS_INF", {}).get("CLASS_OBJ", [])
    matches = [
        {"code": item["@code"], "name": item["@name"]}
        for item in items
        if query.casefold() in item["@name"].casefold()
    ]
    return {
        "total": len(matches),
        "offset": offset,
        "indicators": matches[offset : offset + limit],
    }


@validate_call
async def get_indicator_data(
    indicator_code: IndicatorCode,
    region_code: RegionCode = "00000",
    cycle: Cycle | None = None,
    limit: Limit = 50,
    offset: Offset = 0,
) -> dict[str, Any]:
    """Get series data. Cycles: 1 month, 2 quarter, 3 calendar year, 4 fiscal year."""
    data = await get_json(
        "getData", IndicatorCode=indicator_code, RegionCode=region_code, Cycle=cycle
    )
    result = dashboard_result(data["GET_STATS"])
    statistics = result.get("STATISTICAL_DATA", {})
    rows = statistics.get("DATA_INF", {}).get("DATA_OBJ", [])
    if isinstance(rows, dict):
        rows = [rows]
    return {
        "total": len(rows),
        "offset": offset,
        "observations": rows[offset : offset + limit],
        "metadata": statistics.get("TABLE_INF"),
    }


def _records(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        return [value]
    return value or []


async def _metadata(path: str, envelope: str) -> list[dict[str, Any]]:
    data = await get_json(path)
    result = dashboard_result(data[envelope])
    return _records(result.get("METADATA_INF", {}).get("CLASS_INF", {}).get("CLASS_OBJ"))


def _page(
    records: list[dict[str, Any]], key: str, query: str | None, limit: int, offset: int
) -> dict[str, Any]:
    if query is not None:
        needle = query.strip().casefold()
        records = [
            record
            for record in records
            if any(
                needle in (record.get(field) or "").casefold()
                for field in ("code", "name", "reading")
            )
        ]
    end = offset + limit
    return {
        "total": len(records),
        "offset": offset,
        "next_offset": end if end < len(records) else None,
        key: records[offset:end],
    }


@validate_call
async def search_regions(
    query: Query | None = None, limit: Limit = 10, offset: Offset = 0
) -> dict[str, Any]:
    """Find region codes by name, kana reading or code. Omit query to browse."""
    groups = await _metadata("getRegionInfo", "GET_META_REGION_INF")
    records = [
        {
            "code": item["@regionCode"],
            "name": item["@name"],
            "reading": item.get("@hiragana"),
            "level": item.get("@level"),
            "parent_code": group.get("@parentRegionCode"),
            "parent_name": group.get("@name"),
            "valid_from": item.get("@fromDate"),
            "valid_to": item.get("@toDate"),
        }
        for group in groups
        for item in _records(group.get("CLASS"))
    ]
    return _page(records, "regions", query, limit, offset)


@validate_call
async def search_terms(
    query: Query | None = None, limit: Limit = 10, offset: Offset = 0
) -> dict[str, Any]:
    """Find statistical terms by name or code and read definitions and reference links."""
    groups = await _metadata("getTermInfo", "GET_META_TERM_INFO")
    records = [
        {
            "code": item["@code"],
            "name": item["@name"],
            "category": item.get("@category"),
            "definition": item.get("@detail"),
            "url": item.get("@linkURL"),
        }
        for group in groups
        for item in _records(group.get("CLASS"))
    ]
    return _page(records, "terms", query, limit, offset)


@validate_call
async def search_social_events(
    query: Query | None = None, limit: Limit = 10, offset: Offset = 0
) -> dict[str, Any]:
    """Find social events by name or code, with their periods and statistical categories."""
    groups = await _metadata("getSocialEventInfo", "GET_META_SOCIAL_INFO")
    records = [
        {
            "code": group["@code"],
            "name": group["@name"],
            "level": group.get("@level"),
            "start": group.get("@fromTime"),
            "end": group.get("@toTime"),
            "categories": [
                {"code": item["@code"], "name": item["@name"]}
                for item in _records(group.get("CLASS"))
            ],
        }
        for group in groups
    ]
    return _page(records, "events", query, limit, offset)


@validate_call
async def search_surveys(
    query: Query | None = None, limit: Limit = 10, offset: Offset = 0
) -> dict[str, Any]:
    """Find statistical surveys by name or code, with agency, summary and reference link."""
    groups = await _metadata("getStatInfo", "GET_META_STAT_INFO")
    records = [
        {
            "code": item["@code"],
            "name": item["@name"],
            "agency": item.get("@agency"),
            "kind": item.get("@kind"),
            "summary": item.get("@summary"),
            "url": item.get("@linkUrl"),
        }
        for group in groups
        for item in _records(group.get("CLASS"))
    ]
    return _page(records, "surveys", query, limit, offset)
