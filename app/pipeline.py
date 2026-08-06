"""수집한 JSON을 검증하고 저장 가능한 행으로 결합합니다."""

from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from app.models import (
    CollectedRecord,
    CountryResponse,
    IpResponse,
    WeatherResponse,
)

ModelT = TypeVar("ModelT", bound=BaseModel)


def validate_one(
    model_class: type[ModelT],
    row: dict[str, Any],
    source_name: str,
) -> tuple[ModelT | None, list[dict[str, Any]]]:
    """API 응답 하나를 검증하고 오류를 제출 가능한 형태로 정리합니다."""
    try:
        return model_class.model_validate(row), []
    except ValidationError as exc:
        return None, [
            {
                "source": source_name,
                "errors": exc.errors(include_url=False),
            }
        ]


def validate_responses(
    raw_data: dict[str, dict[str, Any]],
) -> tuple[
    tuple[WeatherResponse, CountryResponse, IpResponse] | None,
    list[dict[str, Any]],
]:
    """세 응답을 각각 알맞은 Pydantic 모델로 검증합니다."""
    weather, weather_errors = validate_one(
        WeatherResponse, raw_data["weather"], "weather"
    )
    country, country_errors = validate_one(
        CountryResponse, raw_data["country"], "country"
    )
    ip_info, ip_errors = validate_one(IpResponse, raw_data["ip"], "ip")
    errors = weather_errors + country_errors + ip_errors

    if errors or weather is None or country is None or ip_info is None:
        return None, errors
    return (weather, country, ip_info), []


def build_records(
    weather: WeatherResponse,
    country: CountryResponse,
    ip_info: IpResponse,
) -> list[CollectedRecord]:
    """72시간 날씨 각각에 한국 정보와 IP 조회 정보를 결합합니다."""
    return [
        CollectedRecord(
            forecast_time=time,
            temperature_c=temperature,
            precipitation_probability=precipitation,
            country_name=country.name,
            country_native_name=country.nativeName,
            capital=country.capital,
            population=country.population,
            lookup_ip=ip_info.query,
            ip_country=ip_info.country,
            ip_city=ip_info.city,
            ip_timezone=ip_info.timezone,
            ip_isp=ip_info.isp,
        )
        for time, temperature, precipitation in zip(
            weather.hourly.time,
            weather.hourly.temperature_2m,
            weather.hourly.precipitation_probability,
            strict=True,
        )
    ]
