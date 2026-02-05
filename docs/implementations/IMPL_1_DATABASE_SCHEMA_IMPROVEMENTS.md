## Financial Database Schema Improvements Implementation

**Document**: IMPL_1_DATABASE_SCHEMA_IMPROVEMENTS.md  
**Date**: February 5, 2026  
**Status**: Ready for Implementation

## Executive Summary

After comprehensive testing of actual financial data from yfinance (AAPL, IONQ) and OPENDART (Samsung 005930, SK Hynix 000660) for 2024 Q1-Q4, we have identified critical improvements needed for the database schema. The primary issues are:

1. **Currency unit ambiguity** - Schema doesn't specify if values are actual or in millions
2. **Missing API field mappings** - No documentation linking database columns to API fields
3. **Incomplete field coverage** - Many important fields not captured

## Key Findings

### Currency Units

**yfinance (US stocks):**
- Returns values in **actual USD** (not millions)
- Example: Total Assets = $115,030,433,000 (stored as-is)
- Currency field in API: "USD"

**OPENDART (Korean stocks):**
- Returns values in **millions of KRW** (백만원)
- Example: 자산총계 = 401,405,399 (means 401,405,399 million KRW = 401 trillion KRW)
- This is standard OPENDART format

### Field Coverage Analysis

**yfinance provides:**
- Balance Sheet: 83 unique fields (we capture ~13)
- Income Statement: 46 unique fields (we capture ~11)
- Cash Flow: 62 unique fields (we capture ~11)

**OPENDART provides:**
- Balance Sheet: 78 unique fields (we capture ~13)
- Income Statement: 51 unique fields (we capture ~11)
- Cash Flow: 91 unique fields (we capture ~11)

**Current coverage: ~15-20% of available fields**

## Implementation Plan

### Phase 1: Add Column Comments (IMMEDIATE - No Schema Changes)

**Objective**: Document currency units and API field mappings without altering table structure.

**Benefits**:
- Zero risk (no schema changes)
- Immediate clarity for developers
- Essential for data validation
- Required for accurate reporting

**Implementation**:

The new schema file `financial_statements_v2.sql` includes:

1. **Table-level comments** documenting currency units:
   ```sql
   COMMENT ON TABLE us_balance_sheet IS 'Balance sheet data from yfinance API - Values in actual USD (not millions)';
   COMMENT ON TABLE korean_balance_sheet IS 'Balance sheet data from OPENDART API - Values in millions of KRW (백만원)';
   ```

2. **Column-level comments** mapping to API fields:
   ```sql
   COMMENT ON COLUMN us_balance_sheet.total_assets IS 'yfinance: Total Assets | Unit: USD | Example avg: $115B';
   COMMENT ON COLUMN korean_balance_sheet.total_assets IS 'OPENDART: 자산총계 | Unit: 백만원 (millions KRW)';
   ```

3. **Format**: `API_NAME: field_name | Unit: unit_description | Notes (if any)`

### Phase 2: Verify Data Types (NEXT SPRINT)

**Objective**: Ensure NUMERIC(20, 2) can handle all actual values.

**Test Cases**:

1. **US stocks - Maximum values**:
   - Total Assets: Up to $380B (Apple)
   - Needs: 12 digits before decimal → NUMERIC(20,2) ✓

2. **Korean stocks - Maximum values**:
   - 자산총계: Up to 401,000,000 (millions) = 401 trillion KRW
   - Needs: 15 digits before decimal → NUMERIC(20,2) ✓

3. **Negative values**:
   - Treasury Stock: Negative values common
   - Net Loss: Negative allowed → NUMERIC(20,2) ✓

4. **Decimal precision**:
   - EPS values: $1.25, $0.05 → NUMERIC(10,4) ✓

**Conclusion**: Current data types are adequate.

### Phase 3: Expand Field Coverage (FUTURE)

**Priority Fields to Add**:

#### US Balance Sheet Additional Fields
```sql
-- High Priority (used in financial analysis)
net_debt NUMERIC(20, 2),                    -- yfinance: Net Debt
working_capital NUMERIC(20, 2),             -- yfinance: Working Capital
invested_capital NUMERIC(20, 2),            -- yfinance: Invested Capital
tangible_book_value NUMERIC(20, 2),         -- yfinance: Tangible Book Value

-- Medium Priority
available_for_sale_securities NUMERIC(20, 2),  -- yfinance: Available For Sale Securities
ordinary_shares_number BIGINT,              -- yfinance: Ordinary Shares Number
```

#### Korean Balance Sheet Additional Fields
```sql
-- High Priority
non_controlling_interest NUMERIC(20, 2),    -- OPENDART: 비지배지분
capital_stock NUMERIC(20, 2),               -- OPENDART: 자본금
treasury_stock NUMERIC(20, 2),              -- OPENDART: Not directly available

-- Medium Priority
deferred_tax_assets NUMERIC(20, 2),         -- OPENDART: 이연법인세자산
deferred_tax_liabilities NUMERIC(20, 2),    -- OPENDART: 이연법인세부채
```

#### Income Statement Additional Fields
```sql
-- US (yfinance)
ebit NUMERIC(20, 2),                        -- yfinance: EBIT
normalized_ebitda NUMERIC(20, 2),           -- yfinance: Normalized EBITDA
total_expenses NUMERIC(20, 2),              -- yfinance: Total Expenses

-- Korean (OPENDART)
equity_method_income NUMERIC(20, 2),        -- OPENDART: 지분법이익
non_controlling_interest_income NUMERIC(20, 2), -- OPENDART: 비지배지분
```

## Migration Strategy

### Step 1: Backup Current Schema
```sql
-- Export current schema
pg_dump -h [host] -U [user] -d [database] --schema-only > backup_schema.sql

-- Export current data
pg_dump -h [host] -U [user] -d [database] --data-only > backup_data.sql
```

### Step 2: Apply Comments (Safe - No Downtime)
```sql
-- Run comments from financial_statements_v2.sql
-- These are additive and won't affect existing data
\i database/financial_statements_v2.sql
```

### Step 3: Verify Comments
```sql
-- Check column comments were applied
SELECT 
    table_name,
    column_name,
    col_description((table_schema||'.'||table_name)::regclass::oid, ordinal_position) as column_comment
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name LIKE '%balance_sheet%'
ORDER BY table_name, ordinal_position;
```

### Step 4: Update Application Code

**Data Insertion Functions** - Add unit conversion awareness:

```python
def insert_us_balance_sheet(data: Dict) -> None:
    """
    Insert US balance sheet data.
    
    Note: yfinance values are in actual USD, no conversion needed.
    Direct mapping from API response to database.
    """
    processed_data = {
        'total_assets': data.get('Total Assets'),  # Already in USD
        'current_assets': data.get('Current Assets'),  # Already in USD
        # ... etc
    }
    # Insert into database
    
def insert_korean_balance_sheet(data: Dict) -> None:
    """
    Insert Korean balance sheet data.
    
    Note: OPENDART values are ALREADY in millions of KRW.
    No conversion needed - store as-is from API.
    """
    processed_data = {
        'total_assets': data.get('자산총계'),  # Already in millions KRW
        'current_assets': data.get('유동자산'),  # Already in millions KRW
        # ... etc
    }
    # Insert into database
```

**Display Functions** - Add unit formatting:

```python
def format_us_amount(amount: Decimal) -> str:
    """Format US amounts for display."""
    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.2f}B"
    elif amount >= 1_000_000:
        return f"${amount / 1_000_000:.2f}M"
    else:
        return f"${amount:,.2f}"

def format_korean_amount(amount: Decimal) -> str:
    """
    Format Korean amounts for display.
    
    Input: millions of KRW (as stored in DB)
    Output: Formatted string in appropriate unit
    """
    # amount is in millions, so 1000 = 1 billion KRW = 1조원
    if amount >= 1_000_000:
        return f"{amount / 1_000_000:.2f}조원"  # Trillions
    elif amount >= 1_000:
        return f"{amount / 1_000:.2f}억원"  # Billions (actually 10억)
    else:
        return f"{amount:.2f}백만원"  # Millions
```

## Testing Plan

### Test 1: Data Integrity Check
```python
# tests/test_schema_improvements.py

def test_us_data_storage_retrieval():
    """Verify US data stored and retrieved correctly."""
    # Insert AAPL data
    test_data = {
        'symbol': 'AAPL',
        'year': 2024,
        'quarter': 4,
        'total_assets': 115030433000,  # $115B in actual USD
        # ... other fields
    }
    insert_us_balance_sheet(test_data)
    
    # Retrieve and verify
    retrieved = get_us_balance_sheet('AAPL', 2024, 4)
    assert retrieved['total_assets'] == 115030433000
    
    # Verify formatting
    formatted = format_us_amount(retrieved['total_assets'])
    assert formatted == "$115.03B"

def test_korean_data_storage_retrieval():
    """Verify Korean data stored and retrieved correctly."""
    # Insert Samsung data
    test_data = {
        'symbol': '005930',
        'year': 2024,
        'quarter': 4,
        'total_assets': 401405399,  # In millions KRW = 401 trillion
        # ... other fields
    }
    insert_korean_balance_sheet(test_data)
    
    # Retrieve and verify
    retrieved = get_korean_balance_sheet('005930', 2024, 4)
    assert retrieved['total_assets'] == 401405399
    
    # Verify formatting
    formatted = format_korean_amount(retrieved['total_assets'])
    assert formatted == "401.41조원"
```

### Test 2: Cross-Market Comparison
```python
def test_cross_market_comparison():
    """Test comparing US and Korean stocks with correct units."""
    # Get data
    aapl = get_us_balance_sheet('AAPL', 2024, 4)
    samsung = get_korean_balance_sheet('005930', 2024, 4)
    
    # Convert both to USD for comparison (using exchange rate)
    exchange_rate = 1300  # KRW per USD (example)
    
    aapl_assets_usd = aapl['total_assets']  # Already in USD
    samsung_assets_usd = (samsung['total_assets'] * 1_000_000) / exchange_rate
    
    # Compare
    print(f"AAPL Assets: ${aapl_assets_usd:,.0f}")
    print(f"Samsung Assets: ${samsung_assets_usd:,.0f}")
```

### Test 3: Comment Verification
```python
def test_column_comments_exist():
    """Verify all columns have proper comments."""
    tables = [
        'us_balance_sheet',
        'korean_balance_sheet',
        'us_income_statement',
        'korean_income_statement',
        'us_cashflow_statement',
        'korean_cashflow_statement'
    ]
    
    for table in tables:
        comments = get_column_comments(table)
        for column, comment in comments.items():
            if column not in ['id', 'created_at', 'updated_at', 'symbol', 'year', 'quarter', 'company_name', 'report_code']:
                # All data columns should have comments
                assert comment is not None, f"{table}.{column} missing comment"
                assert 'Unit:' in comment, f"{table}.{column} comment missing unit"
                assert any(api in comment for api in ['yfinance:', 'OPENDART:']), f"{table}.{column} missing API field"
```

## Documentation Updates

### Update Files:
1. **database/schema.md** - Add currency unit explanations
2. **docs/SUPABASE_INTEGRATION.md** - Add data type notes
3. **docs/API.md** - Add response format documentation
4. **backend/src/models/README.md** - Add model field mapping

### New Documentation:
1. **docs/CURRENCY_UNITS.md** - Detailed explanation of unit handling
2. **docs/API_FIELD_MAPPING.md** - Complete field mapping reference

## Rollback Plan

If issues arise:

1. **Comments causing issues** (unlikely):
   ```sql
   -- Remove all comments
   COMMENT ON TABLE us_balance_sheet IS NULL;
   COMMENT ON COLUMN us_balance_sheet.total_assets IS NULL;
   -- ... etc
   ```

2. **Data type issues** (very unlikely with current NUMERIC(20,2)):
   - Restore from backup_data.sql
   - Investigate specific failing values
   - Adjust precision if needed

## Success Criteria

✅ All 6 tables have table-level comments  
✅ All numeric columns have column-level comments with:
   - API field name
   - Unit specification
   - Example values (where helpful)  
✅ All existing data remains intact  
✅ All tests pass  
✅ Documentation updated  
✅ Team trained on unit handling  

## Timeline

- **Week 1**: Apply comments (1 hour)
- **Week 1**: Verify comments (1 hour)
- **Week 1**: Update documentation (2 hours)
- **Week 2**: Team training (1 hour)
- **Week 2**: Add display formatting functions (4 hours)
- **Week 2**: Comprehensive testing (4 hours)

**Total Effort**: ~2 weeks

## Conclusion

The improved schema with comprehensive comments will:
1. Eliminate currency unit confusion
2. Provide clear API field mappings
3. Enable accurate cross-market comparisons
4. Serve as living documentation
5. Reduce onboarding time for new developers

All changes in Phase 1 are **zero-risk** as they only add metadata without touching data or structure. Implementation is recommended immediately.

---

## Appendix: Sample Data

### US Stock (AAPL) - Actual Values
```json
{
  "symbol": "AAPL",
  "year": 2024,
  "quarter": 4,
  "total_assets": 115030433000,
  "current_assets": 44671400667,
  "cash_and_cash_equivalents": 10127855000,
  "currency": "USD",
  "note": "Values are in actual USD, not millions"
}
```

### Korean Stock (Samsung 005930) - Actual Values
```json
{
  "symbol": "005930",
  "year": 2024,
  "quarter": 4,
  "자산총계": 401405399,
  "유동자산": 163120999,
  "현금및현금성자산": 35051060,
  "unit": "백만원 (millions KRW)",
  "note": "자산총계 401,405,399백만원 = 401조원"
}
```

## References

- Test Results: `backend/test_results/2024_complete_data/`
- Analysis Report: `docs/reports/TEST_1_FINANCIAL_DATA_STRUCTURE_ANALYSIS.md`
- Original Schema: `database/financial_statements.sql`
- Improved Schema: `database/financial_statements_v2.sql`
