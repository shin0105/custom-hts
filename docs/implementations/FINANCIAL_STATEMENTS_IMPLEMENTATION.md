# Financial Statement Data Insertion Implementation

## Overview

This implementation adds comprehensive financial statement storage to the HTS application using Supabase PostgreSQL. It includes separate tables for balance sheets, income statements, and cash flow statements for both Korean and US markets.

## Database Schema

### Tables Created

The implementation adds 6 new tables to the database:

#### Korean Market Tables
1. **korean_balance_sheet** - Balance sheet data from OPENDART
2. **korean_income_statement** - Income statement data from OPENDART
3. **korean_cashflow_statement** - Cash flow data from OPENDART

#### US Market Tables
4. **us_balance_sheet** - Balance sheet data from yfinance
5. **us_income_statement** - Income statement data from yfinance
6. **us_cashflow_statement** - Cash flow data from yfinance

### Table Structure

Each table includes:
- **Structured fields** for common financial metrics (total_assets, revenue, operating_cash_flow, etc.)
- **JSONB raw_data field** to store all additional fields from API responses
- **Year and quarter fields** to support both annual and quarterly data
- **Unique constraints** on (symbol, year, quarter) to prevent duplicates
- **Indexes** on symbol, year, and updated_at for efficient queries
- **Automatic timestamp updates** via triggers

### SQL Files

1. **database/init.sql** - Base schema with korean_financials and us_financials summary tables
2. **database/financial_statements.sql** - Extended schema with detailed financial statement tables

To set up the database:
```sql
-- Run in Supabase SQL editor
-- First, run init.sql to create base tables
-- Then, run financial_statements.sql to add detailed tables
```

## Data Insertion Service

### Service Architecture

The `FinancialStatementService` class in `backend/src/services/financial_statements.py` provides:

- **Korean data insertion** from OPENDART API
- **US data insertion** from yfinance library
- **Automatic data parsing** and field mapping
- **Error handling** and logging
- **Batch operations** to insert all statement types at once

### Key Methods

#### Korean Financial Statements

```python
from src.services.financial_statements import financial_statement_service

# Insert single statement type
financial_statement_service.insert_korean_balance_sheet("005930", 2024, quarter=3)
financial_statement_service.insert_korean_income_statement("005930", 2024, quarter=3)
financial_statement_service.insert_korean_cashflow_statement("005930", 2024, quarter=3)

# Insert all statements at once
results = financial_statement_service.insert_all_korean_statements("005930", 2024, quarter=3)
```

#### US Financial Statements

```python
# Insert single statement type
financial_statement_service.insert_us_balance_sheet("AAPL", 2024, quarter=3)
financial_statement_service.insert_us_income_statement("AAPL", 2024, quarter=3)
financial_statement_service.insert_us_cashflow_statement("AAPL", 2024, quarter=3)

# Insert all statements at once
results = financial_statement_service.insert_all_us_statements("AAPL", 2024, quarter=3)
```

### Data Parsing

The service automatically:
1. Fetches raw data from OPENDART or yfinance
2. Maps Korean/English field names to database columns
3. Stores structured data in typed columns
4. Saves complete raw data in JSONB field for flexibility
5. Handles missing data gracefully

## Usage Scripts

### Insert Financial Data Script

Run `backend/insert_financial_data.py` to insert data for specific periods:

```bash
cd backend
source ../.venv/bin/activate
python insert_financial_data.py
```

This script:
- Inserts data for Samsung (005930) and Apple (AAPL)
- Processes annual and quarterly data
- Verifies insertions were successful
- Reports summary of inserted records

### Test API Data Script

Run `backend/test_api_raw_data.py` to record raw API responses:

```bash
cd backend
source ../.venv/bin/activate
python test_api_raw_data.py
```

This script:
- Fetches raw data from OPENDART and yfinance
- Saves complete responses to JSON files in `backend/data/`
- Useful for understanding API data structure

## Data Structure Documentation

### Sample Data Files

The `backend/data/` directory contains sample data structure files:

1. **sample_opendart_structure.json** - Example OPENDART API response format
2. **sample_yfinance_structure.json** - Example yfinance data structure

These files document:
- Field names and data types
- Available data points
- Response structure
- Common patterns

## Environment Configuration

Required environment variables in `.env`:

```bash
# OPENDART API (required for Korean data)
DART_API_KEY=your_dart_api_key_here

# Supabase (required for all operations)
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
```

## Querying Data

### Example Queries

#### Get Balance Sheet Data
```python
from src.integrations.supabase_client import supabase_client

# Get Korean balance sheet
response = supabase_client.client.table("korean_balance_sheet")\
    .select("*")\
    .eq("symbol", "005930")\
    .eq("year", 2024)\
    .eq("quarter", 3)\
    .execute()

# Get US balance sheet
response = supabase_client.client.table("us_balance_sheet")\
    .select("*")\
    .eq("symbol", "AAPL")\
    .eq("year", 2024)\
    .execute()
```

#### Get All Statements for a Company
```python
# Get all Korean statements for Samsung 2024 Q3
balance_sheet = supabase_client.client.table("korean_balance_sheet")\
    .select("*").eq("symbol", "005930").eq("year", 2024).eq("quarter", 3).execute()

income_statement = supabase_client.client.table("korean_income_statement")\
    .select("*").eq("symbol", "005930").eq("year", 2024).eq("quarter", 3).execute()

cashflow = supabase_client.client.table("korean_cashflow_statement")\
    .select("*").eq("symbol", "005930").eq("year", 2024).eq("quarter", 3).execute()
```

#### Get Historical Data
```python
# Get all annual data for a company
response = supabase_client.client.table("korean_income_statement")\
    .select("year, revenue, operating_income, net_income")\
    .eq("symbol", "005930")\
    .is_("quarter", "null")\
    .order("year", desc=True)\
    .execute()
```

## Data Fields

### Balance Sheet Fields

**Korean Balance Sheet:**
- Assets: total_assets, current_assets, cash_and_cash_equivalents, accounts_receivable, inventory, property_plant_equipment, intangible_assets
- Liabilities: total_liabilities, current_liabilities, accounts_payable, short_term_debt, long_term_debt
- Equity: total_equity, paid_in_capital, retained_earnings

**US Balance Sheet:**
- Similar structure with US-specific fields like goodwill, treasury_stock, stockholders_equity

### Income Statement Fields

**Korean Income Statement:**
- Revenue: revenue, cost_of_revenue, gross_profit
- Operating: operating_expenses, selling_general_admin, research_development, operating_income
- Profit: income_before_tax, income_tax_expense, net_income, earnings_per_share

**US Income Statement:**
- Similar structure with total_revenue, pretax_income, tax_provision, diluted_eps

### Cash Flow Fields

**Korean Cash Flow:**
- Operating: operating_cash_flow, depreciation_amortization, change_working_capital
- Investing: investing_cash_flow, capital_expenditure, acquisition_investments
- Financing: financing_cash_flow, proceeds_debt, dividends_paid, stock_repurchase
- Summary: net_change_cash, free_cash_flow

**US Cash Flow:**
- Similar structure with stock_based_compensation, deferred_income_tax, etc.

## API Integration

### OPENDART Integration

The OPENDART client (`src/integrations/opendart.py`) provides:
- `get_balance_sheet()` - Balance sheet line items
- `get_income_statement()` - Income statement line items
- `get_cash_flow()` - Cash flow line items
- `get_financial_statement_raw()` - Complete raw data

### yfinance Integration

The yfinance client uses the standard `yfinance` library:
- `ticker.balance_sheet` - Annual balance sheet DataFrame
- `ticker.financials` - Annual income statement DataFrame
- `ticker.cashflow` - Annual cash flow DataFrame
- `ticker.quarterly_*` - Quarterly equivalents

## Error Handling

The service includes comprehensive error handling:
- Network errors when fetching from APIs
- Missing data handling (returns None instead of failing)
- Database insertion errors with logging
- Invalid date/quarter handling

## Performance Considerations

- **Upsert operations** prevent duplicate data
- **JSONB indexing** available for raw_data field
- **Batch insertions** reduce API calls
- **Caching strategy** can be implemented at application level

## Future Enhancements

Potential improvements:
1. **Automatic periodic updates** using scheduled jobs
2. **Data validation** to ensure financial data consistency
3. **Historical data backfill** for multiple years
4. **API rate limiting** handling
5. **Data quality checks** and anomaly detection
6. **REST API endpoints** for frontend access

## Testing

To test the implementation:

1. **Ensure environment variables are set**
2. **Run the database schema scripts** in Supabase
3. **Run the insertion script** to populate data
4. **Verify in Supabase dashboard** that tables have data
5. **Query the data** using the examples above

## Troubleshooting

### Common Issues

**Issue: "Supabase client not initialized"**
- Solution: Set SUPABASE_URL and SUPABASE_KEY in .env file

**Issue: "DART API key not configured"**
- Solution: Get API key from https://opendart.fss.or.kr/ and set in .env

**Issue: "No data available for symbol"**
- Possible causes:
  - Symbol not found in corp code mapping
  - Data not available for requested period
  - Network connectivity issues

**Issue: "yfinance network error"**
- Solution: Check internet connectivity, yfinance may be blocked in some environments

## Support

For questions or issues:
1. Check the sample data files in `backend/data/`
2. Review the service code in `backend/src/services/financial_statements.py`
3. Check logs for detailed error messages
4. Verify Supabase connection and table structure

## License

This implementation is part of the Custom HTS application.
