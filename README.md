# Day 1 데이터 수집 미니 파이프라인

## 과제가 요구하는 것

1. Open-Meteo, countries.dev, ip-api를 `asyncio.gather()`로 동시에 호출합니다.
2. 응답 JSON의 필요한 필드를 Pydantic v2 엄격 모드로 검증합니다.
3. 검증된 데이터를 시간대별 한 행으로 결합합니다.
4. 같은 데이터를 CSV와 Parquet로 저장하고 읽기·쓰기 시간과 크기를 비교합니다.
5. pytest와 Ruff로 동작 및 코드 스타일을 확인합니다.

세 API는 공개 API이므로 별도 API 키가 필요 없습니다.

## 실행 순서 (macOS)

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m app.main
pytest -v
ruff check .
```

Python 3.13이 없다면 설치된 Python으로 가상환경을 만들어도 코드 실행은 가능하지만,
제출 화면에는 교수님 권장 버전인 3.13을 사용하는 편이 안전합니다.

## 생성되는 결과

- `data/output/seoul_context.csv`
- `data/output/seoul_context.parquet`
- `data/output/performance_result.json`
- 검증 실패 시 `data/output/validation_errors.json`

`ip-api` 결과가 미국으로 나오는 이유는 내 위치를 조회하는 것이 아니라 과제에 지정된
Google DNS IP `8.8.8.8`의 위치를 조회하기 때문입니다.
