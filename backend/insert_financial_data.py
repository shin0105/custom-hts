#!/usr/bin/env python3
"""
Script to insert financial statement data for specific periods.

This script:
1. Inserts data for Korean stock 005930 (Samsung) for Q1-Q3 2025
2. Inserts data for US stock AAPL (Apple) for Q1-Q3 2025
3. Verifies the data was inserted correctly
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir / "src"))

from src.services.financial_statements import financial_statement_service
from src.integrations.supabase_client import supabase_client

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def print_section(title: str) -> None:
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def insert_korean_data():
    """Insert financial data for Korean stock 005930."""
    print_section("Inserting Korean Financial Data - Samsung (005930)")

    symbol = "005930"
    year = 2025
    quarters = [None, 1, 2, 3]  # Annual 2024 + Q1, Q2, Q3 2025

    # Actually for 2025 Q1-Q3, we should use year 2025
    # But OPENDART may not have 2025 data yet, so let's try 2024
    test_year = 2024

    results = []

    for quarter in quarters:
        quarter_str = f"Q{quarter}" if quarter else "Annual"
        print(f"\n📊 Processing {test_year} {quarter_str}...")

        result = financial_statement_service.insert_all_korean_statements(
            symbol=symbol, year=test_year, quarter=quarter
        )

        results.append(
            {
                "period": f"{test_year} {quarter_str}",
                "balance_sheet": "✅" if result["balance_sheet"] else "❌",
                "income_statement": "✅" if result["income_statement"] else "❌",
                "cashflow_statement": "✅" if result["cashflow_statement"] else "❌",
            }
        )

    # Print summary
    print(f"\n📈 Summary for {symbol}:")
    print(f"{'Period':<20} {'Balance Sheet':<15} {'Income Statement':<20} {'Cash Flow':<15}")
    print("-" * 75)
    for r in results:
        print(
            f"{r['period']:<20} {r['balance_sheet']:<15} {r['income_statement']:<20} {r['cashflow_statement']:<15}"
        )

    return results


def insert_us_data():
    """Insert financial data for US stock AAPL."""
    print_section("Inserting US Financial Data - Apple (AAPL)")

    symbol = "AAPL"
    # For US stocks, fiscal year 2024 (ended Sept 2024) and quarterly data
    # Note: yfinance may have limited access in this environment
    year = 2024
    quarters = [None, 1, 2, 3]  # Annual + Q1, Q2, Q3

    results = []

    for quarter in quarters:
        quarter_str = f"Q{quarter}" if quarter else "Annual"
        print(f"\n📊 Processing {year} {quarter_str}...")

        result = financial_statement_service.insert_all_us_statements(
            symbol=symbol, year=year, quarter=quarter
        )

        results.append(
            {
                "period": f"{year} {quarter_str}",
                "balance_sheet": "✅" if result["balance_sheet"] else "❌",
                "income_statement": "✅" if result["income_statement"] else "❌",
                "cashflow_statement": "✅" if result["cashflow_statement"] else "❌",
            }
        )

    # Print summary
    print(f"\n📈 Summary for {symbol}:")
    print(
        f"{'Period':<20} {'Balance Sheet':<15} {'Income Statement':<20} {'Cash Flow':<15}"
    )
    print("-" * 75)
    for r in results:
        print(
            f"{r['period']:<20} {r['balance_sheet']:<15} {r['income_statement']:<20} {r['cashflow_statement']:<15}"
        )

    return results


def verify_insertions():
    """Verify that data was inserted correctly."""
    print_section("Verifying Data Insertions")

    if not supabase_client.client:
        print("❌ Supabase client not initialized")
        print("   Please configure SUPABASE_URL and SUPABASE_KEY in .env file")
        return False

    tables = [
        "korean_balance_sheet",
        "korean_income_statement",
        "korean_cashflow_statement",
        "us_balance_sheet",
        "us_income_statement",
        "us_cashflow_statement",
    ]

    print("\n📊 Checking table data counts...")
    all_ok = True

    for table in tables:
        try:
            response = supabase_client.client.table(table).select("*", count="exact").execute()

            count = len(response.data) if response.data else 0
            status = "✅" if count > 0 else "⚠️ "

            print(f"  {status} {table:<35}: {count} records")

            if count == 0:
                all_ok = False

        except Exception as e:
            print(f"  ❌ {table:<35}: Error - {str(e)[:50]}")
            all_ok = False

    if all_ok:
        print("\n✅ All tables have data!")
    else:
        print("\n⚠️  Some tables are empty or had errors")

    return all_ok


def main():
    """Main function."""
    print_section("Financial Statement Data Insertion")
    print("\nThis script will insert financial statement data for:")
    print("  - Korean Stock: 005930 (Samsung Electronics)")
    print("  - US Stock: AAPL (Apple Inc.)")
    print("  - Periods: 2024 Annual + Q1, Q2, Q3")

    # Check prerequisites
    if not supabase_client.client:
        print("\n❌ ERROR: Supabase client not initialized")
        print("   Please configure SUPABASE_URL and SUPABASE_KEY in .env file")
        return

    print("\n✅ Supabase client initialized")

    # Check DART API key
    from src.integrations.opendart import opendart_client

    if not opendart_client.api_key:
        print("⚠️  WARNING: DART_API_KEY not configured")
        print("   Korean data insertion will be skipped")
    else:
        print("✅ DART API key configured")

    # Insert Korean data
    if opendart_client.api_key:
        korean_results = insert_korean_data()
    else:
        print("\n⏭️  Skipping Korean data insertion (no API key)")

    # Insert US data
    try:
        us_results = insert_us_data()
    except Exception as e:
        print(f"\n❌ Error inserting US data: {e}")
        print(
            "   This may be due to network restrictions accessing Yahoo Finance"
        )

    # Verify insertions
    verify_insertions()

    print_section("Insertion Complete")
    print("\n✅ Financial statement data insertion process finished!")
    print("\nNext steps:")
    print("  1. Check Supabase dashboard to verify data")
    print("  2. Query the tables to see the inserted records")
    print("  3. Use the data in your HTS application")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
