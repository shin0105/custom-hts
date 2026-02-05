# How to Run API Tests Locally

This guide explains how to run the comprehensive API tests in a local environment where network access is available.

## Prerequisites

1. **Python 3.11+** installed
2. **UV package manager** installed (`pip install uv`)
3. **Environment variables** configured in `.env` file
4. **Network access** to external APIs

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/shin0105/custom-hts.git
cd custom-hts
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your API credentials:

```env
# OPENDART API
DART_API_KEY=your_dart_api_key_here

# Supabase
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# Optional: Korean Investment Securities
HANTU_API_KEY=your_hantu_api_key_here
HANTU_API_SECRET=your_hantu_api_secret_here
```

### 3. Install Dependencies

```bash
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

## Running the Tests

### Comprehensive API Test

This script tests all APIs and retrieves financial data:

```bash
cd backend
source ../.venv/bin/activate
python test_comprehensive_api.py
```

**What it does**:
1. Tests environment variables configuration
2. Tests Supabase connection
3. Tests OPENDART API connection
4. Tests yfinance API connection
5. Tests kdevelopers API connection (optional)
6. Retrieves 202509 financial data for 005930 (Samsung)
7. Retrieves 202509 financial data for AAPL (Apple)
8. Stores data in Supabase
9. Verifies data storage

**Results**: Check `backend/test_results/` directory for JSON files with detailed results.

### Individual Test Scripts

You can also run individual test scripts:

#### Test Workflow (Basic Connection Test)
```bash
python test_workflow.py
```
Tests Supabase and OPENDART basic connectivity.

#### Test Financial Statements
```bash
python test_financial_statements.py
```
Comprehensive test of financial statement functionality.

#### Test Raw API Data
```bash
python test_api_raw_data.py
```
Retrieves and saves raw API responses for inspection.

#### Test OPENDART Structure
```bash
python test_opendart_structure.py
```
Tests OPENDART API response structure.

## Expected Results

### Successful Test Output

When run with proper network access, you should see:

```
================================================================================
                   COMPREHENSIVE API TESTING & DATA RETRIEVAL                  
================================================================================

────────────────────────────────────────────────────────────────────────────────
  1. Testing Environment Variables
────────────────────────────────────────────────────────────────────────────────
  ✅ DART_API_KEY: SET
  ✅ SUPABASE_URL: SET
  ✅ SUPABASE_KEY: SET
  ...

────────────────────────────────────────────────────────────────────────────────
  6. Retrieving Korean Financial Data - 005930 (Q3 2025)
────────────────────────────────────────────────────────────────────────────────
  ✅ Retrieved raw data: 156 items
  ✅ Inserted Korean balance sheet: 005930 (2025Q3)
  ✅ Inserted Korean income statement: 005930 (2025Q3)
  ✅ Inserted Korean cash flow: 005930 (2025Q3)
  ...
```

### Test Results Files

After running, check `backend/test_results/` for:

- `00_summary_report.json` - Overall test summary
- `01_environment_variables.json` - Environment configuration
- `02_supabase_connection.json` - Database connection results
- `03_opendart_connection.json` - OPENDART API results
- `04_yfinance_connection.json` - yfinance API results
- `05_kdevelopers_connection.json` - kdevelopers API results
- `06_korean_financial_data_202509.json` - Korean data retrieval
- `07_us_financial_data_202509.json` - US data retrieval
- `08_database_verification.json` - Database verification
- `raw_opendart_*.json` - Raw OPENDART response data
- `raw_yfinance_*.json` - Raw yfinance response data

## Verifying Data in Supabase

After successful test execution:

1. Log in to your Supabase dashboard
2. Go to Table Editor
3. Check the following tables for new data:
   - `korean_balance_sheet` - Should have 005930 data
   - `korean_income_statement` - Should have 005930 data
   - `korean_cashflow_statement` - Should have 005930 data
   - `us_balance_sheet` - Should have AAPL data
   - `us_income_statement` - Should have AAPL data
   - `us_cashflow_statement` - Should have AAPL data

### Sample Query

```sql
-- Check Samsung (005930) Q3 2025 data
SELECT * FROM korean_balance_sheet 
WHERE symbol = '005930' 
  AND year = 2025 
  AND quarter = 3;

-- Check Apple (AAPL) Q3 2025 data
SELECT * FROM us_balance_sheet 
WHERE symbol = 'AAPL' 
  AND year = 2025 
  AND quarter = 3;
```

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Make sure you've activated the virtual environment and installed dependencies:
```bash
source ../.venv/bin/activate
uv pip install -e .
```

### Issue: "API key not configured"

**Solution**: Check your `.env` file and ensure all required variables are set:
```bash
cat .env
```

### Issue: "No data available for 2025Q3"

**Solution**: This is expected if the data hasn't been published yet. The script will automatically try 2024Q3 as a fallback.

### Issue: "Connection timeout" or "Network error"

**Solution**: Check your internet connection and firewall settings. Make sure the following domains are accessible:
- `opendart.fss.or.kr` (OPENDART API)
- `query1.finance.yahoo.com` (Yahoo Finance)
- `*.supabase.co` (Supabase)

### Issue: "Table not found"

**Solution**: Run the database migration scripts first:
```bash
# In Supabase SQL Editor:
# 1. Run database/init.sql
# 2. Run database/financial_statements.sql
```

## API Rate Limits

Be aware of API rate limits:

- **OPENDART**: 10,000 requests per day
- **yfinance**: No official limit, but use reasonable delays between requests
- **Supabase**: Based on your plan (free tier: 500MB database, 2GB bandwidth)

## Data Freshness

Financial statement data availability:

- **Korean stocks (OPENDART)**: Quarterly data typically available 45 days after quarter end
- **US stocks (yfinance)**: Data usually available within days of earnings release
- **202509 (Q3 2025)**: Data will be available around November 2025

If testing before Q3 2025 data is available, the script will use the most recent available data (e.g., 2024Q3).

## Next Steps

After successfully running tests locally:

1. Review the test results in `backend/test_results/`
2. Check raw API responses to understand data structure
3. Verify data quality in Supabase dashboard
4. Use the stored data in your HTS application frontend
5. Set up automated data refresh workflows

## Getting API Keys

### OPENDART API Key
1. Visit https://opendart.fss.or.kr/
2. Create an account
3. Generate an API key (free)

### Supabase Credentials
1. Visit https://supabase.com/
2. Create a project
3. Get URL and anon key from project settings

### Korean Investment Securities (Optional)
1. Visit https://apiportal.koreainvestment.com/
2. Register and apply for API access
3. Get API key and secret

## Support

For issues or questions:
- Check `backend/API_TEST_REPORT.md` for detailed test information
- Review `backend/README.md` for backend documentation
- Check GitHub Issues for known problems

---

**Last Updated**: 2026-02-05  
**Script Version**: 1.0  
**Compatible with**: Python 3.11+, UV package manager
