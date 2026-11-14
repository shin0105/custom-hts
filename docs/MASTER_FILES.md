# 마스터 파일 · Master Files

[한국어](#한국어) · [English](#english)

---

## 한국어

### 개요

마스터 파일은 한국투자증권(KIS)이 매일 배포하는 종목 목록 파일로, 종목코드·종목명·분류 같은 기본 정보를 담고 있습니다. 이 앱은 다음 용도로 씁니다.

- **주식**: 국내주식 화면의 종목명·코드 검색
- **장내채권**: 장내채권 화면의 채권 목록과 유형·날짜 필터
- **선물옵션**: 선물옵션 화면의 종목 검색, 베이시스·옵션 패리티 계산에 쓰는 월물 목록

파일은 `https://new.real.download.dws.co.kr/common/master/<파일명>.mst.zip`에서 인증키 없이 내려받습니다. ZIP을 풀어 `.mst`를 남기고 ZIP은 지웁니다. 텍스트 인코딩은 cp949입니다. 파싱 방식은 [KIS 공식 샘플](https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info)을 따릅니다.

| 구분 | 코드 | 저장 위치 | 원본 파일 | 갱신 시점 |
|------|------|-----------|-----------|-----------|
| 주식 | [`stock_master.py`](../backend/src/integrations/stock_master.py) | `backend/src/data/kr_stock_master/` | `kospi_code.mst`, `kosdaq_code.mst`, `konex_code.mst` | 파일이 없을 때 조회하면 자동으로 받음 |
| 장내채권 | [`bond_master.py`](../backend/src/integrations/bond_master.py) | `backend/data/kr_bond_master/` | `bond_code.mst` | refresh 엔드포인트를 호출할 때만 |
| 선물옵션 | [`futures_options_master.py`](../backend/src/integrations/futures_options_master.py) | `backend/data/kr_futures_options_master/` | `fo_idx_code_mts.mst`(지수), `fo_stk_code_mts.mst`(주식), `fo_com_code.mst`(상품) | 조회할 때 파일이 없거나 오늘(KST) 이전 것이면 자동으로 다시 받음 |

### Git에 포함되는 파일

- 내려받은 `.mst`와 내보낸 `.csv`는 `.gitignore`(`*.mst`, `*.csv`)에 걸려 커밋되지 않습니다. 실행 중이나 refresh 때 새로 받습니다.
- 예외로 `backend/data/kr_bond_master/bond_codes.json`(채권 마스터를 JSON으로 내보낸 스냅샷)은 커밋되어 있습니다. 채권 refresh를 `output_format=json`으로 실행하면 이 파일이 바뀝니다.
- 선물옵션 refresh를 `output_format=json`으로 실행해 생기는 `*_fo_master.json`은 무시 대상이 아니니 커밋하지 마세요.

### 주식 마스터

`GET /api/korean/stocks/master`

| 파라미터 | 설명 |
|----------|------|
| `query` | 6자리 종목코드 또는 한글 종목명 일부 |
| `market` | `all`(기본), `kospi`, `kosdaq`, `konex` |
| `offset`, `limit` | 페이지 (`limit` 기본 20, 최대 500) |
| `auto_download` | 파일이 없으면 내려받기 (기본 `true`) |
| `force_download` | 다시 내려받아 다시 파싱 (기본 `false`) |

- 처음 조회할 때 없는 파일을 받아 파싱하고, 정리한 행을 시장별로 6시간 동안 메모리에 둡니다.
- 파일이 오래되어도 자동으로 다시 받지는 않습니다. 신규 상장 종목을 반영하려면 `force_download=true`로 한 번 조회하세요. 주식 마스터에는 별도 refresh 엔드포인트가 없습니다.
- 검색 순위: 코드 일치 → 이름 일치 → 코드 앞부분 일치 → 이름 앞부분 일치 → 이름 포함. 같은 순위에서는 시가총액이 큰 종목이 먼저 나옵니다.
- 응답 항목: `market`, `symbol`, `standard_code`, `name`, `security_group_code`, `market_cap_100m`(억원), `listing_date`

```bash
curl -G "http://localhost:8000/api/korean/stocks/master" --data-urlencode "query=삼성전자" -d limit=5
curl "http://localhost:8000/api/korean/stocks/master?query=005930&force_download=true"
```

파이썬에서 직접 쓸 수도 있습니다. 사용 예시는 [`backend/examples/stock_master_example.py`](../backend/examples/stock_master_example.py)에 있습니다.

```python
from src.integrations.stock_master import master_file_manager

master_file_manager.download_all_markets(force=True)
df = master_file_manager.parse_kospi_master()
info = master_file_manager.get_stock_info("kospi", "005930")
rows = master_file_manager.search_stocks("삼성")
master_file_manager.save_to_csv("kospi")
```

`save_to_csv`는 `kospi_stk_master.csv`(코드·이름·그룹코드)와 `kospi_stk_master_full.csv`(전체 열)를 저장 위치에 씁니다.

### 장내채권 마스터

`GET /api/korean/bonds/master`

| 파라미터 | 설명 |
|----------|------|
| `query` | 채권코드 또는 채권명 일부 |
| `type` | 채권 유형 (`A0` 장내소매채권, `F9` 주식관련사채·소액채권, `C0` 국고채권) |
| `bond_class_code`, `bond_interest_class_code` | 분류코드, 이자유형코드 |
| `listed_date_from/to`, `issue_date_from/to`, `maturity_date_from/to` | 상장일·발행일·만기일 범위 (YYYYMMDD) |
| `offset`, `limit` | 페이지 (`limit` 기본 20, 최대 500) |
| `enrich` | 행마다 장내채권 기본조회(`CTPF1114R`)를 호출해 이름·표면금리 등을 보강 (기본 `false`) |
| `include_quotes` | 행마다 현재가를 함께 조회 (기본 `false`) |

- 이 엔드포인트는 내려받지 않고 저장 위치의 파일만 읽습니다. `bond_code.mst` → `bond_codes.csv` → 그 밖의 `*bond*code*` 파일 순으로 찾습니다.
- `bond_code.mst`에서 읽는 필드: `bond_type`, `bond_class_code`, `pdno`(KR로 시작하는 12자리 표준코드), `name`, `bond_interest_class_code`, `listed_date`, `issue_date`, `maturity_date`
- 응답에는 필터 선택지에 쓰는 `available_bond_types`와 유형별 분류코드·이자유형코드 건수도 들어 있습니다.

`POST /api/korean/bonds/master/refresh`는 로컬 마스터가 없거나 `force=true`일 때 `bond_code.mst`를 받고, 파싱 결과를 `bond_codes.csv`(기본) 또는 `bond_codes.json`(`output_format=json`)으로 씁니다. `source_url`로 다운로드 주소를 바꿀 수 있습니다.

처음 클론한 뒤에는 `force=true`로 한 번 실행해 `bond_code.mst`를 받으세요. 이 파일이 있어야 채권명·유형·날짜 필터가 제대로 동작하며, 커밋된 `bond_codes.json`만으로는 부족합니다.

```bash
curl -X POST "http://localhost:8000/api/korean/bonds/master/refresh?force=true"
curl "http://localhost:8000/api/korean/bonds/master?type=C0&limit=10"
```

### 선물옵션 마스터

`GET /api/korean/futures-options/master`

| 파라미터 | 설명 |
|----------|------|
| `market` | `all`(기본), `index`, `stock`, `commodity` |
| `query` | 단축코드·표준코드·종목명·기초자산명 일부 |
| `info_type`, `underlying_short_code` | 정보 구분, 기초자산 단축코드 |
| `offset`, `limit` | 페이지 (`limit` 기본 100, 최대 2000) |
| `auto_download`, `force_download` | 파일이 없을 때 받기, 다시 받기 (기본 모두 `false`) |

- 상장 월물이 매일 바뀌므로, 조회할 때마다 시장별 파일이 없거나 오늘(KST) 이전에 받은 것이면 먼저 다시 받습니다. 실패하면 기존 파일을 계속 쓰고 10분 뒤에 다시 시도합니다. 베이시스 화면도 같은 방식으로 최신 파일을 확인합니다.
- 행 필드: `info_type`, `short_code`, `standard_code`, `name_kr`, `atm_class_code`, `strike_price`, `month_class_code`, `underlying_short_code`, `underlying_name_kr`(상품 파일은 `commodity_type` 추가). 지수·주식 파일은 `|` 구분, 상품 파일은 고정 폭입니다.

`POST /api/korean/futures-options/master/refresh`(`market`, `output_format`=`csv`|`json`, `force`)는 파일을 받고 `<시장>_fo_master.csv` 또는 `.json`으로 내보냅니다.

```bash
curl "http://localhost:8000/api/korean/futures-options/master?market=index&limit=20"
curl -X POST "http://localhost:8000/api/korean/futures-options/master/refresh?market=all&force=true"
```

### 파일 형식 참고

- **주식**: 한 줄이 한 종목입니다. 앞부분은 단축코드(9) + 표준코드(12) + 한글 종목명(가변 길이)이고, 뒷부분은 고정 폭(KOSPI 228자, KOSDAQ 222자, KONEX 184자)입니다. 뒷부분에는 증권그룹구분, 시가총액 규모, 지수 편입 여부, 기준가, 거래정지·관리종목 여부, 상장일자, 상장주수, 매출액·영업이익·ROE 등 수십 개 필드가 있습니다. 필드 정의는 KIS 샘플의 헤더 파일을 보세요.
- **장내채권**: 고정 폭입니다. 앞부분은 유형(2) + 분류코드(2) + 표준코드(12) + 채권명이고, 마지막 26자는 이자유형(2) + 상장일·발행일·만기일(각 8)입니다.

### 문제 해결

- **한글이 깨짐**: 파일은 cp949로 읽어야 합니다.
- **새 종목이 보이지 않음**: 주식은 `force_download=true`, 장내채권은 `refresh?force=true`로 다시 받으세요.
- **내려받기 실패**: 백엔드 로그에서 다운로드 URL과 오류를 확인하세요. 기존 파일이 있으면 그대로 쓰입니다.

### 참고

- [KIS 공식 샘플 코드 (stocks_info)](https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info): 마스터 파일 구조와 파싱 예제
- [KDEVELOPERS_API.md](KDEVELOPERS_API.md): KIS Open API 연동
- [API.md](API.md): 백엔드 REST API

---

## English

### Overview

Master files are instrument lists that Korea Investment & Securities (KIS) publishes daily, with codes, names and classifications. The app uses them for:

- **Stocks**: name/code search on the domestic stock page
- **Listed bonds**: the bond list and its type/date filters on the bond page
- **Futures/options**: instrument search on the futures/options page, and the contract lists behind the basis and option parity calculations

Files are downloaded without an API key from `https://new.real.download.dws.co.kr/common/master/<file>.mst.zip`. The ZIP is extracted to an `.mst` file and then deleted. Text is encoded in cp949. Parsing follows the [official KIS samples](https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info).

| Kind | Code | Location | Source files | When refreshed |
|------|------|----------|--------------|----------------|
| Stocks | [`stock_master.py`](../backend/src/integrations/stock_master.py) | `backend/src/data/kr_stock_master/` | `kospi_code.mst`, `kosdaq_code.mst`, `konex_code.mst` | Downloaded automatically when a lookup finds no file |
| Listed bonds | [`bond_master.py`](../backend/src/integrations/bond_master.py) | `backend/data/kr_bond_master/` | `bond_code.mst` | Only when the refresh endpoint is called |
| Futures/options | [`futures_options_master.py`](../backend/src/integrations/futures_options_master.py) | `backend/data/kr_futures_options_master/` | `fo_idx_code_mts.mst` (index), `fo_stk_code_mts.mst` (stock), `fo_com_code.mst` (commodity) | Re-downloaded on lookup when missing or older than today (KST) |

### What is in git

- Downloaded `.mst` files and exported `.csv` files match `.gitignore` (`*.mst`, `*.csv`) and are not committed. They are fetched at runtime or on refresh.
- The exception is `backend/data/kr_bond_master/bond_codes.json`, a committed JSON export of the bond master. Running the bond refresh with `output_format=json` overwrites it.
- The `*_fo_master.json` files written by the futures/options refresh with `output_format=json` are not ignored; do not commit them.

### Stock master

`GET /api/korean/stocks/master`

| Parameter | Description |
|-----------|-------------|
| `query` | 6-digit stock code or part of the Korean name |
| `market` | `all` (default), `kospi`, `kosdaq`, `konex` |
| `offset`, `limit` | Paging (`limit` default 20, max 500) |
| `auto_download` | Download missing files (default `true`) |
| `force_download` | Re-download and re-parse (default `false`) |

- The first lookup downloads and parses any missing file, then keeps the normalised rows in memory per market for 6 hours.
- An old file is not re-downloaded automatically. To pick up new listings, call once with `force_download=true`. The stock master has no separate refresh endpoint.
- Ranking: exact code → exact name → code prefix → name prefix → name contains. Within a rank, larger market caps come first.
- Response fields: `market`, `symbol`, `standard_code`, `name`, `security_group_code`, `market_cap_100m` (100 million KRW), `listing_date`

```bash
curl -G "http://localhost:8000/api/korean/stocks/master" --data-urlencode "query=삼성전자" -d limit=5
curl "http://localhost:8000/api/korean/stocks/master?query=005930&force_download=true"
```

You can also call it from Python. See [`backend/examples/stock_master_example.py`](../backend/examples/stock_master_example.py) for a worked example.

```python
from src.integrations.stock_master import master_file_manager

master_file_manager.download_all_markets(force=True)
df = master_file_manager.parse_kospi_master()
info = master_file_manager.get_stock_info("kospi", "005930")
rows = master_file_manager.search_stocks("삼성")
master_file_manager.save_to_csv("kospi")
```

`save_to_csv` writes `kospi_stk_master.csv` (code, name, group code) and `kospi_stk_master_full.csv` (all columns) to the master folder.

### Listed bond master

`GET /api/korean/bonds/master`

| Parameter | Description |
|-----------|-------------|
| `query` | Part of the bond code or name |
| `type` | Bond type (`A0` retail bonds, `F9` equity-linked/small-lot bonds, `C0` treasury bonds) |
| `bond_class_code`, `bond_interest_class_code` | Class code, interest type code |
| `listed_date_from/to`, `issue_date_from/to`, `maturity_date_from/to` | Listing, issue and maturity date ranges (YYYYMMDD) |
| `offset`, `limit` | Paging (`limit` default 20, max 500) |
| `enrich` | Call bond basic info (`CTPF1114R`) per row to add name, coupon and more (default `false`) |
| `include_quotes` | Fetch the current price per row (default `false`) |

- This endpoint never downloads; it reads files in the master folder in the order `bond_code.mst` → `bond_codes.csv` → any other `*bond*code*` file.
- Fields read from `bond_code.mst`: `bond_type`, `bond_class_code`, `pdno` (12-character standard code starting with KR), `name`, `bond_interest_class_code`, `listed_date`, `issue_date`, `maturity_date`
- The response also carries `available_bond_types` and per-type counts of class and interest codes for the filter drop-downs.

`POST /api/korean/bonds/master/refresh` downloads `bond_code.mst` when no local master exists or `force=true`, then writes the parsed rows to `bond_codes.csv` (default) or `bond_codes.json` (`output_format=json`). `source_url` overrides the download URL.

After a fresh clone, run it once with `force=true` to get `bond_code.mst`. Bond names, types and date filters only work properly with that file; the committed `bond_codes.json` alone is not enough.

```bash
curl -X POST "http://localhost:8000/api/korean/bonds/master/refresh?force=true"
curl "http://localhost:8000/api/korean/bonds/master?type=C0&limit=10"
```

### Futures/options master

`GET /api/korean/futures-options/master`

| Parameter | Description |
|-----------|-------------|
| `market` | `all` (default), `index`, `stock`, `commodity` |
| `query` | Part of the short code, standard code, name or underlying name |
| `info_type`, `underlying_short_code` | Info type, underlying short code |
| `offset`, `limit` | Paging (`limit` default 100, max 2000) |
| `auto_download`, `force_download` | Download when missing, re-download (both default `false`) |

- Listed contract months change daily, so every lookup first re-downloads a market's file when it is missing or was fetched before today (KST). If that fails, the old file keeps being used and the download is retried after 10 minutes. The basis page checks for a fresh file the same way.
- Row fields: `info_type`, `short_code`, `standard_code`, `name_kr`, `atm_class_code`, `strike_price`, `month_class_code`, `underlying_short_code`, `underlying_name_kr` (plus `commodity_type` in the commodity file). The index and stock files are `|`-delimited; the commodity file is fixed-width.

`POST /api/korean/futures-options/master/refresh` (`market`, `output_format`=`csv`|`json`, `force`) downloads the files and exports them as `<market>_fo_master.csv` or `.json`.

```bash
curl "http://localhost:8000/api/korean/futures-options/master?market=index&limit=20"
curl -X POST "http://localhost:8000/api/korean/futures-options/master/refresh?market=all&force=true"
```

### File format notes

- **Stocks**: one line per stock. The front part is short code (9) + standard code (12) + Korean name (variable length); the tail is fixed-width (228 characters for KOSPI, 222 for KOSDAQ, 184 for KONEX). The tail holds dozens of fields such as security group, market-cap tier, index membership flags, base price, trading-halt and administrative-issue flags, listing date, listed shares, and revenue, operating profit and ROE. See the header files in the KIS samples for definitions.
- **Listed bonds**: fixed-width. The front part is type (2) + class code (2) + standard code (12) + name; the last 26 characters are interest type (2) + listing, issue and maturity dates (8 each).

### Troubleshooting

- **Garbled Korean text**: read the files as cp949.
- **New instruments missing**: re-download with `force_download=true` for stocks or `refresh?force=true` for bonds.
- **Download fails**: check the backend log for the URL and error. An existing file keeps being used.

### References

- [Official KIS samples (stocks_info)](https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info): master file layouts and parsing examples
- [KDEVELOPERS_API.md](KDEVELOPERS_API.md): KIS Open API integration
- [API.md](API.md): backend REST API
