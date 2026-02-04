# KDEVELOPERS API Integration Implementation

This document describes the enhanced implementation of the KDEVELOPERS (Korea Investment Securities) OpenAPI integration.

## Overview

The implementation is based on the official reference repository:
https://github.com/koreainvestment/open-trading-api

## Key Improvements

### 1. Structured API Response Handling

Implemented `APIResponse` class that mirrors the `APIResp` class from `kis_auth.py`:

```python
class APIResponse:
    """Structured API response wrapper."""
    
    def is_ok(self) -> bool:
        """Check if API call was successful."""
        return self.get_body().rt_cd == "0"
    
    def get_error_code(self) -> Optional[str]:
        """Get error code from response."""
    
    def get_error_message(self) -> Optional[str]:
        """Get error message from response."""
    
    def print_error(self, url: str):
        """Print formatted error message."""
```

### 2. Common API Request Wrapper

Implemented `_url_fetch` method following the pattern from `kis_auth.py`:

```python
def _url_fetch(
    self,
    api_url: str,
    tr_id: str,
    tr_cont: str,
    params: Dict[str, Any],
    post_flag: bool = False,
) -> APIResponse:
    """Common API request wrapper."""
```

This method:
- Handles authentication token management
- Sets proper headers (authorization, appkey, appsecret, tr_id, custtype)
- Applies rate limiting with smart_sleep
- Returns structured APIResponse objects

### 3. Enhanced Token Management

Improved token handling:
- 24-hour token validity check
- Automatic token refresh when expired
- Proper datetime parsing for token expiry
- Logging of authentication events

### 4. Better Error Handling

- Comprehensive logging throughout the code
- Structured error messages
- Exception handling with informative logs
- API response error printing

### 5. Rate Limiting

Implemented smart sleep mechanism:
- 0.05s delay for real trading
- Configurable sleep time
- Applied after each API call to prevent throttling

## API Methods

### get_quote(symbol: str)

Get real-time quote for a Korean stock.

**API:** [국내주식] 기본시세 > 주식현재가 시세[v1_국내주식-008]

**Transaction ID:** FHKST01010100

**Parameters:**
- `FID_COND_MRKT_DIV_CODE`: "J" (KRX market)
- `FID_INPUT_ISCD`: Stock code (e.g., "005930")

### get_daily_candle(symbol, period, adjust_price, limit)

Get daily/weekly/monthly candle data.

**API:** [국내주식] 기본시세 > 국내주식기간별시세(일/주/월/년)[v1_국내주식-016]

**Transaction ID:** FHKST01010400

**Parameters:**
- `FID_COND_MRKT_DIV_CODE`: "J" (KRX market)
- `FID_INPUT_ISCD`: Stock code
- `FID_PERIOD_DIV_CODE`: "D" (daily), "W" (weekly), "M" (monthly)
- `FID_ORG_ADJ_PRC`: "0" (adjusted) or "1" (unadjusted)

### get_minute_candle(symbol, interval, limit)

Get minute candle data.

**API:** [국내주식] 기본시세 > 국내주식분봉조회[v1_국내주식-024]

**Transaction ID:** FHKST03010200

**Parameters:**
- `FID_COND_MRKT_DIV_CODE`: "J" (KRX market)
- `FID_INPUT_ISCD`: Stock code
- `FID_INPUT_HOUR_1`: Time filter (empty for all)
- `FID_PW_DATA_INCU_YN`: "Y" (include previous data)
- `FID_TICK_RANGE`: Minute interval (1, 5, 10, 30, 60)

### get_account_balance(account_number, account_product_code)

Get account balance and positions.

**API:** [국내주식] 계좌/잔고 > 주식잔고조회[v1_국내주식-006]

**Transaction ID:** TTTC8434R (real) or VTTC8434R (paper trading)

**Parameters:**
- `CANO`: Account number (8 digits)
- `ACNT_PRDT_CD`: Account product code (default: "01")
- Various inquiry and filter parameters

## Usage Example

```python
from src.integrations.kdevelopers import kdevelopers_client

# Get real-time quote
quote = kdevelopers_client.get_quote("005930")  # Samsung Electronics
if quote:
    print(f"Price: {quote.current_price}")
    print(f"Change: {quote.change_percent}%")

# Get daily candles
candles = kdevelopers_client.get_daily_candle(
    symbol="005930",
    period="D",
    adjust_price=True,
    limit=10
)

# Get minute candles
minute_candles = kdevelopers_client.get_minute_candle(
    symbol="005930",
    interval=1,
    limit=30
)
```

See `examples/kdevelopers_example.py` for more detailed examples.

## Configuration

Required environment variables:
- `HANTU_API_KEY`: Your KIS Developers app key
- `HANTU_API_SECRET`: Your KIS Developers app secret
- `HANTU_BASE_URL`: API base URL
  - Real trading: `https://openapi.koreainvestment.com:9443`
  - Paper trading: `https://openapivts.koreainvestment.com:29443`

## Reference Implementation Mapping

| Reference File | Our Implementation | Description |
|---------------|-------------------|-------------|
| `kis_auth.py` | `kdevelopers.py` | Main API client |
| `kis_auth.APIResp` | `APIResponse` | Response wrapper |
| `kis_auth._url_fetch` | `_url_fetch` | API request method |
| `kis_auth.auth()` | `_get_access_token()` | Token management |
| `domestic_stock_functions.py` | Various methods | API endpoint implementations |

## Key Differences from Reference

1. **Simplified Configuration**: Uses environment variables instead of YAML config files
2. **No File-based Token Caching**: Tokens are cached in memory (can be enhanced if needed)
3. **Pydantic Models**: Uses type-safe Pydantic models for response data
4. **FastAPI Integration**: Designed to work with FastAPI backend

## Future Enhancements

Potential improvements based on the reference repository:

1. **File-based Token Caching**: Implement persistent token storage like in `kis_auth.py`
2. **WebSocket Support**: Add real-time data streaming support
3. **Order Management**: Add order placement and management APIs
4. **More Market Data APIs**: Implement additional APIs from the reference repository
5. **Mock Trading Support**: Add paper trading environment support

## Testing

To test the implementation:

```bash
cd backend
uv run python examples/kdevelopers_example.py
```

Make sure your API credentials are properly configured in the `.env` file.

## References

- Official API Documentation: https://apiportal.koreainvestment.com/
- Reference Repository: https://github.com/koreainvestment/open-trading-api
- API Portal: https://apiportal.koreainvestment.com/
