"""API 주소와 결과 파일 경로를 한곳에서 관리합니다."""

from pathlib import Path

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=37.5665&longitude=126.9780"
    "&hourly=temperature_2m,precipitation_probability"
    "&forecast_days=3&timezone=Asia%2FSeoul"
)
COUNTRY_URL = "https://countries.dev/alpha/KOR"
IP_URL = "http://ip-api.com/json/8.8.8.8"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
CSV_OUTPUT = OUTPUT_DIR / "seoul_context.csv"
PARQUET_OUTPUT = OUTPUT_DIR / "seoul_context.parquet"
PERFORMANCE_OUTPUT = OUTPUT_DIR / "performance_result.json"
VALIDATION_ERROR_OUTPUT = OUTPUT_DIR / "validation_errors.json"

