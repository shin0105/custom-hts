# 로컬 테스트 실행 가이드 · Running Tests Locally

[한국어](#한국어) · [English](#english)

---

## 한국어

### 개요

백엔드 테스트는 `backend/tests/`에 있으며 pytest로 실행합니다. 테스트는 두 종류입니다.

- **오프라인 테스트** — 네트워크와 API 키 없이 실행됩니다. 실제 응답을 줄여 만든 픽스처와 가짜 클라이언트를 씁니다. 평소에는 이것만 실행하면 됩니다.
- **라이브 테스트와 점검 스크립트** — 실제 한국투자증권(KIS)·OpenDART·yfinance·Supabase에 요청을 보냅니다. 본인 키가 필요하고, 결과 파일을 남기거나 Supabase에 데이터를 쓰는 것도 있습니다.

프론트엔드에는 단위 테스트 러너가 없으며, 린트와 빌드(타입 검사 포함)로 점검합니다.

### 준비

[설치 가이드](SETUP.md)대로 의존성을 설치합니다.

```bash
cd backend
uv sync    # add --extra dev for coverage (pytest-cov)
```

### 오프라인 테스트

```bash
cd backend
uv run pytest tests/test_bond_math.py tests/test_bond_analytics.py \
  tests/test_basis.py tests/test_option_parity.py \
  tests/test_stock_master.py tests/test_config.py tests/test_helpers.py
```

| 파일 | 대상 |
|------|------|
| `test_bond_math.py` | 채권 가격·수익률·듀레이션 계산 |
| `test_bond_analytics.py` | 채권 수익률 분석(결제일, 체결가·호가 기반 수익률) |
| `test_basis.py` | 선물과 기초자산 연결, 베이시스·캐리 계산 |
| `test_option_parity.py` | 풋콜 패리티와 합성 선물 |
| `test_stock_master.py` | 종목 마스터 검색(종목 검색 자동완성) |
| `test_config.py`, `test_helpers.py` | 설정과 공통 유틸 |

커버리지를 보려면 `uv sync --extra dev`로 pytest-cov를 설치한 뒤, 위 명령에 `--cov=src --cov-report=term-missing`을 붙입니다.

새 기능의 테스트는 이 파일들처럼 가짜 클라이언트나 캡처한 응답을 써서 네트워크 없이 돌아가게 작성해 주세요.

### 라이브 테스트와 점검 스크립트

`uv run pytest`를 인자 없이 실행하면 아래 파일 대부분이 함께 실행됩니다. 본인 키로 실제 API를 호출하고(계좌 잔고 조회 포함), Supabase에 데이터를 쓰며, 네트워크나 실행 중인 서버가 없으면 실패하는 것도 있습니다. 필요한 파일만 골라 실행하세요.

```bash
cd backend
uv run pytest tests/test_kdevelopers_live_api.py -s     # via pytest
uv run python tests/test_kdevelopers_live_api.py        # or as a script
```

| 파일 | 필요한 것 | 하는 일 |
|------|-----------|---------|
| `test_kdevelopers_live_api.py` | KIS 키, (선택) `HANTU_ACCOUNT_NUMBER` | 시세·일봉·분봉·계좌 잔고·종목 정보·추정실적 응답을 `backend/tests/test-results/kdevelopers_responses/`에 저장 |
| `test_minute_candle_input_hour.py` | KIS 키 | 분봉 원시 응답을 같은 폴더에 저장. pytest가 실행하지 않는 스크립트이므로 `uv run python tests/test_minute_candle_input_hour.py`로 실행합니다. |
| `test_api_live.py` | KIS 키 | 시세·일봉·분봉 조회 |
| `test_api_raw_data.py` | `DART_API_KEY` | OpenDART·yfinance 원시 응답을 `backend/tests/data/`에 저장 |
| `test_comprehensive_api.py` | 모든 키 | 연결을 점검하고 재무제표를 Supabase에 저장, 결과를 `backend/test_results/`에 저장 |
| `test_financial_statements.py` | `DART_API_KEY`, Supabase | 재무제표를 Supabase 테이블에 넣고 확인 |
| `test_api_endpoints.py` | 실행 중인 백엔드(`:8000`) | `/api/financials/...` 엔드포인트 호출 |
| `test_database_check.py`, `insert_financial_data.py` | Supabase | pytest가 실행하지 않는 수동 스크립트(`uv run python tests/<파일>`). Supabase 데이터를 확인하거나 넣습니다. |
| `test_integration.py`, `test_full_integration.py` | — | 예전 CI 환경용으로 작성된 스크립트입니다. 경로가 맞지 않아 실패할 수 있으며 무시해도 됩니다. |

분봉 테스트의 조회 날짜는 `HANTU_MINUTE_CANDLE_DATE=YYYYMMDD`로 지정할 수 있습니다.

### 결과 파일 주의

- `backend/tests/test-results/`와 `backend/test_results/`에는 계좌번호·잔고·보유 종목이 담길 수 있습니다. 두 폴더는 gitignore 대상이며 **절대 커밋하지 마세요**(`git add -f`도 쓰지 마세요).
- `backend/tests/data/`는 gitignore 대상이 아니므로, 여기에 생긴 파일도 커밋하지 않도록 주의하세요.
- 커밋하기 전에 `git status`로 의도하지 않은 파일이 없는지 확인하세요.

### 프론트엔드 점검

```bash
cd frontend
npm run lint    # ESLint; any warning fails the run
npm run build   # tsc type check + production build into dist/
```

`npm test` 스크립트는 없습니다.

### 문제 해결

| 증상 | 해결 방법 |
|------|-----------|
| `ModuleNotFoundError: No module named 'src'` | `backend/`에서 `uv sync`를 실행한 뒤 `uv run`으로 실행합니다. |
| 라이브 테스트의 인증 오류 | `uv run python scripts/check_hantu_keys.py`로 KIS 키를 점검합니다. 실전투자 키가 필요합니다. |
| 최근 분기 재무제표가 없음 | 분기보고서가 공시되기 전이면 OpenDART에서 조회되지 않습니다. 이전 분기로 확인합니다. |
| 네트워크 오류 | `opendart.fss.or.kr`, `openapi.koreainvestment.com`, `query1.finance.yahoo.com`, `*.supabase.co`에 접속할 수 있는지 확인합니다. |

---

## English

### Overview

Backend tests live in `backend/tests/` and run with pytest. There are two kinds:

- **Offline tests** run without network access or API keys. They use fake clients and trimmed copies of real responses as fixtures. This is what you normally run.
- **Live tests and check scripts** send real requests to KIS, OpenDART, yfinance and Supabase. They need your own keys, and some write result files or insert data into Supabase.

The frontend has no unit-test runner; it is checked with lint and a build (which includes type checking).

### Preparation

Install dependencies as described in the [setup guide](SETUP.md).

```bash
cd backend
uv sync    # add --extra dev for coverage (pytest-cov)
```

### Offline tests

```bash
cd backend
uv run pytest tests/test_bond_math.py tests/test_bond_analytics.py \
  tests/test_basis.py tests/test_option_parity.py \
  tests/test_stock_master.py tests/test_config.py tests/test_helpers.py
```

| File | Covers |
|------|--------|
| `test_bond_math.py` | Bond price, yield and duration maths |
| `test_bond_analytics.py` | Bond yield analytics (settlement date, yields from trades and quotes) |
| `test_basis.py` | Linking futures to their underlying; basis and carry |
| `test_option_parity.py` | Put-call parity and synthetic futures |
| `test_stock_master.py` | Stock master search (symbol typeahead) |
| `test_config.py`, `test_helpers.py` | Settings and shared helpers |

For coverage, install pytest-cov with `uv sync --extra dev` and add `--cov=src --cov-report=term-missing` to the command above.

Please write tests for new features the same way: with fake clients or captured responses, so they run without a network.

### Live tests and check scripts

Running `uv run pytest` with no arguments also runs most of the files below. They call real APIs with your keys (including the account balance), write to Supabase, and some fail without a network or a running server. Run only the files you need:

```bash
cd backend
uv run pytest tests/test_kdevelopers_live_api.py -s     # via pytest
uv run python tests/test_kdevelopers_live_api.py        # or as a script
```

| File | Needs | What it does |
|------|-------|--------------|
| `test_kdevelopers_live_api.py` | KIS keys, optionally `HANTU_ACCOUNT_NUMBER` | Saves quote, daily/minute candle, account balance, stock info and earnings-estimate responses to `backend/tests/test-results/kdevelopers_responses/` |
| `test_minute_candle_input_hour.py` | KIS keys | Saves raw minute-candle responses to the same folder. pytest does not run it; use `uv run python tests/test_minute_candle_input_hour.py`. |
| `test_api_live.py` | KIS keys | Fetches quotes and daily/minute candles |
| `test_api_raw_data.py` | `DART_API_KEY` | Saves raw OpenDART and yfinance responses to `backend/tests/data/` |
| `test_comprehensive_api.py` | All keys | Checks connections, stores financial statements in Supabase, writes results to `backend/test_results/` |
| `test_financial_statements.py` | `DART_API_KEY`, Supabase | Inserts financial statements into the Supabase tables and verifies them |
| `test_api_endpoints.py` | A running backend (`:8000`) | Calls the `/api/financials/...` endpoints |
| `test_database_check.py`, `insert_financial_data.py` | Supabase | Manual scripts that pytest does not run (`uv run python tests/<file>`); they inspect or insert Supabase data |
| `test_integration.py`, `test_full_integration.py` | — | Scripts written for an old CI environment. Their paths no longer match, so they may fail; ignore them. |

Set the date for minute-candle tests with `HANTU_MINUTE_CANDLE_DATE=YYYYMMDD`.

### Result files

- `backend/tests/test-results/` and `backend/test_results/` can contain your account number, balance and holdings. Both are gitignored — **never commit them** (and never use `git add -f` on them).
- `backend/tests/data/` is not gitignored, so take care not to commit files generated there either.
- Run `git status` before every commit to catch unintended files.

### Frontend checks

```bash
cd frontend
npm run lint    # ESLint; any warning fails the run
npm run build   # tsc type check + production build into dist/
```

There is no `npm test` script.

### Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'src'` | Run `uv sync` in `backend/`, then run commands through `uv run`. |
| Authentication errors in live tests | Check your KIS keys with `uv run python scripts/check_hantu_keys.py`. Real-trading keys are required. |
| No financial statements for the latest quarter | OpenDART has no data until the quarterly report is filed. Try the previous quarter. |
| Network errors | Make sure `opendart.fss.or.kr`, `openapi.koreainvestment.com`, `query1.finance.yahoo.com` and `*.supabase.co` are reachable. |
