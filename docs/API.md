# REST API 레퍼런스 · REST API Reference

[한국어](#한국어) · [English](#english)

---

## 한국어

Custom HTS 백엔드(FastAPI)가 제공하는 REST 엔드포인트 전체 목록입니다. 모든 기능은 조회·분석용이며 주문 기능은 없습니다.

### 기본 정보

- **Base URL:** `http://127.0.0.1:8000`
- **인터랙티브 문서:** Swagger UI <http://127.0.0.1:8000/docs>, ReDoc <http://127.0.0.1:8000/redoc>. 모든 파라미터와 응답 스키마를 확인하고 바로 호출해 볼 수 있습니다.
- **형식:** 응답은 JSON이며, 오류 응답은 `{"detail": "..."}` 형태입니다.
- **데이터 출처:** 국내 시세·계좌는 한국투자증권 Open API(KIS), 국내 재무제표·공시는 OpenDART, 미국 시장은 yfinance를 사용합니다. 각 서비스의 호출 한도가 그대로 적용됩니다.
- **CORS 허용 Origin:** `http://localhost:5173`, `http://localhost:3000`, `http://127.0.0.1:5173`, `http://127.0.0.1:3000`
- **POST 엔드포인트:** 마스터 파일 새로고침(로컬 파일 쓰기)과 재무제표 저장(Supabase 쓰기) 두 종류뿐입니다.

> [!WARNING]
> **이 API에는 인증이 없습니다.** `GET /api/korean/account`는 `.env`에 설정한 실제 계좌의 잔고와 보유 종목을 그대로 반환합니다. 백엔드는 반드시 `127.0.0.1`에만 바인딩해 실행하고, `--host 0.0.0.0` 실행, 포트 포워딩, 터널, 리버스 프록시 등으로 네트워크에 노출하지 마십시오. CORS 설정은 브라우저 요청만 제한할 뿐 접근 제어 수단이 아닙니다.

### HTTP 상태 코드

| 코드 | 의미 |
|---|---|
| `200` | 성공 |
| `400` | 허용되지 않는 파라미터 값 (예: `market_div_code`, 날짜 형식, `output_format`) |
| `404` | 데이터가 없거나 외부 API 조회에 실패함 |
| `422` | FastAPI 파라미터 검증 실패 (범위 초과, 필수값 누락 등) |
| `500` | 서버 설정 오류 또는 처리 중 예외 (예: 계좌번호 미설정) |
| `503` | Supabase가 설정되지 않음 (`/api/financials/*` 조회 엔드포인트) |

### 엔드포인트

#### 상태 확인

| Method | Path | 반환 |
|---|---|---|
| GET | `/` | 서비스 이름, 버전, 문서 경로 |
| GET | `/health` | `{"status": "healthy", "version": ...}` |
| GET | `/api/korean/health` | `{"status": "healthy", "market": "Korean"}` |
| GET | `/api/us/health` | `{"status": "healthy", "market": "US"}` |

#### 국내 주식

`symbol`은 6자리 종목코드입니다 (예: `005930`).

| Method | Path | 주요 파라미터 | 반환 |
|---|---|---|---|
| GET | `/api/korean/quote/{symbol}` | — | 현재가 시세 |
| GET | `/api/korean/candle/{symbol}` | `period`=`D`/`W`/`M` (기본 `D`), `adjust_price` (기본 `true`), `limit` 1–500, `start_date`·`end_date` (YYYYMMDD) | 일·주·월 캔들(OHLCV) 목록 |
| GET | `/api/korean/candle-minute/{symbol}` | `interval`=1/5/10/30/60 (기본 1), `limit` 1–500, `date` (YYYYMMDD, 기본 오늘 KST), `time_str` (HHMMSS) | 분봉 캔들 목록 |
| GET | `/api/korean/valuation/{symbol}` | `year` (기본 전년도), `quarter` 1–4, `fs_div`=`CFS`/`OFS` | PER·PBR·EPS·BPS 등 밸류에이션 지표 (KIS 가격 + OpenDART 재무) |
| GET | `/api/korean/estimate-perform/{symbol}` | — | 추정실적 (KIS) |
| GET | `/api/korean/stock-info/{pdno}` | `prdt_type_cd` (기본 `300` 주식·ETF·ETN·ELW, `301` 선물옵션, `302` 채권, `306` ELS) | 상품 기본정보 (KIS 원본 output 목록). ETN은 `Q`로 시작하는 코드 사용 |
| GET | `/api/korean/stocks/master` | `query` (종목코드 또는 종목명 일부), `market`=`all`/`kospi`/`kosdaq`/`konex`, `offset`, `limit` 1–500, `auto_download` (기본 `true`), `force_download` | 종목 마스터 검색 결과 (종목 자동완성용) |

#### 국내 장내채권

`pdno`는 채권 표준코드입니다.

| Method | Path | 주요 파라미터 | 반환 |
|---|---|---|---|
| GET | `/api/korean/bonds/master` | `query`, `type` (`A0`/`F9`/`C0`), `bond_class_code`, `bond_interest_class_code`, `listed_date_from`·`listed_date_to`, `issue_date_from`·`issue_date_to`, `maturity_date_from`·`maturity_date_to` (YYYYMMDD), `offset`, `limit` 1–500, `enrich`, `include_quotes` | 채권 마스터 목록. 로컬 마스터 파일(`backend/data/kr_bond_master/`)을 읽으며 자동으로 내려받지 않습니다 |
| POST | `/api/korean/bonds/master/refresh` | `output_format`=`csv`/`json`, `force`, `source_url` | 채권 마스터 파일을 내려받아 CSV/JSON으로 변환한 결과 |
| GET | `/api/korean/bonds/{pdno}/price` | — | 현재 시세 |
| GET | `/api/korean/bonds/{pdno}/valuation` | — | 이론가(dirty/clean), 경과이자, 시장가 대비 괴리 |
| GET | `/api/korean/bonds/{pdno}/daily-price` | `limit` 1–100 | 일별 시세 (캔들 형식) |
| GET | `/api/korean/bonds/{pdno}/info` | — | 채권 기본정보 (KIS 원본) |
| GET | `/api/korean/bonds/{pdno}/issue` | — | 발행정보 (KIS 원본) |
| GET | `/api/korean/bonds/{pdno}/analytics` | — | 체결가·매수·매도 호가 수익률, 듀레이션·컨벡시티, 금리 시나리오, 민평(채권평가사) 대비 스프레드 |
| GET | `/api/korean/bonds/{pdno}/yield-history` | `days` 10–365 (기본 120) | 일별 시장 수익률과 채권평가사 평균 수익률 비교 |

#### 국내 선물옵션

시세·호가·캔들 엔드포인트는 `symbol`(필수, 선물옵션 단축코드 3–12자)과 `market_div_code`(기본 `F`)를 공통으로 받습니다. `market_div_code` 값은 `F` 지수선물, `O` 지수옵션, `JF` 주식선물, `JO` 주식옵션, `CF` 상품·금리·통화선물, `CM` 야간선물, `EU` 야간옵션입니다.

| Method | Path | 주요 파라미터 | 반환 |
|---|---|---|---|
| GET | `/api/korean/futures-options/master` | `market`=`all`/`index`/`stock`/`commodity`, `query`, `info_type`, `underlying_short_code`, `offset`, `limit` 1–2000 (기본 100), `auto_download` (기본 `false`), `force_download` | 선물옵션 종목 마스터 |
| POST | `/api/korean/futures-options/master/refresh` | `market`, `output_format`=`csv`/`json`, `force` | 마스터 파일을 내려받아 변환한 결과 |
| GET | `/api/korean/futures-options/quote` | `symbol`, `market_div_code` | 현재가 시세 (기초자산 지수 정보 포함) |
| GET | `/api/korean/futures-options/orderbook` | `symbol`, `market_div_code` | 5단계 호가 |
| GET | `/api/korean/futures-options/daily-candles` | `symbol`, `market_div_code`, `period`=`D`/`W`/`M`/`Y`, `limit` 1–500, `start_date`·`end_date` (YYYYMMDD) | 일·주·월·년 캔들 |
| GET | `/api/korean/futures-options/minute-candles` | `symbol`, `market_div_code`, `timeframe_sec`=30/60/3600, `date` (YYYYMMDD), `time` (HHMMSS), `include_previous` (기본 `true`), `include_fake_tick`, `limit` 1–200 | 30초·1분·1시간 캔들 |
| GET | `/api/korean/futures-options/option-chain` | `expiry` (YYYYMM, 필수), `market_class`=`""` (KOSPI200), `MKI` (미니), `KQI` (코스닥150), `WKM`/`WKI` (위클리) | 행사가별 콜·풋 옵션 체인 |

#### 베이시스·풋콜 패리티

`underlying`에는 종목코드(`005930`), 지수코드(`2001`) 또는 선물 단축코드를 넣을 수 있습니다.

| Method | Path | 주요 파라미터 | 반환 |
|---|---|---|---|
| GET | `/api/korean/basis/underlyings` | `query` | 상장 선물이 있는 주식·지수 목록 |
| GET | `/api/korean/basis/{underlying}` | `rate` (연 %, -5–30; 생략 시 증권사 이론가 사용), `dividend` (만기 전 예상 배당, 가격 단위), `months` 1–8 (기본 4) | 월물별 베이시스, 내재금리, 이론가 대비 괴리 |
| GET | `/api/korean/basis/{underlying}/history` | `symbol` (선물 단축코드, 기본 최근월물), `days` 5–365 (기본 90) | 일별 베이시스 시계열과 통계 (평균, 표준편차, z-score, 백분위) |
| GET | `/api/korean/basis/{underlying}/options` | `expiry` (YYYYMM, 생략 시 최근월), `rate`, `strikes` 3–15 (기본 9) | 풋콜 패리티로 구한 합성선물과 선물·현물 비교, 컨버전·리버설 엣지. 월물 옵션이 없으면 `expiries`가 빈 목록 |

#### 국내 재무제표·기업정보·공시 (OpenDART)

| Method | Path | 주요 파라미터 | 반환 |
|---|---|---|---|
| GET | `/api/korean/financials/{symbol}` | `year` (기본 올해), `quarter` 1–4, `use_cache` (호환용으로 남아 있으며 무시됨) | 주요 재무 요약 |
| GET | `/api/korean/financials/{symbol}/balance-sheet` | `year` (기본 전년도), `quarter` 1–4 (생략 시 연간) | 재무상태표 계정별 금액 |
| GET | `/api/korean/financials/{symbol}/income-statement` | `year`, `quarter` | 손익계산서 계정별 금액 |
| GET | `/api/korean/financials/{symbol}/cash-flow` | `year`, `quarter` | 현금흐름표 계정별 금액 |
| GET | `/api/korean/financials/{symbol}/all` | `year`, `quarter`, `fs_div`=`CFS` (연결)/`OFS` (별도) | 전체 재무제표 계정 목록 (`count`, `data`) |
| GET | `/api/korean/company/{symbol}` | — | 기업개황 (회사명, 대표자, 주소, 업종, 홈페이지, 설립일 등) |
| GET | `/api/korean/disclosures` | `corp` (종목코드 또는 회사명), `start`·`end` (YYYY-MM-DD 또는 YYYYMMDD), `kind` (공시유형 `A`–`J`), `final` (기본 `true`), `limit` 1–1000 (기본 100) | 공시 목록 |

#### 계좌

| Method | Path | 주요 파라미터 | 반환 |
|---|---|---|---|
| GET | `/api/korean/account` | `account_product_code` (기본 `01`) | 계좌 잔고(`balance`)와 보유 종목(`positions`). 계좌번호는 `HANTU_ACCOUNT_NUMBER`(또는 `HANTU_BANK_ACCOUNT`)의 8자리 값을 사용하며, 형식이 맞지 않으면 `500`을 반환합니다 |

#### 미국 주식 (yfinance)

`symbol`은 티커입니다 (예: `AAPL`). 대소문자를 구분하지 않습니다.

| Method | Path | 주요 파라미터 | 반환 |
|---|---|---|---|
| GET | `/api/us/quote/{symbol}` | — | 시세 |
| GET | `/api/us/valuation/{symbol}` | — | PER·PBR·EPS·BPS 등 밸류에이션 지표 |
| GET | `/api/us/financials/{symbol}` | `use_cache` (무시됨) | 재무제표 목록 |
| GET | `/api/us/candle/{symbol}` | `period`=`1d`/`5d`/`1mo`/`3mo`/`6mo`/`1y`/`2y`/`5y`/`10y`/`ytd`/`max` (기본 `1mo`), `interval`=`1m`/`5m`/`15m`/`30m`/`60m`/`1d`/`1wk`/`1mo` (기본 `1d`), `start`·`end` (YYYY-MM-DD) | 캔들(OHLCV) 목록 |

재무제표는 항상 yfinance에서 조회합니다. `use_cache`는 호환성 때문에 남아 있을 뿐 무시됩니다.

#### 저장된 재무제표 (Supabase, 선택 사항)

OpenDART(국내)·yfinance(미국)에서 재무제표를 가져와 Supabase 테이블에 저장하고 다시 조회합니다. Supabase 설정 방법은 [SUPABASE_INTEGRATION.md](SUPABASE_INTEGRATION.md), 테이블 구조는 [database/schema.md](../database/schema.md)를 참고하십시오.

| Method | Path | 주요 파라미터 | 반환 |
|---|---|---|---|
| POST | `/api/financials/korean/statements/insert` | 본문 `{"symbol", "year", "quarter"?}` | `korean_*` 3개 테이블 저장 결과 (`success`, `message`, `inserted`) |
| POST | `/api/financials/korean/statements/batch-insert` | 본문 `{"symbols": [...], "year", "quarters"?: [...]}` (`quarters` 생략 시 연간만) | 종목·기간별 저장 결과 |
| GET | `/api/financials/korean/balance-sheet/{symbol}` | `year`, `quarter` (선택 필터) | 저장된 행 (`success`, `data`, `count`) |
| GET | `/api/financials/korean/income-statement/{symbol}` | `year`, `quarter` | 저장된 행 |
| GET | `/api/financials/korean/cashflow/{symbol}` | `year`, `quarter` | 저장된 행 |
| POST | `/api/financials/us/statements/insert` | 본문 `{"symbol", "year", "quarter"?}` | `us_*` 3개 테이블 저장 결과 |
| POST | `/api/financials/us/statements/batch-insert` | 본문 `{"symbols": [...], "year", "quarters"?: [...]}` | 종목·기간별 저장 결과 |
| GET | `/api/financials/us/balance-sheet/{symbol}` | `year`, `quarter` | 저장된 행 |
| GET | `/api/financials/us/income-statement/{symbol}` | `year`, `quarter` | 저장된 행 |
| GET | `/api/financials/us/cashflow/{symbol}` | `year`, `quarter` | 저장된 행 |

### 호출 예시

```bash
# 삼성전자 현재가
curl http://127.0.0.1:8000/api/korean/quote/005930

# 종목명으로 종목코드 검색 (한글은 URL 인코딩)
curl -G http://127.0.0.1:8000/api/korean/stocks/master \
  --data-urlencode "query=삼성" -d limit=5

# KOSPI200 지수(2001)의 월물별 베이시스, 연 3.5% 금리 가정
curl "http://127.0.0.1:8000/api/korean/basis/2001?rate=3.5&months=2"

# 삼성전자 2024년 연간 재무제표를 Supabase에 저장
curl -X POST http://127.0.0.1:8000/api/financials/korean/statements/insert \
  -H "Content-Type: application/json" \
  -d '{"symbol": "005930", "year": 2024}'
```

### 관련 문서

- 설치와 환경 변수: [SETUP.md](SETUP.md)
- Supabase 설정: [SUPABASE_INTEGRATION.md](SUPABASE_INTEGRATION.md)
- KIS Open API 원문 명세: <https://apiportal.koreainvestment.com/>
- OpenDART 원문 명세: <https://opendart.fss.or.kr/>

---

## English

The complete list of REST endpoints served by the Custom HTS backend (FastAPI). Everything is read-only market data and analytics; there is no order placement.

### Basics

- **Base URL:** `http://127.0.0.1:8000`
- **Interactive docs:** Swagger UI at <http://127.0.0.1:8000/docs>, ReDoc at <http://127.0.0.1:8000/redoc>. Every parameter and response schema is listed there and can be tried in the browser.
- **Format:** responses are JSON; errors look like `{"detail": "..."}`.
- **Data sources:** Korea Investment & Securities Open API (KIS) for Korean quotes and the account, OpenDART for Korean financial statements and disclosures, and yfinance for US markets. Each provider's rate limits apply.
- **Allowed CORS origins:** `http://localhost:5173`, `http://localhost:3000`, `http://127.0.0.1:5173`, `http://127.0.0.1:3000`
- **POST endpoints:** only two kinds — master-file refreshes (write local files) and financial-statement storage (write to Supabase).

> [!WARNING]
> **The API has no authentication.** `GET /api/korean/account` returns the balance and holdings of the real account configured in `.env`. Always bind the backend to `127.0.0.1` and never expose it on a network: no `--host 0.0.0.0`, port forwarding, tunnels or reverse proxies. CORS only restricts browsers; it is not access control.

### HTTP status codes

| Code | Meaning |
|---|---|
| `200` | Success |
| `400` | Parameter value not allowed (e.g. `market_div_code`, date format, `output_format`) |
| `404` | No data, or the upstream API call failed |
| `422` | FastAPI validation failed (out of range, missing required parameter, …) |
| `500` | Server misconfiguration or an exception while processing (e.g. account number not set) |
| `503` | Supabase not configured (`/api/financials/*` read endpoints) |

### Endpoints

#### Health

| Method | Path | Returns |
|---|---|---|
| GET | `/` | Service name, version, docs path |
| GET | `/health` | `{"status": "healthy", "version": ...}` |
| GET | `/api/korean/health` | `{"status": "healthy", "market": "Korean"}` |
| GET | `/api/us/health` | `{"status": "healthy", "market": "US"}` |

#### Korean stocks

`symbol` is a 6-digit stock code (e.g. `005930`).

| Method | Path | Key parameters | Returns |
|---|---|---|---|
| GET | `/api/korean/quote/{symbol}` | — | Current quote |
| GET | `/api/korean/candle/{symbol}` | `period`=`D`/`W`/`M` (default `D`), `adjust_price` (default `true`), `limit` 1–500, `start_date`·`end_date` (YYYYMMDD) | Daily/weekly/monthly candles (OHLCV) |
| GET | `/api/korean/candle-minute/{symbol}` | `interval`=1/5/10/30/60 (default 1), `limit` 1–500, `date` (YYYYMMDD, default today in KST), `time_str` (HHMMSS) | Minute candles |
| GET | `/api/korean/valuation/{symbol}` | `year` (default last year), `quarter` 1–4, `fs_div`=`CFS`/`OFS` | Valuation metrics such as PER, PBR, EPS, BPS (KIS price + OpenDART financials) |
| GET | `/api/korean/estimate-perform/{symbol}` | — | Earnings estimates (KIS) |
| GET | `/api/korean/stock-info/{pdno}` | `prdt_type_cd` (default `300` stock/ETF/ETN/ELW, `301` futures/options, `302` bonds, `306` ELS) | Product basic info (raw KIS output list). ETN codes start with `Q` |
| GET | `/api/korean/stocks/master` | `query` (stock code or part of the name), `market`=`all`/`kospi`/`kosdaq`/`konex`, `offset`, `limit` 1–500, `auto_download` (default `true`), `force_download` | Stock master search results (for symbol typeahead) |

#### Korean listed bonds

`pdno` is the bond's standard code.

| Method | Path | Key parameters | Returns |
|---|---|---|---|
| GET | `/api/korean/bonds/master` | `query`, `type` (`A0`/`F9`/`C0`), `bond_class_code`, `bond_interest_class_code`, `listed_date_from`·`listed_date_to`, `issue_date_from`·`issue_date_to`, `maturity_date_from`·`maturity_date_to` (YYYYMMDD), `offset`, `limit` 1–500, `enrich`, `include_quotes` | Bond master list. Reads the local master file (`backend/data/kr_bond_master/`) and does not download it automatically |
| POST | `/api/korean/bonds/master/refresh` | `output_format`=`csv`/`json`, `force`, `source_url` | Result of downloading the bond master file and exporting it to CSV/JSON |
| GET | `/api/korean/bonds/{pdno}/price` | — | Current quote |
| GET | `/api/korean/bonds/{pdno}/valuation` | — | Theoretical price (dirty/clean), accrued interest, gap to market price |
| GET | `/api/korean/bonds/{pdno}/daily-price` | `limit` 1–100 | Daily prices (candle format) |
| GET | `/api/korean/bonds/{pdno}/info` | — | Bond basic info (raw KIS) |
| GET | `/api/korean/bonds/{pdno}/issue` | — | Issue info (raw KIS) |
| GET | `/api/korean/bonds/{pdno}/analytics` | — | Yields at last/bid/ask, duration and convexity, rate scenarios, spread to pricing-agency yield |
| GET | `/api/korean/bonds/{pdno}/yield-history` | `days` 10–365 (default 120) | Daily market yield against the pricing agencies' average yield |

#### Korean futures and options

The quote, order book and candle endpoints share `symbol` (required, futures/options short code, 3–12 chars) and `market_div_code` (default `F`). `market_div_code` values: `F` index futures, `O` index options, `JF` stock futures, `JO` stock options, `CF` commodity/rate/currency futures, `CM` night futures, `EU` night options.

| Method | Path | Key parameters | Returns |
|---|---|---|---|
| GET | `/api/korean/futures-options/master` | `market`=`all`/`index`/`stock`/`commodity`, `query`, `info_type`, `underlying_short_code`, `offset`, `limit` 1–2000 (default 100), `auto_download` (default `false`), `force_download` | Futures/options master rows |
| POST | `/api/korean/futures-options/master/refresh` | `market`, `output_format`=`csv`/`json`, `force` | Result of downloading and exporting the master files |
| GET | `/api/korean/futures-options/quote` | `symbol`, `market_div_code` | Current quote (with underlying index data) |
| GET | `/api/korean/futures-options/orderbook` | `symbol`, `market_div_code` | 5-level order book |
| GET | `/api/korean/futures-options/daily-candles` | `symbol`, `market_div_code`, `period`=`D`/`W`/`M`/`Y`, `limit` 1–500, `start_date`·`end_date` (YYYYMMDD) | Daily/weekly/monthly/yearly candles |
| GET | `/api/korean/futures-options/minute-candles` | `symbol`, `market_div_code`, `timeframe_sec`=30/60/3600, `date` (YYYYMMDD), `time` (HHMMSS), `include_previous` (default `true`), `include_fake_tick`, `limit` 1–200 | 30-second, 1-minute or 1-hour candles |
| GET | `/api/korean/futures-options/option-chain` | `expiry` (YYYYMM, required), `market_class`=`""` (KOSPI200), `MKI` (mini), `KQI` (KOSDAQ150), `WKM`/`WKI` (weekly) | Call/put option chain by strike |

#### Basis and put-call parity

`underlying` accepts a stock code (`005930`), an index code (`2001`) or a futures short code.

| Method | Path | Key parameters | Returns |
|---|---|---|---|
| GET | `/api/korean/basis/underlyings` | `query` | Stocks and indexes that have listed futures |
| GET | `/api/korean/basis/{underlying}` | `rate` (annual %, -5–30; omit to use the broker's theoretical price), `dividend` (expected dividends before expiry, in price units), `months` 1–8 (default 4) | Basis, implied rate and gap to theoretical price for each contract month |
| GET | `/api/korean/basis/{underlying}/history` | `symbol` (futures short code, default front month), `days` 5–365 (default 90) | Daily basis series with statistics (mean, std, z-score, percentile) |
| GET | `/api/korean/basis/{underlying}/options` | `expiry` (YYYYMM, default nearest), `rate`, `strikes` 3–15 (default 9) | Synthetic futures from put-call parity against futures and spot, conversion/reversal edges. `expiries` is empty when the underlying has no monthly options |

#### Korean financial statements, company info and disclosures (OpenDART)

| Method | Path | Key parameters | Returns |
|---|---|---|---|
| GET | `/api/korean/financials/{symbol}` | `year` (default this year), `quarter` 1–4, `use_cache` (kept for compatibility, ignored) | Key financials summary |
| GET | `/api/korean/financials/{symbol}/balance-sheet` | `year` (default last year), `quarter` 1–4 (omit for annual) | Balance sheet line items |
| GET | `/api/korean/financials/{symbol}/income-statement` | `year`, `quarter` | Income statement line items |
| GET | `/api/korean/financials/{symbol}/cash-flow` | `year`, `quarter` | Cash flow statement line items |
| GET | `/api/korean/financials/{symbol}/all` | `year`, `quarter`, `fs_div`=`CFS` (consolidated)/`OFS` (separate) | Every statement line item (`count`, `data`) |
| GET | `/api/korean/company/{symbol}` | — | Company profile (name, CEO, address, industry, website, founding date, …) |
| GET | `/api/korean/disclosures` | `corp` (stock code or company name), `start`·`end` (YYYY-MM-DD or YYYYMMDD), `kind` (disclosure type `A`–`J`), `final` (default `true`), `limit` 1–1000 (default 100) | Disclosure list |

#### Account

| Method | Path | Key parameters | Returns |
|---|---|---|---|
| GET | `/api/korean/account` | `account_product_code` (default `01`) | Account balance (`balance`) and holdings (`positions`). The account number is the 8-digit value of `HANTU_ACCOUNT_NUMBER` (or `HANTU_BANK_ACCOUNT`); returns `500` if it is malformed |

#### US stocks (yfinance)

`symbol` is a ticker (e.g. `AAPL`), case-insensitive.

| Method | Path | Key parameters | Returns |
|---|---|---|---|
| GET | `/api/us/quote/{symbol}` | — | Quote |
| GET | `/api/us/valuation/{symbol}` | — | Valuation metrics such as PER, PBR, EPS, BPS |
| GET | `/api/us/financials/{symbol}` | `use_cache` (ignored) | Financial statements |
| GET | `/api/us/candle/{symbol}` | `period`=`1d`/`5d`/`1mo`/`3mo`/`6mo`/`1y`/`2y`/`5y`/`10y`/`ytd`/`max` (default `1mo`), `interval`=`1m`/`5m`/`15m`/`30m`/`60m`/`1d`/`1wk`/`1mo` (default `1d`), `start`·`end` (YYYY-MM-DD) | Candles (OHLCV) |

Financial statements always come from yfinance. `use_cache` is kept only for compatibility and is ignored.

#### Stored financial statements (Supabase, optional)

Fetch financial statements from OpenDART (Korea) or yfinance (US), store them in Supabase tables and read them back. See [SUPABASE_INTEGRATION.md](SUPABASE_INTEGRATION.md) for setup and [database/schema.md](../database/schema.md) for the tables.

| Method | Path | Key parameters | Returns |
|---|---|---|---|
| POST | `/api/financials/korean/statements/insert` | Body `{"symbol", "year", "quarter"?}` | Result for the three `korean_*` tables (`success`, `message`, `inserted`) |
| POST | `/api/financials/korean/statements/batch-insert` | Body `{"symbols": [...], "year", "quarters"?: [...]}` (annual only when `quarters` is omitted) | Result per symbol and period |
| GET | `/api/financials/korean/balance-sheet/{symbol}` | `year`, `quarter` (optional filters) | Stored rows (`success`, `data`, `count`) |
| GET | `/api/financials/korean/income-statement/{symbol}` | `year`, `quarter` | Stored rows |
| GET | `/api/financials/korean/cashflow/{symbol}` | `year`, `quarter` | Stored rows |
| POST | `/api/financials/us/statements/insert` | Body `{"symbol", "year", "quarter"?}` | Result for the three `us_*` tables |
| POST | `/api/financials/us/statements/batch-insert` | Body `{"symbols": [...], "year", "quarters"?: [...]}` | Result per symbol and period |
| GET | `/api/financials/us/balance-sheet/{symbol}` | `year`, `quarter` | Stored rows |
| GET | `/api/financials/us/income-statement/{symbol}` | `year`, `quarter` | Stored rows |
| GET | `/api/financials/us/cashflow/{symbol}` | `year`, `quarter` | Stored rows |

### Examples

```bash
# Samsung Electronics quote
curl http://127.0.0.1:8000/api/korean/quote/005930

# Look up a stock code by Korean name (URL-encode the query)
curl -G http://127.0.0.1:8000/api/korean/stocks/master \
  --data-urlencode "query=삼성" -d limit=5

# Basis for each KOSPI200 (2001) futures month, assuming a 3.5% annual rate
curl "http://127.0.0.1:8000/api/korean/basis/2001?rate=3.5&months=2"

# Store Samsung Electronics' 2024 annual statements in Supabase
curl -X POST http://127.0.0.1:8000/api/financials/korean/statements/insert \
  -H "Content-Type: application/json" \
  -d '{"symbol": "005930", "year": 2024}'
```

### Related documents

- Installation and environment variables: [SETUP.md](SETUP.md)
- Supabase setup: [SUPABASE_INTEGRATION.md](SUPABASE_INTEGRATION.md)
- KIS Open API specification: <https://apiportal.koreainvestment.com/>
- OpenDART specification: <https://opendart.fss.or.kr/>
