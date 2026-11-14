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
| `GET /api/us/financials/{symbol}`의 `use_cache` | `backend/src/services/us_market.py` | `us_financials` (제공 스키마에 없으므로 "테이블 없음" 로그를 남기고 건너뜀) |

Supabase를 **쓰지 않는** 곳은 다음과 같습니다.

- `/api/korean/financials/*`: OpenDART를 직접 조회합니다. `use_cache` 파라미터는 무시됩니다.
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
2. SQL Editor에서 트리거 함수를 먼저 만듭니다. `database/financial_statements.sql`의 트리거가 이 함수를 사용하지만 SQL 파일에는 정의가 들어 있지 않습니다. (파일 머리말에 나오는 `init.sql`은 더 이상 저장소에 없으며, 아래 함수가 그 역할을 대신합니다.)

   ```sql
   CREATE OR REPLACE FUNCTION update_updated_at_column()
   RETURNS TRIGGER AS $$
   BEGIN
       NEW.updated_at = NOW();
       RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;
   ```

3. [`database/financial_statements.sql`](../database/financial_statements.sql) 전체를 SQL Editor에서 실행합니다. `CREATE TRIGGER`에 `IF NOT EXISTS`가 없으므로 한 번만 실행하십시오.
4. (권장) 행 수준 보안(RLS)을 켭니다. 정책 없이 RLS를 켜 두면 공개(anon/publishable) 키로는 이 테이블에 접근할 수 없고, RLS를 우회하는 서버용 키를 쓰는 백엔드만 읽고 쓸 수 있습니다.

   ```sql
   ALTER TABLE korean_balance_sheet      ENABLE ROW LEVEL SECURITY;
   ALTER TABLE korean_income_statement   ENABLE ROW LEVEL SECURITY;
   ALTER TABLE korean_cashflow_statement ENABLE ROW LEVEL SECURITY;
   ALTER TABLE us_balance_sheet          ENABLE ROW LEVEL SECURITY;
   ALTER TABLE us_income_statement       ENABLE ROW LEVEL SECURITY;
   ALTER TABLE us_cashflow_statement     ENABLE ROW LEVEL SECURITY;
   ```

5. 저장소 루트의 `.env`(`.env.example`을 복사)에 다음 값을 넣고 백엔드를 다시 시작합니다.

   ```dotenv
   SUPABASE_URL=https://<project-ref>.supabase.co
   SUPABASE_KEY=<service-role-or-secret-key>
   ```

   | 변수 | 설명 |
   |---|---|
   | `SUPABASE_URL` | 프로젝트 URL. Supabase 대시보드의 프로젝트 API 설정에서 확인합니다 |
   | `SUPABASE_KEY` | 서버용 키(service_role 또는 secret 키). 백엔드에서만 사용하며 커밋하거나 프런트엔드에 넣지 마십시오 |

6. 동작을 확인합니다. 국내 데이터 저장에는 `DART_API_KEY`도 필요합니다.

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
| 서버 시작 | 누락된 환경 변수 경고(또는 클라이언트 초기화 실패 메시지)가 출력되지만 서버는 정상적으로 뜹니다 |
| `GET /api/financials/...` | `503` `Database connection not available` |
| `POST /api/financials/*/statements/insert` | `200`, `success: false`, `inserted`의 값이 모두 `false`. 원천 데이터는 먼저 조회하며, 메시지는 `No data available ...`로 표시됩니다 |
| `POST /api/financials/*/statements/batch-insert` | `200`, `success: true`이지만 종목·기간별 결과가 모두 `false` |
| `GET /api/us/financials/{symbol}` | 캐시를 건너뛰고 yfinance에서 조회합니다 |
| 그 밖의 모든 엔드포인트 | 영향 없음 |

Supabase는 설정했지만 테이블을 만들지 않았다면, 조회 엔드포인트는 PostgREST 오류 메시지와 함께 `500`을 반환하고 저장 엔드포인트는 `false`를 반환합니다.

### 알려진 제약

중복 저장 시 동작, 국내 금액 단위 등 스키마 관련 제약은 [database/schema.md](../database/schema.md#알려진-제약)에 정리되어 있습니다.

---

## English

### Overview

Supabase (hosted PostgreSQL) is **optional**. Today it is only used to store financial statements fetched from OpenDART and yfinance and to read them back. Without Supabase, quotes, charts, bonds, futures/options, basis, the account check and OpenDART financial statements/disclosures all keep working.

All Supabase access in the backend goes through the singleton client (`supabase-py`) in `backend/src/integrations/supabase_client.py`.

### Where it is used

| Use | Code | Tables |
|---|---|---|
| The 10 `/api/financials/*` endpoints: store (upsert) and read financial statements | `backend/src/api/financial_statements.py`, `backend/src/services/financial_statements.py` | `korean_balance_sheet`, `korean_income_statement`, `korean_cashflow_statement`, `us_balance_sheet`, `us_income_statement`, `us_cashflow_statement` |
| `use_cache` on `GET /api/us/financials/{symbol}` | `backend/src/services/us_market.py` | `us_financials` (not in the shipped schema, so it logs "table not found" and is skipped) |

Supabase is **not** used by:

- `/api/korean/financials/*`: these call OpenDART directly; the `use_cache` parameter is ignored.
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
2. In the SQL Editor, create the trigger function first. The triggers in `database/financial_statements.sql` call it, but the SQL file does not define it. (The `init.sql` mentioned in the file header no longer exists in the repository; this function replaces it.)

   ```sql
   CREATE OR REPLACE FUNCTION update_updated_at_column()
   RETURNS TRIGGER AS $$
   BEGIN
       NEW.updated_at = NOW();
       RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;
   ```

3. Run all of [`database/financial_statements.sql`](../database/financial_statements.sql) in the SQL Editor. Run it only once: `CREATE TRIGGER` has no `IF NOT EXISTS`.
4. (Recommended) Turn on Row Level Security. With RLS on and no policies, the public (anon/publishable) key cannot touch these tables; only the backend, using a server key that bypasses RLS, can read and write them.

   ```sql
   ALTER TABLE korean_balance_sheet      ENABLE ROW LEVEL SECURITY;
   ALTER TABLE korean_income_statement   ENABLE ROW LEVEL SECURITY;
   ALTER TABLE korean_cashflow_statement ENABLE ROW LEVEL SECURITY;
   ALTER TABLE us_balance_sheet          ENABLE ROW LEVEL SECURITY;
   ALTER TABLE us_income_statement       ENABLE ROW LEVEL SECURITY;
   ALTER TABLE us_cashflow_statement     ENABLE ROW LEVEL SECURITY;
   ```

5. Put these values in `.env` at the repository root (copied from `.env.example`) and restart the backend.

   ```dotenv
   SUPABASE_URL=https://<project-ref>.supabase.co
   SUPABASE_KEY=<service-role-or-secret-key>
   ```

   | Variable | Description |
   |---|---|
   | `SUPABASE_URL` | Project URL, shown in the project's API settings in the Supabase dashboard |
   | `SUPABASE_KEY` | Server key (service_role or secret key). Use it only in the backend; never commit it or put it in the frontend |

6. Check that it works. Storing Korean data also needs `DART_API_KEY`.

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
| Server start | Prints a missing-environment-variable warning (or a client-initialisation error), then starts normally |
| `GET /api/financials/...` | `503` `Database connection not available` |
| `POST /api/financials/*/statements/insert` | `200`, `success: false`, every value in `inserted` is `false`. The source data is still fetched first, and the message reads `No data available ...` |
| `POST /api/financials/*/statements/batch-insert` | `200`, `success: true`, but every per-symbol, per-period result is `false` |
| `GET /api/us/financials/{symbol}` | Skips the cache and fetches from yfinance |
| Every other endpoint | Unaffected |

If Supabase is configured but the tables were not created, the read endpoints return `500` with the PostgREST error message and the store endpoints return `false`.

### Known limitations

Schema-level limitations, such as what happens when the same period is stored twice and the unit of Korean amounts, are listed in [database/schema.md](../database/schema.md#known-limitations).
