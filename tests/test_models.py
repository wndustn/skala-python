"""Pydantic 엄격 타입과 범위 검증 테스트입니다."""

import pytest
from pydantic import ValidationError

from app.models import HourlyWeather, IpResponse


def test_weather_rejects_out_of_range_probability() -> None:
    """강수확률이 100을 넘으면 거부합니다."""
    with pytest.raises(ValidationError):
        HourlyWeather.model_validate(
            {
                "time": ["2026-08-06T00:00"],
                "temperature_2m": [25.0],
                "precipitation_probability": [101],
            }
        )


def test_ip_rejects_string_latitude() -> None:
    """엄격 모드에서는 문자열 위도를 숫자로 자동 변환하지 않습니다."""
    with pytest.raises(ValidationError):
        IpResponse.model_validate(
            {
                "status": "success",
                "country": "United States",
                "city": "Ashburn",
                "lat": "39.03",
                "lon": -77.5,
                "timezone": "America/New_York",
                "isp": "Google LLC",
                "query": "8.8.8.8",
            }
        )

