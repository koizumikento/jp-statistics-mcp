from __future__ import annotations

from typing import Annotated, Any, Literal

import httpx
from pydantic import Field, validate_call

BASE_URL = "https://www.stat-search.boj.or.jp/api/v1/"
Frequency = Literal["CY", "FY", "CH", "FH", "Q", "M", "W", "D"]
Layer = Annotated[str, Field(pattern=r"^(?:[0-9]+|\*)(?:,(?:[0-9]+|\*)){0,4}$", max_length=50)]
Query = Annotated[str, Field(min_length=1, max_length=200, pattern=r"\S")]
Limit = Annotated[int, Field(ge=1, le=100)]
Offset = Annotated[int, Field(ge=0, le=10000)]
Database = Annotated[str, Field(pattern=r"^[A-Za-z0-9]{2,4}$")]
SeriesCode = Annotated[str, Field(pattern=r"^[A-Za-z0-9_@.+/-]+$", max_length=50)]
Period = Annotated[str, Field(pattern=r"^\d{4}(?:0[1-9]|1[0-2])?$")]


def checked(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("STATUS") != 200:
        raise ValueError(f"BOJ API returned status {data.get('STATUS')}.")
    return data


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
async def search_series(
    database: Database, query: Query, limit: Limit = 10, offset: Offset = 0
) -> dict[str, Any]:
    """Find series by Japanese name, English name or code within a BOJ database."""
    data = checked(await get_json("getMetadata", db=database))
    matches = [
        item
        for item in data["RESULTSET"]
        if item["SERIES_CODE"]
        and any(
            query.casefold() in item[key].casefold()
            for key in ("SERIES_CODE", "NAME_OF_TIME_SERIES_J", "NAME_OF_TIME_SERIES")
        )
    ]
    return {
        "database": data["DB"],
        "total": len(matches),
        "offset": offset,
        "series": matches[offset : offset + limit],
    }


def _check_periods(start_period: str, end_period: str) -> None:
    if len(start_period) != len(end_period) or start_period > end_period:
        raise ValueError("Use matching period formats and put the earlier period first.")


async def _data_by_code(
    database: str, codes: str, start_period: str, end_period: str, start_position: int
) -> dict[str, Any]:
    _check_periods(start_period, end_period)
    return checked(
        await get_json(
            "getDataCode",
            db=database,
            code=codes,
            startDate=start_period,
            endDate=end_period,
            startPosition=start_position,
        )
    )


@validate_call
async def get_series_data(
    database: Database,
    series_code: SeriesCode,
    start_period: Period,
    end_period: Period,
    start_position: Annotated[int, Field(ge=1)] = 1,
) -> dict[str, Any]:
    """Fetch observations for one BOJ series. Periods are YYYY or YYYYMM by frequency."""
    return await _data_by_code(database, series_code, start_period, end_period, start_position)


@validate_call
async def get_multiple_series_data(
    database: Database,
    series_codes: Annotated[list[SeriesCode], Field(min_length=1, max_length=250)],
    start_period: Period,
    end_period: Period,
    start_position: Annotated[int, Field(ge=1)] = 1,
) -> dict[str, Any]:
    """Fetch up to 250 codes from one DB and one frequency. Resume from NEXTPOSITION."""
    return await _data_by_code(
        database, ",".join(series_codes), start_period, end_period, start_position
    )


@validate_call
async def get_series_data_by_layer(
    database: Database,
    frequency: Frequency,
    layer: Layer,
    start_period: Period,
    end_period: Period,
    start_position: Annotated[int, Field(ge=1)] = 1,
) -> dict[str, Any]:
    """Fetch observations by comma-separated layer path (e.g. '1,2,*'). Resume from NEXTPOSITION."""
    _check_periods(start_period, end_period)
    if frequency in ("CY", "FY"):
        if len(start_period) != 4:
            raise ValueError("Use YYYY for calendar-year and fiscal-year series.")
    else:
        last_period = {"CH": "02", "FH": "02", "Q": "04"}.get(frequency, "12")
        if len(start_period) != 6 or start_period[4:] > last_period or end_period[4:] > last_period:
            raise ValueError(f"Use a six-digit period with a suffix from 01 to {last_period}.")
    return checked(
        await get_json(
            "getDataLayer",
            db=database,
            frequency=frequency,
            layer=layer,
            startDate=start_period,
            endDate=end_period,
            startPosition=start_position,
        )
    )
