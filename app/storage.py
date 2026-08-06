"""검증된 데이터를 CSV·Parquet로 저장하고 성능을 비교합니다."""

import json
from pathlib import Path
from time import perf_counter
from typing import Any

import pandas as pd

from app.models import CollectedRecord


def save_json(data: Any, file_path: Path) -> None:
    """오류 또는 성능 결과를 UTF-8 JSON으로 저장합니다."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def save_with_performance(
    records: list[CollectedRecord],
    csv_path: Path,
    parquet_path: Path,
    performance_path: Path,
) -> dict[str, float | int]:
    """동일 데이터를 두 형식으로 저장하고 시간·크기를 기록합니다."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe = pd.DataFrame([record.model_dump() for record in records])

    csv_start = perf_counter()
    dataframe.to_csv(csv_path, index=False, encoding="utf-8-sig")
    csv_seconds = perf_counter() - csv_start

    parquet_start = perf_counter()
    dataframe.to_parquet(
        parquet_path,
        index=False,
        engine="pyarrow",
        compression="snappy",
    )
    parquet_seconds = perf_counter() - parquet_start

    performance: dict[str, float | int] = {
        "rows": len(dataframe),
        "csv_seconds": round(csv_seconds, 6),
        "parquet_seconds": round(parquet_seconds, 6),
        "csv_bytes": csv_path.stat().st_size,
        "parquet_bytes": parquet_path.stat().st_size,
    }
    save_json(performance, performance_path)
    return performance


def verify_saved_data(
    csv_path: Path,
    parquet_path: Path,
) -> tuple[int, int, float, float]:
    """두 파일의 읽기 시간을 측정하고 내용이 같은지 확인합니다."""
    csv_start = perf_counter()
    csv_data = pd.read_csv(csv_path)
    csv_read_seconds = perf_counter() - csv_start

    parquet_start = perf_counter()
    parquet_data = pd.read_parquet(parquet_path, engine="pyarrow")
    parquet_read_seconds = perf_counter() - parquet_start

    if len(csv_data) != len(parquet_data):
        raise ValueError("CSV와 Parquet의 행 수가 다릅니다.")
    if csv_data["forecast_time"].tolist() != parquet_data[
        "forecast_time"
    ].tolist():
        raise ValueError("CSV와 Parquet의 시간 데이터가 다릅니다.")
    return (
        len(csv_data),
        len(parquet_data),
        round(csv_read_seconds, 6),
        round(parquet_read_seconds, 6),
    )
