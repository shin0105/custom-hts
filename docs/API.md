# Custom HTS API Documentation

This document provides detailed information about the Custom HTS Backend API endpoints.

## Base URL

```
http://localhost:8000
```

## API Endpoints

### Health Check

#### GET `/health`

Check the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

---

## Korean Market Endpoints

Base path: `/api/korean`

### Get Stock Quote

#### GET `/api/korean/quote/{symbol}`

Get real-time quote for a Korean stock.

**Parameters:**
- `symbol` (path, required): Korean stock code (e.g., "005930" for Samsung Electronics)

**Response:**
```json
{
  "symbol": "005930",
  "name": "삼성전자",
  "current_price": 70000,
  "change": 1000,
  "change_percent": 1.45,
  "volume": 15000000,
  "timestamp": "2024-02-03T12:00:00Z",
  "high": 71000,
  "low": 69000,
  "open": 69500,
  "previous_close": 69000
}
```

**Error Responses:**
- `404`: Quote not found for the specified symbol
- `500`: Internal server error

### Get Financial Statements

#### GET `/api/korean/financials/{symbol}`

Get financial statement data for a Korean company.

**Parameters:**
- `symbol` (path, required): Korean stock code
- `year` (query, optional): Fiscal year (defaults to current year)
- `quarter` (query, optional): Quarter (1-4)
- `use_cache` (query, optional): Whether to use cached data (default: true)

**Example Request:**
```
GET /api/korean/financials/005930?year=2024&quarter=1&use_cache=true
```

**Response:**
```json
{
  "symbol": "005930",
  "company_name": "삼성전자주식회사",
  "year": 2024,
  "quarter": 1,
  "revenue": 67000000000000,
  "operating_income": 6500000000000,
  "net_income": 5200000000000,
  "total_assets": 400000000000000,
  "total_liabilities": 100000000000000,
  "total_equity": 300000000000000,
  "eps": 7850,
  "updated_at": "2024-02-03T12:00:00Z"
}
```

**Error Responses:**
- `404`: Financials not found for the specified symbol
- `500`: Internal server error

### Health Check

#### GET `/api/korean/health`

Check Korean market API health.

**Response:**
```json
{
  "status": "healthy",
  "market": "Korean"
}
```

---

## US Market Endpoints

Base path: `/api/us`

### Get Stock Quote

#### GET `/api/us/quote/{symbol}`

Get real-time quote for a US stock.

**Parameters:**
- `symbol` (path, required): US stock ticker symbol (e.g., "AAPL" for Apple)

**Response:**
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "current_price": 175.50,
  "change": 2.50,
  "change_percent": 1.45,
  "volume": 50000000,
  "timestamp": "2024-02-03T12:00:00Z",
  "high": 176.00,
  "low": 174.00,
  "open": 174.50,
  "previous_close": 173.00,
  "market_cap": 2800000000000
}
```

**Error Responses:**
- `404`: Quote not found for the specified symbol
- `500`: Internal server error

### Get Financial Statements

#### GET `/api/us/financials/{symbol}`

Get financial statement data for a US company.

**Parameters:**
- `symbol` (path, required): US stock ticker symbol
- `use_cache` (query, optional): Whether to use cached data (default: true)

**Example Request:**
```
GET /api/us/financials/AAPL?use_cache=true
```

**Response:**
```json
[
  {
    "symbol": "AAPL",
    "company_name": "Apple Inc.",
    "year": 2024,
    "quarter": null,
    "revenue": 394000000000,
    "operating_income": 115000000000,
    "net_income": 97000000000,
    "total_assets": 350000000000,
    "total_liabilities": 280000000000,
    "total_equity": 70000000000,
    "eps": 6.13,
    "pe_ratio": 28.5,
    "updated_at": "2024-02-03T12:00:00Z"
  },
  {
    "symbol": "AAPL",
    "company_name": "Apple Inc.",
    "year": 2023,
    "quarter": null,
    "revenue": 383000000000,
    "operating_income": 110000000000,
    "net_income": 94000000000,
    "eps": 5.89,
    "pe_ratio": 27.0,
    "updated_at": "2024-02-03T12:00:00Z"
  }
]
```

**Error Responses:**
- `404`: Financials not found for the specified symbol
- `500`: Internal server error

### Health Check

#### GET `/api/us/health`

Check US market API health.

**Response:**
```json
{
  "status": "healthy",
  "market": "US"
}
```

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200`: Success
- `400`: Bad Request - Invalid parameters
- `404`: Not Found - Resource not found
- `500`: Internal Server Error - Server error

Error responses include a detail message:

```json
{
  "detail": "Quote not found for symbol INVALID"
}
```

## Rate Limiting

The API does not currently implement rate limiting on the backend, but external API calls are subject to the rate limits of:

- **Korean Investment Securities**: As per their API terms
- **OPENDART**: 10,000 calls per day
- **Yahoo Finance**: Subject to yfinance library limitations

## Caching

Financial statement data is cached in the Supabase database to reduce external API calls. The cache duration is 24 hours by default. You can bypass the cache by setting `use_cache=false` in query parameters.

## CORS

The API is configured to allow requests from:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000`
- `http://127.0.0.1:5173`
- `http://127.0.0.1:3000`

## Interactive Documentation

Visit the following URLs for interactive API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

Currently, the API does not require authentication. This should be added for production use.

## Future Enhancements

Planned API improvements:

1. **Authentication**: JWT-based authentication
2. **Rate Limiting**: Per-user rate limiting
3. **Websockets**: Real-time quote updates
4. **Search**: Stock search endpoints
5. **Watchlists**: User watchlist management
6. **Alerts**: Price alert configuration
