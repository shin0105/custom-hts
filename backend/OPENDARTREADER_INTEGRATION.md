# OpenDartReader Integration Summary

This document describes the integration of the OpenDartReader library into the HTS backend application.

## Overview

The backend now uses the [OpenDartReader](https://github.com/FinanceData/OpenDartReader) library to enhance OPENDART API integration. This provides improved parsing, automatic corp code management, and additional financial data features.

## What Was Changed

### 1. Dependencies (`pyproject.toml`)
- Added `opendartreader>=0.1.6` to the project dependencies
- The library is automatically installed with `uv pip install -e .` or `pip install -e .`

### 2. OPENDART Client (`src/integrations/opendart.py`)

#### Enhanced Features:
- **Automatic Corp Code Lookup**: When a corp code is not in the cache, the client can now automatically fetch it using OpenDartReader's `find_corp_code()` method
- **Pandas-Based Parsing**: Financial statements are now parsed using pandas DataFrames for better performance and data handling
- **Fallback Mechanism**: If OpenDartReader is unavailable or fails, the client automatically falls back to raw API calls

#### New Methods:
1. **`get_company_info(symbol)`**: Get comprehensive company profile information including CEO, address, industry code, website, etc.
   
2. **`get_disclosure_list(symbol, start, end, kind, final)`**: Get list of corporate disclosures with advanced filtering:
   - Filter by company, date range, and disclosure type
   - Support for all disclosure types (A-J: regular, major matters, issues, equity, etc.)
   - Option to include or exclude corrected reports
   
3. **`get_finstate_all(symbol, year, reprt_code)`**: Get comprehensive financial statements with all line items using OpenDartReader's pandas-based parsing

### 3. API Endpoints (`src/api/korean.py`)

#### New Endpoints:

1. **`GET /api/korean/company/{symbol}`**
   - Get detailed company information
   - Returns comprehensive company profile data
   - Example: `/api/korean/company/005930` (Samsung Electronics)

2. **`GET /api/korean/disclosures`**
   - Get list of corporate disclosures
   - Query parameters:
     - `symbol` (optional): Stock code
     - `start` (optional): Start date (YYYY-MM-DD)
     - `end` (optional): End date (YYYY-MM-DD)
     - `kind` (optional): Disclosure type (A-J)
     - `final` (default: true): Only final reports
     - `limit` (default: 100): Maximum results
   - Example: `/api/korean/disclosures?symbol=005930&kind=A&limit=50`

3. **`GET /api/korean/financials/{symbol}/all`**
   - Get comprehensive financial statements with all line items
   - Query parameters:
     - `year` (default: previous year): Fiscal year
     - `quarter` (optional): Quarter (1-4)
   - Returns all balance sheet, income statement, and cash flow line items
   - Example: `/api/korean/financials/005930/all?year=2023&quarter=3`

## How It Works

### Initialization
```python
from src.integrations.opendart import opendart_client

# The client automatically:
# 1. Loads OpenDartReader library if available
# 2. Initializes with DART_API_KEY from environment
# 3. Falls back to raw API if necessary
```

### Corp Code Management
```python
# Get corp code (auto-fetches if not in cache)
corp_code = opendart_client.get_corp_code("005930")
# Returns: "00126380"

# The client will:
# 1. Check local cache first (10 major companies pre-loaded)
# 2. If not found and OpenDartReader available, fetch automatically
# 3. Cache the result for future use
```

### Financial Statement Retrieval
```python
# Get financial statement (uses OpenDartReader if available)
statement = opendart_client.get_financial_statement(
    symbol="005930",
    year=2023,
    quarter=None  # Annual report
)

# The client will:
# 1. Try OpenDartReader.finstate() for pandas-based parsing
# 2. If that fails, fall back to raw API call
# 3. Return standardized KoreanFinancialStatement object
```

### Company Information
```python
# Get detailed company info (OpenDartReader feature)
company_info = opendart_client.get_company_info("005930")
# Returns: Dictionary with company profile data
```

### Disclosure Listings
```python
# Get disclosure list (OpenDartReader feature)
disclosures = opendart_client.get_disclosure_list(
    symbol="005930",
    start="2023-01-01",
    end="2023-12-31",
    kind="A",  # Regular disclosures
    final=True  # Only final reports
)
# Returns: pandas DataFrame with disclosure listings
```

## Configuration

### Environment Variables
Set in `.env` file:
```bash
DART_API_KEY=your_dart_api_key_here
```

Get your API key from: https://opendart.fss.or.kr/

### Installation
```bash
# Install all dependencies including OpenDartReader
cd backend
uv pip install -e .

# Or using pip
pip install -e .
```

## Testing

### Test Scripts

1. **Structure Test** (`test_opendart_structure.py`):
   ```bash
   cd backend
   PYTHONPATH=$(pwd)/src python test_opendart_structure.py
   ```
   - Verifies client initialization and method availability
   - No API key required

2. **Integration Test** (`test_opendart_reader_integration.py`):
   ```bash
   cd backend
   python test_opendart_reader_integration.py
   ```
   - Verifies OpenDartReader library integration
   - Tests fallback mechanism
   - No API key required

3. **Demo Test** (`test_opendart_demo.py`):
   ```bash
   cd backend
   python test_opendart_demo.py
   ```
   - Full demonstration with real API calls
   - **Requires valid DART_API_KEY**

## Backward Compatibility

All existing functionality is preserved:
- Existing methods work exactly as before
- Same return types and data structures
- Fallback to raw API if OpenDartReader is unavailable
- No breaking changes to existing code

## Benefits

### Performance
- Faster parsing using pandas DataFrames
- Automatic caching of corp codes
- Reduced API calls through intelligent caching

### Features
- Access to OpenDartReader's 30+ methods
- Company information and profiles
- Disclosure listings and searches
- Comprehensive financial data

### Reliability
- Automatic fallback mechanism
- Backward compatible
- Maintains existing functionality
- Graceful degradation

## Usage Examples

### Basic Financial Statement
```python
from src.integrations.opendart import opendart_client

# Get Samsung Electronics 2023 annual report
statement = opendart_client.get_financial_statement(
    symbol="005930",
    year=2023
)

if statement:
    print(f"Revenue: {statement.revenue:,.0f} KRW")
    print(f"Net Income: {statement.net_income:,.0f} KRW")
```

### Company Profile
```python
# Get company information
company = opendart_client.get_company_info("005930")

if company:
    print(f"CEO: {company.get('ceo_nm')}")
    print(f"Address: {company.get('adres')}")
    print(f"Website: {company.get('hm_url')}")
```

### Disclosure Search
```python
# Get all regular disclosures in 2023
disclosures = opendart_client.get_disclosure_list(
    symbol="005930",
    start="2023-01-01",
    end="2023-12-31",
    kind="A"  # Regular disclosures
)

if disclosures is not None:
    print(f"Found {len(disclosures)} disclosures")
    print(disclosures[['corp_name', 'report_nm', 'rcept_dt']])
```

### Complete Financial Data
```python
# Get all financial statement line items
df = opendart_client.get_finstate_all(
    symbol="005930",
    year=2023,
    reprt_code="11011"  # Annual report
)

if df is not None:
    # Access all line items
    print(df[['account_nm', 'thstrm_amount']])
```

## API Endpoints Usage

### Company Information Endpoint
```bash
# Get Samsung Electronics company info
curl http://localhost:8000/api/korean/company/005930
```

### Disclosures Endpoint
```bash
# Get Samsung Electronics regular disclosures in 2023
curl "http://localhost:8000/api/korean/disclosures?symbol=005930&start=2023-01-01&end=2023-12-31&kind=A&limit=50"
```

### Complete Financials Endpoint
```bash
# Get Samsung Electronics 2023 Q3 complete financials
curl "http://localhost:8000/api/korean/financials/005930/all?year=2023&quarter=3"
```

## Troubleshooting

### OpenDartReader not available
- Install the library: `pip install opendartreader`
- The client will fall back to raw API automatically

### API key not configured
- Set `DART_API_KEY` in `.env` file
- Get key from https://opendart.fss.or.kr/
- Client will log warning and use raw API

### Corp code not found
- The client will try to auto-fetch if OpenDartReader is available
- Pre-loaded cache includes 10 major companies
- Call `download_corp_code_list()` to download full list

## Future Enhancements

Possible improvements for future development:
1. Add more OpenDartReader methods (major shareholders, events, etc.)
2. Implement Redis caching for corp codes
3. Add background job to refresh corp code list
4. Create financial ratio calculations using the data
5. Add multi-company comparison endpoints
6. Implement data validation and consistency checks

## References

- OpenDartReader GitHub: https://github.com/FinanceData/OpenDartReader
- OPENDART API Documentation: https://opendart.fss.or.kr/
- Custom HTS Documentation: `/docs/OPENDART_API.md`
- Testing Documentation: `/backend/OPENDART_TESTING.md`
