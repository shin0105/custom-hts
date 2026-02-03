# Backend API Examples

This directory contains example scripts demonstrating how to use the Custom HTS backend APIs.

## Korean Investment Securities API Examples

### korean_api_example.py

Demonstrates the usage of KDevelopers (한국투자증권) OpenAPI integration:

1. **Real-time Stock Quote**: Fetch current price, volume, and trading data
2. **Daily Candle Charts**: Get OHLCV data for daily, weekly, or monthly periods
3. **Minute Candle Charts**: Get intraday minute-level candle data
4. **Account Balance**: Fetch account balance and stock positions (requires valid credentials)

#### Running the Example

```bash
cd backend
uv run python examples/korean_api_example.py
```

#### Requirements

Set up your environment variables in `.env` file:
```bash
HANTU_API_KEY=your_api_key_here
HANTU_API_SECRET=your_api_secret_here
```

Get your API credentials from: https://apiportal.koreainvestment.com/

#### Expected Output

The script will:
- Fetch real-time quote for Samsung Electronics (005930)
- Display current price, volume, and price changes
- Show 5 most recent daily candles with OHLCV data
- Display 5 most recent minute candles
- Demonstrate account balance structure (commented out)

#### Notes

- The account balance example is commented out by default as it requires a valid account number
- API calls will fail gracefully if credentials are not configured
- All prices are displayed in Korean Won (KRW)
- The example uses Samsung Electronics (005930) as a demo stock symbol

## Adding More Examples

To add more examples:
1. Create a new Python file in this directory
2. Import necessary services and models
3. Add clear documentation and comments
4. Update this README with usage instructions
