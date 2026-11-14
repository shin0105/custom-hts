# 백엔드 예제 · Backend Examples

[한국어](#한국어) · [English](#english)

---

## 한국어

백엔드 모듈을 HTTP 서버 없이 직접 호출하는 예제 스크립트입니다. 모두 실제 외부 서비스에 요청을 보내며, 키는 저장소 루트의 `.env`에서 읽습니다. 설정 방법은 [설치 가이드](../../docs/SETUP.md)를 참고하세요.

### 실행

`backend/`에서 실행합니다.

```bash
cd backend
uv run python examples/korean_api_example.py
uv run python examples/kdevelopers_example.py
uv run python examples/stock_master_example.py
```

### 예제 목록

| 파일 | 필요한 키 | 내용 |
|------|-----------|------|
| `korean_api_example.py` | `HANTU_API_KEY`, `HANTU_API_SECRET` | 서비스 계층(`korean_market_service`)으로 삼성전자(005930)의 현재가, 최근 일봉 5개, 당일 5분봉 5개를 조회합니다. 계좌 잔고는 조회하지 않고 안내 문구만 출력합니다. |
| `kdevelopers_example.py` | `HANTU_API_KEY`, `HANTU_API_SECRET` | KIS 클라이언트(`kdevelopers_client`)를 직접 써서 삼성전자의 현재가, 일봉, 1분봉을 조회합니다. |
| `stock_master_example.py` | 없음 | KIS 서버에서 코스피·코스닥·코넥스 종목 마스터 파일을 내려받아 pandas DataFrame으로 읽고, 종목 정보 조회와 이름 검색(`삼성`)을 보여 줍니다. |

### 참고

- KIS 예제는 앱과 같은 접근 토큰 캐시(`backend/.cache/kis_tokens.json`)를 씁니다. 토큰 발급은 앱키당 1분에 1회로 제한됩니다.
- 분봉은 당일 데이터를 조회하므로 장 시작 전이나 휴장일에는 비어 있을 수 있습니다.
- 가격 단위는 원(KRW)입니다.
- `stock_master_example.py`의 엑셀 내보내기 단계는 `openpyxl`이 필요합니다. 기본 의존성에 없으므로 설치하지 않으면 이 단계만 실패하고 나머지는 계속 실행됩니다.
- 종목 마스터 파일에 대한 자세한 내용은 [마스터 파일 가이드](../../docs/MASTER_FILES.md)를 참고하세요.

### 예제 추가하기

- `backend/examples/`에 파일을 만들고 맨 위 docstring에 목적과 실행 방법을 적은 뒤, 이 README의 표에 추가합니다.
- 키와 계좌번호는 `.env`에서 읽고 코드에 직접 쓰지 않습니다. 예제가 만든 결과 파일은 커밋하지 않습니다.

---

## English

Example scripts that call backend modules directly, without the HTTP server. All of them send real requests to external services and read keys from `.env` at the repository root. See the [setup guide](../../docs/SETUP.md) for configuration.

### Running

Run them from `backend/`.

```bash
cd backend
uv run python examples/korean_api_example.py
uv run python examples/kdevelopers_example.py
uv run python examples/stock_master_example.py
```

### Examples

| File | Keys needed | What it does |
|------|-------------|--------------|
| `korean_api_example.py` | `HANTU_API_KEY`, `HANTU_API_SECRET` | Uses the service layer (`korean_market_service`) to fetch the current price, the last 5 daily candles and 5 of today's 5-minute candles for Samsung Electronics (005930). It does not query the account balance; it only prints a note. |
| `kdevelopers_example.py` | `HANTU_API_KEY`, `HANTU_API_SECRET` | Uses the KIS client (`kdevelopers_client`) directly to fetch Samsung Electronics' current price, daily candles and 1-minute candles. |
| `stock_master_example.py` | None | Downloads the KOSPI, KOSDAQ and KONEX stock master files from the KIS server, loads them into pandas DataFrames, and shows a stock lookup and a name search (`삼성`). |

### Notes

- The KIS examples share the app's access-token cache (`backend/.cache/kis_tokens.json`). Each App Key can issue only one token per minute.
- Minute candles are for the current day, so they can be empty before the market opens or on holidays.
- Prices are in Korean won (KRW).
- The Excel export step in `stock_master_example.py` needs `openpyxl`, which is not a default dependency. Without it, only that step fails and the rest keeps running.
- For details on the stock master files, see the [master files guide](../../docs/MASTER_FILES.md).

### Adding an example

- Create a file in `backend/examples/`, describe its purpose and how to run it in the top docstring, and add it to the table in this README.
- Read keys and account numbers from `.env`; never hard-code them. Do not commit files that an example produces.
