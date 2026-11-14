# 화면 사용 가이드 · User Guide

[한국어](#한국어) · [English](#english)

---

## 한국어

### 시작하기

백엔드와 프론트엔드를 실행한 뒤 브라우저에서 `http://localhost:5173`을 엽니다. 설치와 실행은 [SETUP.md](SETUP.md)를 보세요. 이 앱은 조회 전용이라 주문 기능이 없고, 값은 실시간 스트리밍이 아니라 조회한 시점의 스냅샷입니다.

### 공통 요소

- **상단 메뉴**: 국내(국내주식 · 장내채권 · 선물옵션 · 베이시스), 해외(해외주식), 계좌(계좌조회). 왼쪽의 Custom HTS를 누르면 홈으로 갑니다.
- **등락 색상**: 메뉴 오른쪽 토글로 고릅니다. 국내식은 상승 빨강·하락 파랑, 글로벌식은 상승 초록·하락 빨강이며 선택은 브라우저에 저장됩니다. 해외주식 화면은 항상 글로벌식입니다.
- **캔들 차트**: 위쪽은 가격 창(캔들과 종가 선), 아래쪽은 거래량 창이고 두 창의 커서가 함께 움직입니다. 마우스를 올리면 날짜·시각과 시가·고가·저가·종가, 시가 대비 등락률이 보입니다.

### 홈

국내주식, 장내채권, 선물옵션, 해외주식, 계좌조회로 가는 카드가 있습니다. 베이시스는 상단 메뉴에서 들어갑니다.

### 국내주식

- **종목 검색**: 종목명이나 6자리 코드를 입력하면 KOSPI·KOSDAQ·KONEX 마스터 파일에서 후보를 보여 줍니다. ↑/↓로 고르고 Enter로 선택하며, 목록에서 고르지 않고 코드를 그대로 Enter해도 됩니다. 아래 칩으로 자주 찾는 종목과 최근 조회(최대 6개)를 다시 열 수 있습니다. 선택한 종목은 주소(`/korean?symbol=005930`)에 남아 새로고침하거나 즐겨찾기해도 유지됩니다. 기본 종목은 삼성전자입니다.
- **시세 카드**: 현재가, 전일대비·등락률, 시가·고가·저가·전일종가·거래량, 일중 범위, 시가총액·상장주식수
- **투자지표**: PER·PBR·EPS·BPS를 확정 실적 기준, TTM, 12개월 선행(PER·EPS) 세 묶음으로 보여 줍니다. 고른 기간에 재무 데이터가 없으면 직전 기간 값을 쓰고 '대체 적용' 배지를 붙입니다.
- **차트**: 차트 종류에서 일봉 또는 분봉을 고릅니다.
  - 일봉: 주기(일·주·월), 시작일·종료일(선택). 한국투자증권 API가 최근 30개 봉만 주므로 기간을 넓혀도 30개를 넘지 않고, 시작일·종료일은 그 안에서 범위를 좁힙니다.
  - 분봉: 간격(1·5·10·30·60분), 기준일(기본 오늘), 기준시각(기본 15:30). 그날 09:00부터 기준시각까지 그립니다.
- **재무제표 (OpenDART)**: 연도(최근 5년, 기본 전년도), 연간/분기, 분기(1~4), 연결/별도를 고르고 손익계산서·재무상태표·현금흐름표 칩으로 표를 바꿉니다. 위쪽 타일에 핵심 값(매출액·영업이익·당기순이익, 자산·부채·자본총계 등)이 나오고, 아래 표는 계정과목 검색으로 거를 수 있습니다. 금액 단위는 원입니다. 현금흐름표는 OpenDART 주요계정 API 범위 밖이라 대개 비어 있습니다([OPENDART_API.md](OPENDART_API.md)).
- **추정실적 (KDevelopers)**: 종목 요약, 손익 추정, 투자지표 추정 표. 금액 단위는 억원입니다.
- **새로고침** 버튼은 모든 패널을 다시 조회합니다. 같은 조건의 데이터는 1분 동안 캐시됩니다.

### 장내채권

- **채권 조회**: 채권코드(PDNO, 예: `KR2033022D33`)를 입력하고 조회합니다.
- **채권 정보**: 현재가, 전일대비, 중간가, 최우선 매도/매수, 수익률, 시가/고가/저가, 거래량
- **수익률 분석**: 만기수익률(YTM), 세후 수익률, 민평 수익률과 민평 대비 차이, 매수·매도 호가 수익률, 수정 듀레이션, DV01, 경과이자. 호가별 수익률, 금리 변동 시 가격, 채권평가사별 평가 표가 이어집니다. 가격은 액면 10,000원당(경과이자 포함)입니다.
- **수익률 추이: 시장 vs 민평**: 시장 수익률과 민평 수익률 두 선, 그 차이(시장 − 민평) 막대, 일별 표. 기간은 2개월·4개월·8개월입니다.
- **장내채권 현재가 (일별)**: 최근 일별 시세 캔들 차트(최대 100일)
- **채권 기본정보**와 **원본 필드 전체**(장내채권 기본조회 응답)
- **채권 마스터 코드**: 채권코드·채권명 검색, 채권 유형(A0 장내소매채권, F9 주식관련사채/소액채권, C0 국고채권), 분류코드, 이자유형, 상장일·발행일·상환일 범위로 거릅니다. 10건씩 더 불러오며, 찾은 코드를 위 조회 칸에 입력하면 됩니다. 목록이 비어 있거나 채권명이 이상하면 채권 마스터를 먼저 받아야 합니다([MASTER_FILES.md](MASTER_FILES.md)).

### 선물옵션

- 표준코드나 단축코드를 입력하면 마스터에서 종목을 확인한 뒤 차트를 그립니다.
- **일봉**: 시작일·종료일(기본 최근 3일)
- **분봉**: 1분봉. 기준일, 기준시각(기본 15:30), 조회 범위(30분·1시간·2시간·4시간·장 전체)
- **선물옵션 마스터 코드**: 표준코드·단축코드·종목명으로 검색하며 시장(지수·주식·상품), 단축코드, 표준코드, 종목명, 기초자산명을 보여 줍니다.

### 베이시스

- **기초자산**: 종목명, 종목코드 또는 지수(예: 삼성전자, 005930, KOSPI200)를 입력하거나 빠른 선택 칩을 누릅니다. 선물이 상장된 종목·지수만 나옵니다.
- **조달금리(연 %)**: 비워 두면 증권사 이론가를 기준으로 삼고, 입력하면 그 금리와 **만기 전 예상 배당**으로 이론가를 계산합니다.
- **요약**: 현물, 최근월물, 베이시스(선물 − 현물), 이론가 대비 괴리율(선물 고평가/저평가), 내재금리(연)
- **월물 표**: 잔존일, 현재가, 매수/매도, 베이시스와 베이시스 %, 호가중간 베이시스, 이론가, 괴리율, 내재금리, 거래량, 미결제. 행을 누르면 그 월물의 추이를 봅니다.
- **옵션 합성선물 (풋-콜 패리티)**: 월물 옵션이 없는 기초자산은 안내 문구만 나옵니다. 옵션 월물과 행사가 개수를 고르면 합성선물 가격, 선물·현물 대비 차이, 컨버전·리버설 차익을 행사가별로 보여 줍니다.
- **베이시스 추이**: 1개월·3개월·6개월. 최근 베이시스, 평균, 범위, Z-점수와 현물·선물 두 선, 베이시스 막대, 일별 표가 나옵니다.

### 해외주식

화면 문구는 영어입니다. 데이터는 Yahoo Finance(yfinance)에서 가져옵니다.

- 티커(예: AAPL)를 입력하고 Search를 누르면 시세 카드, Market Cap, PER·PBR·EPS·BPS가 나옵니다.
- **차트**: Period(1 Day ~ Max), Interval(1 Minute ~ Monthly), Start/End Date(둘 다 입력하면 Period 대신 사용), Time(분 단위 간격일 때 미국 동부시간 기준 이 시각 이전 봉을 숨김, 기본 09:30). 가로축은 뉴욕 시간이고 서울 시간이 보조 축으로 붙습니다. 분봉은 Yahoo Finance가 제공하는 최근 기간만 볼 수 있습니다.
- **재무 표**: 연도별 Revenue, Operating Income, Net Income, EPS

### 계좌조회

- `.env`의 `HANTU_ACCOUNT_NUMBER` 계좌 한 개의 국내주식 잔고를 화면을 열 때 조회합니다. 계좌번호는 끝 4자리만 보입니다.
- 기준 시각과 총 평가금액(현금 포함), 예수금, 매입금액, 평가손익 카드
- 계좌 요약, 종목 비중(도넛 차트), 종목별 손익(막대), 보유 종목 표(수량, 평균단가, 현재가, 평가금액, 평가손익)
- 보유 종목이 한 페이지(50종목)를 넘으면 일부가 빠질 수 있습니다([KDEVELOPERS_API.md](KDEVELOPERS_API.md)).

### 문제 해결

- **모든 패널이 비거나 오류**: 백엔드가 실행 중인지, `.env`의 한국투자증권 키가 맞는지 확인하세요. `backend/scripts/check_hantu_keys.py`로 점검할 수 있습니다.
- **국내주식 검색 결과가 없음**: 주식 마스터 파일 다운로드가 실패했을 수 있습니다. 백엔드 로그를 확인하세요.
- **재무제표가 없음**: 다른 연도나 분기를 고르고 `DART_API_KEY`를 확인하세요.
- **분봉이 비어 있음**: 휴장일이거나 장 시작 전 날짜·시각일 수 있습니다.

---

## English

### Getting started

Start the backend and frontend, then open `http://localhost:5173` in a browser. See [SETUP.md](SETUP.md) for installation and start-up. The app is read-only, with no order entry, and values are snapshots taken when you look them up, not a live stream.

### Common elements

- **Top menu**: 국내 (domestic: 국내주식 stocks · 장내채권 listed bonds · 선물옵션 futures/options · 베이시스 basis), 해외 (overseas: 해외주식 US stocks), 계좌 (account: 계좌조회). Click Custom HTS on the left to return home.
- **Up/down colours (등락 색상)**: a toggle at the right of the menu. 국내식 (Korean) shows up in red and down in blue; 글로벌식 (global) shows up in green and down in red. The choice is saved in the browser. The US stock page always uses the global convention.
- **Candle chart**: a price pane on top (candles plus a close line) and a volume pane below, with a shared cursor. Hovering shows the date/time, open, high, low and close, and the change from the open.

### Home (홈)

Cards link to the domestic stock, listed bond, futures/options, US stock and account pages. The basis page is reached from the top menu.

### Domestic stocks (국내주식)

- **Search**: type a company name or 6-digit code and the box suggests matches from the KOSPI/KOSDAQ/KONEX master files. Use ↑/↓ and Enter to pick one, or press Enter on a raw code without picking. Chips below reopen popular stocks (자주 찾는 종목) and recent lookups (최근 조회, up to 6). The selected stock stays in the URL (`/korean?symbol=005930`), so reloads and bookmarks keep it. The default stock is Samsung Electronics.
- **Quote card**: price, change and change rate, open/high/low/previous close/volume, intraday range, market cap and shares outstanding
- **Valuation (투자지표)**: PER, PBR, EPS and BPS in three groups: reported results, TTM, and 12-month forward (PER, EPS). When the chosen period has no financials, the previous period is used and a 대체 적용 (fallback) badge appears.
- **Chart**: choose daily (일봉) or minute (분봉) under chart type.
  - Daily: period (day/week/month) and optional start/end dates. The KIS API returns only the latest 30 candles, so a wider range never shows more than 30; the dates narrow the range within them.
  - Minute: interval (1/5/10/30/60 minutes), date (default today) and cut-off time (default 15:30). The chart covers 09:00 to the cut-off on that day.
- **Financial statements (OpenDART)**: choose a year (last 5 years, default the previous year), annual/quarterly, quarter (1–4) and consolidated/separate, then switch between income statement, balance sheet and cash flow with the chips. Tiles show the key figures (revenue, operating income, net income, total assets/liabilities/equity and so on); the table below can be filtered by account name. Amounts are in KRW. The cash flow tab is usually empty because cash flow items are outside OpenDART's major-account APIs ([OPENDART_API.md](OPENDART_API.md)).
- **Estimates (KDevelopers)**: stock summary, earnings estimates and valuation estimates tables. Amounts are in 억원 (100 million KRW).
- The **새로고침** (refresh) button reloads every panel. Data for the same settings is cached for one minute.

### Listed bonds (장내채권)

- **Lookup**: enter a bond code (PDNO, e.g. `KR2033022D33`) and click 조회.
- **Bond info**: price, change, mid price, best ask/bid, yield, open/high/low, volume
- **Yield analysis (수익률 분석)**: yield to maturity, after-tax yield, pricing-agency yield (민평) and the spread to it, bid/ask yields, modified duration, DV01 and accrued interest, followed by tables of yields per order-book level, prices under rate shifts, and each pricing agency's valuation. Prices are per 10,000 KRW face value, including accrued interest.
- **Yield history, market vs agency (수익률 추이)**: two lines for the market and agency yields, bars for the spread (market − agency) and a daily table, over 2, 4 or 8 months.
- **Daily prices (장내채권 현재가 (일별))**: a candle chart of recent daily prices (up to 100 days)
- **Basic info (채권 기본정보)** and **all raw fields (원본 필드 전체)** from the bond basic info response
- **Bond master list (채권 마스터 코드)**: search by code or name and filter by bond type (A0 retail bonds, F9 equity-linked/small-lot bonds, C0 treasury bonds), class code, interest type, and listing, issue and maturity date ranges. Load 10 more at a time, then type a code you found into the lookup box. If the list is empty or names look wrong, download the bond master first ([MASTER_FILES.md](MASTER_FILES.md)).

### Futures/options (선물옵션)

- Enter a standard or short code; the page confirms the instrument in the master file and then draws the chart.
- **Daily**: start/end dates (default the last 3 days)
- **Minute**: 1-minute candles with a date, cut-off time (default 15:30) and range (30 minutes, 1, 2 or 4 hours, or the whole session)
- **Futures/options master list (선물옵션 마스터 코드)**: search by standard code, short code or name; shows market (index, stock, commodity), short code, standard code, name and underlying.

### Basis (베이시스)

- **Underlying**: type a stock name, stock code or index (e.g. 삼성전자, 005930, KOSPI200) or click a quick-pick chip. Only stocks and indices with listed futures appear.
- **Funding rate (조달금리, % p.a.)**: leave it blank to use the broker's theoretical price as fair value; enter a rate to compute the theoretical price from it and the **expected dividends before expiry (만기 전 예상 배당)**.
- **Summary**: spot, front month, basis (futures − spot), mispricing against the theoretical price (futures rich/cheap), and the implied rate (p.a.)
- **Contract table**: days to expiry, price, bid/ask, basis and basis %, mid-quote basis, theoretical price, mispricing, implied rate, volume and open interest. Click a row to see that month's history.
- **Synthetic futures from options (put-call parity)**: underlyings without monthly options show a short note instead. Pick an option month and the number of strikes to see, per strike, the synthetic futures price, its gap to futures and spot, and conversion/reversal edges.
- **Basis history**: 1, 3 or 6 months, with latest basis, mean, range and Z-score, spot and futures lines, basis bars and a daily table.

### US stocks (해외주식)

The page text is in English. Data comes from Yahoo Finance (yfinance).

- Enter a ticker (e.g. AAPL) and click Search to see the quote card, market cap, and PER, PBR, EPS and BPS.
- **Chart**: Period (1 Day to Max), Interval (1 Minute to Monthly), Start/End Date (used instead of Period when both are set), and Time (for minute intervals, hides candles before this US Eastern time; default 09:30). The time axis is New York time with Seoul time as a secondary axis. Minute data only goes back as far as Yahoo Finance provides.
- **Financials table**: Revenue, Operating Income, Net Income and EPS by year

### Account (계좌조회)

- Loads the domestic stock balance of the single account in `HANTU_ACCOUNT_NUMBER` (`.env`) when the page opens. Only the last 4 digits of the account number are shown.
- Cards for the as-of time, total value (cash included), deposit, purchase amount and unrealised P&L
- Account summary, holdings weight (donut chart), P&L by stock (bars), and a holdings table (quantity, average price, current price, value, P&L)
- Holdings beyond one page (50 stocks) may be missing ([KDEVELOPERS_API.md](KDEVELOPERS_API.md)).

### Troubleshooting

- **Every panel is empty or shows an error**: check that the backend is running and the KIS keys in `.env` are right. `backend/scripts/check_hantu_keys.py` checks them.
- **Domestic stock search finds nothing**: the stock master download may have failed. Check the backend log.
- **No financial statements**: try another year or quarter and check `DART_API_KEY`.
- **Minute chart is empty**: the date may be a market holiday, or the time may be before the open.
