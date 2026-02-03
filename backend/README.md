# Custom HTS Backend

Python backend server for the Custom HTS application using FastAPI.

## Setup

1. Install UV package manager:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create virtual environment and install dependencies:
```bash
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

3. For development dependencies:
```bash
uv pip install -e ".[dev]"
```

## Running the Server

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/docs for API documentation.

## Project Structure

```
backend/
├── src/
│   ├── api/              # FastAPI route handlers
│   │   ├── korean.py     # Korean market endpoints
│   │   └── us.py         # US market endpoints
│   ├── services/         # Business logic
│   │   ├── korean_market.py
│   │   └── us_market.py
│   ├── models/           # Data models and schemas
│   │   ├── korean.py
│   │   └── us.py
│   ├── integrations/     # External API integrations
│   │   ├── kdevelopers.py
│   │   ├── opendart.py
│   │   ├── yfinance_client.py
│   │   └── supabase_client.py
│   ├── utils/            # Utility functions
│   │   ├── config.py
│   │   └── helpers.py
│   └── main.py           # FastAPI application entry point
└── tests/                # Test files
```

## API Endpoints

### Korean Market
- `GET /api/korean/quote/{symbol}` - Get real-time quote
- `GET /api/korean/candle/{symbol}` - Get daily/weekly/monthly candle data
- `GET /api/korean/candle-minute/{symbol}` - Get minute candle data
- `GET /api/korean/account/{account_number}` - Get account balance and positions ⚠️ **Requires authentication (not yet implemented)**
- `GET /api/korean/financials/{symbol}` - Get financial statements
- `GET /api/korean/search` - Search Korean stocks

### US Market
- `GET /api/us/quote/{symbol}` - Get real-time quote
- `GET /api/us/financials/{symbol}` - Get financial statements
- `GET /api/us/search` - Search US stocks

## Environment Variables

Required environment variables (set in `.env` file in project root):

```
HANTU_API_KEY=your_korean_investment_api_key
HANTU_API_SECRET=your_korean_investment_api_secret
DART_API_KEY=your_opendart_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Testing

Run tests:
```bash
uv run pytest
```

Run tests with coverage:
```bash
uv run pytest --cov=src --cov-report=html
```

## Examples

See the `examples/` directory for usage examples:

```bash
# Run Korean API example
uv run python examples/korean_api_example.py
```

Examples demonstrate:
- Real-time stock quotes
- Candle chart data (daily/minute)
- Account balance and positions

## Code Quality

Format code:
```bash
uv run black src tests
```

Lint code:
```bash
uv run flake8 src tests
```

Type check:
```bash
uv run mypy src
```
