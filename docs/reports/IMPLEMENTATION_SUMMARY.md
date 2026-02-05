# KDevelopers API Implementation Summary

## Overview

Successfully implemented comprehensive integration with Korean Investment Securities (한국투자증권) OpenAPI (KDevelopers) for the Custom HTS backend. The implementation provides access to real-time stock data, candle charts, and account information for Korean stocks.

## Implemented Features

### 1. Stock Price Data
- **Real-time Quotes**: Current price, volume, high/low, changes
- **Transaction ID**: FHKST01010100
- **Endpoint**: `GET /api/korean/quote/{symbol}`

### 2. Candle Chart Data (OHLCV)

#### Daily/Weekly/Monthly Candles
- **Functionality**: Historical candle data with customizable periods
- **Parameters**:
  - Period: Daily (D), Weekly (W), Monthly (M)
  - Adjust Price: Stock split adjustment
  - Limit: 1-500 candles
- **Transaction ID**: FHKST01010400
- **Endpoint**: `GET /api/korean/candle/{symbol}`

#### Minute Candles
- **Functionality**: Intraday minute-level candle data
- **Parameters**:
  - Interval: 1, 5, 10, 30, 60 minutes
  - Limit: 1-500 candles
- **Transaction ID**: FHKST03010200
- **Endpoint**: `GET /api/korean/candle-minute/{symbol}`

### 3. Account Information

#### Account Balance
- **Functionality**: Complete account overview with balance and positions
- **Data Included**:
  - Total evaluation amount
  - Cash balance
  - Investment amount
  - Profit/loss (amount and percentage)
  - List of stock positions
- **Transaction ID**: TTTC8434R (real) / VTTC8434R (mock)
- **Endpoint**: `GET /api/korean/account/{account_number}`

## Technical Implementation

### Architecture

```
Frontend/User Request
    ↓
API Router (korean.py)
    ↓
Service Layer (korean_market.py)
    ↓
Integration Client (kdevelopers.py)
    ↓
Korean Investment Securities API
```

### Data Models

#### KoreanCandleData
```python
- symbol: str          # Stock code (e.g., "005930")
- date: str            # Date/time (YYYYMMDD or HHMMSS)
- open: float          # Opening price in KRW
- high: float          # High price in KRW
- low: float           # Low price in KRW
- close: float         # Closing price in KRW
- volume: int          # Trading volume
- change: float        # Price change (optional)
- change_percent: float # Change percentage (optional)
```

#### KoreanAccountBalance
```python
- account_number: str       # Account number
- total_evaluation: float   # Total value in KRW
- cash_balance: float       # Cash in KRW
- investment_amount: float  # Total invested in KRW
- profit_loss: float        # P&L in KRW
- profit_loss_percent: float # P&L percentage
- timestamp: datetime       # Balance timestamp
```

#### KoreanStockPosition
```python
- symbol: str               # Stock code
- name: str                 # Company name
- quantity: int             # Number of shares
- average_price: float      # Average purchase price
- current_price: float      # Current market price
- evaluation_amount: float  # Current value
- profit_loss: float        # P&L in KRW
- profit_loss_percent: float # P&L percentage
```

### Authentication

- **Method**: OAuth2 with client credentials
- **Token Management**: Automatic caching and refresh
- **Required Credentials**:
  - HANTU_API_KEY: Application key
  - HANTU_API_SECRET: Application secret

### API Configuration

#### Base URLs
- **Production**: `https://openapi.koreainvestment.com:9443`
- **Mock Trading**: `https://openapivts.koreainvestment.com:29443`

#### Request Headers
```python
{
    "content-type": "application/json",
    "authorization": "Bearer {access_token}",
    "appkey": "{api_key}",
    "appsecret": "{api_secret}",
    "tr_id": "{transaction_id}"  # Varies by endpoint
}
```

## Files Modified/Created

### New Files
1. `backend/tests/test_korean_models.py` - Test suite for new models
2. `docs/KDEVELOPERS_API.md` - Comprehensive API documentation
3. `backend/examples/korean_api_example.py` - Runnable usage example
4. `backend/examples/README.md` - Examples documentation
5. `backend/uv.lock` - Dependency lock file

### Modified Files
1. `backend/src/integrations/kdevelopers.py` - Added candle and account methods
2. `backend/src/models/korean.py` - Added new data models
3. `backend/src/models/__init__.py` - Exported new models
4. `backend/src/api/korean.py` - Added new endpoints
5. `backend/src/services/korean_market.py` - Added service methods
6. `backend/README.md` - Updated documentation

## Testing

### Test Coverage
- **Total Tests**: 16 (all passing)
- **New Tests**: 5 for Korean models
- **Existing Tests**: 11 (still passing)

### Test Categories
1. Model creation and validation
2. Optional field handling
3. Data type validation
4. Edge case testing

### Running Tests
```bash
cd backend
uv run pytest tests/ -v
```

## Usage Examples

### Python Client
```python
from src.services.korean_market import korean_market_service

# Get real-time quote
quote = await korean_market_service.get_quote("005930")
print(f"Price: {quote.current_price} KRW")

# Get daily candles
candles = await korean_market_service.get_daily_candle(
    "005930", period="D", limit=30
)

# Get account balance
account = await korean_market_service.get_account_balance("12345678")
print(f"Total: {account['balance'].total_evaluation} KRW")
```

### HTTP API
```bash
# Real-time quote
curl http://localhost:8000/api/korean/quote/005930

# Daily candles
curl "http://localhost:8000/api/korean/candle/005930?period=D&limit=100"

# Minute candles
curl "http://localhost:8000/api/korean/candle-minute/005930?interval=5"

# Account balance
curl http://localhost:8000/api/korean/account/12345678
```

## Security Considerations

1. **API Credentials**: Never commit credentials to version control
2. **Environment Variables**: Store credentials in `.env` file
3. **Token Caching**: Tokens are cached to minimize authentication requests
4. **Error Handling**: Sensitive information is not exposed in error messages

## Performance Optimizations

1. **Token Caching**: OAuth tokens cached to reduce authentication overhead
2. **Type Safety**: Pydantic models provide validation and serialization
3. **Async Operations**: All service methods use async/await pattern
4. **Efficient Parsing**: Direct field mapping reduces processing overhead

## Rate Limiting

- KIS API has rate limits per account
- Implement appropriate throttling in production
- Cache frequently accessed data
- Use WebSocket for real-time updates when available

## Future Enhancements

1. **WebSocket Integration**: Real-time price updates
2. **Trading Functions**: Order placement and management
3. **Advanced Queries**: Market depth, investor information
4. **Caching Layer**: Redis for frequently accessed data
5. **Batch Operations**: Multiple symbol queries in single request

## Documentation

### Main Documentation
- `docs/KDEVELOPERS_API.md` - Complete API reference
- `backend/README.md` - Backend setup and usage
- `backend/examples/README.md` - Example scripts guide

### External Resources
- [KIS Developers Portal](https://apiportal.koreainvestment.com/intro)
- [Official GitHub Samples](https://github.com/koreainvestment/open-trading-api)
- [API Service List](https://apiportal.koreainvestment.com/apiservice)

## Support and Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check HANTU_API_KEY and HANTU_API_SECRET in .env
   - Verify credentials at KIS Developers portal

2. **No Data Returned**
   - Verify stock symbol format (e.g., "005930" not "005930.KS")
   - Check market hours for real-time data
   - Ensure account number is correct (8 digits)

3. **Rate Limiting**
   - Implement exponential backoff
   - Cache frequently accessed data
   - Use appropriate request intervals

### Getting Help

- Review documentation in `docs/KDEVELOPERS_API.md`
- Check example scripts in `backend/examples/`
- Refer to official KIS Developers portal
- Review test files for expected behavior

## Conclusion

The KDevelopers API integration is fully implemented and tested, providing comprehensive access to Korean stock market data through a clean, type-safe Python API. The implementation follows best practices for security, performance, and maintainability, and includes comprehensive documentation and examples for easy adoption.
