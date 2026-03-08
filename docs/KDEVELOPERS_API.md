# Korean Investment Securities API Integration

This document describes the KDevelopers (한국투자증권) OpenAPI integration for the Custom HTS backend.

## Overview

The integration provides access to real-time stock data, historical price data, and account information for Korean stocks using the Korean Investment Securities OpenAPI.

## API Documentation

Official API Portal: https://apiportal.koreainvestment.com/

## Market Master Files

### Stock Information Files (종목정보파일)
You can download stock master files for various Korean markets:

- **KOSPI (코스피)**: Download from [종목정보파일 페이지](https://apiportal.koreainvestment.com/apiservice-category)
- **KOSDAQ (코스닥)**: Download from [종목정보파일 페이지](https://apiportal.koreainvestment.com/apiservice-category)
- Python parsing sample code: [GitHub Repository](https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info)

Note: These master files (.mst) contain stock codes, names, and other metadata. You can rename .mst to .txt to view as plain text.

## Implemented Features

### 1. Stock Price and Quote Data

#### Get Current Stock Price
- **KIS API Endpoint**: `/uapi/domestic-stock/v1/quotations/inquire-price`
- **Backend Endpoint**: `GET /api/korean/quote/{symbol}`
- **Method**: GET
- **Transaction ID**: `FHKST01010100` (both real and mock)
- **Description**: Get current stock price and detailed market information
- **Example**: `/api/korean/quote/005930` (Samsung Electronics)
- **Required Parameters**:
  - `FID_COND_MRKT_DIV_CODE`: Market division code (J: KRX, NX: NXT, UN: Unified)
  - `FID_INPUT_ISCD`: Stock code (e.g., 005930 for Samsung Electronics)
  
**Important Note**: For real-time data, use WebSocket API. This REST API provides snapshot data.

### 2. Historical Daily Price Data (OHLCV)

#### Get Historical Daily/Weekly/Monthly Candle Data
- **KIS API Endpoint**: `/uapi/domestic-stock/v1/quotations/inquire-daily-price`
- **Backend Endpoint**: `GET /api/korean/candle/{symbol}`
- **Method**: GET
- **Transaction ID**: `FHKST01010400` (both real and mock)
- **Description**: Get historical OHLCV (Open, High, Low, Close, Volume) data
- **Limit**: Maximum 30 days/weeks/months of data
- **Parameters**:
  - `FID_COND_MRKT_DIV_CODE`: Market division code (J: KRX, NX: NXT, UN: Unified)
  - `FID_INPUT_ISCD`: Stock code (e.g., 005930)
  - `FID_PERIOD_DIV_CODE`: Period type
    - `D`: Daily (최근 30거래일)
    - `W`: Weekly (최근 30주)
    - `M`: Monthly (최근 30개월)
  - `FID_ORG_ADJ_PRC`: Price adjustment
    - `0`: Unadjusted price
    - `1`: Adjusted for splits/mergers
- **Example**: `/api/korean/candle/005930?period=D&limit=30`
- **Response**: Array of candle data with date, open, high, low, close, volume

### 3. Account Balance and Positions

#### Get Account Balance
- **KIS API Endpoint**: `/uapi/domestic-stock/v1/trading/inquire-balance`
- **Backend Endpoint**: `GET /api/korean/account`
- **Method**: GET
- **Transaction ID**:
  - Real: `TTTC8434R`
  - Mock: `VTTC8434R`
- **Description**: Query stock account balance and holdings
- **Important**: This API is slow due to comprehensive data. For simple order preparation, use buy/sell quantity inquiry APIs instead.
- **Pagination**:
  - Real account: Max 50 items per call
  - Mock account: Max 20 items per call
  - Use continuation query for additional items
- **Parameters**:
  - `CANO`: Account number (first 8 digits)
  - `ACNT_PRDT_CD`: Account product code (last 2 digits)
  - `AFHR_FLPR_YN`: After-hours/Exchange flag
    - `N`: Default
    - `Y`: After-hours single price
    - `X`: NXT regular market
  - `INQR_DVSN`: Inquiry type
    - `01`: By loan date
    - `02`: By stock
  - `UNPR_DVSN`: Unit price type (`01`: Default)
  - `FUND_STTL_ICLD_YN`: Include fund settlement (`N`/`Y`)
  - `FNCG_AMT_AUTO_RDPT_YN`: Auto loan repayment (`N`: Default)
  - `PRCS_DVSN`: Process type
    - `00`: Include previous day trades
    - `01`: Exclude previous day trades
- **Example**: `curl "http://localhost:8000/api/korean/account?account_product_code=01"`
- **Response**: Account balance information and list of stock positions

### 4. Domestic Futures/Options Period Candles (Daily/Weekly/Monthly/Yearly)

#### Get Domestic Futures/Options Period Candle Data
- **KIS API Endpoint**: `/uapi/domestic-futureoption/v1/quotations/inquire-daily-fuopchartprice`
- **Backend Endpoint**: `GET /api/korean/futures-options/daily-candles`
- **Method**: GET
- **Transaction ID**: `FHKIF03020100` (real/mock)
- **Description**: Fetch futures/options candles for period `D/W/M/Y`
- **Per-call limit**: KIS returns up to 100 rows per call
- **Key Parameters**:
  - `FID_COND_MRKT_DIV_CODE` (`market_div_code`): `F`, `O`, `JF`, `JO`, `CF`, `CM`, `EU`
  - `FID_INPUT_ISCD` (`symbol`): instrument code
  - `FID_INPUT_DATE_1` (`start_date`): range start (`YYYYMMDD`)
  - `FID_INPUT_DATE_2` (`end_date`): range end (`YYYYMMDD`)
  - `FID_PERIOD_DIV_CODE` (`period`): `D`, `W`, `M`, `Y`
- **Important**:
  - `FID_INPUT_DATE_1` and `FID_INPUT_DATE_2` must both be valid `YYYYMMDD`
  - `start_date <= end_date`
  - Use repeated calls with adjusted date windows for ranges larger than one call can return


**Response Structure**:
```json
{
  "output1": [
    {
      "pdno": "005930",
      "prdt_name": "삼성전자",
      "hldg_qty": "100",
      "pchs_avg_pric": "70000.00",
      "prpr": "72000",
      "evlu_amt": "7200000",
      "evlu_pfls_amt": "200000",
      "evlu_pfls_rt": "2.86"
    }
  ],
  "output2": [
    {
      "dnca_tot_amt": "20000000",
      "tot_evlu_amt": "100000000",
      "nass_amt": "100000000",
      "pchs_amt_smtl_amt": "80000000",
      "evlu_amt_smtl_amt": "85000000",
      "evlu_pfls_smtl_amt": "5000000"
    }
  ]
}
```

## Authentication

The API uses OAuth2 authentication with app key and app secret credentials. Authentication tokens are automatically managed by the client and cached for subsequent requests.

### Required Environment Variables

```bash
HANTU_API_KEY=your_app_key_here
HANTU_API_SECRET=your_app_secret_here
```

## API Implementation Details

### Base URL

- **Production**: `https://openapi.koreainvestment.com:9443`
- **Mock Trading**: `https://openapivts.koreainvestment.com:29443`

### Common Headers

All API requests require the following headers:

- `content-type`: `application/json; charset=utf-8`
- `authorization`: Access token from OAuth2
- `appkey`: Your application key
- `appsecret`: Your application secret
- `tr_id`: Transaction ID (varies by endpoint)
- `custtype`: Customer type (`P`: Personal, `B`: Corporate)

### Transaction IDs (tr_id)

Different API endpoints require different transaction IDs:

- **Current Stock Price**: `FHKST01010100`
- **Historical Daily Price**: `FHKST01010400`
- **Account Balance (Real)**: `TTTC8434R`
- **Account Balance (Mock)**: `VTTC8434R`

### Market Division Codes

- `J`: KRX (Korean Exchange)
- `NX`: NXT (Next market)
- `UN`: Unified (통합)

## Data Models

### KoreanStockQuote
Represents current stock quote data:
- `symbol`: Stock code (e.g., "005930")
- `stck_prpr`: Current stock price
- `prdy_vrss`: Change from previous day
- `prdy_vrss_sign`: Change sign (1: up, 2: unchanged, 3/4/5: down)
- `prdy_ctrt`: Change percentage from previous day
- `acml_vol`: Accumulated volume
- `acml_tr_pbmn`: Accumulated trading amount
- `stck_oprc`: Opening price
- `stck_hgpr`: High price
- `stck_lwpr`: Low price

### KoreanCandleData
Represents OHLCV (Open, High, Low, Close, Volume) candle data:
- `symbol`: Stock code (e.g., "005930")
- `stck_bsop_date`: Trading date (YYYYMMDD format)
- `stck_oprc`: Opening price
- `stck_hgpr`: High price
- `stck_lwpr`: Low price
- `stck_clpr`: Closing price
- `acml_vol`: Accumulated volume
- `prdy_vrss`: Change from previous day
- `prdy_vrss_sign`: Change sign
- `prdy_ctrt`: Change percentage

### KoreanAccountBalance
Represents account balance information:
- `dnca_tot_amt`: Total deposit amount
- `tot_evlu_amt`: Total evaluation amount
- `nass_amt`: Net asset amount
- `pchs_amt_smtl_amt`: Total purchase amount
- `evlu_amt_smtl_amt`: Total evaluation amount
- `evlu_pfls_smtl_amt`: Total profit/loss amount

### KoreanStockPosition
Represents individual stock position:
- `pdno`: Stock code
- `prdt_name`: Product name (Korean)
- `hldg_qty`: Holding quantity
- `pchs_avg_pric`: Average purchase price
- `prpr`: Current price
- `evlu_amt`: Evaluation amount
- `evlu_pfls_amt`: Profit/loss amount
- `evlu_pfls_rt`: Profit/loss ratio

## Usage Examples

### Python Client Example

```python
from src.integrations.kdevelopers import kdevelopers_client

# Get current stock quote
quote = kdevelopers_client.get_quote("005930")
print(f"Current price: {quote.stck_prpr} KRW")

# Get daily candle data (last 30 days)
candles = kdevelopers_client.get_daily_candle("005930", period="D", adjust_price=True)
for candle in candles:
    print(f"Date: {candle.stck_bsop_date}, Close: {candle.stck_clpr} KRW")

# Get account balance
account_data = kdevelopers_client.get_account_balance("12345678", "01")
positions = account_data["output1"]
balance = account_data["output2"][0]
print(f"Total evaluation: {balance.tot_evlu_amt} KRW")
for position in positions:
    print(f"{position.prdt_name}: {position.hldg_qty} shares")
```

### HTTP API Example

```bash
# Get stock quote
curl -X GET "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price?FID_COND_MRKT_DIV_CODE=J&FID_INPUT_ISCD=005930" \
  -H "content-type: application/json" \
  -H "authorization: Bearer YOUR_TOKEN" \
  -H "appkey: YOUR_APP_KEY" \
  -H "appsecret: YOUR_APP_SECRET" \
  -H "tr_id: FHKST01010100" \
  -H "custtype: P"

# Get daily candles
curl -X GET "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-daily-price?FID_COND_MRKT_DIV_CODE=J&FID_INPUT_ISCD=005930&FID_PERIOD_DIV_CODE=D&FID_ORG_ADJ_PRC=1" \
  -H "content-type: application/json" \
  -H "authorization: Bearer YOUR_TOKEN" \
  -H "appkey: YOUR_APP_KEY" \
  -H "appsecret: YOUR_APP_SECRET" \
  -H "tr_id: FHKST01010400" \
  -H "custtype: P"

# Get account balance
curl -X GET "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/trading/inquire-balance?CANO=12345678&ACNT_PRDT_CD=01&AFHR_FLPR_YN=N&INQR_DVSN=02&UNPR_DVSN=01&FUND_STTL_ICLD_YN=N&FNCG_AMT_AUTO_RDPT_YN=N&PRCS_DVSN=00" \
  -H "content-type: application/json" \
  -H "authorization: Bearer YOUR_TOKEN" \
  -H "appkey: YOUR_APP_KEY" \
  -H "appsecret: YOUR_APP_SECRET" \
  -H "tr_id: TTTC8434R" \
  -H "custtype: P"
```


## Error Handling

The API includes comprehensive error handling:
- Returns proper error codes and messages
- Logs errors for debugging
- Returns HTTP 404 if data not found
- Validates input parameters
- Handles authentication failures

### Common Error Codes

- `rt_cd = "0"`: Success
- `rt_cd != "0"`: Failure (check `msg_cd` and `msg1` for details)

## Rate Limiting

Be aware of KIS API rate limits:
- Implement proper throttling for production use
- Cache frequently accessed data where appropriate
- Use appropriate intervals for data updates
- Monitor API usage to avoid exceeding limits

## Important Notes

1. **Stock Codes**: Korean stock codes are 6-digit numbers (e.g., "005930" for Samsung Electronics)
2. **Master Files**: Download master files for complete stock lists from [종목정보파일](https://apiportal.koreainvestment.com/apiservice-category)
3. **Real-time Data**: For true real-time streaming, use WebSocket API instead of REST API
4. **Account Balance**: The balance API is comprehensive but slow. Use specific buy/sell inquiry APIs for faster order preparation
5. **Continuation Queries**: Use `CTX_AREA_FK100` and `CTX_AREA_NK100` for paginated results when more than 50 (real) or 20 (mock) items exist
6. **Price Adjustment**: Always consider whether to use adjusted prices (`FID_ORG_ADJ_PRC=1`) for historical analysis

## Testing

Run tests with:
```bash
cd backend
uv run pytest tests/test_korean_models.py -v
```

## References

- [KIS Developers Portal](https://apiportal.koreainvestment.com/intro)
- [Official GitHub Samples](https://github.com/koreainvestment/open-trading-api)
- [API Documentation](https://apiportal.koreainvestment.com/apiservice)
- [Stock Master Files](https://apiportal.koreainvestment.com/apiservice-category)
- [Current Stock Price API](https://apiportal.koreainvestment.com/apiservice-apiservice?/uapi/domestic-stock/v1/quotations/inquire-price)
- [Historical Daily Price API](https://apiportal.koreainvestment.com/apiservice-apiservice?/uapi/domestic-stock/v1/quotations/inquire-daily-price)
- [Account Balance API](https://apiportal.koreainvestment.com/apiservice-apiservice?/uapi/domestic-stock/v1/trading/inquire-balance)
