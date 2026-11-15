# 데이터베이스 스키마 · Database Schema

[한국어](#한국어) · [English](#english)

---

## 한국어

### 개요

- 데이터베이스(Supabase PostgreSQL)는 **선택 사항**이며, 재무제표 저장용 테이블 6개에만 사용됩니다. 시세, 차트, 채권, 선물옵션, 베이시스, 계좌 조회 등 나머지 기능은 데이터베이스 없이 동작합니다.
- 스키마 정의 파일은 [financial_statements.sql](financial_statements.sql) 하나뿐입니다. 필요한 함수까지 모두 들어 있어 단독으로 실행되며, 여러 번 실행해도 됩니다.
- 테이블 생성 순서와 환경 변수 설정은 [Supabase 연동 가이드](../docs/SUPABASE_INTEGRATION.md)를 참고하십시오.
- 이 테이블을 읽고 쓰는 API는 `/api/financials/*`입니다 ([API 레퍼런스](../docs/API.md)).
- KIS 접근 토큰은 데이터베이스가 아니라 로컬 파일(`backend/.cache/kis_tokens.json`)에 캐시됩니다.

### 테이블

| 테이블 | 시장 | 출처 | 내용 |
|---|---|---|---|
| `korean_balance_sheet` | 국내 | OpenDART | 재무상태표 |
| `korean_income_statement` | 국내 | OpenDART | 손익계산서 |
| `korean_cashflow_statement` | 국내 | OpenDART | 현금흐름표 |
| `us_balance_sheet` | 미국 | yfinance | 대차대조표 |
| `us_income_statement` | 미국 | yfinance | 손익계산서 |
| `us_cashflow_statement` | 미국 | yfinance | 현금흐름표 |

### 공통 컬럼과 제약

| 컬럼 | 타입 | 설명 |
|---|---|---|
| `id` | `SERIAL PRIMARY KEY` | 내부 식별자 |
| `symbol` | `VARCHAR(10) NOT NULL` | 국내 종목코드 또는 미국 티커 |
| `company_name` | `VARCHAR(255) NOT NULL` | 회사명 |
| `year` | `INTEGER NOT NULL` | 회계연도 |
| `quarter` | `INTEGER` | 분기(1–4). 연간 데이터는 `NULL` |
| `report_code` | `VARCHAR(10)` | 국내 테이블에만 있음. OpenDART 보고서 코드 (현재 저장 서비스는 값을 채우지 않음) |
| 금액 컬럼 | `NUMERIC(20, 2)` | 아래 표 참고. 주당순이익(EPS) 컬럼만 `NUMERIC(10, 4)` |
| `raw_data` | `JSONB` | 원본 계정 데이터 전체 |
| `created_at`, `updated_at` | `TIMESTAMPTZ DEFAULT NOW()` | 생성·수정 시각 |

- **고유 제약:** 테이블마다 `UNIQUE(symbol, year, quarter)` (`<테이블명>_unique`)
- **인덱스:** 테이블마다 `symbol`, `year`, `updated_at`에 인덱스 (`idx_kr_bs_symbol`, `idx_us_cf_updated` 등)
- **트리거:** 테이블마다 `BEFORE UPDATE` 트리거가 `update_updated_at_column()` 함수(같은 SQL 파일에 정의)로 `updated_at`을 갱신합니다.
- **주석:** 각 컬럼이 어떤 OpenDART 계정명 또는 yfinance 항목에서 오는지는 SQL 파일의 `COMMENT ON COLUMN`에 적혀 있습니다.

### 금액 컬럼

#### 재무상태표 (`*_balance_sheet`)

| 구분 | `korean_balance_sheet` | `us_balance_sheet` |
|---|---|---|
| 자산총계·유동자산 | `total_assets`, `current_assets`, `cash_and_cash_equivalents`, `short_term_financial_instruments`, `accounts_receivable`, `inventory`, `other_current_assets` | `total_assets`, `current_assets`, `cash_and_cash_equivalents`, `short_term_investments`, `receivables`, `inventory`, `other_current_assets` |
| 비유동자산 | `non_current_assets`, `long_term_financial_instruments`, `property_plant_equipment`, `intangible_assets`, `investments`, `other_non_current_assets` | `non_current_assets`, `long_term_investments`, `property_plant_equipment`, `goodwill`, `intangible_assets`, `other_non_current_assets` |
| 부채 | `total_liabilities`, `current_liabilities`, `accounts_payable`, `short_term_debt`, `other_current_liabilities`, `non_current_liabilities`, `long_term_debt`, `other_non_current_liabilities` | `total_liabilities`, `current_liabilities`, `accounts_payable`, `short_term_debt`, `current_portion_long_term_debt`, `other_current_liabilities`, `non_current_liabilities`, `long_term_debt`, `deferred_tax_liabilities`, `other_non_current_liabilities` |
| 자본 | `total_equity`, `paid_in_capital`, `retained_earnings`, `other_equity` | `stockholders_equity`, `common_stock`, `retained_earnings`, `treasury_stock`, `other_equity` |

#### 손익계산서 (`*_income_statement`)

| 구분 | `korean_income_statement` | `us_income_statement` |
|---|---|---|
| 매출 | `revenue`, `cost_of_revenue`, `gross_profit` | `total_revenue`, `cost_of_revenue`, `gross_profit` |
| 영업 | `operating_expenses`, `selling_general_admin`, `research_development`, `operating_income` | `operating_expense`, `selling_general_admin`, `research_development`, `operating_income` |
| 영업외 | `non_operating_income`, `non_operating_expenses`, `financial_income`, `financial_expenses` | `interest_income`, `interest_expense`, `other_income_expense` |
| 이익 | `income_before_tax`, `income_tax_expense`, `net_income` | `pretax_income`, `tax_provision`, `net_income`, `net_income_common_stockholders` |
| 기타 | `ebitda`, `earnings_per_share`, `diluted_eps` | `ebitda`, `basic_eps`, `diluted_eps`, `basic_average_shares`, `diluted_average_shares` |

#### 현금흐름표 (`*_cashflow_statement`)

| 구분 | `korean_cashflow_statement` | `us_cashflow_statement` |
|---|---|---|
| 영업활동 | `operating_cash_flow`, `net_income_for_cf`, `depreciation_amortization`, `change_working_capital`, `change_accounts_receivable`, `change_inventory`, `change_accounts_payable`, `other_operating_activities` | `operating_cash_flow`, `net_income_from_continuing_ops`, `depreciation_amortization`, `deferred_income_tax`, `stock_based_compensation`, `change_working_capital`, `change_receivables`, `change_inventory`, `change_payables`, `other_operating_cash_flows` |
| 투자활동 | `investing_cash_flow`, `capital_expenditure`, `acquisition_investments`, `sale_of_investments`, `other_investing_activities` | `investing_cash_flow`, `capital_expenditure`, `net_intangibles`, `net_investment_purchase_sale`, `sale_purchase_investment`, `other_investing_cash_flows` |
| 재무활동 | `financing_cash_flow`, `proceeds_debt`, `repayment_debt`, `proceeds_stock_issuance`, `dividends_paid`, `stock_repurchase`, `other_financing_activities` | `financing_cash_flow`, `long_term_debt_issuance`, `long_term_debt_payments`, `short_term_debt_issuance`, `common_stock_issuance`, `common_stock_payments`, `cash_dividends_paid`, `repurchase_capital_stock`, `other_financing_cash_flows` |
| 합계 | `net_change_cash`, `free_cash_flow` | `net_change_cash`, `free_cash_flow` |

### 단위

- **미국 테이블:** 실제 달러 금액(USD)입니다. EPS는 주당 달러, `*_average_shares`는 주식 수입니다.
- **국내 테이블:** SQL 주석에는 백만원 단위라고 적혀 있지만, 현재 저장 서비스(`backend/src/services/financial_statements.py`)는 OpenDART가 반환한 금액을 변환 없이 저장하므로 실제 값은 원 단위입니다. EPS는 주당 원입니다.

### 알려진 제약

- 저장 서비스의 upsert는 충돌 기준 컬럼을 지정하지 않습니다. 그래서 같은 분기 데이터를 다시 저장하면 고유 제약 위반으로 실패하고, 연간 데이터(`quarter`가 `NULL`)는 고유 제약에 걸리지 않아 중복 행이 쌓일 수 있습니다.
- 행 수준 보안(RLS)은 설정되어 있지 않습니다. 권장 설정은 [Supabase 연동 가이드](../docs/SUPABASE_INTEGRATION.md)를 참고하십시오.

---

## English

### Overview

- The database (Supabase PostgreSQL) is **optional** and is only used for six financial-statement tables. Quotes, charts, bonds, futures/options, basis and the account check all work without it.
- The only schema file is [financial_statements.sql](financial_statements.sql). It is self-contained, including the helper function it needs, and safe to run more than once.
- For the setup order and environment variables, see the [Supabase integration guide](../docs/SUPABASE_INTEGRATION.md).
- The API that reads and writes these tables is `/api/financials/*` ([API reference](../docs/API.md)).
- KIS access tokens are cached in a local file (`backend/.cache/kis_tokens.json`), not in the database.

### Tables

| Table | Market | Source | Contents |
|---|---|---|---|
| `korean_balance_sheet` | Korea | OpenDART | Balance sheet |
| `korean_income_statement` | Korea | OpenDART | Income statement |
| `korean_cashflow_statement` | Korea | OpenDART | Cash flow statement |
| `us_balance_sheet` | US | yfinance | Balance sheet |
| `us_income_statement` | US | yfinance | Income statement |
| `us_cashflow_statement` | US | yfinance | Cash flow statement |

### Common columns and constraints

| Column | Type | Description |
|---|---|---|
| `id` | `SERIAL PRIMARY KEY` | Internal ID |
| `symbol` | `VARCHAR(10) NOT NULL` | Korean stock code or US ticker |
| `company_name` | `VARCHAR(255) NOT NULL` | Company name |
| `year` | `INTEGER NOT NULL` | Fiscal year |
| `quarter` | `INTEGER` | Quarter (1–4); `NULL` for annual data |
| `report_code` | `VARCHAR(10)` | Korean tables only. OpenDART report code (not filled by the current storage service) |
| Amount columns | `NUMERIC(20, 2)` | See below. Only the EPS columns are `NUMERIC(10, 4)` |
| `raw_data` | `JSONB` | Full raw line items |
| `created_at`, `updated_at` | `TIMESTAMPTZ DEFAULT NOW()` | Creation and update times |

- **Unique constraint:** `UNIQUE(symbol, year, quarter)` on every table (`<table>_unique`)
- **Indexes:** on `symbol`, `year` and `updated_at` for every table (`idx_kr_bs_symbol`, `idx_us_cf_updated`, …)
- **Triggers:** a `BEFORE UPDATE` trigger on every table sets `updated_at` via the `update_updated_at_column()` function, defined in the same SQL file.
- **Comments:** the OpenDART account name or yfinance field behind each column is recorded in the SQL file's `COMMENT ON COLUMN` statements.

### Amount columns

#### Balance sheet (`*_balance_sheet`)

| Group | `korean_balance_sheet` | `us_balance_sheet` |
|---|---|---|
| Total and current assets | `total_assets`, `current_assets`, `cash_and_cash_equivalents`, `short_term_financial_instruments`, `accounts_receivable`, `inventory`, `other_current_assets` | `total_assets`, `current_assets`, `cash_and_cash_equivalents`, `short_term_investments`, `receivables`, `inventory`, `other_current_assets` |
| Non-current assets | `non_current_assets`, `long_term_financial_instruments`, `property_plant_equipment`, `intangible_assets`, `investments`, `other_non_current_assets` | `non_current_assets`, `long_term_investments`, `property_plant_equipment`, `goodwill`, `intangible_assets`, `other_non_current_assets` |
| Liabilities | `total_liabilities`, `current_liabilities`, `accounts_payable`, `short_term_debt`, `other_current_liabilities`, `non_current_liabilities`, `long_term_debt`, `other_non_current_liabilities` | `total_liabilities`, `current_liabilities`, `accounts_payable`, `short_term_debt`, `current_portion_long_term_debt`, `other_current_liabilities`, `non_current_liabilities`, `long_term_debt`, `deferred_tax_liabilities`, `other_non_current_liabilities` |
| Equity | `total_equity`, `paid_in_capital`, `retained_earnings`, `other_equity` | `stockholders_equity`, `common_stock`, `retained_earnings`, `treasury_stock`, `other_equity` |

#### Income statement (`*_income_statement`)

| Group | `korean_income_statement` | `us_income_statement` |
|---|---|---|
| Revenue | `revenue`, `cost_of_revenue`, `gross_profit` | `total_revenue`, `cost_of_revenue`, `gross_profit` |
| Operating | `operating_expenses`, `selling_general_admin`, `research_development`, `operating_income` | `operating_expense`, `selling_general_admin`, `research_development`, `operating_income` |
| Non-operating | `non_operating_income`, `non_operating_expenses`, `financial_income`, `financial_expenses` | `interest_income`, `interest_expense`, `other_income_expense` |
| Profit | `income_before_tax`, `income_tax_expense`, `net_income` | `pretax_income`, `tax_provision`, `net_income`, `net_income_common_stockholders` |
| Other | `ebitda`, `earnings_per_share`, `diluted_eps` | `ebitda`, `basic_eps`, `diluted_eps`, `basic_average_shares`, `diluted_average_shares` |

#### Cash flow statement (`*_cashflow_statement`)

| Group | `korean_cashflow_statement` | `us_cashflow_statement` |
|---|---|---|
| Operating | `operating_cash_flow`, `net_income_for_cf`, `depreciation_amortization`, `change_working_capital`, `change_accounts_receivable`, `change_inventory`, `change_accounts_payable`, `other_operating_activities` | `operating_cash_flow`, `net_income_from_continuing_ops`, `depreciation_amortization`, `deferred_income_tax`, `stock_based_compensation`, `change_working_capital`, `change_receivables`, `change_inventory`, `change_payables`, `other_operating_cash_flows` |
| Investing | `investing_cash_flow`, `capital_expenditure`, `acquisition_investments`, `sale_of_investments`, `other_investing_activities` | `investing_cash_flow`, `capital_expenditure`, `net_intangibles`, `net_investment_purchase_sale`, `sale_purchase_investment`, `other_investing_cash_flows` |
| Financing | `financing_cash_flow`, `proceeds_debt`, `repayment_debt`, `proceeds_stock_issuance`, `dividends_paid`, `stock_repurchase`, `other_financing_activities` | `financing_cash_flow`, `long_term_debt_issuance`, `long_term_debt_payments`, `short_term_debt_issuance`, `common_stock_issuance`, `common_stock_payments`, `cash_dividends_paid`, `repurchase_capital_stock`, `other_financing_cash_flows` |
| Totals | `net_change_cash`, `free_cash_flow` | `net_change_cash`, `free_cash_flow` |

### Units

- **US tables:** actual US dollar amounts. EPS is USD per share; `*_average_shares` are share counts.
- **Korean tables:** the SQL comments say millions of KRW, but the current storage service (`backend/src/services/financial_statements.py`) stores the amounts returned by OpenDART unchanged, so the values are in KRW (won). EPS is KRW per share.

### Known limitations

- The storage service's upsert does not name a conflict target. Re-storing the same quarter therefore fails on the unique constraint, while annual rows (`quarter` is `NULL`) are not caught by it and can be duplicated.
- Row Level Security (RLS) is not configured. See the [Supabase integration guide](../docs/SUPABASE_INTEGRATION.md) for the recommended setting.
