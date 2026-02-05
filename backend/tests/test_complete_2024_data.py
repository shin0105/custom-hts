#!/usr/bin/env python3
"""
Comprehensive test to fetch complete financial data for 2024 Q1-Q4.

This test fetches:
- US stocks: AAPL, IONQ via yfinance
- Korean stocks: 005930 (Samsung), 056080 (Solactive) via OPENDART

Purpose:
1. Collect raw JSON responses from all APIs
2. Analyze actual data structures
3. Compare with database schema
4. Identify missing fields and data type issues
5. Verify currency units (Won/Dollars vs Million Won/Dollars)
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any, List
import os

# Add src to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir / "src"))

import yfinance as yf
import pandas as pd
from src.integrations.opendart import opendart_client


# Output directory for test results
OUTPUT_DIR = backend_dir / "test_results" / "2024_complete_data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def convert_to_json_serializable(obj: Any) -> Any:
    """Convert pandas/numpy objects to JSON-serializable formats."""
    if isinstance(obj, dict):
        return {
            str(k): convert_to_json_serializable(v) for k, v in obj.items()
        }
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    elif pd.isna(obj):
        return None
    elif hasattr(obj, "item"):  # numpy types
        return obj.item()
    else:
        return obj


def save_json(data: Any, filename: str, subfolder: str = "") -> Path:
    """Save data as JSON file."""
    if subfolder:
        output_path = OUTPUT_DIR / subfolder
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = OUTPUT_DIR

    # Convert data to JSON-serializable format
    serializable_data = convert_to_json_serializable(data)

    filepath = output_path / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(
            serializable_data, f, ensure_ascii=False, indent=2, default=str
        )

    return filepath


def test_yfinance_stock(symbol: str, year: int = 2024) -> Dict[str, Any]:
    """
    Fetch complete financial data for a US stock using yfinance.

    Returns all available financial statements and metadata.
    """
    print(f"\n{'='*80}")
    print(f"Testing yfinance: {symbol} - {year}")
    print(f"{'='*80}")

    ticker = yf.Ticker(symbol)
    results = {
        "symbol": symbol,
        "year": year,
        "company_name": None,
        "test_date": datetime.now().isoformat(),
        "quarterly_data": {},
        "annual_data": {},
        "info": {},
        "metadata": {},
    }

    try:
        # Get company info
        info = ticker.info
        results["info"] = info
        results["company_name"] = (
            info.get("longName") or info.get("shortName") or symbol
        )

        print(f"  Company: {results['company_name']}")
        print(f"  Currency: {info.get('currency', 'N/A')}")
        print(f"  Financial Currency: {info.get('financialCurrency', 'N/A')}")

    except Exception as e:
        print(f"  ⚠️  Error fetching info: {e}")

    # Quarterly Financial Statements
    print("\n  Fetching quarterly financial statements...")

    try:
        # Balance Sheet
        quarterly_bs = ticker.quarterly_balance_sheet
        if quarterly_bs is not None and not quarterly_bs.empty:
            print(f"    ✓ Quarterly Balance Sheet: {quarterly_bs.shape}")
            results["quarterly_data"]["balance_sheet"] = {
                "columns": [str(col) for col in quarterly_bs.columns],
                "index": list(quarterly_bs.index),
                "data": quarterly_bs.to_dict(),
            }

            # Extract 2024 quarters
            for col in quarterly_bs.columns:
                if col.year == year:
                    quarter = (col.month - 1) // 3 + 1
                    quarter_key = f"2024Q{quarter}"
                    results["quarterly_data"][quarter_key] = {
                        "balance_sheet": quarterly_bs[col].to_dict()
                    }

        # Income Statement
        quarterly_is = ticker.quarterly_income_stmt
        if quarterly_is is not None and not quarterly_is.empty:
            print(f"    ✓ Quarterly Income Statement: {quarterly_is.shape}")
            results["quarterly_data"]["income_statement"] = {
                "columns": [str(col) for col in quarterly_is.columns],
                "index": list(quarterly_is.index),
                "data": quarterly_is.to_dict(),
            }

            # Extract 2024 quarters
            for col in quarterly_is.columns:
                if col.year == year:
                    quarter = (col.month - 1) // 3 + 1
                    quarter_key = f"2024Q{quarter}"
                    if quarter_key not in results["quarterly_data"]:
                        results["quarterly_data"][quarter_key] = {}
                    results["quarterly_data"][quarter_key][
                        "income_statement"
                    ] = quarterly_is[col].to_dict()

        # Cash Flow Statement
        quarterly_cf = ticker.quarterly_cashflow
        if quarterly_cf is not None and not quarterly_cf.empty:
            print(f"    ✓ Quarterly Cash Flow: {quarterly_cf.shape}")
            results["quarterly_data"]["cashflow_statement"] = {
                "columns": [str(col) for col in quarterly_cf.columns],
                "index": list(quarterly_cf.index),
                "data": quarterly_cf.to_dict(),
            }

            # Extract 2024 quarters
            for col in quarterly_cf.columns:
                if col.year == year:
                    quarter = (col.month - 1) // 3 + 1
                    quarter_key = f"2024Q{quarter}"
                    if quarter_key not in results["quarterly_data"]:
                        results["quarterly_data"][quarter_key] = {}
                    results["quarterly_data"][quarter_key][
                        "cashflow_statement"
                    ] = quarterly_cf[col].to_dict()

    except Exception as e:
        print(f"    ⚠️  Error fetching quarterly statements: {e}")

    # Annual Financial Statements
    print("\n  Fetching annual financial statements...")

    try:
        # Balance Sheet
        annual_bs = ticker.balance_sheet
        if annual_bs is not None and not annual_bs.empty:
            print(f"    ✓ Annual Balance Sheet: {annual_bs.shape}")
            results["annual_data"]["balance_sheet"] = {
                "columns": [str(col) for col in annual_bs.columns],
                "index": list(annual_bs.index),
                "data": annual_bs.to_dict(),
            }

        # Income Statement
        annual_is = ticker.income_stmt
        if annual_is is not None and not annual_is.empty:
            print(f"    ✓ Annual Income Statement: {annual_is.shape}")
            results["annual_data"]["income_statement"] = {
                "columns": [str(col) for col in annual_is.columns],
                "index": list(annual_is.index),
                "data": annual_is.to_dict(),
            }

        # Cash Flow Statement
        annual_cf = ticker.cashflow
        if annual_cf is not None and not annual_cf.empty:
            print(f"    ✓ Annual Cash Flow: {annual_cf.shape}")
            results["annual_data"]["cashflow_statement"] = {
                "columns": [str(col) for col in annual_cf.columns],
                "index": list(annual_cf.index),
                "data": annual_cf.to_dict(),
            }

    except Exception as e:
        print(f"    ⚠️  Error fetching annual statements: {e}")

    # Save results
    filename = f"yfinance_{symbol}_{year}_complete.json"
    filepath = save_json(results, filename, "us_stocks")
    print(f"\n  ✅ Saved to: {filepath}")

    return results


def test_opendart_stock(symbol: str, year: int = 2024) -> Dict[str, Any]:
    """
    Fetch complete financial data for a Korean stock using OPENDART.

    Returns all available financial statements and metadata.
    """
    print(f"\n{'='*80}")
    print(f"Testing OPENDART: {symbol} - {year}")
    print(f"{'='*80}")

    results = {
        "symbol": symbol,
        "year": year,
        "test_date": datetime.now().isoformat(),
        "quarterly_data": {},
        "annual_data": {},
        "corp_code": None,
        "metadata": {},
    }

    try:
        # Get corp code
        corp_code = opendart_client.get_corp_code(symbol)
        results["corp_code"] = corp_code
        print(f"  Corp Code: {corp_code}")

        if not corp_code:
            print(f"  ⚠️  Could not find corp code for {symbol}")
            return results

    except Exception as e:
        print(f"  ⚠️  Error getting corp code: {e}")
        return results

    # Fetch quarterly data for 2024 Q1-Q4
    print("\n  Fetching quarterly financial statements...")
    for quarter in [1, 2, 3, 4]:
        quarter_key = f"2024Q{quarter}"
        print(f"\n    Processing {quarter_key}...")

        try:
            # Balance Sheet
            bs_data = opendart_client.get_balance_sheet(symbol, year, quarter)
            if bs_data:
                print(f"      ✓ Balance Sheet: {len(bs_data)} items")
                results["quarterly_data"][quarter_key] = {
                    "balance_sheet": bs_data
                }

            # Income Statement
            is_data = opendart_client.get_income_statement(
                symbol, year, quarter
            )
            if is_data:
                print(f"      ✓ Income Statement: {len(is_data)} items")
                if quarter_key not in results["quarterly_data"]:
                    results["quarterly_data"][quarter_key] = {}
                results["quarterly_data"][quarter_key][
                    "income_statement"
                ] = is_data

            # Cash Flow Statement
            cf_data = opendart_client.get_cash_flow(symbol, year, quarter)
            if cf_data:
                print(f"      ✓ Cash Flow: {len(cf_data)} items")
                if quarter_key not in results["quarterly_data"]:
                    results["quarterly_data"][quarter_key] = {}
                results["quarterly_data"][quarter_key][
                    "cashflow_statement"
                ] = cf_data

        except Exception as e:
            print(f"      ⚠️  Error fetching Q{quarter}: {e}")

    # Fetch annual data
    print("\n  Fetching annual financial statements...")
    try:
        # Balance Sheet
        bs_data = opendart_client.get_balance_sheet(symbol, year, None)
        if bs_data:
            print(f"    ✓ Annual Balance Sheet: {len(bs_data)} items")
            results["annual_data"]["balance_sheet"] = bs_data

        # Income Statement
        is_data = opendart_client.get_income_statement(symbol, year, None)
        if is_data:
            print(f"    ✓ Annual Income Statement: {len(is_data)} items")
            results["annual_data"]["income_statement"] = is_data

        # Cash Flow Statement
        cf_data = opendart_client.get_cash_flow(symbol, year, None)
        if cf_data:
            print(f"    ✓ Annual Cash Flow: {len(cf_data)} items")
            results["annual_data"]["cashflow_statement"] = cf_data

    except Exception as e:
        print(f"    ⚠️  Error fetching annual data: {e}")

    # Save results
    filename = f"opendart_{symbol}_{year}_complete.json"
    filepath = save_json(results, filename, "korean_stocks")
    print(f"\n  ✅ Saved to: {filepath}")

    return results


def generate_summary_report(
    us_results: List[Dict], korean_results: List[Dict]
) -> Dict[str, Any]:
    """Generate a summary report of all collected data."""
    print(f"\n{'='*80}")
    print("GENERATING SUMMARY REPORT")
    print(f"{'='*80}")

    report = {
        "test_date": datetime.now().isoformat(),
        "summary": {
            "us_stocks_tested": len(us_results),
            "korean_stocks_tested": len(korean_results),
            "total_stocks": len(us_results) + len(korean_results),
        },
        "us_stocks": {},
        "korean_stocks": {},
        "data_structure_analysis": {
            "yfinance_fields": {},
            "opendart_fields": {},
        },
        "recommendations": [],
    }

    # Analyze US stocks
    print("\n  Analyzing US stocks...")
    for result in us_results:
        symbol = result["symbol"]
        print(f"    {symbol}:")

        stock_summary = {
            "symbol": symbol,
            "company_name": result.get("company_name"),
            "quarters_available": list(
                result.get("quarterly_data", {}).keys()
            ),
            "field_counts": {},
        }

        # Count unique fields
        if "quarterly_data" in result:
            for quarter_key, quarter_data in result["quarterly_data"].items():
                if quarter_key.startswith("2024Q"):
                    for stmt_type in [
                        "balance_sheet",
                        "income_statement",
                        "cashflow_statement",
                    ]:
                        if stmt_type in quarter_data:
                            field_count = len(quarter_data[stmt_type])
                            stock_summary["field_counts"][
                                stmt_type
                            ] = field_count
                            print(
                                f"      {quarter_key} {stmt_type}: {field_count} fields"
                            )

                            # Collect unique fields for overall analysis
                            if (
                                stmt_type
                                not in report["data_structure_analysis"][
                                    "yfinance_fields"
                                ]
                            ):
                                report["data_structure_analysis"][
                                    "yfinance_fields"
                                ][stmt_type] = set()

                            report["data_structure_analysis"][
                                "yfinance_fields"
                            ][stmt_type].update(quarter_data[stmt_type].keys())

        report["us_stocks"][symbol] = stock_summary

    # Analyze Korean stocks
    print("\n  Analyzing Korean stocks...")
    for result in korean_results:
        symbol = result["symbol"]
        print(f"    {symbol}:")

        stock_summary = {
            "symbol": symbol,
            "corp_code": result.get("corp_code"),
            "quarters_available": list(
                result.get("quarterly_data", {}).keys()
            ),
            "field_counts": {},
        }

        # Count unique fields
        if "quarterly_data" in result:
            for quarter_key, quarter_data in result["quarterly_data"].items():
                for stmt_type in [
                    "balance_sheet",
                    "income_statement",
                    "cashflow_statement",
                ]:
                    if stmt_type in quarter_data:
                        field_count = len(quarter_data[stmt_type])
                        stock_summary["field_counts"][stmt_type] = field_count
                        print(
                            f"      {quarter_key} {stmt_type}: {field_count} fields"
                        )

                        # Collect unique fields for overall analysis
                        if (
                            stmt_type
                            not in report["data_structure_analysis"][
                                "opendart_fields"
                            ]
                        ):
                            report["data_structure_analysis"][
                                "opendart_fields"
                            ][stmt_type] = set()

                        report["data_structure_analysis"]["opendart_fields"][
                            stmt_type
                        ].update(quarter_data[stmt_type].keys())

        report["korean_stocks"][symbol] = stock_summary

    # Convert sets to lists for JSON serialization
    for stmt_type in report["data_structure_analysis"]["yfinance_fields"]:
        report["data_structure_analysis"]["yfinance_fields"][stmt_type] = list(
            report["data_structure_analysis"]["yfinance_fields"][stmt_type]
        )

    for stmt_type in report["data_structure_analysis"]["opendart_fields"]:
        report["data_structure_analysis"]["opendart_fields"][stmt_type] = list(
            report["data_structure_analysis"]["opendart_fields"][stmt_type]
        )

    # Save report
    filepath = save_json(report, "00_summary_report.json")
    print(f"\n  ✅ Summary report saved to: {filepath}")

    return report


def main():
    """Main test execution."""
    print("=" * 80)
    print("COMPREHENSIVE 2024 FINANCIAL DATA COLLECTION TEST")
    print("=" * 80)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"Test execution time: {datetime.now().isoformat()}")

    # US Stocks
    us_symbols = ["AAPL", "IONQ"]
    us_results = []

    print("\n" + "=" * 80)
    print("PHASE 1: US STOCKS (yfinance)")
    print("=" * 80)

    for symbol in us_symbols:
        try:
            result = test_yfinance_stock(symbol, 2024)
            us_results.append(result)
        except Exception as e:
            print(f"\n  ❌ Error testing {symbol}: {e}")
            import traceback

            traceback.print_exc()

    # Korean Stocks
    korean_symbols = ["005930", "000660"]  # Samsung Electronics, SK Hynix
    korean_results = []

    print("\n" + "=" * 80)
    print("PHASE 2: KOREAN STOCKS (OPENDART)")
    print("=" * 80)

    for symbol in korean_symbols:
        try:
            result = test_opendart_stock(symbol, 2024)
            korean_results.append(result)
        except Exception as e:
            print(f"\n  ❌ Error testing {symbol}: {e}")
            import traceback

            traceback.print_exc()

    # Generate summary report
    print("\n" + "=" * 80)
    print("PHASE 3: SUMMARY REPORT")
    print("=" * 80)

    try:
        summary = generate_summary_report(us_results, korean_results)

        # Print key findings
        print("\n" + "=" * 80)
        print("KEY FINDINGS")
        print("=" * 80)

        print("\n📊 yfinance Field Counts:")
        for stmt_type, fields in summary["data_structure_analysis"][
            "yfinance_fields"
        ].items():
            print(f"  {stmt_type}: {len(fields)} unique fields")

        print("\n📊 OPENDART Field Counts:")
        for stmt_type, fields in summary["data_structure_analysis"][
            "opendart_fields"
        ].items():
            print(f"  {stmt_type}: {len(fields)} unique fields")

        print("\n✅ All data collected successfully!")
        print(f"\nResults saved in: {OUTPUT_DIR}")

    except Exception as e:
        print(f"\n❌ Error generating summary: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
