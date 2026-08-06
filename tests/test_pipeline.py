"""세 API 데이터를 한 행 구조로 결합하는 로직을 검사합니다."""

from app.models import CountryResponse, HourlyWeather, IpResponse, WeatherResponse
from app.pipeline import build_records


def test_build_records() -> None:
    """시간대 개수만큼 결과가 생성되고 세 출처가 합쳐지는지 확인합니다."""
    weather = WeatherResponse(
        latitude=37.55,
        longitude=127.0,
        timezone="Asia/Seoul",
        hourly=HourlyWeather(
            time=["2026-08-06T00:00", "2026-08-06T01:00"],
            temperature_2m=[25.0, 26.0],
            precipitation_probability=[10, 20],
        ),
    )
    country = CountryResponse(
        name="Korea (Republic of)",
        nativeName="대한민국",
        capital="Seoul",
        region="Asia",
        alpha3Code="KOR",
        population=51_780_579,
    )
    ip_info = IpResponse(
        status="success",
        country="United States",
        city="Ashburn",
        lat=39.03,
        lon=-77.5,
        timezone="America/New_York",
        isp="Google LLC",
        query="8.8.8.8",
    )

    records = build_records(weather, country, ip_info)

    assert len(records) == 2
    assert records[0].capital == "Seoul"
    assert records[0].temperature_c == 25.0
    assert records[0].lookup_ip == "8.8.8.8"

