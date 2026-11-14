# 백엔드 · Backend

[한국어](#한국어) · [English](#english)

---

## 한국어

Custom HTS의 FastAPI 백엔드입니다. 한국투자증권(KIS) Open API, OpenDART, yfinance에서 데이터를 받아 REST API로 제공합니다. Python 3.11 이상과 [uv](https://docs.astral.sh/uv/)를 사용합니다.

### 설치와 실행

```bash
cd backend
uv sync                # add --extra dev for black, flake8, mypy, pytest-cov
uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

API 문서는 http://127.0.0.1:8000/docs 에서 볼 수 있습니다. 저장소 루트의 `bash run-dev.sh`로 프론트엔드와 함께 실행할 수도 있습니다.

> [!WARNING]
> 이 API에는 인증이 없고 계좌 잔고를 조회할 수 있습니다. `127.0.0.1`에만 바인딩하고 외부 네트워크에 노출하지 마세요. 자세한 내용은 [SECURITY.md](../SECURITY.md)를 참고하세요.

### 설정

설정은 `src/utils/config.py`가 저장소 루트의 `.env`에서 읽습니다. [`.env.example`](../.env.example)을 복사해 쓰세요.

| 변수 | 용도 |
|------|------|
| `HANTU_API_KEY`, `HANTU_API_SECRET` | KIS 앱키·앱시크릿(실전투자) |
| `HANTU_ACCOUNT_NUMBER` | 계좌조회용 종합계좌번호 앞 8자리. 예전 이름 `HANTU_BANK_ACCOUNT`도 읽습니다. |
| `HANTU_TOKEN_CACHE_PATH` | (선택) KIS 접근 토큰 캐시 경로. 기본값 `backend/.cache/kis_tokens.json` |
| `DART_API_KEY` | OpenDART 인증키 |
| `SUPABASE_URL`, `SUPABASE_KEY` | (선택) 재무제표 테이블을 저장할 Supabase 프로젝트 |

키 발급 방법은 [설치 가이드](../docs/SETUP.md)를 참고하세요.

### 프로젝트 구조

```
backend/
├── src/
│   ├── main.py              # FastAPI app (src.main:app), CORS, routers, /health
│   ├── api/                 # routers
│   │   ├── korean.py        # /api/korean/*
│   │   ├── us.py            # /api/us/*
│   │   └── financial_statements.py  # /api/financials/*
│   ├── services/            # business logic
│   │   ├── korean_market.py, us_market.py, financial_statements.py
│   │   ├── bond_math.py, bond_analytics.py   # bond price/yield maths and analytics
│   │   └── basis.py, option_parity.py        # futures basis, put-call parity
│   ├── integrations/        # external clients
│   │   ├── kdevelopers.py   # KIS Open API client
│   │   ├── token_store.py   # local KIS access-token cache
│   │   ├── opendart.py, yfinance_client.py, supabase_client.py
│   │   └── stock_master.py, bond_master.py, futures_options_master.py  # KIS master files
│   ├── models/              # Pydantic models
│   └── utils/               # config.py (settings), helpers.py, concurrency.py
├── scripts/                 # helper scripts (see below)
├── examples/                # example scripts
├── tests/                   # pytest tests
├── data/                    # master files and sample payloads
├── pyproject.toml
└── uv.lock
```

### API 개요

| 경로 | 내용 | 데이터 출처 |
|------|------|-------------|
| `/api/korean/quote/{symbol}`, `/candle/{symbol}`, `/candle-minute/{symbol}` | 국내 주식 현재가, 일/주/월봉, 분봉 | KIS |
| `/api/korean/valuation/{symbol}`, `/estimate-perform/{symbol}` | 밸류에이션(PER·PBR 등), 추정실적 | KIS, OpenDART |
| `/api/korean/stocks/master`, `/stock-info/{pdno}` | 종목 검색, 종목 정보 | KIS |
| `/api/korean/bonds/...` | 장내채권 마스터, 시세, 발행 정보, 수익률 분석·추이 | KIS |
| `/api/korean/futures-options/...` | 선물옵션 마스터, 시세, 호가, 일봉·분봉, 옵션 체인 | KIS |
| `/api/korean/basis/...` | 베이시스, 베이시스 추이, 풋콜 패리티 | KIS |
| `/api/korean/financials/{symbol}...`, `/company/{symbol}`, `/disclosures` | 재무제표, 기업 개황, 공시 | OpenDART |
| `/api/korean/account` | 계좌 잔고와 보유 종목 | KIS |
| `/api/us/...` | 미국 주식 시세, 캔들, 밸류에이션, 재무제표 | yfinance |
| `/api/financials/...` | 재무제표 테이블 조회·저장 | Supabase |
| `/health` | 헬스 체크 | — |

엔드포인트별 파라미터와 응답은 [API 레퍼런스](../docs/API.md)와 http://127.0.0.1:8000/docs 를 참고하세요.

### 데이터와 캐시 파일

- `backend/.cache/kis_tokens.json` — KIS 접근 토큰 캐시(권한 0600, gitignore 대상). 토큰 발급이 앱키당 1분에 1회로 제한되므로 재시작해도 다시 씁니다.
- `backend/data/`, `backend/src/data/` — KIS 종목·채권·선물옵션 마스터 파일과 OpenDART 고유번호(corp code) 캐시. 마스터 파일은 필요할 때 내려받습니다. 자세한 내용은 [마스터 파일 가이드](../docs/MASTER_FILES.md)를 참고하세요.

### 스크립트

`backend/`에서 실행합니다.

```bash
# Validate each KIS key pair in .env (never prints secrets or tokens)
uv run python scripts/check_hantu_keys.py

# Bulk-download OpenDART financial statements for all listed Korean stocks
uv run python scripts/fetch_opendart_all_stocks.py --years 2024 2025
```

- `check_hantu_keys.py` — 키 쌍마다 접근 토큰을 발급받고 삼성전자(005930) 현재가를 조회한 뒤 토큰을 캐시에 저장합니다. 실전투자 키인지 모의투자 키인지도 알려 줍니다.
- `fetch_opendart_all_stocks.py` — `DART_API_KEY`가 필요합니다. 결과는 기본적으로 `database/raw_data/<연도>/<기간>/`에 재무상태표·손익계산서·현금흐름표 CSV로 저장하고, 진행 상황은 `database/raw_data/progress/`에 기록해 중단 후 이어서 받을 수 있습니다. `--periods 2025Q1 2025Y`, `--symbols 005930 000660`, `--limit`, `--sleep`, `--output-root` 옵션이 있습니다.

### 테스트와 코드 품질

```bash
# offline tests (no keys or network needed)
uv run pytest tests/test_bond_math.py tests/test_bond_analytics.py \
  tests/test_basis.py tests/test_option_parity.py \
  tests/test_stock_master.py tests/test_config.py tests/test_helpers.py

# formatting and linting (needs: uv sync --extra dev)
uv run black path/to/changed_file.py
uv run flake8 path/to/changed_file.py
```

인자 없이 `uv run pytest`를 실행하면 실제 API를 호출하는 라이브 테스트까지 실행되고, 그 결과가 `tests/test-results/`에 저장됩니다. 이 폴더에는 계좌 정보가 담길 수 있으므로 절대 커밋하지 마세요. 자세한 내용은 [로컬 테스트 실행 가이드](../docs/RUNNING_TESTS_LOCALLY.md)를 참고하세요.

black 줄 길이는 79자입니다. 기존 코드가 아직 black·flake8 기준을 모두 만족하지 않으므로 바꾼 파일에만 실행해 주세요.

### 예제

KIS 클라이언트와 종목 마스터를 직접 쓰는 예제는 [examples/README.md](examples/README.md)를 참고하세요.

---

## English

The FastAPI backend of Custom HTS. It pulls data from the Korea Investment & Securities (KIS) Open API, OpenDART and yfinance and serves it as a REST API. It uses Python 3.11+ and [uv](https://docs.astral.sh/uv/).

### Install and run

```bash
cd backend
uv sync                # add --extra dev for black, flake8, mypy, pytest-cov
uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

API docs are at http://127.0.0.1:8000/docs. You can also start it together with the frontend using `bash run-dev.sh` at the repository root.

> [!WARNING]
> This API has no authentication and can read your account balance. Bind it to `127.0.0.1` only and never expose it to a network. See [SECURITY.md](../SECURITY.md).

### Configuration

`src/utils/config.py` reads settings from `.env` at the repository root. Start from [`.env.example`](../.env.example).

| Variable | Purpose |
|----------|---------|
| `HANTU_API_KEY`, `HANTU_API_SECRET` | KIS App Key and App Secret (real trading) |
| `HANTU_ACCOUNT_NUMBER` | First 8 digits of your account number, for the account page. The legacy name `HANTU_BANK_ACCOUNT` is also read. |
| `HANTU_TOKEN_CACHE_PATH` | (Optional) KIS access-token cache path. Default: `backend/.cache/kis_tokens.json` |
| `DART_API_KEY` | OpenDART API key |
| `SUPABASE_URL`, `SUPABASE_KEY` | (Optional) Supabase project for the financial-statement tables |

See the [setup guide](../docs/SETUP.md) for how to get the keys.

### Project structure

```
backend/
├── src/
│   ├── main.py              # FastAPI app (src.main:app), CORS, routers, /health
│   ├── api/                 # routers
│   │   ├── korean.py        # /api/korean/*
│   │   ├── us.py            # /api/us/*
│   │   └── financial_statements.py  # /api/financials/*
│   ├── services/            # business logic
│   │   ├── korean_market.py, us_market.py, financial_statements.py
│   │   ├── bond_math.py, bond_analytics.py   # bond price/yield maths and analytics
│   │   └── basis.py, option_parity.py        # futures basis, put-call parity
│   ├── integrations/        # external clients
│   │   ├── kdevelopers.py   # KIS Open API client
│   │   ├── token_store.py   # local KIS access-token cache
│   │   ├── opendart.py, yfinance_client.py, supabase_client.py
│   │   └── stock_master.py, bond_master.py, futures_options_master.py  # KIS master files
│   ├── models/              # Pydantic models
│   └── utils/               # config.py (settings), helpers.py, concurrency.py
├── scripts/                 # helper scripts (see below)
├── examples/                # example scripts
├── tests/                   # pytest tests
├── data/                    # master files and sample payloads
├── pyproject.toml
└── uv.lock
```

### API overview

| Path | What | Source |
|------|------|--------|
| `/api/korean/quote/{symbol}`, `/candle/{symbol}`, `/candle-minute/{symbol}` | Korean stock price; daily/weekly/monthly and minute candles | KIS |
| `/api/korean/valuation/{symbol}`, `/estimate-perform/{symbol}` | Valuation (PER, PBR, …), earnings estimates | KIS, OpenDART |
| `/api/korean/stocks/master`, `/stock-info/{pdno}` | Stock search, stock information | KIS |
| `/api/korean/bonds/...` | Exchange-listed bond master, quotes, issue info, yield analytics and history | KIS |
| `/api/korean/futures-options/...` | Futures/options master, quotes, order book, daily/minute candles, option chain | KIS |
| `/api/korean/basis/...` | Basis, basis history, put-call parity | KIS |
| `/api/korean/financials/{symbol}...`, `/company/{symbol}`, `/disclosures` | Financial statements, company overview, disclosures | OpenDART |
| `/api/korean/account` | Account balance and holdings | KIS |
| `/api/us/...` | US quotes, candles, valuation, financial statements | yfinance |
| `/api/financials/...` | Read and store financial-statement tables | Supabase |
| `/health` | Health check | — |

For parameters and responses, see the [API reference](../docs/API.md) and http://127.0.0.1:8000/docs.

### Data and cache files

- `backend/.cache/kis_tokens.json` — KIS access-token cache (mode 0600, gitignored). Each App Key can issue only one token per minute, so tokens are reused across restarts.
- `backend/data/`, `backend/src/data/` — KIS stock, bond and futures/options master files and the OpenDART corp-code cache. Master files are downloaded on demand; see the [master files guide](../docs/MASTER_FILES.md).

### Scripts

Run these from `backend/`.

```bash
# Validate each KIS key pair in .env (never prints secrets or tokens)
uv run python scripts/check_hantu_keys.py

# Bulk-download OpenDART financial statements for all listed Korean stocks
uv run python scripts/fetch_opendart_all_stocks.py --years 2024 2025
```

- `check_hantu_keys.py` — For each key pair, requests an access token, fetches the price of Samsung Electronics (005930) and saves the token to the cache. It also tells you whether a key is for real or paper trading.
- `fetch_opendart_all_stocks.py` — Needs `DART_API_KEY`. By default it writes balance-sheet, income-statement and cash-flow CSVs to `database/raw_data/<year>/<period>/` and records progress in `database/raw_data/progress/`, so an interrupted run can resume. Options include `--periods 2025Q1 2025Y`, `--symbols 005930 000660`, `--limit`, `--sleep` and `--output-root`.

### Tests and code quality

```bash
# offline tests (no keys or network needed)
uv run pytest tests/test_bond_math.py tests/test_bond_analytics.py \
  tests/test_basis.py tests/test_option_parity.py \
  tests/test_stock_master.py tests/test_config.py tests/test_helpers.py

# formatting and linting (needs: uv sync --extra dev)
uv run black path/to/changed_file.py
uv run flake8 path/to/changed_file.py
```

Running `uv run pytest` with no arguments also runs live tests that call real APIs and save their output to `tests/test-results/`. That folder can contain account data — never commit it. See [Running tests locally](../docs/RUNNING_TESTS_LOCALLY.md).

The black line length is 79. The existing code is not yet fully black/flake8 clean, so run them only on the files you change.

### Examples

For scripts that use the KIS client and the stock master directly, see [examples/README.md](examples/README.md).
