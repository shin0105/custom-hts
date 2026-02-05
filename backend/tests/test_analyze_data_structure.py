#!/usr/bin/env python3
"""
Analyze collected financial data and compare with database schema.

This script:
1. Loads all collected JSON data
2. Analyzes field names, data types, and value ranges
3. Identifies currency units (dollars vs millions)
4. Compares with current database schema
5. Generates recommendations for schema improvements
"""

import sys
from pathlib import Path
import json
from typing import Dict, Any, List, Set
from collections import defaultdict
import re

# Add src to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir / "src"))


DATA_DIR = backend_dir / "test_results" / "2024_complete_data"
REPORT_DIR = backend_dir.parent / "docs" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(filepath: Path) -> Dict[str, Any]:
    """Load JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_yfinance_field(
    field_name: str, values: List[Any]
) -> Dict[str, Any]:
    """Analyze a yfinance field to determine its characteristics."""
    non_null_values = [v for v in values if v is not None]

    if not non_null_values:
        return {
            "field_name": field_name,
            "all_null": True,
            "data_type": "unknown",
            "unit": "unknown",
        }

    # Determine data type
    sample_value = non_null_values[0]
    if isinstance(sample_value, (int, float)):
        data_type = "numeric"
        min_val = min(non_null_values) if non_null_values else None
        max_val = max(non_null_values) if non_null_values else None
        avg_val = (
            sum(non_null_values) / len(non_null_values)
            if non_null_values
            else None
        )
    else:
        data_type = "text"
        min_val = max_val = avg_val = None

    # Determine unit based on field name and magnitude
    unit = "unknown"
    if data_type == "numeric" and avg_val:
        # Check field name for hints
        field_lower = field_name.lower()
        if any(
            word in field_lower
            for word in ["price", "eps", "ratio", "rate", "margin", "percent"]
        ):
            unit = "dollars_or_ratio"
        elif abs(avg_val) > 1_000_000:
            unit = "dollars_actual"  # Actual dollar amounts
        else:
            unit = "dollars_or_count"

    return {
        "field_name": field_name,
        "all_null": False,
        "data_type": data_type,
        "unit": unit,
        "min": min_val,
        "max": max_val,
        "avg": avg_val,
        "null_count": len(values) - len(non_null_values),
        "non_null_count": len(non_null_values),
    }


def analyze_opendart_field(
    field_name: str, values: List[str]
) -> Dict[str, Any]:
    """Analyze an OPENDART field to determine its characteristics."""
    non_null_values = [v for v in values if v]

    if not non_null_values:
        return {
            "field_name": field_name,
            "all_null": True,
            "data_type": "unknown",
            "unit": "unknown",
        }

    # Try to convert to numeric
    numeric_values = []
    for val in non_null_values:
        try:
            # Remove commas and convert
            clean_val = str(val).replace(",", "").strip()
            if clean_val and clean_val != "-":
                numeric_values.append(float(clean_val))
        except (ValueError, AttributeError):
            pass

    if numeric_values:
        data_type = "numeric"
        min_val = min(numeric_values)
        max_val = max(numeric_values)
        avg_val = sum(numeric_values) / len(numeric_values)

        # Determine unit - OPENDART typically uses millions of KRW
        field_lower = field_name.lower()
        if "금액" in field_name or "amount" in field_lower:
            if abs(avg_val) > 1_000:
                unit = "KRW_millions"  # Values are in millions of KRW
            else:
                unit = "KRW_actual"
        else:
            unit = "numeric_value"
    else:
        data_type = "text"
        min_val = max_val = avg_val = None
        unit = "text"

    return {
        "field_name": field_name,
        "all_null": False,
        "data_type": data_type,
        "unit": unit,
        "min": min_val,
        "max": max_val,
        "avg": avg_val,
        "null_count": len(values) - len(non_null_values),
        "non_null_count": len(non_null_values),
    }


def analyze_us_stocks() -> Dict[str, Any]:
    """Analyze US stock data from yfinance."""
    print("\n" + "=" * 80)
    print("ANALYZING US STOCKS (yfinance)")
    print("=" * 80)

    us_dir = DATA_DIR / "us_stocks"
    analysis = {
        "stocks": {},
        "field_analysis": {
            "balance_sheet": {},
            "income_statement": {},
            "cashflow_statement": {},
        },
        "field_mapping": {
            "balance_sheet": {},
            "income_statement": {},
            "cashflow_statement": {},
        },
    }

    if not us_dir.exists():
        print("  ⚠️  US stocks directory not found")
        return analysis

    # Collect all fields and values
    field_values = {
        "balance_sheet": defaultdict(list),
        "income_statement": defaultdict(list),
        "cashflow_statement": defaultdict(list),
    }

    for json_file in us_dir.glob("*.json"):
        print(f"\n  Processing: {json_file.name}")
        data = load_json(json_file)
        symbol = data["symbol"]

        # Process quarterly data
        for quarter_key, quarter_data in data.get(
            "quarterly_data", {}
        ).items():
            if not quarter_key.startswith("2024Q"):
                continue

            for stmt_type in [
                "balance_sheet",
                "income_statement",
                "cashflow_statement",
            ]:
                if stmt_type in quarter_data:
                    for field_name, value in quarter_data[stmt_type].items():
                        field_values[stmt_type][field_name].append(value)

    # Analyze each field
    print("\n  Analyzing fields...")
    for stmt_type in [
        "balance_sheet",
        "income_statement",
        "cashflow_statement",
    ]:
        print(f"\n    {stmt_type.replace('_', ' ').title()}:")

        for field_name, values in sorted(field_values[stmt_type].items()):
            field_analysis = analyze_yfinance_field(field_name, values)
            analysis["field_analysis"][stmt_type][field_name] = field_analysis

            if not field_analysis["all_null"]:
                print(
                    f"      {field_name}: {field_analysis['data_type']}, unit: {field_analysis['unit']}"
                )
                if field_analysis["avg"]:
                    print(f"        avg: {field_analysis['avg']:,.0f}")

    return analysis


def analyze_korean_stocks() -> Dict[str, Any]:
    """Analyze Korean stock data from OPENDART."""
    print("\n" + "=" * 80)
    print("ANALYZING KOREAN STOCKS (OPENDART)")
    print("=" * 80)

    korean_dir = DATA_DIR / "korean_stocks"
    analysis = {
        "stocks": {},
        "field_analysis": {
            "balance_sheet": {},
            "income_statement": {},
            "cashflow_statement": {},
        },
        "field_mapping": {
            "balance_sheet": {},
            "income_statement": {},
            "cashflow_statement": {},
        },
    }

    if not korean_dir.exists():
        print("  ⚠️  Korean stocks directory not found")
        return analysis

    # Collect all fields and values
    field_values = {
        "balance_sheet": defaultdict(list),
        "income_statement": defaultdict(list),
        "cashflow_statement": defaultdict(list),
    }

    for json_file in korean_dir.glob("*.json"):
        print(f"\n  Processing: {json_file.name}")
        data = load_json(json_file)
        symbol = data["symbol"]

        # Process quarterly data
        for quarter_key, quarter_data in data.get(
            "quarterly_data", {}
        ).items():
            for stmt_type in [
                "balance_sheet",
                "income_statement",
                "cashflow_statement",
            ]:
                if stmt_type in quarter_data:
                    for field_name, value in quarter_data[stmt_type].items():
                        field_values[stmt_type][field_name].append(value)

    # Analyze each field
    print("\n  Analyzing fields...")
    for stmt_type in [
        "balance_sheet",
        "income_statement",
        "cashflow_statement",
    ]:
        print(f"\n    {stmt_type.replace('_', ' ').title()}:")

        for field_name, values in sorted(field_values[stmt_type].items()):
            field_analysis = analyze_opendart_field(field_name, values)
            analysis["field_analysis"][stmt_type][field_name] = field_analysis

            if not field_analysis["all_null"]:
                print(
                    f"      {field_name}: {field_analysis['data_type']}, unit: {field_analysis['unit']}"
                )
                if field_analysis.get("avg"):
                    print(f"        avg: {field_analysis['avg']:,.0f}")

    return analysis


def compare_with_schema(
    us_analysis: Dict, korean_analysis: Dict
) -> Dict[str, Any]:
    """Compare analysis results with current database schema."""
    print("\n" + "=" * 80)
    print("COMPARING WITH DATABASE SCHEMA")
    print("=" * 80)

    comparison = {
        "us_missing_fields": {},
        "korean_missing_fields": {},
        "type_mismatches": {},
        "unit_issues": {},
        "recommendations": [],
    }

    # Current schema columns (simplified - focusing on main fields)
    us_schema_columns = {
        "balance_sheet": [
            "total_assets",
            "current_assets",
            "cash_and_cash_equivalents",
            "total_liabilities",
            "current_liabilities",
            "stockholders_equity",
        ],
        "income_statement": [
            "total_revenue",
            "cost_of_revenue",
            "gross_profit",
            "operating_income",
            "net_income",
            "basic_eps",
        ],
        "cashflow_statement": [
            "operating_cash_flow",
            "investing_cash_flow",
            "financing_cash_flow",
            "free_cash_flow",
            "net_change_cash",
        ],
    }

    korean_schema_columns = {
        "balance_sheet": [
            "total_assets",
            "current_assets",
            "cash_and_cash_equivalents",
            "total_liabilities",
            "current_liabilities",
            "total_equity",
        ],
        "income_statement": [
            "revenue",
            "cost_of_revenue",
            "gross_profit",
            "operating_income",
            "net_income",
            "earnings_per_share",
        ],
        "cashflow_statement": [
            "operating_cash_flow",
            "investing_cash_flow",
            "financing_cash_flow",
            "free_cash_flow",
            "net_change_cash",
        ],
    }

    print("\n  Checking for schema coverage...")

    # Check US data coverage
    print("\n  US Stocks (yfinance):")
    for stmt_type, schema_cols in us_schema_columns.items():
        print(f"\n    {stmt_type}:")
        available_fields = set(us_analysis["field_analysis"][stmt_type].keys())

        for col in schema_cols:
            # Try to find matching field
            matches = [
                f
                for f in available_fields
                if col.replace("_", " ").lower() in f.lower()
                or f.replace("_", " ").lower() in col.replace("_", " ").lower()
            ]

            if matches:
                print(f"      ✓ {col} -> {matches[0]}")
            else:
                print(f"      ✗ {col} -> NOT FOUND")
                if stmt_type not in comparison["us_missing_fields"]:
                    comparison["us_missing_fields"][stmt_type] = []
                comparison["us_missing_fields"][stmt_type].append(col)

    # Check Korean data coverage
    print("\n  Korean Stocks (OPENDART):")
    for stmt_type, schema_cols in korean_schema_columns.items():
        print(f"\n    {stmt_type}:")
        available_fields = set(
            korean_analysis["field_analysis"][stmt_type].keys()
        )

        for col in schema_cols:
            # Try to find matching field (Korean fields are in Korean)
            korean_keywords = {
                "total_assets": "자산총계",
                "current_assets": "유동자산",
                "cash": "현금",
                "total_liabilities": "부채총계",
                "current_liabilities": "유동부채",
                "total_equity": "자본총계",
                "revenue": "매출액",
                "operating_income": "영업이익",
                "net_income": "당기순이익",
            }

            keyword = korean_keywords.get(col, col)
            matches = [f for f in available_fields if keyword in f]

            if matches:
                print(f"      ✓ {col} -> {matches[0]}")
            else:
                print(
                    f"      ✗ {col} -> NOT FOUND (searching for '{keyword}')"
                )
                if stmt_type not in comparison["korean_missing_fields"]:
                    comparison["korean_missing_fields"][stmt_type] = []
                comparison["korean_missing_fields"][stmt_type].append(col)

    # Generate recommendations
    print("\n  Generating recommendations...")

    comparison["recommendations"] = [
        {
            "priority": "HIGH",
            "issue": "Currency units need clarification",
            "detail": "yfinance values are in actual dollars, OPENDART values appear to be in millions of KRW",
            "action": "Add COMMENT to each column specifying the unit (e.g., 'USD' or 'KRW millions')",
        },
        {
            "priority": "HIGH",
            "issue": "Many fields available but not captured",
            "detail": f"yfinance: {len(us_analysis['field_analysis']['balance_sheet'])} fields, OPENDART: {len(korean_analysis['field_analysis']['balance_sheet'])} fields",
            "action": "Consider adding most important missing fields or expand raw_data JSONB usage",
        },
        {
            "priority": "MEDIUM",
            "issue": "Field name mapping needed",
            "detail": "Current schema uses generic names but API fields are more specific",
            "action": "Add COMMENT with exact API field name for each column",
        },
    ]

    for rec in comparison["recommendations"]:
        print(f"    [{rec['priority']}] {rec['issue']}")
        print(f"        {rec['detail']}")
        print(f"        Action: {rec['action']}")

    return comparison


def generate_markdown_report(
    us_analysis: Dict, korean_analysis: Dict, comparison: Dict
):
    """Generate detailed markdown report."""
    print("\n" + "=" * 80)
    print("GENERATING MARKDOWN REPORT")
    print("=" * 80)

    report_content = f"""# Financial Data Structure Analysis Report

**Generated:** {Path(__file__).name}  
**Date:** 2024 Q1-Q4 Complete Data Analysis

## Executive Summary

This report analyzes the actual financial data structure from yfinance (US stocks) and OPENDART (Korean stocks) and compares it with our current database schema.

### Data Collected

- **US Stocks:** AAPL, IONQ (2024 Q1-Q4)
- **Korean Stocks:** 005930 (Samsung), 000660 (SK Hynix) (2024 Q1-Q4)

### Key Findings

#### yfinance Data Structure
- Balance Sheet: {len(us_analysis['field_analysis']['balance_sheet'])} unique fields
- Income Statement: {len(us_analysis['field_analysis']['income_statement'])} unique fields
- Cash Flow Statement: {len(us_analysis['field_analysis']['cashflow_statement'])} unique fields
- **Currency:** USD (actual dollar amounts, not millions)

#### OPENDART Data Structure
- Balance Sheet: {len(korean_analysis['field_analysis']['balance_sheet'])} unique fields
- Income Statement: {len(korean_analysis['field_analysis']['income_statement'])} unique fields
- Cash Flow Statement: {len(korean_analysis['field_analysis']['cashflow_statement'])} unique fields
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

"""

    # Add top US balance sheet fields
    us_bs_fields = us_analysis["field_analysis"]["balance_sheet"]
    important_us_bs = [
        f
        for f, data in us_bs_fields.items()
        if not data["all_null"] and data.get("non_null_count", 0) > 3
    ][:20]

    for field in important_us_bs:
        field_data = us_bs_fields[field]
        report_content += f"\n- **{field}**"
        report_content += f"\n  - Type: {field_data['data_type']}"
        report_content += f"\n  - Unit: {field_data['unit']}"
        if field_data.get("avg"):
            report_content += f"\n  - Average: ${field_data['avg']:,.0f}"

    # Add Korean balance sheet fields
    report_content += "\n\n### Korean Balance Sheet (OPENDART)\n\nTop 20 most important fields:\n"

    korean_bs_fields = korean_analysis["field_analysis"]["balance_sheet"]
    important_korean_bs = [
        f
        for f, data in korean_bs_fields.items()
        if not data["all_null"] and data.get("non_null_count", 0) > 3
    ][:20]

    for field in important_korean_bs:
        field_data = korean_bs_fields[field]
        report_content += f"\n- **{field}**"
        report_content += f"\n  - Type: {field_data['data_type']}"
        report_content += f"\n  - Unit: {field_data['unit']}"
        if field_data.get("avg"):
            report_content += f"\n  - Average: {field_data['avg']:,.0f} (likely millions KRW)"

    # Add recommendations section
    report_content += "\n\n## Recommendations for Schema Updates\n\n"

    for i, rec in enumerate(comparison["recommendations"], 1):
        report_content += f"\n### {i}. [{rec['priority']}] {rec['issue']}\n\n"
        report_content += f"**Issue:** {rec['detail']}\n\n"
        report_content += f"**Action:** {rec['action']}\n"

    # Add implementation plan
    report_content += """

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
"""

    # Save report
    report_path = REPORT_DIR / "TEST_1_FINANCIAL_DATA_STRUCTURE_ANALYSIS.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"\n  ✅ Report saved to: {report_path}")

    # Also save detailed JSON analysis
    full_analysis = {
        "us_analysis": us_analysis,
        "korean_analysis": korean_analysis,
        "comparison": comparison,
    }

    json_path = DATA_DIR / "complete_analysis.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(full_analysis, f, indent=2, ensure_ascii=False)

    print(f"  ✅ Detailed JSON saved to: {json_path}")


def main():
    """Main analysis execution."""
    print("=" * 80)
    print("FINANCIAL DATA STRUCTURE ANALYSIS")
    print("=" * 80)

    # Analyze US stocks
    us_analysis = analyze_us_stocks()

    # Analyze Korean stocks
    korean_analysis = analyze_korean_stocks()

    # Compare with schema
    comparison = compare_with_schema(us_analysis, korean_analysis)

    # Generate report
    generate_markdown_report(us_analysis, korean_analysis, comparison)

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\n📊 Summary:")
    print(
        f"  - US fields analyzed: {sum(len(v) for v in us_analysis['field_analysis'].values())}"
    )
    print(
        f"  - Korean fields analyzed: {sum(len(v) for v in korean_analysis['field_analysis'].values())}"
    )
    print(f"  - Recommendations: {len(comparison['recommendations'])}")
    print("\n✅ Check the reports directory for detailed analysis!")


if __name__ == "__main__":
    main()
