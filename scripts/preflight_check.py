"""제출 전 실행 결과, 테스트, Ruff, Git 이력을 검사합니다."""

import subprocess
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"


def run(command: list[str], title: str) -> None:
    """명령 하나를 실행하고 실패하면 검사를 중단합니다."""
    print(f"\n[검사] {title}")
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def check_outputs() -> None:
    """필수 결과 파일과 두 저장 형식의 행 수를 확인합니다."""
    csv_path = OUTPUT_DIR / "seoul_context.csv"
    parquet_path = OUTPUT_DIR / "seoul_context.parquet"
    performance_path = OUTPUT_DIR / "performance_result.json"
    for path in (csv_path, parquet_path, performance_path):
        if not path.exists():
            raise RuntimeError(f"필수 결과 파일 누락: {path.name}")
    if len(pd.read_csv(csv_path)) != len(pd.read_parquet(parquet_path)):
        raise RuntimeError("CSV와 Parquet 행 수가 다릅니다.")
    performance = pd.read_json(performance_path, typ="series")
    required_metrics = {
        "csv_seconds",
        "parquet_seconds",
        "csv_read_seconds",
        "parquet_read_seconds",
    }
    if not required_metrics.issubset(performance.index):
        raise RuntimeError("CSV·Parquet 읽기/쓰기 시간 측정값이 누락됐습니다.")


def main() -> None:
    """채점표 핵심 항목을 한 번에 검사합니다."""
    check_outputs()
    run([sys.executable, "-m", "pytest", "-v"], "pytest")
    run([sys.executable, "-m", "ruff", "check", "."], "Ruff")
    run(["git", "log", "--oneline", "-1"], "Git 커밋")
    print("\n전체 제출 전 검사를 통과했습니다.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"[FAIL] {exc}")
        raise SystemExit(1) from exc
