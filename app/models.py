"""세 API 응답과 최종 저장 행의 Pydantic v2 모델입니다."""

from pydantic import BaseModel, ConfigDict, Field, model_validator


class HourlyWeather(BaseModel):
    """서울 3일 시간대별 날씨 배열입니다."""

    model_config = ConfigDict(strict=True)

    time: list[str] = Field(min_length=1)
    temperature_2m: list[float] = Field(min_length=1)
    precipitation_probability: list[int] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_hourly_arrays(self) -> "HourlyWeather":
        """시간·기온·강수확률 배열의 길이와 범위를 확인합니다."""
        lengths = {
            len(self.time),
            len(self.temperature_2m),
            len(self.precipitation_probability),
        }
        if len(lengths) != 1:
            raise ValueError("시간대별 날씨 배열 길이가 서로 다릅니다.")
        if not all(-100 <= value <= 70 for value in self.temperature_2m):
            raise ValueError("기온이 허용 범위를 벗어났습니다.")
        if not all(0 <= value <= 100 for value in self.precipitation_probability):
            raise ValueError("강수확률은 0~100이어야 합니다.")
        return self


class WeatherResponse(BaseModel):
    """Open-Meteo 응답에서 필요한 필드만 검증합니다."""

    model_config = ConfigDict(strict=True)

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str = Field(min_length=1)
    hourly: HourlyWeather


class CountryResponse(BaseModel):
    """countries.dev 한국 국가 정보입니다."""

    model_config = ConfigDict(strict=True)

    name: str = Field(min_length=1)
    nativeName: str = Field(min_length=1)
    capital: str = Field(min_length=1)
    region: str = Field(min_length=1)
    alpha3Code: str = Field(pattern=r"^[A-Z]{3}$")
    population: int = Field(gt=0)


class IpResponse(BaseModel):
    """ip-api의 IP 기반 지역 정보입니다."""

    model_config = ConfigDict(strict=True)

    status: str = Field(pattern=r"^success$")
    country: str = Field(min_length=1)
    city: str = Field(min_length=1)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    timezone: str = Field(min_length=1)
    isp: str = Field(min_length=1)
    query: str = Field(pattern=r"^\d{1,3}(\.\d{1,3}){3}$")


class CollectedRecord(BaseModel):
    """검증된 세 API를 합쳐 CSV와 Parquet에 저장할 한 행입니다."""

    model_config = ConfigDict(strict=True)

    forecast_time: str = Field(min_length=1)
    temperature_c: float = Field(ge=-100, le=70)
    precipitation_probability: int = Field(ge=0, le=100)
    country_name: str = Field(min_length=1)
    country_native_name: str = Field(min_length=1)
    capital: str = Field(min_length=1)
    population: int = Field(gt=0)
    lookup_ip: str = Field(min_length=7)
    ip_country: str = Field(min_length=1)
    ip_city: str = Field(min_length=1)
    ip_timezone: str = Field(min_length=1)
    ip_isp: str = Field(min_length=1)

