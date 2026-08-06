"""httpx와 asyncio.gather로 세 공개 API를 동시에 호출합니다."""

import asyncio
from typing import Any

import httpx

from app.config import COUNTRY_URL, IP_URL, WEATHER_URL


class ApiFetchError(RuntimeError):
    """API 요청 또는 응답 형식이 잘못되었을 때 발생합니다."""


async def fetch_json(
    client: httpx.AsyncClient,
    name: str,
    url: str,
) -> tuple[str, dict[str, Any]]:
    """API 하나를 호출하고 JSON 객체를 반환합니다."""
    try:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPStatusError as exc:
        raise ApiFetchError(
            f"{name} HTTP 오류: {exc.response.status_code}"
        ) from exc
    except httpx.RequestError as exc:
        raise ApiFetchError(f"{name} 네트워크 오류: {exc}") from exc
    except ValueError as exc:
        raise ApiFetchError(f"{name} JSON 변환 오류") from exc

    if not isinstance(data, dict):
        raise ApiFetchError(f"{name} 응답이 JSON 객체가 아닙니다.")
    return name, data


async def fetch_all_data(
    client: httpx.AsyncClient,
) -> dict[str, dict[str, Any]]:
    """날씨, 국가, IP API를 asyncio.gather로 동시에 수집합니다."""
    results = await asyncio.gather(
        fetch_json(client, "weather", WEATHER_URL),
        fetch_json(client, "country", COUNTRY_URL),
        fetch_json(client, "ip", IP_URL),
    )
    return dict(results)

