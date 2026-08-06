"""Day 1 과제의 수집→검증→결합→저장 흐름을 실행합니다."""

import asyncio

import httpx

from app.api_client import ApiFetchError, fetch_all_data
from app.config import (
    CSV_OUTPUT,
    PARQUET_OUTPUT,
    PERFORMANCE_OUTPUT,
    VALIDATION_ERROR_OUTPUT,
)
from app.pipeline import build_records, validate_responses
from app.storage import save_json, save_with_performance, verify_saved_data


async def run_pipeline() -> None:
    """세 API 데이터를 동시에 수집한 뒤 검증하고 저장합니다."""
    print("=== 1. 공개 API 3개 동시 수집 ===")
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        raw_data = await fetch_all_data(client)
    print("수집 완료: weather=1, country=1, ip=1")

    print("\n=== 2. Pydantic v2 스키마 검증 ===")
    validated, validation_errors = validate_responses(raw_data)
    if validation_errors or validated is None:
        save_json(validation_errors, VALIDATION_ERROR_OUTPUT)
        raise RuntimeError(
            "검증 오류가 발생했습니다. validation_errors.json을 확인하세요."
        )
    if VALIDATION_ERROR_OUTPUT.exists():
        VALIDATION_ERROR_OUTPUT.unlink()
    weather, country, ip_info = validated
    print("검증 완료: weather, country, ip")

    print("\n=== 3. 데이터 결합 ===")
    records = build_records(weather, country, ip_info)
    print(f"결합 완료: {len(records)}시간")

    print("\n=== 4. CSV / Parquet 저장 및 성능 비교 ===")
    performance = save_with_performance(
        records, CSV_OUTPUT, PARQUET_OUTPUT, PERFORMANCE_OUTPUT
    )
    print(f"CSV: {performance['csv_seconds']}초, {performance['csv_bytes']} bytes")
    print(
        "Parquet:",
        f"{performance['parquet_seconds']}초,",
        f"{performance['parquet_bytes']} bytes",
    )

    print("\n=== 5. 저장 결과 재검증 ===")
    csv_rows, parquet_rows, csv_read_seconds, parquet_read_seconds = (
        verify_saved_data(CSV_OUTPUT, PARQUET_OUTPUT)
    )
    performance["csv_read_seconds"] = csv_read_seconds
    performance["parquet_read_seconds"] = parquet_read_seconds
    save_json(performance, PERFORMANCE_OUTPUT)
    print(f"재로딩 완료: CSV={csv_rows}건, Parquet={parquet_rows}건")
    print(f"CSV 읽기 시간: {csv_read_seconds}초")
    print(f"Parquet 읽기 시간: {parquet_read_seconds}초")
    print("\n전체 파이프라인이 정상 완료되었습니다.")


def main() -> None:
    """예상 가능한 오류를 이해하기 쉬운 문장으로 출력합니다."""
    try:
        asyncio.run(run_pipeline())
    except ApiFetchError as exc:
        print(f"[API 오류] {exc}")
        raise SystemExit(1) from exc
    except ImportError as exc:
        print("[의존성 오류] requirements.txt를 다시 설치하세요.")
        raise SystemExit(1) from exc
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"[실행 오류] {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
