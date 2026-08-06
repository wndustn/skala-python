"""실제 인터넷 없이 비동기 수집 구조를 검사합니다."""

import httpx
import pytest

from app.api_client import fetch_all_data


@pytest.mark.asyncio
async def test_fetch_all_data_calls_three_apis() -> None:
    """날씨·국가·IP 주소가 모두 호출되는지 확인합니다."""
    called_hosts: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        called_hosts.append(request.url.host)
        payloads = {
            "api.open-meteo.com": {"hourly": {}},
            "countries.dev": {"alpha3Code": "KOR"},
            "ip-api.com": {"status": "success"},
        }
        return httpx.Response(200, json=payloads[request.url.host])

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await fetch_all_data(client)

    assert set(called_hosts) == {
        "api.open-meteo.com",
        "countries.dev",
        "ip-api.com",
    }
    assert set(result) == {"weather", "country", "ip"}

