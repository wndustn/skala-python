# Practice 3: 비동기 API 데이터 수집 파이프라인

Open-Meteo, Countries.dev, ip-api에서 데이터를 동시에 수집하고,
Pydantic v2로 검증한 뒤 CSV와 Parquet 형식으로 저장하는 실습입니다.

## 환경 설정

```bash
cd practice3
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 프로그램 실행

```bash
python -m app.main
```

정상 실행되면 세 API의 수집과 검증 결과가 출력됩니다. 검증된 서울 3일치
날씨 데이터 72건은 CSV와 Parquet로 저장되며, 두 파일의 읽기·쓰기 시간과
파일 크기도 함께 확인할 수 있습니다.

결과 파일은 `data/output` 폴더에 생성됩니다.

## 테스트 및 코드 검사

```bash
pytest -v
ruff check .
```

CSV는 내용을 바로 확인하기 편하고, Parquet는 자료형을 유지하면서 데이터를
저장할 수 있습니다. 실행 환경에 따라 측정 시간이 달라질 수 있으므로 프로그램을
직접 실행한 결과를 기준으로 비교했습니다.
