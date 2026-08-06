"""CSV·Parquet 저장 및 재로딩 검증 테스트입니다."""

from pathlib import Path

from app.models import CollectedRecord
from app.storage import save_with_performance, verify_saved_data


def test_save_and_verify(tmp_path: Path) -> None:
    """동일 데이터가 두 형식으로 저장되고 다시 읽히는지 확인합니다."""
    records = [
        CollectedRecord(
            forecast_time="2026-08-06T00:00",
            temperature_c=25.0,
            precipitation_probability=10,
            country_name="Korea (Republic of)",
            country_native_name="대한민국",
            capital="Seoul",
            population=51_780_579,
            lookup_ip="8.8.8.8",
            ip_country="United States",
            ip_city="Ashburn",
            ip_timezone="America/New_York",
            ip_isp="Google LLC",
        )
    ]
    csv_path = tmp_path / "result.csv"
    parquet_path = tmp_path / "result.parquet"
    performance_path = tmp_path / "performance.json"

    performance = save_with_performance(
        records, csv_path, parquet_path, performance_path
    )
    csv_rows, parquet_rows = verify_saved_data(csv_path, parquet_path)

    assert performance["rows"] == 1
    assert csv_rows == parquet_rows == 1
    assert performance_path.exists()

