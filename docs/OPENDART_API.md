# OpenDART 연동 · OpenDART Integration

[한국어](#한국어) · [English](#english)

---

## 한국어

### 개요

금융감독원 전자공시시스템의 [OpenDART](https://opendart.fss.or.kr/) API로 국내 상장사의 재무제표(주요계정), 기업 개황, 공시 목록을 가져옵니다.

- 클라이언트: [`backend/src/integrations/opendart.py`](../backend/src/integrations/opendart.py) (`OpenDartClient`, 전역 인스턴스 `opendart_client`)
- 기본 URL: `https://opendart.fss.or.kr/api`
- 요청·응답 필드 전체 명세는 OpenDART 사이트의 개발가이드를 보세요.

### 인증키

OpenDART에서 인증키(40자)를 발급받아 저장소 루트 `.env`에 넣습니다. 모든 요청에 `crtfc_key` 파라미터로 전달됩니다.

```bash
DART_API_KEY=your_dart_api_key
```

키가 없으면 재무제표·기업 개황·공시 요청은 데이터 없이 끝나고, 해당 엔드포인트는 404를 돌려줍니다.

### 사용하는 API

| OpenDART API | 경로 | 용도 |
|--------------|------|------|
| 고유번호 | `corpCode.xml` (ZIP) | 종목코드 → 고유번호(corp_code) 매핑 |
| 단일회사 주요계정 | `fnlttSinglAcnt.json` | 재무제표 |
| 다중회사 주요계정 | `fnlttMultiAcnt.json` | 재무제표 (위 결과와 합친 뒤 중복 제거) |
| 기업개황 | `company.json` | 기업 정보 |
| 공시검색 | `list.json` | 공시 목록 |

- 재무제표 요청 파라미터는 `corp_code`, `bsns_year`, `reprt_code`입니다. 두 주요계정 API 결과를 합치고 `fs_div`(`CFS` 연결, `OFS` 별도)로 거른 뒤 중복을 없앱니다.
- 보고서 코드: `11013` 1분기, `11012` 반기, `11014` 3분기, `11011` 사업보고서. 백엔드는 `quarter` 1·2·3·4를 각각 이 순서로 매핑하고, 분기를 주지 않으면 `11011`을 씁니다.
- 주요계정 API는 재무상태표(BS)와 손익계산서(IS)의 주요 계정만 제공하고 현금흐름표(CF) 항목은 없습니다(삼성전자 실제 응답으로 확인). 그래서 화면에는 현금흐름표 탭이 없고, `/cash-flow` 엔드포인트는 `501`을 돌려주며, Supabase 저장도 국내 현금흐름표는 건너뜁니다.
- 응답 `status`: `000` 정상, `013` 데이터 없음(빈 결과로 처리), `020` 요청 한도 초과. 그 밖의 값은 오류로 보고 404를 돌려줍니다.

### 백엔드 엔드포인트

| 엔드포인트 | 내용 |
|------------|------|
| `GET /api/korean/financials/{symbol}` | 요약 값(매출액, 영업이익, 당기순이익, 자산·부채·자본총계, EPS, BPS) |
| `GET /api/korean/financials/{symbol}/all` | 주요계정 원본 항목 전체. 국내주식 화면의 재무제표 표가 사용 |
| `GET /api/korean/financials/{symbol}/balance-sheet`, `/income-statement` | `sj_div`가 BS·IS인 항목만 |
| `GET /api/korean/financials/{symbol}/cash-flow` | 항상 `501` (주요계정 API에 현금흐름표 항목이 없음) |
| `GET /api/korean/valuation/{symbol}` | KIS 현재가와 DART 재무로 계산한 PER·PBR·EPS·BPS |
| `GET /api/korean/company/{symbol}` | 기업개황 |
| `GET /api/korean/disclosures` | 공시 목록 (`corp`, `start`, `end`, `kind`, `final`, `limit`) |

- 재무 관련 엔드포인트는 `year`, `quarter`를 받고, `/all`과 `/valuation`은 `fs_div`도 받습니다. `year` 기본값은 `/financials/{symbol}`만 올해이고 나머지는 전년도입니다.
- `/disclosures`의 `corp`는 6자리 종목코드만 인식합니다. 회사명을 넣으면 필터가 적용되지 않아 전체 회사의 공시가 돌아옵니다.
- (선택) [`backend/src/services/financial_statements.py`](../backend/src/services/financial_statements.py)는 같은 데이터를 Supabase 테이블에 저장하며 `/api/financials/korean/...` 엔드포인트가 이를 씁니다. [SUPABASE_INTEGRATION.md](SUPABASE_INTEGRATION.md)를 보세요.
- 전체 파라미터는 [API.md](API.md)에 있습니다.

### 고유번호(corp_code) 매핑

OpenDART의 기업별 API는 6자리 종목코드가 아니라 8자리 고유번호를 받습니다. 클라이언트는 다음 순서로 고유번호를 찾습니다.

1. 메모리의 매핑. 시작할 때 [`backend/src/data/opendart/corp_codes.json`](../backend/src/data/opendart/corp_codes.json)을 저장 시점과 관계없이 읽어 둡니다. 고유번호는 회사마다 바뀌지 않으므로 오래된 파일도 그 안에 있는 회사에는 맞는 값입니다. 코드에 따로 박아 둔 매핑은 없습니다.
2. 매핑에 없고 파일이 저장된 지 24시간이 지났으면(또는 파일이 없으면) `corpCode.xml`을 내려받아 종목코드가 있는 회사만 매핑에 넣고 `corp_codes.json`을 다시 씁니다. 내려받기에 실패해도 이미 읽어 둔 매핑은 그대로 씁니다. 파일이 24시간 안에 저장됐으면 없는 종목이라도 다시 내려받지 않습니다.

```json
{
  "timestamp": "2025-01-01T00:00:00+00:00",
  "codes": {
    "005930": "00126380"
  }
}
```

- `corp_codes.json`은 상장사 전체 스냅샷으로 커밋되어 있습니다. 내려받기가 일어나면 이 파일이 바뀌므로 git 변경 사항으로 나타납니다.
- 새로 상장한 종목을 바로 쓰고 싶으면 아래 명령으로 매핑을 직접 새로 받을 수 있습니다.

```bash
cd backend
uv run python -c "from src.integrations.opendart import opendart_client as c; print(c.download_corp_code_list())"
```

### 요청 한도

- OpenDART는 인증키별로 하루 요청 수를 제한하며(일반적으로 약 20,000건), 넘으면 `status` `020`을 돌려줍니다. 정확한 한도는 OpenDART 안내를 따르세요.
- 재무제표 한 번 조회에 주요계정 API 2건이 나갑니다.
- 클라이언트 자체에는 요청 간 대기가 없습니다. 많은 종목을 조회할 때는 아래 스크립트를 쓰세요.

### 전 종목 일괄 수집 스크립트

[`backend/scripts/fetch_opendart_all_stocks.py`](../backend/scripts/fetch_opendart_all_stocks.py)는 여러 종목의 재무제표를 받아 CSV로 저장합니다.

```bash
cd backend
uv run python scripts/fetch_opendart_all_stocks.py --years 2024
uv run python scripts/fetch_opendart_all_stocks.py --years 2025 --periods 2025Q1 2025Q2 --symbols 005930 000660
```

| 옵션 | 설명 |
|------|------|
| `--years` | 필수. 수집할 연도 목록 |
| `--periods` | 예: `2025Q2 2025Y`. 생략하면 1~4분기와 연간(`Y`) 모두 |
| `--symbols` | 일부 종목만 수집. 생략하면 고유번호 매핑의 전체 종목 |
| `--limit` | 종목코드 순으로 앞의 N개만 |
| `--sleep` | 분기별 조회 사이 대기(초), 기본 0.3 |
| `--retries`, `--retry-sleep` | 실패 시 재시도 횟수(기본 2)와 대기(기본 30초) |
| `--output-root` | 출력 폴더, 기본 저장소 루트의 `database/raw_data` |

- 결과: `<output-root>/<연도>/<기간>/{balance_sheet,income_statement,cashflow_statement}.csv`와 같은 이름의 `.schema.json`. 주요계정 API에는 현금흐름표 항목이 없으므로 `cashflow_statement.csv`에는 금액이 들어가지 않습니다.
- 진행 상황은 `<output-root>/progress/opendart_<연도>.json`에 저장되어, 다시 실행하면 끝난 종목은 건너뜁니다. 재시도 후에도 실패하면 진행 상황을 저장하고 멈춥니다.
- 연결·별도를 모두 받으므로 종목·연도마다 최대 16건을 요청합니다. 전 종목 수집은 하루 한도를 넘을 수 있으니 며칠에 나눠 실행하세요.
- 분기 값: 스크립트는 반기·사업보고서의 손익·현금흐름 금액을 누적값, 3분기 금액을 3개월 값으로 보고 2분기 = 반기 − 1분기, 4분기 = 연간 − 반기 − 3분기로 계산합니다. 재무상태표는 시점 값을 그대로 씁니다.
- `.gitignore`는 CSV만 제외합니다. `.schema.json`과 진행 파일도 커밋하지 마세요.

### 참고

- [OpenDART](https://opendart.fss.or.kr/): 인증키 신청, 개발가이드
- [API.md](API.md): 백엔드 REST API

---

## English

### Overview

The backend uses the [OpenDART](https://opendart.fss.or.kr/) API of the Financial Supervisory Service's disclosure system to fetch financial statements (major accounts), company overviews and filing lists for Korean listed companies.

- Client: [`backend/src/integrations/opendart.py`](../backend/src/integrations/opendart.py) (`OpenDartClient`, global instance `opendart_client`)
- Base URL: `https://opendart.fss.or.kr/api`
- For the full request/response field specs, see the developer guide on the OpenDART site.

### API key

Get an API key (40 characters) from OpenDART and put it in the repository-root `.env`. It is sent with every request as the `crtfc_key` parameter.

```bash
DART_API_KEY=your_dart_api_key
```

Without a key, financial statement, company and filing requests return no data, and those endpoints respond with 404.

### APIs used

| OpenDART API | Path | Purpose |
|--------------|------|---------|
| Corp code list | `corpCode.xml` (ZIP) | Stock code → corp code (corp_code) mapping |
| Single-company major accounts | `fnlttSinglAcnt.json` | Financial statements |
| Multi-company major accounts | `fnlttMultiAcnt.json` | Financial statements (merged with the above, then de-duplicated) |
| Company overview | `company.json` | Company details |
| Disclosure search | `list.json` | Filing list |

- Financial statement requests take `corp_code`, `bsns_year` and `reprt_code`. Results from both major-account APIs are merged, filtered by `fs_div` (`CFS` consolidated, `OFS` separate) and de-duplicated.
- Report codes: `11013` Q1, `11012` half-year, `11014` Q3, `11011` annual report. The backend maps `quarter` 1, 2, 3, 4 to these in that order and uses `11011` when no quarter is given.
- The major-account APIs provide the main balance sheet (BS) and income statement (IS) accounts only; they have no cash flow (CF) items (confirmed against real responses for Samsung Electronics). So the UI has no cash-flow tab, the `/cash-flow` endpoint returns `501`, and Supabase storage skips Korean cash flow statements.
- Response `status`: `000` OK, `013` no data (treated as an empty result), `020` request limit exceeded. Any other value is treated as an error and the endpoint returns 404.

### Backend endpoints

| Endpoint | Content |
|----------|---------|
| `GET /api/korean/financials/{symbol}` | Summary values (revenue, operating income, net income, total assets/liabilities/equity, EPS, BPS) |
| `GET /api/korean/financials/{symbol}/all` | Every raw major-account line item. Used by the statements table on the domestic stock page |
| `GET /api/korean/financials/{symbol}/balance-sheet`, `/income-statement` | Only items whose `sj_div` is BS or IS |
| `GET /api/korean/financials/{symbol}/cash-flow` | Always `501` (the major-account APIs have no cash flow items) |
| `GET /api/korean/valuation/{symbol}` | PER, PBR, EPS and BPS from the KIS price and DART financials |
| `GET /api/korean/company/{symbol}` | Company overview |
| `GET /api/korean/disclosures` | Filing list (`corp`, `start`, `end`, `kind`, `final`, `limit`) |

- The financial endpoints take `year` and `quarter`; `/all` and `/valuation` also take `fs_div`. `year` defaults to the current year for `/financials/{symbol}` and to the previous year everywhere else.
- `corp` on `/disclosures` only recognises 6-digit stock codes. A company name is not applied as a filter, so filings for all companies come back.
- (Optional) [`backend/src/services/financial_statements.py`](../backend/src/services/financial_statements.py) stores the same data in Supabase tables, served by the `/api/financials/korean/...` endpoints. See [SUPABASE_INTEGRATION.md](SUPABASE_INTEGRATION.md).
- All parameters are listed in [API.md](API.md).

### Corp code mapping

OpenDART's per-company APIs take an 8-digit corp code, not the 6-digit stock code. The client resolves it in this order:

1. The in-memory mapping. At start-up it loads [`backend/src/data/opendart/corp_codes.json`](../backend/src/data/opendart/corp_codes.json) however old the file is. A company's corp code never changes, so even a stale file is correct for every company it lists. There is no built-in table in the code.
2. On a miss, if the file is more than 24 hours old (or missing), it downloads `corpCode.xml`, adds every company that has a stock code, and rewrites `corp_codes.json`. If the download fails, the mapping already loaded is still used. If the file was saved within 24 hours, a miss does not trigger another download.

```json
{
  "timestamp": "2025-01-01T00:00:00+00:00",
  "codes": {
    "005930": "00126380"
  }
}
```

- `corp_codes.json` is committed as a snapshot of every listed company. A download rewrites it, so it shows up as a git change.
- To pick up newly listed stocks right away, re-download the mapping yourself with the command below.

```bash
cd backend
uv run python -c "from src.integrations.opendart import opendart_client as c; print(c.download_corp_code_list())"
```

### Rate limits

- OpenDART limits daily requests per API key (typically about 20,000) and returns `status` `020` when exceeded. Follow OpenDART's notice for the exact limit.
- One financial statement lookup sends two major-account requests.
- The client itself does not pause between requests. Use the script below for many stocks.

### Bulk download script

[`backend/scripts/fetch_opendart_all_stocks.py`](../backend/scripts/fetch_opendart_all_stocks.py) downloads financial statements for many stocks and writes CSV files.

```bash
cd backend
uv run python scripts/fetch_opendart_all_stocks.py --years 2024
uv run python scripts/fetch_opendart_all_stocks.py --years 2025 --periods 2025Q1 2025Q2 --symbols 005930 000660
```

| Option | Description |
|--------|-------------|
| `--years` | Required. Years to fetch |
| `--periods` | E.g. `2025Q2 2025Y`. Defaults to Q1–Q4 plus annual (`Y`) |
| `--symbols` | Fetch only these stocks. Defaults to every stock in the corp code mapping |
| `--limit` | Only the first N stocks by stock code |
| `--sleep` | Pause between quarterly requests in seconds, default 0.3 |
| `--retries`, `--retry-sleep` | Retries on failure (default 2) and the wait between them (default 30 s) |
| `--output-root` | Output folder, default `database/raw_data` at the repository root |

- Output: `<output-root>/<year>/<period>/{balance_sheet,income_statement,cashflow_statement}.csv`, each with a matching `.schema.json`. The major-account APIs have no cash flow items, so `cashflow_statement.csv` carries no amounts.
- Progress is saved to `<output-root>/progress/opendart_<year>.json`; a rerun skips finished stocks. If a request still fails after the retries, the script saves progress and stops.
- It fetches both consolidated and separate statements, so each stock and year costs up to 16 requests. A run over all stocks can exceed the daily limit; spread it over several days.
- Quarterly values: the script treats half-year and annual income and cash-flow amounts as cumulative and Q3 amounts as three-month figures, and derives Q2 = half-year − Q1 and Q4 = annual − half-year − Q3. Balance sheet values are used as-is.
- `.gitignore` excludes only the CSV files. Do not commit the `.schema.json` or progress files either.

### References

- [OpenDART](https://opendart.fss.or.kr/): API key sign-up and developer guide
- [API.md](API.md): backend REST API
