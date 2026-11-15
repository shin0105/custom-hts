# Supabase 연동 가이드 · Supabase Integration Guide

[한국어](#한국어) · [English](#english)

---

## 한국어

### 개요

Supabase(호스팅 PostgreSQL)는 **선택 사항**입니다. 현재는 OpenDART·yfinance에서 가져온 재무제표를 저장하고 다시 조회하는 용도로만 쓰입니다. Supabase를 설정하지 않아도 시세, 차트, 채권, 선물옵션, 베이시스, 계좌 조회, OpenDART 재무제표·공시 조회는 모두 동작합니다.

백엔드의 모든 Supabase 접근은 `backend/src/integrations/supabase_client.py`의 싱글턴 클라이언트(`supabase-py`)를 거칩니다.

### 사용처

| 사용처 | 코드 | 테이블 |
|---|---|---|
| `/api/financials/*` 엔드포인트 10개: 재무제표 저장(upsert)과 조회 | `backend/src/api/financial_statements.py`, `backend/src/services/financial_statements.py` | `korean_balance_sheet`, `korean_income_statement`, `korean_cashflow_statement`, `us_balance_sheet`, `us_income_statement`, `us_cashflow_statement` |

Supabase를 **쓰지 않는** 곳은 다음과 같습니다.

- `/api/korean/financials/*`, `/api/us/financials/{symbol}`: OpenDART·yfinance를 직접 조회합니다. `use_cache` 파라미터는 호환성 때문에 남아 있을 뿐 무시됩니다.
- 프런트엔드: Supabase에 직접 접속하지 않습니다.
- KIS 접근 토큰: 아래 설명처럼 로컬 파일에 캐시합니다.

엔드포인트 목록은 [API.md](API.md), 테이블 구조는 [database/schema.md](../database/schema.md)를 참고하십시오.

### KIS 접근 토큰은 로컬 파일에 저장됩니다

KIS 접근 토큰은 Supabase가 아니라 로컬 JSON 파일 `backend/.cache/kis_tokens.json`에 캐시됩니다 (`backend/src/integrations/token_store.py`). 토큰 발급은 앱 키당 1분에 1회로 제한되므로, 서버를 재시작해도 유효한 토큰을 재사용합니다.

- 앱 키 자체가 아니라 앱 키의 SHA-256 해시를 키로 저장합니다.
- 파일 권한은 `0600`이며 `.gitignore`에 포함되어 있습니다.
- 경로는 `HANTU_TOKEN_CACHE_PATH` 환경 변수로 바꿀 수 있습니다.

### 설정 방법

1. [Supabase](https://supabase.com)에서 프로젝트를 만듭니다.
2. [`database/financial_statements.sql`](../database/financial_statements.sql) 전체를 SQL Editor에서 실행합니다. 트리거 함수(`update_updated_at_column()`)까지 이 파일 안에 정의되어 있어 따로 준비할 것이 없고, 이미 테이블이 있는 데이터베이스에서 다시 실행해도 됩니다. PostgreSQL 15 이상이 필요하며 현재 Supabase 프로젝트는 모두 해당합니다. 이전 버전 스크립트로 만든 테이블은 다시 실행하면 고유 제약이 갱신되고, 중복된 연간 행은 가장 최근에 갱신된 행만 남습니다.
3. (권장) 행 수준 보안(RLS)을 켭니다. 정책 없이 RLS를 켜 두면 공개(anon/publishable) 키로는 이 테이블에 접근할 수 없고, RLS를 우회하는 서버용 키를 쓰는 백엔드만 읽고 쓸 수 있습니다.

   ```sql
   ALTER TABLE korean_balance_sheet      ENABLE ROW LEVEL SECURITY;
   ALTER TABLE korean_income_statement   ENABLE ROW LEVEL SECURITY;
   ALTER TABLE korean_cashflow_statement ENABLE ROW LEVEL SECURITY;
   ALTER TABLE us_balance_sheet          ENABLE ROW LEVEL SECURITY;
   ALTER TABLE us_income_statement       ENABLE ROW LEVEL SECURITY;
   ALTER TABLE us_cashflow_statement     ENABLE ROW LEVEL SECURITY;
   ```

4. 저장소 루트의 `.env`(`.env.example`을 복사)에 다음 값을 넣고 백엔드를 다시 시작합니다.

   ```dotenv
   SUPABASE_URL=https://<project-ref>.supabase.co
   SUPABASE_KEY=<service-role-or-secret-key>
   ```

   | 변수 | 설명 |
   |---|---|
   | `SUPABASE_URL` | 프로젝트 URL. Supabase 대시보드의 프로젝트 API 설정에서 확인합니다 |
   | `SUPABASE_KEY` | 서버용 키(service_role 또는 secret 키). 백엔드에서만 사용하며 커밋하거나 프런트엔드에 넣지 마십시오 |

5. 동작을 확인합니다. 국내 데이터 저장에는 `DART_API_KEY`도 필요합니다.

   ```bash
   curl -X POST http://127.0.0.1:8000/api/financials/korean/statements/insert \
     -H "Content-Type: application/json" \
     -d '{"symbol": "005930", "year": 2024}'

   curl "http://127.0.0.1:8000/api/financials/korean/balance-sheet/005930?year=2024"
   ```

### Supabase를 설정하지 않은 경우

`SUPABASE_URL`이 비어 있거나 클라이언트 생성에 실패하면(예: `.env.example`의 자리표시자 값을 그대로 둔 경우) 클라이언트가 `None`이 되고, 다음과 같이 동작합니다.

| 상황 | 동작 |
|---|---|
| 서버 시작 | 정상적으로 뜹니다. Supabase 변수를 비워 두면 경고하지 않고, 둘 중 하나만 넣었거나 클라이언트 생성에 실패하면 경고(또는 초기화 실패 메시지)를 출력합니다 |
| `GET /api/financials/...` | `503` `Database connection not available` |
| `POST /api/financials/*/statements/insert`, `.../batch-insert` | `503` `Database connection not available`. 원천 데이터(OpenDART·yfinance)는 조회하지 않습니다 |
| 그 밖의 모든 엔드포인트 | 영향 없음 |

Supabase는 설정했지만 테이블을 만들지 않았다면, 조회 엔드포인트는 PostgREST 오류 메시지와 함께 `500`을 반환하고 저장 엔드포인트는 해당 재무제표를 `false`로 표시합니다.

### 저장 동작

- 저장은 `(symbol, year, quarter)`를 기준으로 upsert합니다. 같은 기간을 다시 저장하면 기존 행을 갱신하며, 연간 데이터(`quarter`가 `NULL`)도 마찬가지입니다.
- `insert`의 `success`는 재무제표 3종 중 하나라도 저장되면 `true`입니다.
- `batch-insert`는 요청한 모든 종목·기간에서 하나 이상 저장됐을 때만 `success: true`이며, 저장 건수(`stored`/`attempted`), 아무것도 저장하지 못한 종목·기간 목록(`failed`), 재무제표별 결과(`results`)를 함께 돌려줍니다.

### 알려진 제약

스키마 관련 제약은 [database/schema.md](../database/schema.md#알려진-제약)에, 국내 금액 단위는 [같은 문서의 단위 항목](../database/schema.md#단위)에 정리되어 있습니다.

---

## English

### Overview

Supabase (hosted PostgreSQL) is **optional**. Today it is only used to store financial statements fetched from OpenDART and yfinance and to read them back. Without Supabase, quotes, charts, bonds, futures/options, basis, the account check and OpenDART financial statements/disclosures all keep working.

All Supabase access in the backend goes through the singleton client (`supabase-py`) in `backend/src/integrations/supabase_client.py`.

### Where it is used

| Use | Code | Tables |
|---|---|---|
| The 10 `/api/financials/*` endpoints: store (upsert) and read financial statements | `backend/src/api/financial_statements.py`, `backend/src/services/financial_statements.py` | `korean_balance_sheet`, `korean_income_statement`, `korean_cashflow_statement`, `us_balance_sheet`, `us_income_statement`, `us_cashflow_statement` |

Supabase is **not** used by:

- `/api/korean/financials/*` and `/api/us/financials/{symbol}`: these call OpenDART and yfinance directly. The `use_cache` parameter is kept only for compatibility and is ignored.
- The frontend: it never connects to Supabase.
- KIS access tokens: cached in a local file, as described below.

See [API.md](API.md) for the endpoint list and [database/schema.md](../database/schema.md) for the tables.

### KIS access tokens live in a local file

KIS access tokens are cached in a local JSON file, `backend/.cache/kis_tokens.json`, not in Supabase (`backend/src/integrations/token_store.py`). Token issuance is limited to once per minute per app key, so a valid token is reused across server restarts.

- Entries are keyed by the SHA-256 hash of the app key, never the key itself.
- The file is created with `0600` permissions and is gitignored.
- Override the path with the `HANTU_TOKEN_CACHE_PATH` environment variable.

### Setup

1. Create a project on [Supabase](https://supabase.com).
2. Run all of [`database/financial_statements.sql`](../database/financial_statements.sql) in the SQL Editor. It defines everything it needs, including the trigger function (`update_updated_at_column()`), and is safe to run again on a database that already has the tables. It needs PostgreSQL 15 or later, which every current Supabase project runs. Re-running it on tables made by an older version of the script updates the unique constraint and keeps only the most recently updated row of any duplicated annual rows.
3. (Recommended) Turn on Row Level Security. With RLS on and no policies, the public (anon/publishable) key cannot touch these tables; only the backend, using a server key that bypasses RLS, can read and write them.

   ```sql
   ALTER TABLE korean_balance_sheet      ENABLE ROW LEVEL SECURITY;
   ALTER TABLE korean_income_statement   ENABLE ROW LEVEL SECURITY;
   ALTER TABLE korean_cashflow_statement ENABLE ROW LEVEL SECURITY;
   ALTER TABLE us_balance_sheet          ENABLE ROW LEVEL SECURITY;
   ALTER TABLE us_income_statement       ENABLE ROW LEVEL SECURITY;
   ALTER TABLE us_cashflow_statement     ENABLE ROW LEVEL SECURITY;
   ```

4. Put these values in `.env` at the repository root (copied from `.env.example`) and restart the backend.

   ```dotenv
   SUPABASE_URL=https://<project-ref>.supabase.co
   SUPABASE_KEY=<service-role-or-secret-key>
   ```

   | Variable | Description |
   |---|---|
   | `SUPABASE_URL` | Project URL, shown in the project's API settings in the Supabase dashboard |
   | `SUPABASE_KEY` | Server key (service_role or secret key). Use it only in the backend; never commit it or put it in the frontend |

5. Check that it works. Storing Korean data also needs `DART_API_KEY`.

   ```bash
   curl -X POST http://127.0.0.1:8000/api/financials/korean/statements/insert \
     -H "Content-Type: application/json" \
     -d '{"symbol": "005930", "year": 2024}'

   curl "http://127.0.0.1:8000/api/financials/korean/balance-sheet/005930?year=2024"
   ```

### When Supabase is not configured

If `SUPABASE_URL` is empty or the client cannot be created (for example, the `.env.example` placeholder was left in place), the client is `None` and the backend behaves as follows.

| Situation | Behaviour |
|---|---|
| Server start | Starts normally. Empty Supabase variables cause no warning; setting only one of them, or a client that fails to initialise, prints a warning (or an initialisation error) |
| `GET /api/financials/...` | `503` `Database connection not available` |
| `POST /api/financials/*/statements/insert`, `.../batch-insert` | `503` `Database connection not available`. The source data (OpenDART, yfinance) is not fetched |
| Every other endpoint | Unaffected |

If Supabase is configured but the tables were not created, the read endpoints return `500` with the PostgREST error message and the store endpoints mark the affected statements `false`.

### How storing works

- Rows are upserted on `(symbol, year, quarter)`. Storing the same period again updates the existing row, including annual rows (`quarter` is `NULL`).
- `success` from `insert` is `true` when at least one of the three statements was stored.
- `batch-insert` returns `success: true` only when every requested symbol and period stored at least one statement. It also returns the statement counts (`stored`/`attempted`), the symbol/period pairs that stored nothing (`failed`), and per-statement `results`.

### Known limitations

Schema-level limitations are listed in [database/schema.md](../database/schema.md#known-limitations), and the unit of Korean amounts under [Units](../database/schema.md#units) in the same document.
