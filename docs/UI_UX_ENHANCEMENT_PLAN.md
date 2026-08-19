# UI/UX Enhancement Plan — 국내 주식 / 채권 / 파생

Date: 2026-08-18
Scope: `frontend/src` — with emphasis on the three Korean-market surfaces
(`KoreanMarketPage`, `BondMarketPage`, `DomesticFuturesOptionsPage`).

This is an audit and a prioritized backlog, not a set of applied changes. Every item
names the file it lives in so it can be picked up independently.

---

## 구현 현황

**1차 (기반) — 구현 완료.** C-01, C-02, C-04, C-05, C-06, X-01, X-02, X-03 이 반영되었고,
`frontend/src` 아래에 `theme/`(토큰·색상 관행 컨텍스트), `i18n/ko.ts`(한국어 라벨),
`components/ui/`(프리미티브), `utils/marketColors.ts`, `utils/apiError.ts` 가 추가되었다.
`npm run lint` 는 이번 작업에서 21건 → 0건으로 정리되어 이제 게이트로 쓸 수 있다.

나머지 항목은 아래 순서 그대로 남아 있다.

---

## 0. The one-line summary

The backend is well ahead of the frontend. Three of the richest Korean endpoints —
선물옵션 시세(그릭스/IV/미결제), 5단계 호가, 옵션 체인 — are fully implemented in
`services/koreanMarket.ts` and **called by nothing**. Meanwhile the UI that does exist
renders American color semantics, English labels over Korean data, and raw API field
dumps. The highest-value work is not new plumbing; it is surfacing what is already there
in a form a Korean trader recognizes.

---

## 1. Cross-cutting (affects all three KR pages)

### C-01 · P0 · 등락 색상이 한국 관행과 반대
`utils/format.ts:51` `getChangeColor()` returns green for up and red for down.
`components/CandleChart.tsx:298` paints candles `#16a34a` up / `#dc2626` down, and
volume bars `#10b981` / `#ef4444` at line 428.

In every Korean HTS (영웅문, eFriend, M-STOCK, MTS 전반) **빨강 = 상승, 파랑 = 하락**.
A Korean user reading this screen will misread direction at a glance — this is the most
serious usability defect in the project, and it is a ~30-line fix.

**Do:** introduce a market-convention module.

```ts
// utils/marketColors.ts
export type ColorConvention = 'kr' | 'global';
export const changeColor = (v: number, c: ColorConvention) => { ... }
```

Cover 상한가/하한가 as distinct emphasis states (상한가 is conventionally a stronger red
with an arrow glyph ▲, 하한가 a stronger blue ▼, 보합 neutral gray with ―). Default to
`'kr'` on the Korean pages and `'global'` on `USMarketPage`; expose a user toggle in the
nav that persists to `localStorage`. Never hard-code a change color in a component again.

### C-02 · P0 · 언어가 페이지마다 다름
Nav (`components/Navigation.tsx`) is English. `KoreanMarketPage` is English chrome over
Korean data — DART returns `매출액`, `영업이익` into a table headed "Account / Value".
`BondMarketPage` and `DomesticFuturesOptionsPage` are fully Korean. `CandleChart`
tooltips say Open/High/Low/Close/Volume and the legend says Up/Down, on Korean charts,
with `Intl.DateTimeFormat('en-US')` axis labels (`CandleChart.tsx:83`).

**Do:** Korean-first for all `/korean`, `/bonds`, `/futures-options` surfaces. A flat
`i18n/ko.ts` label dictionary is enough — no i18n framework needed at this size. Chart
tooltips become 시가/고가/저가/종가/거래량, legend 상승/하락, axis `Intl` locale `ko-KR`.

### C-03 · P0 · 종목 검색이 코드 정타 입력만 지원
- 주식: you must type `005930`. No name search, no autocomplete.
- 채권: the master table lists PDNO but rows are not clickable — you copy the code by
  hand into the search box at the top of the same page.
- 파생: you must type a 12-character 표준코드 (`KR4201…`). Nobody types those.

`integrations/stock_master.py` already parses KOSPI/KOSDAQ/KONEX masters *with names*,
but unlike bonds and futures there is **no `/api/korean/stocks/master` route** exposing it.

**Do:**
1. Add the stock master search route (mirror `/bonds/master`).
2. Build one `<InstrumentSearch>` combobox used by all three pages, searching across
   stocks + bonds + 선물옵션 in one list, grouped by asset class.
3. Support 초성 검색 (`ㅅㅅㅈㅈ` → 삼성전자) — standard in Korean apps, ~20 lines of
   Hangul jamo decomposition.
4. Make every master-table row clickable → loads detail. This alone removes the most
   painful interaction in the product.
5. Global `Ctrl/⌘+K` command palette over the same index, plus 최근 조회 종목.

### C-04 · P1 · 디자인 시스템 부재
Every style is an inline `React.CSSProperties` object, re-declared per page. Four
different primary button colors are in use — `#3b82f6` (주식), `#0f766e` (채권),
`#1d4ed8` (파생), plus `AccountCheckPage`'s slate/shadow dialect with `borderRadius: 16px`
while everything else uses 6–8px. Inline styles also can't express `:hover` or media
queries, which is why `HomePage` resorts to `onMouseOver` handlers mutating
`e.currentTarget.style`.

**Do:** a token file (`theme.ts`: color, space, radius, type scale, elevation) plus a
small primitive set — `Panel`, `SectionHeader`, `DataTable`, `Field`, `Button`, `Tabs`,
`StatTile`, `Badge`, `Skeleton`. Conservatively this deletes 30–40% of the page code and
makes the three KR pages read as one product. Add a dark theme at the same time: HTS
users sit in front of these screens for hours and dark is the expected default.

### C-05 · P1 · 숫자 조판이 금융 UI 기준에 못 미침
Prices and quantities are set in the proportional body font almost everywhere (only a few
tables opt into `monospace`), so digits don't align down a column.
`utils/format.ts:35` `formatLargeNumber()` abbreviates to K/M/B — meaningless in a Korean
context, where amounts are read in 만 / 억 / 조.

**Do:** `font-variant-numeric: tabular-nums` on every numeric cell and right-align them.
Add `formatKrwCompact()` producing `348조 2,000억`, and use 억원 as the default unit for
재무제표 figures with the unit stated once in the panel header instead of repeated per row.

### C-06 · P1 · 로딩/에러 상태가 빈약
A search on `KoreanMarketPage` awaits five calls **sequentially** (`handleSearch`,
lines 79–126: quote → valuation → candles → financials → estimate) and the page shows
nothing until the chain finishes. `BondMarketPage` already does the right thing with
`Promise.allSettled` (line 277) — the pattern exists, it just isn't applied.
Errors surface as raw strings (`조회 실패: ${err.message}`) or a generic English sentence.

**Do:** render the quote card as soon as it resolves and stream the other panels in
independently, each with its own skeleton and its own inline error + 다시 시도 button.
Map API error codes to plain Korean ("시세 제공 대상 종목이 아닙니다", not an axios message).

### C-07 · P2 · 시장 컨텍스트가 어디에도 없음
No KST clock, no 장 상태 (장전 동시호가 / 장중 / 장마감 / 시간외), no index strip.
Every Korean HTS shows KOSPI · KOSDAQ · KOSPI200 · USD/KRW · 국고채 3년 permanently.

**Do:** a persistent header ticker strip + a market-status pill in the nav. Restructure
the nav from a flat six-link row into grouped sections (국내 · 해외 · 계좌) — it already
doesn't fit its own line comfortably and there are more pages coming.

### C-08 · P2 · 반응형·접근성 없음
No media query in the codebase. Page widths disagree (900px 채권 / 1200px 파생 /
1400px 주식). Tables carry `minWidth: 1120px` with no horizontal scroll affordance.
State is signalled by color alone; focus styling is browser-default; `onKeyPress`
(`KoreanMarketPage.tsx:493`) is deprecated.

---

## 2. 국내 주식 — `pages/KoreanMarketPage.tsx`

### S-01 · P0 · 호가창(orderbook)이 없다
The most-used panel in any HTS is absent for stocks. Add a 10-단계 호가 ladder with
잔량 bars, 총잔량, and 체결강도. (Requires a backend route; the 선물옵션 orderbook service
at `korean_market.py:1366` is the template.)

### S-02 · P1 · 시세 카드가 데이터를 버리고 있음
`StockCard` shows only 현재가 / 전일대비 / 등락률. `KoreanStockQuote` already carries
`open`, `high`, `low`, `previous_close`, `volume` (`types/korean.ts:5-17`) and they are
never rendered. Missing entirely: 시가총액, 52주 최고/최저, 거래대금, 상한가/하한가,
외국인소진율, and PER/PBR shown next to the price rather than in a separate slab.

### S-03 · P1 · 밸류에이션 패널이 읽히지 않는다
Ten equally-weighted tiles — PER, PER(TTM), PER(12MF), PBR, PBR(TTM), EPS, EPS(TTM),
EPS(12MF), BPS, BPS(TTM) — plus a run-on metadata line
(`Requested … Used … (fallback) … TTM … 12MF`) at `KoreanMarketPage.tsx:546`.

**Do:** group into three columns — 확정 실적 기준 / TTM / 12개월 선행 — with the primary
metric (PER, PBR) sized up and the variants secondary. Replace the metadata sentence with
a 기준 시점 badge; when the requested period falls back, show a `대체 적용` chip with the
actual period, not the word "(fallback)" in a sentence. Add a tooltip per metric.

### S-04 · P1 · 재무제표가 DART 원본 그대로
A flat two-column list of every line item, no hierarchy (재무제표 is inherently a tree),
no 전년동기 비교, no 매출 대비 비중, no trend. The highlight tiles print raw won values
with no unit.

**Do:** indent by account depth, add a 전년동기 column with YoY %, add a 매출액 대비 %
column for IS, and a sparkline per key account across the last 5 periods. Add CSV export
— people take these numbers to Excel.

### S-05 · P1 · 추정실적 패널에 ELW 라벨이 노출됨
`estimateOutput1Labels` (line 335) labels a plain stock's summary as "ELW Short Code",
"ELW Current Price", "Strike Price". That is the KDevelopers field naming leaking into
the UI and it looks broken. Remap to 종목코드 / 종목명 / 현재가 / 전일대비 / 등락률 / 거래량.
Also: `output2`/`output3` tables are numbers only — add a 매출·영업이익 추정 추이 bar chart
and mark 확정 vs 추정 years distinctly.

### S-06 · P1 · 차트 조작이 원시적
Two date inputs and a Type/Period select pair. No presets, no MAs.

**Do:** period chips (1일 · 1주 · 1개월 · 3개월 · 6개월 · 1년 · 3년 · 전체) as the primary
control, dates as an advanced fallback. Add 이동평균선 5/20/60/120일 — universally expected
on Korean charts and currently absent. Add a crosshair with an OHLC readout, a
전일종가 reference line, a last-price label on the axis, and drag-zoom.

### S-07 · P2 · 인기 종목 안내가 죽은 텍스트
Line 1196 is an English sentence listing five tickers. Make them clickable chips, and
replace with 관심종목 (a real, persisted watchlist) once C-03 lands.

---

## 3. 장내채권 — `pages/BondMarketPage.tsx`

### B-01 · P0 · 화면이 API 중심으로 구성되어 있음
The title is 장내채권 **기본조회**, the subtitle names the TR ID (CTPF1114R), the main
panel is a 30-row key/value dump, and below it sits a second panel literally headed
"CTPF1114R 원본 필드 전체 (54개)". That is a debug view shipped as the product.

**Do:** restructure around what a bond buyer decides with —
1. 요약 헤더: 채권명 · 잔존만기 · 표면금리 · 매수수익률(YTM) · 신용등급
2. 가격/수익률: 현재가 · 중간가 · 이론가 · 괴리율 (저평가/고평가 라벨 + 색)
3. 이자지급 스케줄
4. 발행 정보 (접힌 상태)
5. 원본 필드 (개발자용, 접힌 상태 — keep it, just stop leading with it)

### B-02 · P0 · 이자지급 스케줄이 없음
The single most useful bond panel, and the backend already builds it —
`korean_market.py:1765` `_build_coupon_schedule()`. Nothing surfaces it.

**Do:** expose it and render 지급일 / 이자 / 원금 / 세후 / 누적 as a table plus a
cashflow bar chart, with 총 수령액 and 세후 수익률 summarized above.

### B-03 · P0 · 수익률 중심 지표 부재
Bond investors work in 수익률, 듀레이션, 잔존만기 — this page works in 가격.
`KoreanBondValuation` already returns `annual_yield_rate`, `mispricing_percent`,
`accrued_interest`, `theoretical_clean_price`. Not returned and needed: 듀레이션,
수정듀레이션, 컨벡시티, YTM from market price.

**Do (frontend-only, no backend change):** compute and display 잔존만기 as `Y년 M개월`
plus a D-day to 만기; label 괴리율 as 저평가 / 적정 / 고평가 with the KR color convention;
put 표면금리 and 만기수익률 side by side so the spread is visible.
**Do (backend):** add Macaulay/modified duration + convexity to the valuation response.

### B-04 · P0 · 마스터 목록 행이 클릭되지 않음
`masterRows.map` (line 986) renders 11 columns of which four are raw codes (`F9`, `03`,
`13`) — even though the human labels for those codes are defined 800 lines above in
`BOND_TYPE_OPTIONS` / `BOND_CLASS_OPTIONS_BY_TYPE`. And selecting a bond means reading a
PDNO off the table and retyping it into the box at the top of the page.

**Do:** render code → label (keep the code as a small mono subtitle), make rows clickable
to load the detail panel, and add column sorting on 표면금리 / 만기일 / 등락률.

### B-05 · P1 · 필터 UX가 세 갈래로 갈라져 있음
Enter in the search box runs a query; a 검색 button runs a query; a separate
필터 적용 button parked bottom-right runs a query; 필터 초기화 hard-resets to `F9`.
Applied filters are reported as a concatenated sentence of raw codes (line 930).

**Do:** one Apply path, filters as removable chips, and — critically — replace the
만기일 single-date field (currently used as *both* `maturityDateFrom` and `maturityDateTo`,
line 322, i.e. exact-match, near-useless) with a **잔존만기 range** selector:
1년 이내 / 1~3년 / 3~5년 / 5~10년 / 10년+. That is how bonds are actually screened.

### B-06 · P1 · 페이지네이션이 10건 단위
`PAGE_SIZE = 10` against a master of thousands: 100 clicks to see 1,000 bonds. Offer
50/100/200, or virtualize the table and drop the button entirely.

### B-07 · P2 · 채권 랜딩에 금리 커브가 없음
The canonical bond landing screen is the 국고채 수익률 곡선 (1/3/5/10/20/30년) with
전일 대비 변화. Add it above the search — it gives the page a reason to exist before the
user knows which bond they want.

---

## 4. 국내 선물옵션 — `pages/DomesticFuturesOptionsPage.tsx`

### D-01 · P0 · 구현된 API 중 가장 좋은 것들이 UI에 없음
Verified unused anywhere in `frontend/src`:

| service method | payload it returns | UI usage |
|---|---|---|
| `getFuturesOptionQuote` | delta, gamma, theta, vega, rho, IV, HV, 미결제약정, 이론가, 베이시스, 괴리율, 상/하한가, 잔존일수 | none |
| `getFuturesOptionOrderbook` | 5단계 호가 + 총잔량/건수 | none |
| `getFuturesOptionChain` | calls/puts × strike, with greeks, IV, OI, 내재가치, 시간가치, moneyness | none |

The page is a chart plus a code table. **옵션 T자 배열** is *the* screen for Korean
derivatives, and the data is already flowing.

**Do:** build the T-board — calls left, strikes centered, puts right; ATM row highlighted
and auto-scrolled into view; columns 현재가 · 등락 · 거래량 · 미결제 · IV · 델타; KR color
convention throughout. Add a quote panel with a Greeks row and a 5단계 호가 ladder beside
the chart.

### D-02 · P0 · 표준코드 정타 입력 요구
`resolveInstrument` (line 172) demands an exact 표준코드 or 단축코드 match. The master
table right below has every code and is not clickable.

**Do:** clickable master rows, plus a 종목 선택 flow that matches how derivatives are
actually chosen: 기초자산 (KOSPI200 / 개별주식 / 상품) → 월물 → 콜/풋 → 행사가. Default to
근월물. Add a 잔존일수 badge next to the selected instrument.

### D-03 · P1 · 실패가 조용히 빈 차트로 끝남
The candidate loop over `marketDivCode` × symbol (lines 240–262) swallows 404s and, when
everything 404s, sets empty arrays and returns — the user sees
"조회된 차트 데이터가 없습니다" with no explanation and no idea that six combinations were
tried. Surface the real cause: 시세 미제공 종목 / 만기 경과 / 휴장일.

### D-04 · P1 · 마스터 테이블이 파생상품 정보를 안 보여줌
Five columns: 시장 (raw `index`/`stock`/`commodity`), 단축코드, 표준코드, 종목명, 기초자산명.
`KoreanFuturesOptionsMasterItem` also carries `strike_price`, `month_class_code`,
`atm_class_code`, `info_type` — i.e. 행사가, 만기월, ATM 구분, 콜/풋 — none shown.
Add those columns, translate `market` to 지수/주식/상품, and add 만기월 · 콜풋 filters.

### D-05 · P2 · 분석 시각화 없음
Two high-value, low-cost additions once the option chain is wired:
- **IV 스마일**: implied volatility across strikes for the selected expiry — a ~20-line
  recharts `LineChart` over data you already have.
- **손익 다이어그램**: payoff at expiry for the selected contract (and, later, for a
  multi-leg position).

---

## 5. 차트 컴포넌트 — `components/CandleChart.tsx`

### X-01 · P1 · `CandlesLayer`가 렌더마다 재생성됨
It is defined inside the `CandleChart` render body (line 235) and calls `React.useId()`
(line 251). New component identity every render → the layer unmounts and remounts on every
parent state change. Hoist it to module scope and pass what it needs as props.

### X-02 · P1 · 가격/거래량이 별개 차트
Two independent `ResponsiveContainer`s with two independent `Tooltip`s: hovering the price
chart doesn't highlight the corresponding volume bar, and the two x-axes can drift out of
alignment because their y-axis tick widths differ. Use recharts `syncId`, or one chart with
two y-axes and a shared cursor.

### X-03 · P2 · 높이 계산이 취약
`height - 100` (line 331) is hard-coded: `height={320}` yields a 220px price chart, and
anything under ~150 collapses. Take an explicit `volumeHeight` prop or a ratio.

### X-04 · P2 · 차트 상호작용 부재
No crosshair, no 마지막 가격 라벨, no 전일종가 기준선, no zoom/pan, no log scale, no MA
overlay — see S-06. These are the baseline for a chart Korean users will take seriously.

---

## 6. 제안 실행 순서

**1차 (기반, ~1주) — 완료** — C-01 색상 관행, C-02 한국어 통일, C-04 토큰/프리미티브,
C-05 숫자 조판, C-06 로딩·에러 상태, X-01/X-02/X-03 차트. Nothing user-visible is added,
but every later change lands on a stable base and C-01 alone fixes the most serious defect.

**2차 (검색·탐색, ~1주)** — C-03 전 자산군 통합 검색 + 마스터 행 클릭 (B-04, D-02) +
Ctrl+K 팔레트. This removes the product's biggest friction point on all three pages at once.

**3차 (자산별 심화, ~2주)** — D-01 옵션 T자 배열과 그릭스/호가 (the single largest jump
in capability per unit of work, since the API is done), B-01/B-02/B-03 채권 화면 재구성과
이자 스케줄, S-02/S-03/S-06 주식 시세·밸류에이션·차트.

**4차 (마감)** — C-07 시장 컨텍스트, B-07 금리 커브, D-05 IV 스마일/손익도, C-08 반응형과
접근성, 다크 테마.
