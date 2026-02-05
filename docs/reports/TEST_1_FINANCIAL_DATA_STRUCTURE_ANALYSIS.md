# Financial Data Structure Analysis Report

**Generated:** test_analyze_data_structure.py  
**Date:** 2024 Q1-Q4 Complete Data Analysis

## Executive Summary

This report analyzes the actual financial data structure from yfinance (US stocks) and OPENDART (Korean stocks) and compares it with our current database schema.

### Data Collected

- **US Stocks:** AAPL, IONQ (2024 Q1-Q4)
- **Korean Stocks:** 005930 (Samsung), 000660 (SK Hynix) (2024 Q1-Q4)

### Key Findings

#### yfinance Data Structure
- Balance Sheet: 83 unique fields
- Income Statement: 46 unique fields
- Cash Flow Statement: 62 unique fields
- **Currency:** USD (actual dollar amounts, not millions)

#### OPENDART Data Structure
- Balance Sheet: 78 unique fields
- Income Statement: 51 unique fields
- Cash Flow Statement: 91 unique fields
- **Currency:** KRW (values appear to be in millions of KRW based on magnitudes)

## Critical Issues

### 1. Currency Unit Inconsistency

**Issue:** The database schema does not clearly specify currency units.

- yfinance returns values in **actual USD** (e.g., $100,000,000 for 100M)
- OPENDART returns values that appear to be in **millions of KRW** (e.g., 100000 for 100B KRW)

**Recommendation:** Add explicit COMMENT to each numeric column specifying:
- For US tables: "Value in USD"
- For Korean tables: "Value in millions of KRW (단위: 백만원)"

### 2. Missing Field Mappings

**Issue:** Current schema uses generic field names but doesn't map to actual API field names.

**Recommendation:** Add COMMENT for each column showing the exact field name from the API:

'''sql
COMMENT ON COLUMN us_balance_sheet.total_assets IS 'yfinance: Total Assets (USD)';
COMMENT ON COLUMN korean_balance_sheet.total_assets IS 'OPENDART: 자산총계 (백만원)';
'''

### 3. Data Type Considerations

All numeric fields should use `NUMERIC(20, 2)` to handle:
- Large values (billions in USD or trillions in KRW)
- Negative values (losses, debt, etc.)
- Decimal precision for ratios and per-share values

## Detailed Field Analysis

### US Balance Sheet (yfinance)

Top 20 most important fields:


- **Other Current Liabilities**
  - Type: numeric
  - Unit: dollars_actual
  - Average: $15,288,042,750

### Korean Balance Sheet (OPENDART)

Top 20 most important fields:

- **공동기업 및 관계기업투자**
  - Type: numeric
  - Unit: numeric_value
  - Average: 32,147,080,250,000 (likely millions KRW)
- **금융업채권**
  - Type: numeric
  - Unit: numeric_value
  - Average: 71,206,959,000,000 (likely millions KRW)
- **기타금융부채**
  - Type: numeric
  - Unit: numeric_value
  - Average: 99,227,750,000 (likely millions KRW)
- **기타금융자산**
  - Type: numeric
  - Unit: numeric_value
  - Average: 5,680,095,000,000 (likely millions KRW)
- **기타부채**
  - Type: numeric
  - Unit: numeric_value
  - Average: 6,505,134,000,000 (likely millions KRW)
- **기타비유동자산**
  - Type: numeric
  - Unit: numeric_value
  - Average: 12,854,487,750,000 (likely millions KRW)
- **기타유동자산**
  - Type: numeric
  - Unit: numeric_value
  - Average: 6,117,942,250,000 (likely millions KRW)
- **기타자본항목**
  - Type: numeric
  - Unit: numeric_value
  - Average: 4,328,089,000,000 (likely millions KRW)
- **기타자산**
  - Type: numeric
  - Unit: numeric_value
  - Average: 2,569,482,250,000 (likely millions KRW)
- **기타채권**
  - Type: numeric
  - Unit: numeric_value
  - Average: 1,314,308,500,000 (likely millions KRW)
- **기타포괄손익누계액**
  - Type: numeric
  - Unit: numeric_value
  - Average: 1,826,817,750,000 (likely millions KRW)
- **단기금융상품**
  - Type: numeric
  - Unit: numeric_value
  - Average: 29,369,822,875,000 (likely millions KRW)
- **단기당기손익-공정가치금융자산**
  - Type: numeric
  - Unit: numeric_value
  - Average: 30,834,500,000 (likely millions KRW)
- **단기차입금**
  - Type: numeric
  - Unit: numeric_value
  - Average: 9,447,686,375,000 (likely millions KRW)
- **당기법인세부채**
  - Type: numeric
  - Unit: numeric_value
  - Average: 3,157,259,625,000 (likely millions KRW)
- **당기법인세자산**
  - Type: numeric
  - Unit: numeric_value
  - Average: 153,295,750,000 (likely millions KRW)
- **당기손익-공정가치금융자산**
  - Type: numeric
  - Unit: numeric_value
  - Average: 1,283,919,750,000 (likely millions KRW)
- **리스부채**
  - Type: numeric
  - Unit: numeric_value
  - Average: 881,550,000,000 (likely millions KRW)
- **매각예정비유동자산**
  - Type: numeric
  - Unit: numeric_value
  - Average: 43,162,000,000 (likely millions KRW)
- **매입채무**
  - Type: numeric
  - Unit: numeric_value
  - Average: 12,270,416,875,000 (likely millions KRW)

## Recommendations for Schema Updates


### 1. [HIGH] Currency units need clarification

**Issue:** yfinance values are in actual dollars, OPENDART values appear to be in millions of KRW

**Action:** Add COMMENT to each column specifying the unit (e.g., 'USD' or 'KRW millions')

### 2. [HIGH] Many fields available but not captured

**Issue:** yfinance: 83 fields, OPENDART: 78 fields

**Action:** Consider adding most important missing fields or expand raw_data JSONB usage

### 3. [MEDIUM] Field name mapping needed

**Issue:** Current schema uses generic names but API fields are more specific

**Action:** Add COMMENT with exact API field name for each column


## Implementation Plan

### Phase 1: Add Column Comments (Immediate)

1. Add COMMENT to each column specifying:
   - Original API field name
   - Currency unit (USD or millions of KRW)
   - Any special handling notes

Example:
```sql
COMMENT ON COLUMN us_balance_sheet.total_assets IS 
  'yfinance: Total Assets | Unit: USD | API field: Total Assets';

COMMENT ON COLUMN korean_balance_sheet.total_assets IS 
  'OPENDART: 자산총계 | Unit: 백만원 (millions KRW) | API field: 자산총계';
```

### Phase 2: Verify Data Types (Next Sprint)

1. Ensure all numeric columns use NUMERIC(20, 2)
2. Test with actual max values from APIs
3. Verify handling of NULL values

### Phase 3: Expand Coverage (Future)

1. Identify most valuable missing fields
2. Add new columns for critical metrics not currently captured
3. Enhance raw_data JSONB documentation

## Conclusion

The current schema provides a good foundation but needs:
1. **Clear currency unit documentation**
2. **API field name mappings**
3. **Consistent data type usage**

All recommended changes can be implemented through SQL COMMENT statements without altering table structure, making this a low-risk improvement.
