# OPENDART API Integration Test Scripts

This directory contains test scripts to demonstrate the OPENDART API integration for Korean company financial statements.

## Test Scripts

### 1. test_opendart_structure.py
Verifies the structure and implementation of the OPENDART client without requiring an API key.

**Tests:**
- Client initialization
- Corp code mapping for major Korean companies
- Available methods verification
- Method signatures and usage examples

**Run:**
```bash
cd backend
PYTHONPATH=$(pwd)/src python test_opendart_structure.py
```

### 2. test_opendart_demo.py
Full demonstration of OPENDART API functionality with real API calls. **Requires a valid DART_API_KEY**.

**Demonstrates:**
1. Financial statement retrieval (summary)
2. Detailed balance sheet data
3. Detailed income statement data
4. Detailed cash flow statement data
5. Quarterly financial data

**Run:**
```bash
cd backend
# First, set up your .env file with DART_API_KEY
cp ../.env.example ../.env
# Edit .env and add your DART_API_KEY

# Then run the demo
PYTHONPATH=$(pwd)/src python test_opendart_demo.py
```

## What Has Been Implemented

### Enhanced OPENDART Client Features

The backend implements direct API calls to OPENDART without using external packages, providing:

- **Corp Code Management**: Hardcoded mapping for 10 major Korean companies with ability to download full list
- **Financial Statement Retrieval**: Complete financial data parsing from OPENDART API
- **Company Information**: Detailed company profiles using OPENDART company.json endpoint
- **Disclosure Listings**: Corporate disclosure search using OPENDART list.json endpoint
- **All Own Functions**: All requests to OPENDART are made by own implementation functions

#### 1. Corp Code Mapping
- **Problem:** DART uses 8-digit corp codes, different from 6-digit stock codes
- **Solution:** 
  - Hardcoded mapping for 10 major Korean companies
  - `download_corp_code_list()` method to fetch and cache complete mapping from DART
  - `find_corp_code()` method to search by company name or stock code
  - `download_corp_code_list()` method to fetch and cache complete mapping from DART

**Mapped Companies:**
- Samsung Electronics (005930 → 00126380)
- SK Hynix (000660 → 00164742)
- NAVER (035420 → 00234904)
- Kakao (035720 → 00164779)
- LG Chemicals (051910 → 00164384)
- Samsung SDI (006400 → 00126186)
- Samsung Biologics (207940 → 00401731)
- Celltrion (068270 → 00356370)
- Samsung C&T (028260 → 00164308)
- Hyundai Mobis (012330 → 00164485)

#### 2. Financial Statement Methods

##### `get_financial_statement(symbol, year, quarter=None, fs_div='CFS')`
Returns a summarized `KoreanFinancialStatement` object with key metrics:
- Revenue
- Operating Income
- Net Income
- Total Assets
- Total Liabilities
- Total Equity
- EPS (if available)

**Parameters:**
- `symbol`: Stock code (e.g., "005930")
- `year`: Fiscal year
- `quarter`: Optional (1-4 for quarterly, None for annual)
- `fs_div`: "CFS" for consolidated, "OFS" for separate

##### `get_balance_sheet(symbol, year, quarter=None)`
Returns a dictionary with all balance sheet line items including:
- Current assets
- Non-current assets
- Total assets
- Current liabilities
- Non-current liabilities
- Total liabilities
- Total equity
- And many more detailed items

##### `get_income_statement(symbol, year, quarter=None)`
Returns a dictionary with all income statement line items including:
- Revenue (by segment if available)
- Cost of sales
- Gross profit
- Operating expenses
- Operating income
- Non-operating income/expenses
- Income tax
- Net income
- And many more detailed items

##### `get_cash_flow(symbol, year, quarter=None)`
Returns a dictionary with all cash flow statement line items including:
- Operating activities
- Investing activities
- Financing activities
- And detailed breakdown of each category

##### `get_financial_statement_raw(symbol, year, quarter=None, fs_div='CFS')`
Returns raw, unprocessed data from DART API for custom processing.

##### `find_corp_code(corp_name_or_stock_code)` (NEW)
Find corp code by company name or stock code.
- Searches local cache first
- Suggests downloading full corp code list for company name searches

##### `get_company_info(symbol)` (NEW)
Get detailed company information from OPENDART company.json endpoint.
- Company names (Korean and English)
- CEO name
- Address and contact information
- Industry code
- Website URLs
- Establishment date

##### `get_disclosure_list(corp, start, end, kind, final)` (NEW)
Get list of corporate disclosures from OPENDART list.json endpoint.
- Filter by company, date range, and disclosure type
- Support for all disclosure types (A-J)
- Option to include or exclude corrected reports
- Returns list of disclosure dictionaries

##### `get_finstate_all(symbol, year, reprt_code, fs_div)` (NEW)
Get all financial statement line items from OPENDART.
- Comprehensive financial data with all line items
- Alias for get_financial_statement_raw() with reprt_code parameter
- Compatible with OpenDartReader-style API

#### 3. Report Period Support

The client correctly handles different report periods:
- **Annual Report:** `reprt_code = "11011"`
- **Q1 Report:** `reprt_code = "11013"`
- **Q2 Report:** `reprt_code = "11012"`
- **Q3 Report:** `reprt_code = "11014"`
- **Q4/Annual:** `reprt_code = "11011"`

#### 4. Error Handling

- Validates API key configuration
- Handles network errors gracefully
- Checks DART API response status
- Provides informative error messages
- Returns None for missing data

## API Endpoint Used

The implementation uses the OPENDART `fnlttSinglAcntAll.json` endpoint which provides comprehensive financial statement data in a single call:

```
https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json
```

**Parameters:**
- `crtfc_key`: API authentication key
- `corp_code`: DART corporation code (8 digits)
- `bsns_year`: Business year (YYYY)
- `reprt_code`: Report type code
- `fs_div`: Financial statement division (CFS/OFS)

## Usage Examples

### Example 1: Get Samsung Electronics Annual Report

```python
from src.integrations.opendart import opendart_client

# Get 2023 annual financial statement
statement = opendart_client.get_financial_statement(
    symbol="005930",      # Samsung Electronics
    year=2023,
    quarter=None          # Annual report
)

if statement:
    print(f"Company: {statement.company_name}")
    print(f"Revenue: {statement.revenue:,.0f} KRW")
    print(f"Operating Income: {statement.operating_income:,.0f} KRW")
    print(f"Net Income: {statement.net_income:,.0f} KRW")
    print(f"Total Assets: {statement.total_assets:,.0f} KRW")
```

### Example 2: Get Detailed Balance Sheet

```python
# Get detailed balance sheet for NAVER
balance_sheet = opendart_client.get_balance_sheet(
    symbol="035420",      # NAVER
    year=2023
)

# Display top 10 items by value
sorted_items = sorted(
    balance_sheet.items(),
    key=lambda x: abs(x[1]) if x[1] else 0,
    reverse=True
)

for account, amount in sorted_items[:10]:
    print(f"{account}: {amount:,.0f} KRW")
```

### Example 3: Get Quarterly Income Statement

```python
# Get Q3 2023 income statement for Kakao
income_stmt = opendart_client.get_income_statement(
    symbol="035720",      # Kakao
    year=2023,
    quarter=3             # Q3
)

# Display all income items
for account, amount in income_stmt.items():
    if amount:
        print(f"{account}: {amount:,.0f} KRW")
```

### Example 4: Compare Multiple Companies

```python
companies = [
    ("005930", "Samsung Electronics"),
    ("035420", "NAVER"),
    ("035720", "Kakao")
]

for symbol, name in companies:
    stmt = opendart_client.get_financial_statement(
        symbol=symbol,
        year=2023
    )
    
    if stmt:
        print(f"\n{name} ({symbol}):")
        print(f"  Revenue: {stmt.revenue:,.0f} KRW")
        print(f"  Net Income: {stmt.net_income:,.0f} KRW")
        print(f"  Total Assets: {stmt.total_assets:,.0f} KRW")
```

## Getting a DART API Key

1. Visit https://opendart.fss.or.kr/
2. Create an account (requires Korean phone number verification)
3. Navigate to "API 인증키 신청" (Apply for API authentication key)
4. Copy your API key
5. Add to `.env` file:
   ```
   DART_API_KEY=your_api_key_here
   ```

## Limitations

1. **Corp Code Mapping**: Currently only 10 major companies are hardcoded. For other companies, you need to:
   - Call `opendart_client.download_corp_code_list()` to download the full mapping
   - Or add additional mappings to the `_load_common_corp_codes()` method

2. **Rate Limits**: OPENDART has rate limits (exact limits not publicly documented). Implement appropriate throttling for production use.

3. **Historical Data**: Older financial statements may not be available or may have different formats.

4. **Account Names**: Financial line item names are in Korean. The parser handles common account names but may need expansion for specialized items.

## Integration with Existing Codebase

The OPENDART client is already integrated with:

1. **API Endpoints** (`src/api/korean.py`):
   - `/api/korean/financials/{symbol}` - Get financial statements via HTTP API

2. **Service Layer** (`src/services/korean_market.py`):
   - `korean_market_service.get_financials()` - Includes caching logic

3. **Database** (Supabase):
   - Financial statements are cached in `korean_financials` table

4. **Data Models** (`src/models/korean.py`):
   - `KoreanFinancialStatement` - Pydantic model for API responses

## Next Steps

To extend this implementation:

1. **Add More Companies**: Expand corp code mapping or implement automatic lookup
2. **Add Caching**: Implement Redis or in-memory caching for frequently accessed data
3. **Add Validation**: Validate data consistency and completeness
4. **Add Analytics**: Build financial ratios and analysis on top of the raw data
5. **Add Comparison**: Implement multi-company and multi-period comparisons
6. **Add Visualization**: Create charts and graphs for financial trends

## Troubleshooting

### "DART API key not configured"
- Ensure `DART_API_KEY` is set in your `.env` file
- Verify the `.env` file is in the repository root
- Check that `python-dotenv` is installed

### "Corp code not found"
- The stock code may not be in the hardcoded mapping
- Call `opendart_client.download_corp_code_list()` to download the full list
- Or manually add the mapping to `_load_common_corp_codes()`

### "No financial data available"
- The company may not have filed reports for that period
- Try a different year or quarter
- Verify the stock code is correct
- Check DART website directly to confirm data availability

### Network Errors
- Check internet connectivity
- Verify DART API is accessible
- Check for rate limiting
- Try again after a delay
