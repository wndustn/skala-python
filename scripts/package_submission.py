"""Day 1 프로젝트의 제출용 ZIP 파일을 생성합니다."""

from __future__ import annotations

import argparse
import subprocess
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
EXCLUDED_NAMES = {
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".DS_Store",
    "git_log.txt",
    "image.png",
}
EXCLUDED_SUFFIXES = {".docx", ".pages", ".pyc", ".pyo", ".zip"}


def should_exclude(path: Path) -> bool:
    """가상환경, 캐시, 임시 파일과 기존 ZIP을 제외합니다."""
    relative_parts = path.relative_to(PROJECT_ROOT).parts
    return (
        any(part in EXCLUDED_NAMES for part in relative_parts)
        or path.suffix.lower() in EXCLUDED_SUFFIXES
    )


def find_report_pdf() -> Path:
    """reports 폴더에서 최종 실행 결과 PDF 하나를 찾습니다."""
    pdf_files = sorted(REPORTS_DIR.glob("*.pdf"))
    if not pdf_files:
        raise RuntimeError(
            "reports 폴더에 실행 결과 PDF가 없습니다. "
            "Pages에서 보고서를 PDF로 내보낸 후 다시 실행하세요."
        )
    if len(pdf_files) > 1:
        names = ", ".join(path.name for path in pdf_files)
        raise RuntimeError(f"보고서 PDF가 여러 개입니다. 하나만 남기세요: {names}")
    return pdf_files[0]


def verify_required_files() -> None:
    """결과 데이터, Git 이력, PDF 보고서 존재 여부를 확인합니다."""
    required_files = (
        PROJECT_ROOT / "requirements.txt",
        OUTPUT_DIR / "seoul_context.csv",
        OUTPUT_DIR / "seoul_context.parquet",
        OUTPUT_DIR / "performance_result.json",
    )
    missing = [path.name for path in required_files if not path.exists()]
    if missing:
        raise RuntimeError(f"필수 제출 파일 누락: {', '.join(missing)}")
    if not (PROJECT_ROOT / ".git").is_dir():
        raise RuntimeError(".git 폴더가 없어 커밋 이력을 포함할 수 없습니다.")
    find_report_pdf()


def create_archive(output_path: Path) -> None:
    """프로젝트 최상위 폴더를 포함하여 ZIP 파일을 생성합니다."""
    root_name = PROJECT_ROOT.name
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(PROJECT_ROOT.rglob("*")):
            if path.is_dir() or should_exclude(path):
                continue
            archive.write(path, Path(root_name) / path.relative_to(PROJECT_ROOT))
        git_log = subprocess.check_output(
            ["git", "log", "--oneline"],
            cwd=PROJECT_ROOT,
            text=True,
        )
        archive.writestr(Path(root_name) / "git_log.txt", git_log)


def main() -> None:
    """자동 검사를 통과한 프로젝트만 제출용 ZIP으로 생성합니다."""
    parser = argparse.ArgumentParser(description="Day 1 제출 ZIP 생성")
    parser.add_argument(
        "filename",
        help="예: 서울_1반_홍길동_day1종합실습.zip",
    )
    args = parser.parse_args()
    filename = (
        args.filename
        if args.filename.endswith(".zip")
        else f"{args.filename}.zip"
    )
    output_path = PROJECT_ROOT.parent / filename

    subprocess.run(
        [sys.executable, "scripts/preflight_check.py"],
        cwd=PROJECT_ROOT,
        check=True,
    )
    verify_required_files()
    create_archive(output_path)
    print(f"제출 ZIP 생성 완료: {output_path}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"[FAIL] {exc}")
        raise SystemExit(1) from exc
