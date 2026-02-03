# Korean Investment Securities API Integration

This document describes the KDevelopers (한국투자증권) OpenAPI integration for the Custom HTS backend.

## Overview

The integration provides access to real-time stock data, candle charts, and account information for Korean stocks using the Korean Investment Securities OpenAPI.

## API Documentation

Official API Portal: https://apiportal.koreainvestment.com/

## Implemented Features

### 1. Stock Price and Quote Data

#### Get Real-time Stock Quote
- **Endpoint**: `GET /api/korean/quote/{symbol}`
- **Description**: Get current stock price and trading information
- **Example**: `/api/korean/quote/005930` (Samsung Electronics)
- **Response**: Real-time quote with current price, volume, changes, etc.

### 2. Candle Chart Data (OHLCV)

#### Get Daily/Weekly/Monthly Candle Data
- **Endpoint**: `GET /api/korean/candle/{symbol}`
- **Parameters**:
  - `period`: Period type (D: daily, W: weekly, M: monthly) - default: "D"
  - `adjust_price`: Adjust for stock splits - default: true
  - `limit`: Number of candles (1-500) - default: 100
- **Example**: `/api/korean/candle/005930?period=D&limit=100`
- **Response**: List of candle data with open, high, low, close, volume

#### Get Minute Candle Data
- **Endpoint**: `GET /api/korean/candle-minute/{symbol}`
- **Parameters**:
  - `interval`: Minute interval (1, 5, 10, 30, 60) - default: 1
  - `limit`: Number of candles (1-500) - default: 100
- **Example**: `/api/korean/candle-minute/005930?interval=5&limit=50`
- **Response**: List of minute candle data

### 3. Account Balance and Positions

#### Get Account Balance
- **Endpoint**: `GET /api/korean/account/{account_number}`
- **Parameters**:
  - `account_product_code`: Account product code - default: "01"
- **Example**: `/api/korean/account/12345678`
- **Response**: Account balance information and list of stock positions

**Response Structure**:
```json
{
  "balance": {
    "account_number": "12345678",
    "total_evaluation": 100000000,
    "cash_balance": 20000000,
    "investment_amount": 80000000,
    "profit_loss": 5000000,
    "profit_loss_percent": 6.25,
    "timestamp": "2024-01-01T12:00:00"
  },
  "positions": [
    {
      "symbol": "005930",
      "name": "삼성전자",
      "quantity": 100,
      "average_price": 70000,
      "current_price": 72000,
      "evaluation_amount": 7200000,
      "profit_loss": 200000,
      "profit_loss_percent": 2.86
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

### Transaction IDs (tr_id)

Different API endpoints require different transaction IDs:

- **Real-time Quote**: `FHKST01010100`
- **Daily/Period Candle**: `FHKST01010400`
- **Minute Candle**: `FHKST03010200`
- **Account Balance**: `TTTC8434R` (real) / `VTTC8434R` (mock)

### Base URL

- **Production**: `https://openapi.koreainvestment.com:9443`
- **Mock Trading**: `https://openapivts.koreainvestment.com:29443`

## Data Models

### KoreanCandleData
Represents OHLCV (Open, High, Low, Close, Volume) candle data:
- `symbol`: Stock symbol (e.g., "005930")
- `date`: Date/time in YYYYMMDD or HHMMSS format
- `open`: Opening price in KRW
- `high`: High price in KRW
- `low`: Low price in KRW
- `close`: Closing price in KRW
- `volume`: Trading volume
- `change`: Price change in KRW (optional)
- `change_percent`: Price change percentage (optional)

### KoreanAccountBalance
Represents account balance information:
- `account_number`: Account number
- `total_evaluation`: Total evaluation amount in KRW
- `cash_balance`: Cash balance in KRW
- `investment_amount`: Total investment amount in KRW
- `profit_loss`: Total profit/loss in KRW
- `profit_loss_percent`: Total profit/loss percentage
- `timestamp`: Balance timestamp

### KoreanStockPosition
Represents individual stock position:
- `symbol`: Stock symbol
- `name`: Company name in Korean
- `quantity`: Number of shares held
- `average_price`: Average purchase price
- `current_price`: Current market price
- `evaluation_amount`: Current evaluation amount
- `profit_loss`: Profit/loss in KRW
- `profit_loss_percent`: Profit/loss percentage

## Usage Examples

### Python Client Example

```python
from src.integrations.kdevelopers import kdevelopers_client

# Get real-time quote
quote = kdevelopers_client.get_quote("005930")
print(f"Current price: {quote.current_price} KRW")

# Get daily candle data
candles = kdevelopers_client.get_daily_candle("005930", period="D", limit=30)
for candle in candles:
    print(f"Date: {candle.date}, Close: {candle.close} KRW")

# Get account balance
account_data = kdevelopers_client.get_account_balance("12345678")
balance = account_data["balance"]
positions = account_data["positions"]
print(f"Total evaluation: {balance.total_evaluation} KRW")
for position in positions:
    print(f"{position.name}: {position.quantity} shares")
```

### HTTP API Example

```bash
# Get stock quote
curl http://localhost:8000/api/korean/quote/005930

# Get daily candles
curl "http://localhost:8000/api/korean/candle/005930?period=D&limit=100"

# Get minute candles
curl "http://localhost:8000/api/korean/candle-minute/005930?interval=5&limit=50"

# Get account balance
curl http://localhost:8000/api/korean/account/12345678
```

## Error Handling

The API includes comprehensive error handling:
- Returns `None` or empty list if data fetch fails
- Logs errors for debugging
- Returns HTTP 404 if data not found
- Validates input parameters

## Rate Limiting

Be aware of KIS API rate limits:
- Implement proper throttling for production use
- Cache frequently accessed data
- Use appropriate intervals for real-time data updates

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
