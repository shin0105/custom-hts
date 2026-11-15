# 한국투자증권 Open API 연동 · KIS Open API Integration

[한국어](#한국어) · [English](#english)

---

## 한국어

### 개요

백엔드는 한국투자증권(KIS) Open API(KIS Developers)의 REST API로 국내 주식·장내채권·선물옵션 시세와 계좌 잔고를 조회합니다. 주문 API는 호출하지 않는 조회 전용 연동이며, WebSocket 실시간 시세도 쓰지 않습니다. 모든 값은 화면에서 조회한 시점의 스냅샷입니다.

- 클라이언트: [`backend/src/integrations/kdevelopers.py`](../backend/src/integrations/kdevelopers.py) (`KDevelopersClient`, 전역 인스턴스 `kdevelopers_client`)
- 토큰 캐시: [`backend/src/integrations/token_store.py`](../backend/src/integrations/token_store.py)
- 요청·응답 필드 전체 명세: [KIS Developers 포털](https://apiportal.koreainvestment.com/)

### 설정

저장소 루트의 `.env`에 아래 값을 넣습니다. 자세한 설치 과정은 [SETUP.md](SETUP.md)를 보세요.

| 변수 | 설명 |
|------|------|
| `HANTU_API_KEY` | 앱키(appkey) |
| `HANTU_API_SECRET` | 앱시크릿(appsecret) |
| `HANTU_ACCOUNT_NUMBER` | 계좌번호 앞 8자리(CANO). 계좌조회에만 필요하며, 예전 이름 `HANTU_BANK_ACCOUNT`도 읽습니다 |
| `HANTU_TOKEN_CACHE_PATH` | (선택) 토큰 캐시 파일 경로. 기본값 `backend/.cache/kis_tokens.json` |

```bash
HANTU_API_KEY=your_app_key
HANTU_API_SECRET=your_app_secret
HANTU_ACCOUNT_NUMBER=12345678
# HANTU_TOKEN_CACHE_PATH=/path/to/kis_tokens.json
```

계좌상품코드(ACNT_PRDT_CD)는 환경 변수가 아니라 `/api/korean/account?account_product_code=01` 쿼리로 넘기며 기본값은 `01`입니다.

### 실전투자 서버만 지원

서버 주소는 `backend/src/utils/config.py`의 `HANTU_BASE_URL`(`https://openapi.koreainvestment.com:9443`)로 고정되어 있고, TR ID도 실전투자용(예: 잔고조회 `TTTC8434R`)을 씁니다. 모의투자 서버로 바꾸는 설정은 없으므로 모의투자 앱키로는 토큰 발급부터 실패합니다. 어떤 종류의 키인지는 아래 [키 점검 스크립트](#키-점검-스크립트)로 확인할 수 있습니다.

### 인증과 토큰 캐시

접근 토큰은 다음 순서로 구합니다.

1. 메모리에 유효한 토큰이 있으면 그대로 씁니다.
2. 없으면 로컬 캐시 파일에서 읽습니다. 항목은 앱키의 SHA-256 해시로 구분하며 앱키 자체는 저장하지 않습니다.
3. 그래도 없으면 `POST /oauth2/tokenP`(`grant_type=client_credentials`)로 새로 발급받아 캐시에 저장합니다.

- 토큰은 약 24시간 유효하고, KIS는 토큰 발급을 앱키당 1분에 1회로 제한합니다. 그래서 서버를 재시작해도 캐시된 토큰을 재사용합니다.
- 만료 시각은 응답의 `access_token_token_expired`(KST) 또는 `expires_in`으로 계산하며, 만료 60초 전부터는 만료된 것으로 봅니다.
- API가 토큰 만료(`EGW00123` 등)를 응답하면 캐시를 지우고 한 번 재발급한 뒤 같은 요청을 다시 보냅니다.
- 캐시 파일은 권한 0600으로 원자적으로 기록되고 `.gitignore`에 포함되어 있습니다. 여러 앱키가 한 파일을 공유할 수 있습니다.
- `revoke_access_token()`은 `POST /oauth2/revokeP`로 토큰을 폐기하고 캐시를 지웁니다. API 라우트로는 노출되어 있지 않습니다.

```json
{
  "<sha256 of app key>": {
    "access_token": "<access token>",
    "expires_at": "2025-01-02T00:00:00+00:00",
    "updated_at": "2025-01-01T00:00:00+00:00"
  }
}
```

캐시 파일을 지우면 다음 요청에서 새 토큰을 발급받습니다. 1분 제한이 있으니 연달아 지우지 마세요.

### 공통 요청 형식

- 헤더: `authorization: Bearer <token>`, `appkey`, `appsecret`, `tr_id`, `custtype: P`(개인), `tr_cont`(연속조회)
- 응답의 `rt_cd`가 `"0"`이면 성공이고, 실패하면 `msg_cd`·`msg1`을 로그에 남깁니다. 백엔드 엔드포인트는 이때 대부분 404를 돌려줍니다.
- 주식기본조회·종목추정실적·채권 평균단가조회는 응답 헤더 `tr_cont`가 다음 페이지가 있다고 알리면 `tr_cont: N`으로 이어서 요청하며, 최대 10페이지까지 읽습니다.
- 시장 구분 코드(`FID_COND_MRKT_DIV_CODE`): `J` 주식, `U` 업종·지수, `B` 장내채권, `F` 지수선물, `O` 지수옵션, `JF` 주식선물, `JO` 주식옵션. `CF`·`CM`·`EU`의 의미는 포털 명세를 참고하세요.

### 속도 제한

- 클라이언트는 모든 요청 뒤에 0.05초 쉽니다(`_smart_sleep`). KIS의 초당 호출 한도는 포털 공지를 따릅니다.
- 옵션 전광판(`/futures-options/option-chain`)은 같은 조건을 1초 안에 다시 요청하면 직전 결과를 돌려줍니다.
- 토큰 발급은 1분에 1회이므로 위의 캐시를 거칩니다.

### 사용하는 API

국내주식 (`/uapi/domestic-stock/v1/...`)

| 기능 | 경로 | TR ID | 백엔드 사용처 |
|------|------|-------|---------------|
| 주식현재가 시세 | `quotations/inquire-price` | `FHKST01010100` | `/api/korean/quote/{symbol}`, 투자지표, 베이시스 |
| 주식현재가 일자별 (일·주·월봉 최근 30개) | `quotations/inquire-daily-price` | `FHKST01010400` | `/api/korean/candle/{symbol}` |
| 주식일별분봉조회 | `quotations/inquire-time-dailychartprice` | `FHKST03010230` | `/api/korean/candle-minute/{symbol}` |
| 국내주식기간별시세 | `quotations/inquire-daily-itemchartprice` | `FHKST03010100` | 베이시스 추이(현물 일별 종가) |
| 국내업종 현재지수 | `quotations/inquire-index-price` | `FHPUP02100000` | 베이시스(지수 현물) |
| 국내업종기간별시세 | `quotations/inquire-daily-indexchartprice` | `FHKUP03500100` | 베이시스 추이(지수) |
| 주식기본조회 | `quotations/search-stock-info` | `CTPF1002R` | `/api/korean/stock-info/{pdno}`, 투자지표 |
| 국내주식 종목추정실적 | `quotations/estimate-perform` | `HHKST668300C0` | `/api/korean/estimate-perform/{symbol}` |
| 주식잔고조회 | `trading/inquire-balance` | `TTTC8434R` | `/api/korean/account` |

장내채권 (`/uapi/domestic-bond/v1/quotations/...`)

| 기능 | 경로 | TR ID | 백엔드 사용처 |
|------|------|-------|---------------|
| 장내채권현재가(시세) | `inquire-price` | `FHKBJ773400C0` | `/api/korean/bonds/{pdno}/price`, 수익률 분석 |
| 장내채권현재가(호가) | `inquire-asking-price` | `FHKBJ773401C0` | 최우선 호가, 수익률 분석 |
| 장내채권현재가(일별) | `inquire-daily-price` | `FHKBJ773404C0` | `/api/korean/bonds/{pdno}/daily-price`, 수익률 추이 |
| 장내채권 기본조회 | `search-bond-info` | `CTPF1114R` | `/api/korean/bonds/{pdno}/info`, 수익률 분석 |
| 장내채권 발행정보 | `issue-info` | `CTPF1101R` | `/api/korean/bonds/{pdno}/issue` |
| 장내채권 평균단가조회(민평) | `avg-unit` | `CTPF2005R` | 수익률 분석·추이 |

국내선물옵션 (`/uapi/domestic-futureoption/v1/quotations/...`)

| 기능 | 경로 | TR ID | 백엔드 사용처 |
|------|------|-------|---------------|
| 선물옵션 시세 | `inquire-price` | `FHMIF10000000` | `/api/korean/futures-options/quote`, 베이시스, 옵션 패리티 |
| 선물옵션 시세호가 | `inquire-asking-price` | `FHMIF10010000` | `/api/korean/futures-options/orderbook`, 베이시스, 옵션 패리티 |
| 선물옵션 분봉조회 | `inquire-time-fuopchartprice` | `FHKIF03020200` | `/api/korean/futures-options/minute-candles` |
| 선물옵션기간별시세 | `inquire-daily-fuopchartprice` | `FHKIF03020100` | `/api/korean/futures-options/daily-candles`, 베이시스 추이 |
| 국내옵션전광판_콜풋 | `display-board-callput` | `FHPIF05030100` | `/api/korean/futures-options/option-chain` |

백엔드 엔드포인트의 파라미터는 [API.md](API.md)에 정리되어 있습니다.

### 동작 참고

- **일·주·월봉**: `inquire-daily-price`는 최근 30개 봉만 돌려줍니다. `start_date`·`end_date`는 그 30개 안에서 범위를 좁히는 필터입니다. `adjust_price=true`(기본)이면 수정주가를 받습니다. 이 API의 `FID_ORG_ADJ_PRC`는 `1`이 수정주가 반영이며, 기간별 일봉(`inquire-daily-itemchartprice`)은 반대로 `0`이 수정주가입니다.
- **분봉**: 한 번에 최대 120건씩 시각을 거슬러 올라가며 하루치를 모은 뒤 09:00부터 기준시각(기본 15:30)까지만 남깁니다. 5·10·30·60분봉은 1분봉을 합쳐 만듭니다.
- **기간별 일봉(주식·지수)**: 한 번의 응답 상한(주식 100건, 지수 50건)을 넘는 구간은 종료일을 앞당기며 여러 번 조회합니다.
- **계좌 잔고**: 첫 페이지만 조회하고 연속조회는 하지 않습니다. 한 페이지(실전 계좌 기준 50종목)를 넘게 보유하면 일부 종목이 빠질 수 있습니다.
- **종목추정실적**: 매출액·영업이익 등 금액 단위는 억원입니다.

### 키 점검 스크립트

[`backend/scripts/check_hantu_keys.py`](../backend/scripts/check_hantu_keys.py)는 `.env`의 앱키가 실제로 동작하는지 확인합니다.

```bash
cd backend
uv run python scripts/check_hantu_keys.py
```

- 저장소 루트 `.env`에서 `HANTU_API_KEY`/`HANTU_API_SECRET`과, 있으면 두 번째 키(`HANTU_API_KEY_2`/`HANTU_API_SECRET_2` 또는 `HANTU_API_KEY2`/`HANTU_API_SECRET2`)를 읽습니다.
- 키마다 실전투자 서버에서 토큰을 발급받고, 실패하면 모의투자 서버(`https://openapivts.koreainvestment.com:29443`)에서 다시 시도해 모의투자 키인지 알려 줍니다. 이어서 삼성전자(005930) 현재가를 조회합니다.
- 실전투자 서버에서 받은 토큰은 토큰 캐시에 저장하므로 앱이 바로 재사용합니다.
- 앱키는 앞뒤 4자리만 보여 주고 시크릿·토큰은 출력하지 않습니다. 모든 키가 통과하면 종료 코드 0을 돌려줍니다.
- 실행할 때마다 새 토큰을 발급하므로 1분 안에 다시 실행하면 발급 제한에 걸릴 수 있습니다.

### 문제 해결

- **토큰 발급 실패**: 앱키·시크릿을 확인하고, 스크립트로 모의투자 키인지 확인하세요.
- **1분당 1회 발급 제한 오류**: 1분 뒤 다시 시도하세요. 캐시 파일이 있으면 앱은 새로 발급하지 않습니다.
- **계좌조회 500 오류(`HANTU_ACCOUNT_NUMBER ... is not configured correctly`)**: 계좌번호가 숫자 8자리인지 확인하세요.

### 참고

- [KIS Developers 포털](https://apiportal.koreainvestment.com/): API 명세, 공지, 신청
- [KIS 공식 샘플 코드](https://github.com/koreainvestment/open-trading-api)
- [MASTER_FILES.md](MASTER_FILES.md): 종목 마스터 파일
- [API.md](API.md): 백엔드 REST API

---

## English

### Overview

The backend uses the REST API of the Korea Investment & Securities (KIS) Open API, also called KIS Developers, to read domestic stock, listed bond and futures/options quotes plus the account balance. The integration is read-only: no order APIs are called, and the WebSocket real-time feed is not used. Every value is a snapshot taken when a page requests it.

- Client: [`backend/src/integrations/kdevelopers.py`](../backend/src/integrations/kdevelopers.py) (`KDevelopersClient`, global instance `kdevelopers_client`)
- Token cache: [`backend/src/integrations/token_store.py`](../backend/src/integrations/token_store.py)
- Full request/response field specs: [KIS Developers portal](https://apiportal.koreainvestment.com/)

### Configuration

Put these values in the `.env` at the repository root. See [SETUP.md](SETUP.md) for the full setup.

| Variable | Description |
|----------|-------------|
| `HANTU_API_KEY` | App key (appkey) |
| `HANTU_API_SECRET` | App secret (appsecret) |
| `HANTU_ACCOUNT_NUMBER` | First 8 digits of the account number (CANO). Only needed for the account page; the legacy name `HANTU_BANK_ACCOUNT` is also read |
| `HANTU_TOKEN_CACHE_PATH` | (Optional) token cache file path. Default `backend/.cache/kis_tokens.json` |

```bash
HANTU_API_KEY=your_app_key
HANTU_API_SECRET=your_app_secret
HANTU_ACCOUNT_NUMBER=12345678
# HANTU_TOKEN_CACHE_PATH=/path/to/kis_tokens.json
```

The account product code (ACNT_PRDT_CD) is not an environment variable; pass it as `/api/korean/account?account_product_code=01`. It defaults to `01`.

### Real-trading server only

The server is fixed by `HANTU_BASE_URL` in `backend/src/utils/config.py` (`https://openapi.koreainvestment.com:9443`), and the TR IDs are the real-account ones (for example `TTTC8434R` for the balance). There is no setting to switch to the paper-trading (모의투자) server, so a paper-trading app key already fails at token issuance. Use the [key check script](#key-check-script) to see which kind of key you have.

### Authentication and token cache

The client obtains an access token in this order:

1. Use a valid token held in memory.
2. Otherwise read it from the local cache file. Entries are keyed by the SHA-256 hash of the app key; the key itself is never stored.
3. Otherwise issue a new one with `POST /oauth2/tokenP` (`grant_type=client_credentials`) and save it to the cache.

- A token is valid for about 24 hours, and KIS allows one token issuance per minute per app key. That is why the cached token is reused across server restarts.
- Expiry comes from `access_token_token_expired` (KST) or `expires_in` in the response; a token is treated as expired 60 seconds early.
- If an API call reports an expired token (`EGW00123` and similar), the client clears the cache, issues a new token once and retries the same request.
- The cache file is written atomically with 0600 permissions and is listed in `.gitignore`. Several app keys can share one file.
- `revoke_access_token()` revokes a token with `POST /oauth2/revokeP` and clears the cache. It is not exposed as an API route.

```json
{
  "<sha256 of app key>": {
    "access_token": "<access token>",
    "expires_at": "2025-01-02T00:00:00+00:00",
    "updated_at": "2025-01-01T00:00:00+00:00"
  }
}
```

Deleting the cache file makes the next request issue a new token. Because of the one-per-minute limit, do not delete it repeatedly.

### Common request format

- Headers: `authorization: Bearer <token>`, `appkey`, `appsecret`, `tr_id`, `custtype: P` (individual), `tr_cont` (continuation)
- `rt_cd == "0"` means success; on failure `msg_cd` and `msg1` are logged, and most backend endpoints then return 404.
- Stock basic info, estimate performance and bond average unit price follow continuation: when the response header `tr_cont` signals another page, the next one is requested with `tr_cont: N`, up to 10 pages.
- Market division codes (`FID_COND_MRKT_DIV_CODE`): `J` stocks, `U` sector/index, `B` listed bonds, `F` index futures, `O` index options, `JF` stock futures, `JO` stock options. See the portal for `CF`, `CM` and `EU`.

### Rate limits

- The client sleeps 0.05 seconds after every request (`_smart_sleep`). KIS's per-second call limits are announced on the portal.
- The option board (`/futures-options/option-chain`) returns the previous result when the same request arrives within one second.
- Token issuance is limited to once per minute, hence the cache above.

### APIs used

Domestic stocks (`/uapi/domestic-stock/v1/...`)

| Function | Path | TR ID | Used by |
|----------|------|-------|---------|
| Current price | `quotations/inquire-price` | `FHKST01010100` | `/api/korean/quote/{symbol}`, valuation, basis |
| Daily prices (latest 30 daily/weekly/monthly candles) | `quotations/inquire-daily-price` | `FHKST01010400` | `/api/korean/candle/{symbol}` |
| Minute candles for a day | `quotations/inquire-time-dailychartprice` | `FHKST03010230` | `/api/korean/candle-minute/{symbol}` |
| Period prices | `quotations/inquire-daily-itemchartprice` | `FHKST03010100` | Basis history (spot daily close) |
| Current index | `quotations/inquire-index-price` | `FHPUP02100000` | Basis (index spot) |
| Index period prices | `quotations/inquire-daily-indexchartprice` | `FHKUP03500100` | Basis history (index) |
| Stock basic info | `quotations/search-stock-info` | `CTPF1002R` | `/api/korean/stock-info/{pdno}`, valuation |
| Estimate performance | `quotations/estimate-perform` | `HHKST668300C0` | `/api/korean/estimate-perform/{symbol}` |
| Stock balance | `trading/inquire-balance` | `TTTC8434R` | `/api/korean/account` |

Listed bonds (`/uapi/domestic-bond/v1/quotations/...`)

| Function | Path | TR ID | Used by |
|----------|------|-------|---------|
| Bond price | `inquire-price` | `FHKBJ773400C0` | `/api/korean/bonds/{pdno}/price`, yield analytics |
| Bond order book | `inquire-asking-price` | `FHKBJ773401C0` | Best bid/ask, yield analytics |
| Bond daily prices | `inquire-daily-price` | `FHKBJ773404C0` | `/api/korean/bonds/{pdno}/daily-price`, yield history |
| Bond basic info | `search-bond-info` | `CTPF1114R` | `/api/korean/bonds/{pdno}/info`, yield analytics |
| Bond issue info | `issue-info` | `CTPF1101R` | `/api/korean/bonds/{pdno}/issue` |
| Pricing-agency average unit price (민평) | `avg-unit` | `CTPF2005R` | Yield analytics and history |

Domestic futures/options (`/uapi/domestic-futureoption/v1/quotations/...`)

| Function | Path | TR ID | Used by |
|----------|------|-------|---------|
| Futures/options quote | `inquire-price` | `FHMIF10000000` | `/api/korean/futures-options/quote`, basis, option parity |
| Futures/options order book | `inquire-asking-price` | `FHMIF10010000` | `/api/korean/futures-options/orderbook`, basis, option parity |
| Minute candles | `inquire-time-fuopchartprice` | `FHKIF03020200` | `/api/korean/futures-options/minute-candles` |
| Period candles | `inquire-daily-fuopchartprice` | `FHKIF03020100` | `/api/korean/futures-options/daily-candles`, basis history |
| Option board (calls/puts) | `display-board-callput` | `FHPIF05030100` | `/api/korean/futures-options/option-chain` |

Backend endpoint parameters are listed in [API.md](API.md).

### Behaviour notes

- **Daily/weekly/monthly candles**: `inquire-daily-price` returns only the latest 30 candles. `start_date` and `end_date` filter within those 30. `adjust_price=true` (the default) requests adjusted prices (수정주가). For this API `FID_ORG_ADJ_PRC=1` means adjusted, whereas the period daily chart (`inquire-daily-itemchartprice`) uses `0` for adjusted.
- **Minute candles**: the client walks back in time up to 120 rows per call to collect one day, then keeps 09:00 up to the cut-off time (default 15:30). 5/10/30/60-minute candles are built from 1-minute candles.
- **Period daily prices (stocks, indices)**: ranges longer than one response (100 rows for stocks, 50 for indices) are fetched in several calls, moving the end date back each time.
- **Account balance**: only the first page is read; continuation is not implemented. Holdings beyond one page (50 stocks for a real account) may be missing.
- **Estimate performance**: amounts such as revenue and operating income are in 억원 (100 million KRW).

### Key check script

[`backend/scripts/check_hantu_keys.py`](../backend/scripts/check_hantu_keys.py) checks that the app keys in `.env` actually work.

```bash
cd backend
uv run python scripts/check_hantu_keys.py
```

- Reads `HANTU_API_KEY`/`HANTU_API_SECRET` from the repository-root `.env`, plus an optional second pair (`HANTU_API_KEY_2`/`HANTU_API_SECRET_2` or `HANTU_API_KEY2`/`HANTU_API_SECRET2`).
- For each key it issues a token on the real-trading server; if that fails it retries on the paper-trading server (`https://openapivts.koreainvestment.com:29443`) to tell you it is a paper-trading key. It then requests the current price of Samsung Electronics (005930).
- A token issued by the real-trading server is saved to the token cache, so the app reuses it right away.
- Only the first and last four characters of an app key are shown; secrets and tokens are never printed. The exit code is 0 when every key passes.
- Each run issues a new token, so running it again within a minute can hit the issuance limit.

### Troubleshooting

- **Token issuance fails**: check the app key and secret, and use the script to see whether it is a paper-trading key.
- **One-issuance-per-minute error**: wait a minute and try again. While a cached token exists, the app does not issue a new one.
- **Account page returns 500 (`HANTU_ACCOUNT_NUMBER ... is not configured correctly`)**: make sure the account number is exactly 8 digits.

### References

- [KIS Developers portal](https://apiportal.koreainvestment.com/): API specs, notices, sign-up
- [Official KIS sample code](https://github.com/koreainvestment/open-trading-api)
- [MASTER_FILES.md](MASTER_FILES.md): instrument master files
- [API.md](API.md): backend REST API
