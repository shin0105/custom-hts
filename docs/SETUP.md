# 설치 가이드 · Setup Guide

[한국어](#한국어) · [English](#english)

---

## 한국어

Custom HTS를 내 컴퓨터에서 실행하는 방법을 설명합니다. 이 앱은 한 사람이 자기 컴퓨터에서 쓰는 조회·분석 전용 도구이며, 주문 기능은 없습니다.

### 준비물

| 도구 | 버전 | 확인 명령 |
|------|------|-----------|
| Python | 3.11 이상 | `python3 --version` |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | 최신 | `uv --version` |
| Node.js | 20.19 이상 또는 22.12 이상 (Vite 7 요구 사항) | `node --version` |
| Git | — | `git --version` |

시스템에 맞는 Python이 없으면 uv가 자동으로 내려받습니다.

### API 키 발급

| 서비스 | 용도 | 필요 여부 |
|--------|------|-----------|
| 한국투자증권 KIS Developers | 국내 주식·장내채권·선물옵션 시세, 캔들(봉), 호가, 계좌 잔고 | 국내 기능에 필요 |
| OpenDART | 국내 재무제표, 기업 개황, 공시 | 국내 재무제표·공시에 필요 |
| Supabase | 재무제표 테이블 저장 | 선택 |
| yfinance | 미국 주식 | 키 없음 |

**한국투자증권 (KIS)**

1. 한국투자증권 계좌를 개설하고 [KIS Developers](https://apiportal.koreainvestment.com/)에서 Open API 서비스를 신청합니다.
2. 앱키(App Key)와 앱시크릿(App Secret)을 발급받습니다.
3. 이 앱은 **실전투자** 서버(`openapi.koreainvestment.com:9443`)만 사용합니다. 모의투자 앱키로는 동작하지 않습니다.
4. 계좌조회 화면을 쓰려면 종합계좌번호 앞 8자리가 필요합니다. 상품코드는 기본값 `01`을 씁니다.

**OpenDART** — [OpenDART](https://opendart.fss.or.kr/)에 가입한 뒤 인증키를 신청합니다.

**Supabase (선택)** — 재무제표 테이블을 저장할 때만 씁니다. [Supabase](https://supabase.com/)에서 프로젝트를 만들고 Project Settings → API에서 Project URL과 API 키를 확인합니다. 이 키는 백엔드에서만 쓰이며 프론트엔드에 넣지 않습니다. 설정하지 않으면 Supabase를 쓰는 기능만 건너뜁니다.

### 설치

#### 1. 저장소 복제

```bash
git clone https://github.com/shin0105/custom-hts.git
cd custom-hts
```

#### 2. 환경 변수 설정

```bash
cp .env.example .env
```

`.env`는 저장소 루트에 둡니다. 백엔드와 스크립트가 모두 이 파일을 읽으며, gitignore 대상이라 커밋되지 않습니다.

```env
HANTU_API_KEY=your_api_key
HANTU_API_SECRET=your_api_secret
HANTU_ACCOUNT_NUMBER=12345678
DART_API_KEY=your_dart_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key
# HANTU_TOKEN_CACHE_PATH=/path/to/kis_tokens.json
```

| 변수 | 설명 |
|------|------|
| `HANTU_API_KEY`, `HANTU_API_SECRET` | KIS 앱키·앱시크릿 |
| `HANTU_ACCOUNT_NUMBER` | 계좌조회용 종합계좌번호 앞 8자리(숫자 8자리). 비어 있으면 예전 이름인 `HANTU_BANK_ACCOUNT`를 읽습니다. |
| `HANTU_TOKEN_CACHE_PATH` | (선택) KIS 접근 토큰 캐시 파일 경로. 기본값은 `backend/.cache/kis_tokens.json` |
| `DART_API_KEY` | OpenDART 인증키 |
| `SUPABASE_URL`, `SUPABASE_KEY` | (선택) Supabase 프로젝트 URL과 키 |

빠진 변수가 있으면 백엔드가 시작할 때 `Warning: Missing environment variables: ...`를 출력하고, 그 키가 필요한 기능만 실패합니다.

#### 3. 백엔드 의존성

```bash
cd backend
uv sync                # creates backend/.venv from uv.lock
uv sync --extra dev    # optional: adds black, flake8, mypy, pytest-cov
```

#### 4. 프론트엔드 의존성

```bash
cd frontend
npm install
```

#### 5. (선택) Supabase 테이블

Supabase 대시보드의 SQL Editor에서 `database/financial_statements.sql`을 실행하면 국내·미국 재무상태표, 손익계산서, 현금흐름표 테이블 6개가 만들어집니다. 스크립트는 트리거가 쓰는 함수까지 모두 정의하므로 따로 준비할 것이 없고, 여러 번 실행해도 됩니다.

자세한 내용은 [Supabase 연동](SUPABASE_INTEGRATION.md)을 참고하세요.

#### 6. (선택) KIS 키 점검

```bash
cd backend
uv run python scripts/check_hantu_keys.py
```

`.env`의 키 쌍마다 접근 토큰을 발급받고(실전투자 서버가 거부하면 모의투자 서버로 다시 시도해 어떤 종류의 키인지 알려 줍니다), 삼성전자(005930) 현재가를 조회한 뒤, 토큰을 로컬 캐시에 저장합니다. 앱키는 앞뒤 4자리만, 시크릿은 길이만 출력하며 토큰은 출력하지 않습니다.

### 실행

```bash
bash run-dev.sh
```

백엔드(`127.0.0.1:8000`)와 프론트엔드(`localhost:5173`)를 함께 띄웁니다. Ctrl+C로 둘 다 종료하거나, 다른 터미널에서 `bash stop-dev.sh`를 실행합니다.

두 서버를 따로 실행할 수도 있습니다.

```bash
# terminal 1
cd backend
uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# terminal 2
cd frontend
npm run dev
```

| 주소 | 내용 |
|------|------|
| http://localhost:5173 | 웹 앱 |
| http://127.0.0.1:8000/docs | API 문서 (Swagger UI) |
| http://127.0.0.1:8000/redoc | API 문서 (ReDoc) |
| http://127.0.0.1:8000/health | 헬스 체크 |

프론트엔드 개발 서버는 `/api` 요청을 `http://localhost:8000`으로 프록시합니다.

> [!WARNING]
> 백엔드 API에는 **인증이 없고** 계좌 잔고를 조회할 수 있습니다. `127.0.0.1`에만 바인딩한 상태로 쓰고, 다른 주소에 바인딩하거나 포트 포워딩·터널 등으로 외부 네트워크에 노출하지 마세요. 자세한 내용은 [SECURITY.md](../SECURITY.md)를 참고하세요.

### 동작 확인

1. http://127.0.0.1:8000/health 가 `{"status": "healthy", "version": "0.1.0"}`을 반환하는지 확인합니다.
2. http://127.0.0.1:8000/api/us/quote/AAPL 에서 미국 주식 시세가 나오는지 확인합니다(키 없이 동작).
3. http://localhost:5173 의 **해외주식** 화면에서 `AAPL`을, **국내주식** 화면에서 `005930`을 조회합니다.

### KIS 접근 토큰 캐시

KIS 접근 토큰은 약 24시간 유효하며, 발급은 앱키당 1분에 1회로 제한됩니다. 그래서 백엔드는 토큰을 `backend/.cache/kis_tokens.json`(권한 0600, gitignore 대상)에 저장하고 서버를 재시작해도 다시 씁니다. 캐시 키로는 앱키가 아니라 앱키의 SHA-256 해시를 씁니다. 경로는 `HANTU_TOKEN_CACHE_PATH`로 바꿀 수 있고, 파일을 지우면 다음 요청 때 새로 발급받습니다.

### 테스트

[로컬 테스트 실행 가이드](RUNNING_TESTS_LOCALLY.md)를 참고하세요. 키 없이 돌아가는 오프라인 테스트와 실제 API를 호출하는 테스트를 구분해 설명합니다.

### 문제 해결

| 증상 | 해결 방법 |
|------|-----------|
| 시작할 때 `Missing environment variables` 경고 | 저장소 루트의 `.env`를 확인합니다. Supabase를 쓰지 않으면 `SUPABASE_*` 항목은 무시해도 됩니다. |
| 국내 시세 조회 실패, 토큰 발급 오류 | `scripts/check_hantu_keys.py`로 키를 점검합니다. 모의투자 키라면 실전투자 키로 바꿉니다. 방금 토큰을 발급받았다면 1분 뒤 다시 시도합니다. |
| 계좌조회에서 `HANTU_ACCOUNT_NUMBER ... is not configured correctly` | 계좌번호를 숫자 8자리로 입력했는지 확인합니다. |
| 화면의 모든 API 호출이 실패 | 백엔드가 8000번 포트에서 실행 중인지 확인합니다. |
| `npm run dev`가 Node 버전 오류로 실패 | Node.js를 20.19 이상 또는 22.12 이상으로 올립니다. |
| Python `ModuleNotFoundError` | `backend/`에서 `uv sync`를 다시 실행하고, 명령은 `uv run`으로 실행합니다. |

---

## English

This guide explains how to run Custom HTS on your own machine. The app is a read-only analysis tool for a single user on their own computer; it has no order placement.

### Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.11+ | `python3 --version` |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | latest | `uv --version` |
| Node.js | 20.19+ or 22.12+ (required by Vite 7) | `node --version` |
| Git | — | `git --version` |

If no suitable Python is installed, uv downloads one automatically.

### Getting API keys

| Service | Used for | Needed? |
|---------|----------|---------|
| Korea Investment & Securities (KIS) Developers | Quotes, candles, order books for Korean stocks, exchange-listed bonds and futures/options; account balance | For Korean market features |
| OpenDART | Korean financial statements, company overviews, disclosures | For Korean financials and disclosures |
| Supabase | Storing financial-statement tables | Optional |
| yfinance | US stocks | No key |

**Korea Investment & Securities (KIS)**

1. Open a KIS brokerage account and apply for the Open API service on [KIS Developers](https://apiportal.koreainvestment.com/).
2. Get an App Key and App Secret.
3. The app only talks to the **real-trading** (실전투자) server (`openapi.koreainvestment.com:9443`). Paper-trading (모의투자) keys do not work.
4. The account page needs the first 8 digits of your account number. The product code defaults to `01`.

**OpenDART** — Sign up at [OpenDART](https://opendart.fss.or.kr/) and request an API key.

**Supabase (optional)** — Only used to store financial-statement tables. Create a project at [Supabase](https://supabase.com/) and copy the Project URL and an API key from Project Settings → API. The key is used only by the backend; never put it in the frontend. Without Supabase, only the features that use it are skipped.

### Installation

#### 1. Clone the repository

```bash
git clone https://github.com/shin0105/custom-hts.git
cd custom-hts
```

#### 2. Configure environment variables

```bash
cp .env.example .env
```

Keep `.env` at the repository root. Both the backend and the scripts read it, and it is gitignored.

```env
HANTU_API_KEY=your_api_key
HANTU_API_SECRET=your_api_secret
HANTU_ACCOUNT_NUMBER=12345678
DART_API_KEY=your_dart_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key
# HANTU_TOKEN_CACHE_PATH=/path/to/kis_tokens.json
```

| Variable | Description |
|----------|-------------|
| `HANTU_API_KEY`, `HANTU_API_SECRET` | KIS App Key and App Secret |
| `HANTU_ACCOUNT_NUMBER` | First 8 digits of your account number, for the account page. If empty, the legacy name `HANTU_BANK_ACCOUNT` is read instead. |
| `HANTU_TOKEN_CACHE_PATH` | (Optional) KIS access-token cache file. Default: `backend/.cache/kis_tokens.json` |
| `DART_API_KEY` | OpenDART API key |
| `SUPABASE_URL`, `SUPABASE_KEY` | (Optional) Supabase project URL and key |

If a variable is missing, the backend prints `Warning: Missing environment variables: ...` at startup, and only the features that need that key fail.

#### 3. Backend dependencies

```bash
cd backend
uv sync                # creates backend/.venv from uv.lock
uv sync --extra dev    # optional: adds black, flake8, mypy, pytest-cov
```

#### 4. Frontend dependencies

```bash
cd frontend
npm install
```

#### 5. (Optional) Supabase tables

Run `database/financial_statements.sql` in the Supabase SQL Editor. It creates six tables: balance sheet, income statement and cash-flow statement for Korean and US companies. The script defines everything it needs, including the trigger function, and is safe to run more than once.

See [Supabase integration](SUPABASE_INTEGRATION.md) for details.

#### 6. (Optional) Check your KIS keys

```bash
cd backend
uv run python scripts/check_hantu_keys.py
```

For each key pair in `.env`, the script requests an access token (if the real-trading server rejects it, it retries the paper-trading server to tell you which kind of key you have), fetches the current price of Samsung Electronics (005930), and saves the token to the local cache. It prints only the first and last 4 characters of the App Key and the length of the secret, and never prints tokens.

### Running

```bash
bash run-dev.sh
```

This starts the backend (`127.0.0.1:8000`) and the frontend (`localhost:5173`) together. Press Ctrl+C to stop both, or run `bash stop-dev.sh` from another terminal.

You can also run the two servers separately:

```bash
# terminal 1
cd backend
uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# terminal 2
cd frontend
npm run dev
```

| URL | What |
|-----|------|
| http://localhost:5173 | Web app |
| http://127.0.0.1:8000/docs | API docs (Swagger UI) |
| http://127.0.0.1:8000/redoc | API docs (ReDoc) |
| http://127.0.0.1:8000/health | Health check |

The frontend dev server proxies `/api` requests to `http://localhost:8000`.

> [!WARNING]
> The backend API has **no authentication** and can read your account balance. Keep it bound to `127.0.0.1`; do not bind it to any other address or expose it to a network through port forwarding, tunnels or similar. See [SECURITY.md](../SECURITY.md).

### Verifying the setup

1. http://127.0.0.1:8000/health should return `{"status": "healthy", "version": "0.1.0"}`.
2. http://127.0.0.1:8000/api/us/quote/AAPL should return a US quote (no key needed).
3. At http://localhost:5173, look up `AAPL` on the **US stocks** (해외주식) page and `005930` on the **KR stocks** (국내주식) page.

### KIS access-token cache

KIS access tokens are valid for about 24 hours, and each App Key can issue at most one token per minute. The backend therefore stores tokens in `backend/.cache/kis_tokens.json` (mode 0600, gitignored) and reuses them across restarts. Entries are keyed by the SHA-256 hash of the App Key, not the key itself. Change the location with `HANTU_TOKEN_CACHE_PATH`; delete the file to force a new token on the next request.

### Tests

See [Running tests locally](RUNNING_TESTS_LOCALLY.md). It separates the offline tests, which need no keys, from the tests that call real APIs.

### Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Missing environment variables` warning at startup | Check `.env` at the repository root. If you do not use Supabase, ignore the `SUPABASE_*` entries. |
| Korean quotes fail, token errors | Check your keys with `scripts/check_hantu_keys.py`. Replace paper-trading keys with real-trading keys. If a token was just issued, wait a minute and retry. |
| Account page shows `HANTU_ACCOUNT_NUMBER ... is not configured correctly` | Make sure the account number is exactly 8 digits. |
| Every API call in the UI fails | Make sure the backend is running on port 8000. |
| `npm run dev` fails with a Node version error | Upgrade Node.js to 20.19+ or 22.12+. |
| Python `ModuleNotFoundError` | Run `uv sync` again in `backend/` and run commands through `uv run`. |
