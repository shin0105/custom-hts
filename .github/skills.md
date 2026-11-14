# 에이전트 스킬 레퍼런스 · Agent Skills Reference

이 문서는 AI 코딩 에이전트가 이 저장소에서 자주 하는 작업의 **절차(레시피)**와 **도메인 지식**을 정리한 것입니다. 기본 규칙과 명령은 [CLAUDE.md](../CLAUDE.md)에 있습니다.
This document collects **recipes** for common tasks and the **domain knowledge** an AI coding agent needs in this repository. Ground rules and commands live in [CLAUDE.md](../CLAUDE.md).

[한국어](#한국어) · [English](#english)

---

## 한국어

### 1. 기능 지도 — 어디를 고쳐야 하나

| 영역 | 백엔드 | 프론트엔드 |
|------|--------|------------|
| 국내주식 시세·캔들·예상실적 | `integrations/kdevelopers.py` → `services/korean_market.py` → `api/korean.py` | `pages/KoreanMarketPage.tsx`, `components/CandleChart.tsx`, `hooks/useKoreanMarket.ts` |
| 종목 검색 (마스터 파일) | `integrations/stock_master.py`, `GET /api/korean/stocks/master` | `components/SymbolSearch.tsx` |
| 국내 재무제표·공시 | `integrations/opendart.py` → `api/korean.py` (`/financials/*`, `/company`, `/disclosures`), `src/data/opendart/corp_codes.json` | `pages/KoreanMarketPage.tsx`, `hooks/useKoreanMarket.ts` |
| 장내채권 | `integrations/bond_master.py`, `services/bond_math.py`, `services/bond_analytics.py` | `pages/BondMarketPage.tsx`, `components/BondYieldPanel.tsx`, `services/koreanAnalytics.ts` |
| 선물옵션 | `integrations/futures_options_master.py`, `services/korean_market.py` | `pages/DomesticFuturesOptionsPage.tsx` |
| 베이시스·풋콜 패리티 | `services/basis.py`, `services/option_parity.py` | `pages/BasisPage.tsx`, `components/BasisParts.tsx`, `components/OptionParityPanel.tsx` |
| 해외주식 | `integrations/yfinance_client.py`, `services/us_market.py`, `api/us.py` | `pages/USMarketPage.tsx`, `services/usMarket.ts` |
| 계좌 잔고 | `kdevelopers.get_account_balance`, `GET /api/korean/account` | `pages/AccountCheckPage.tsx` |
| 재무제표 저장 (선택) | `integrations/supabase_client.py`, `services/financial_statements.py`, `api/financial_statements.py`, `database/financial_statements.sql` | — |

경로는 `backend/src/`, `frontend/src/` 기준입니다.

### 2. 레시피

#### 새 KIS API 연동하기
1. [KIS Developers 포털](https://apiportal.koreainvestment.com/)에서 API 경로, `tr_id`, 파라미터를 확인합니다. 로컬에 `docs/kdevelopers_api/` 사본이 있다면 참고해도 되지만 커밋하지 마세요.
2. `integrations/kdevelopers.py`에 메서드를 추가합니다. 기존 메서드(`get_bond_asking_price` 등)처럼 `self._url_fetch(api_url, tr_id, "", params)`를 호출하고, `res.is_ok()`를 확인한 뒤 `_output_to_dict` / `_output_to_list`로 변환합니다. 토큰과 속도 제한은 `_url_fetch`가 처리합니다.
3. `models/korean.py`(또는 `korean_analytics.py`)에 Pydantic 응답 모델을 정의합니다.
4. `services/`에서 원시 필드(`stck_prpr` 등)를 의미 있는 이름과 숫자 타입으로 바꿉니다. 호출 여러 개를 묶으면 `run_blocking`과 `TTLCache`를 씁니다.
5. `api/korean.py`에 라우트를 추가하고, 결과가 없으면 `HTTPException(404)`를 반환합니다.
6. `frontend/src/types/`, `services/koreanMarket.ts`, `hooks/`에 타입·호출·React Query 훅을 추가합니다.
7. 계산 로직이 있으면 `backend/tests/`에 오프라인 단위 테스트를 추가합니다(네트워크 호출 금지).

#### 새 화면 추가하기
1. `frontend/src/pages/`에 페이지를 만들고 `App.tsx`에 `<Route>`를, `components/Navigation.tsx`의 `NAV_GROUPS`에 메뉴를 추가합니다.
2. 문구는 `i18n/ko.ts`에, 레이아웃은 `components/ui/`(Panel, StatTile, DataTable, Field …)로 구성합니다.
3. 숫자 표시는 `utils/format.ts`, 등락 색상은 `useMarketColors()`, 에러 메시지는 `utils/apiError.ts`, 공용 라인·막대 차트는 `components/AnalyticsCharts.tsx`를 씁니다.

#### 테스트 작성
- 순수 계산(채권 가격·수익률, 베이시스, 패리티)은 알려진 값으로 검증하는 오프라인 테스트를 씁니다. 예: `tests/test_bond_math.py`.
- 실제 API를 부르는 테스트는 키가 없으면 건너뛰도록 만들고, 결과 파일은 `tests/test-results/`(gitignore)에만 씁니다.

### 3. 도메인 지식

- **KIS 토큰**: 접근 토큰은 약 24시간 유효하고 발급은 앱키당 1분에 1회입니다. 만료 응답을 받으면 캐시를 지우고 한 번 재발급합니다(`_is_token_expired_response`).
- **KIS 속도 제한**: 클라이언트가 호출마다 간격을 둡니다(`_smart_sleep`, 0.05초). 앱은 실전투자 서버(`HANTU_BASE_URL`)를 씁니다. 병렬 호출로 제한을 우회하지 마세요.
- **종목코드**: 국내 주식은 6자리(`005930`), 채권·선물옵션은 상품번호(`pdno`)를 씁니다. OpenDART는 종목코드가 아닌 8자리 고유번호(`corp_code`)를 쓰므로 `corp_codes.json`으로 변환합니다.
- **등락 색상**: 한국 관행은 상승=빨강, 하락=파랑이며 기본값입니다.
- **채권 관행**: 한국 시장 관행을 따릅니다. 가격은 액면 10,000원당 경과이자를 포함한 가격(dirty price)이고, 이표채는 이표 주기 복리 + 첫 구간 단리로 할인합니다. 수정 전에 `services/bond_math.py`의 docstring과 `tests/test_bond_math.py`를 먼저 읽으세요.
- **베이시스**: 선물가격 − 현물가격. 풋콜 패리티로 옵션 시장이 암시하는 선물 이론가를 계산해 비교합니다.

### 4. 용어 대조표

| 한국어 | English | 한국어 | English |
|--------|---------|--------|---------|
| 시세 / 현재가 | quote / last price | 호가 | order book (bid/ask) |
| 일봉 / 분봉 | daily / minute candles | 재무제표 | financial statements |
| 재무상태표 | balance sheet | 손익계산서 | income statement |
| 현금흐름표 | cash-flow statement | 공시 | disclosure / filing |
| 예상실적 | earnings estimates | 장내채권 | exchange-listed bonds |
| 만기수익률 | yield to maturity | 듀레이션 / 볼록성 | duration / convexity |
| 선물옵션 | futures & options | 기초자산 | underlying |
| 베이시스 | basis | 풋콜 패리티 | put-call parity |
| 실전투자 / 모의투자 | live / paper trading | 계좌 잔고 | account balance |

---

## English

### 1. Feature map — where to make a change

| Area | Backend | Frontend |
|------|---------|----------|
| KR stock quotes, candles, estimates | `integrations/kdevelopers.py` → `services/korean_market.py` → `api/korean.py` | `pages/KoreanMarketPage.tsx`, `components/CandleChart.tsx`, `hooks/useKoreanMarket.ts` |
| Symbol search (master files) | `integrations/stock_master.py`, `GET /api/korean/stocks/master` | `components/SymbolSearch.tsx` |
| KR financial statements, filings | `integrations/opendart.py` → `api/korean.py` (`/financials/*`, `/company`, `/disclosures`), `src/data/opendart/corp_codes.json` | `pages/KoreanMarketPage.tsx`, `hooks/useKoreanMarket.ts` |
| Exchange-listed bonds | `integrations/bond_master.py`, `services/bond_math.py`, `services/bond_analytics.py` | `pages/BondMarketPage.tsx`, `components/BondYieldPanel.tsx`, `services/koreanAnalytics.ts` |
| Futures & options | `integrations/futures_options_master.py`, `services/korean_market.py` | `pages/DomesticFuturesOptionsPage.tsx` |
| Basis, put-call parity | `services/basis.py`, `services/option_parity.py` | `pages/BasisPage.tsx`, `components/BasisParts.tsx`, `components/OptionParityPanel.tsx` |
| US stocks | `integrations/yfinance_client.py`, `services/us_market.py`, `api/us.py` | `pages/USMarketPage.tsx`, `services/usMarket.ts` |
| Account balance | `kdevelopers.get_account_balance`, `GET /api/korean/account` | `pages/AccountCheckPage.tsx` |
| Financial-statement storage (optional) | `integrations/supabase_client.py`, `services/financial_statements.py`, `api/financial_statements.py`, `database/financial_statements.sql` | — |

Paths are relative to `backend/src/` and `frontend/src/`.

### 2. Recipes

#### Integrating a new KIS API
1. Look up the API path, `tr_id` and parameters on the [KIS Developers portal](https://apiportal.koreainvestment.com/). If a local copy exists in `docs/kdevelopers_api/`, you may read it, but never commit it.
2. Add a method to `integrations/kdevelopers.py`. Like the existing methods (e.g. `get_bond_asking_price`), call `self._url_fetch(api_url, tr_id, "", params)`, check `res.is_ok()`, then convert with `_output_to_dict` / `_output_to_list`. `_url_fetch` handles tokens and rate limiting.
3. Define a Pydantic response model in `models/korean.py` (or `korean_analytics.py`).
4. In `services/`, map raw fields (such as `stck_prpr`) to meaningful names and numeric types. When fanning out several calls, use `run_blocking` and `TTLCache`.
5. Add the route in `api/korean.py`; return `HTTPException(404)` when there is no result.
6. Add the type, call and React Query hook in `frontend/src/types/`, `services/koreanMarket.ts` and `hooks/`.
7. If there is calculation logic, add an offline unit test in `backend/tests/` (no network calls).

#### Adding a new page
1. Create the page in `frontend/src/pages/`, add a `<Route>` in `App.tsx` and a menu entry to `NAV_GROUPS` in `components/Navigation.tsx`.
2. Put copy in `i18n/ko.ts` and build the layout from `components/ui/` (Panel, StatTile, DataTable, Field, …).
3. Use `utils/format.ts` for numbers, `useMarketColors()` for up/down colours, `utils/apiError.ts` for error messages and `components/AnalyticsCharts.tsx` for shared line/bar charts.

#### Writing tests
- Test pure calculations (bond price/yield, basis, parity) offline against known values, e.g. `tests/test_bond_math.py`.
- Tests that call real APIs must skip when keys are missing and write output only to `tests/test-results/` (gitignored).

### 3. Domain knowledge

- **KIS tokens**: an access token lasts about 24 hours, and issuance is limited to once per minute per app key. On an expired-token response the client purges the cache and reissues once (`_is_token_expired_response`).
- **KIS rate limits**: the client spaces out every call (`_smart_sleep`, 0.05 s). The app uses the live-trading server (`HANTU_BASE_URL`). Do not work around the limit with parallel calls.
- **Codes**: Korean stocks use 6-digit codes (`005930`); bonds and futures/options use a product number (`pdno`). OpenDART uses an 8-digit `corp_code` rather than the stock code, mapped through `corp_codes.json`.
- **Up/down colours**: the Korean convention, up = red and down = blue, is the default.
- **Bond conventions**: Korean market convention. Prices are per 10,000 KRW face and include accrued interest (dirty prices); coupon bonds discount whole coupon periods with compounding and the first partial period with simple interest. Read the docstring of `services/bond_math.py` and `tests/test_bond_math.py` before changing anything.
- **Basis**: futures price − spot price. Put-call parity gives the futures fair value implied by the option market, for comparison.

### 4. Glossary

See the Korean–English glossary table in the Korean section above (§4); it is shared by both languages.
