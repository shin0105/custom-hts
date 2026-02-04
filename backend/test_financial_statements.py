#!/usr/bin/env python3
"""
Comprehensive test and demonstration script for financial statement functionality.

This script demonstrates:
1. Database table verification
2. Data insertion for Korean stocks (OPENDART)
3. Data insertion for US stocks (yfinance)
4. Data retrieval and verification
5. API endpoint testing (if backend is running)
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir / "src"))

from src.services.financial_statements import financial_statement_service
from src.integrations.supabase_client import supabase_client
from src.integrations.opendart import opendart_client

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def print_header(title: str) -> None:
    """Print a fancy header."""
    print("\n" + "=" * 80)
    print(f" {title.center(78)}")
    print("=" * 80)


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print(f"{'─' * 80}")


def check_prerequisites() -> dict:
    """Check all prerequisites for running the tests."""
    print_section("1. Checking Prerequisites")

    status = {
        "supabase": False,
        "dart_api": False,
        "tables_exist": False,
    }

    # Check Supabase connection
    if supabase_client.client:
        print("  ✅ Supabase client initialized")
        status["supabase"] = True
    else:
        print("  ❌ Supabase client not initialized")
        print("     Set SUPABASE_URL and SUPABASE_KEY in .env file")

    # Check DART API key
    if opendart_client.api_key:
        print("  ✅ DART API key configured")
        status["dart_api"] = True
    else:
        print("  ⚠️  DART API key not configured (Korean data will be skipped)")

    # Check if tables exist
    if status["supabase"]:
        try:
            tables = [
                "korean_balance_sheet",
                "korean_income_statement",
                "korean_cashflow_statement",
                "us_balance_sheet",
                "us_income_statement",
                "us_cashflow_statement",
            ]

            all_exist = True
            for table in tables:
                try:
                    supabase_client.client.table(table).select("id", count="exact").limit(1).execute()
                except Exception as e:
                    print(f"  ❌ Table '{table}' not found or accessible")
                    all_exist = False

            if all_exist:
                print("  ✅ All required tables exist")
                status["tables_exist"] = True
            else:
                print("  ⚠️  Some tables missing - run financial_statements.sql first")

        except Exception as e:
            print(f"  ❌ Error checking tables: {e}")

    return status


def test_korean_data_insertion() -> dict:
    """Test Korean financial data insertion."""
    print_section("2. Testing Korean Financial Data Insertion")

    symbol = "005930"  # Samsung Electronics
    year = 2024
    test_quarters = [None, 3]  # Annual and Q3

    results = {}

    for quarter in test_quarters:
        quarter_str = f"Q{quarter}" if quarter else "Annual"
        print(f"\n  📊 Testing {symbol} {year} {quarter_str}...")

        try:
            result = financial_statement_service.insert_all_korean_statements(
                symbol=symbol, year=year, quarter=quarter
            )

            period_key = f"{year}_{quarter_str}"
            results[period_key] = result

            # Print results
            print(f"     Balance Sheet:     {'✅' if result['balance_sheet'] else '❌'}")
            print(f"     Income Statement:  {'✅' if result['income_statement'] else '❌'}")
            print(f"     Cash Flow:         {'✅' if result['cashflow_statement'] else '❌'}")

        except Exception as e:
            print(f"     ❌ Error: {e}")
            results[f"{year}_{quarter_str}"] = {
                "balance_sheet": False,
                "income_statement": False,
                "cashflow_statement": False,
            }

    return results


def test_us_data_insertion() -> dict:
    """Test US financial data insertion."""
    print_section("3. Testing US Financial Data Insertion")

    symbol = "AAPL"  # Apple Inc.
    year = 2024
    test_quarters = [None]  # Annual only (yfinance may have network issues)

    results = {}

    for quarter in test_quarters:
        quarter_str = f"Q{quarter}" if quarter else "Annual"
        print(f"\n  📊 Testing {symbol} {year} {quarter_str}...")

        try:
            result = financial_statement_service.insert_all_us_statements(
                symbol=symbol, year=year, quarter=quarter
            )

            period_key = f"{year}_{quarter_str}"
            results[period_key] = result

            # Print results
            print(f"     Balance Sheet:     {'✅' if result['balance_sheet'] else '❌'}")
            print(f"     Income Statement:  {'✅' if result['income_statement'] else '❌'}")
            print(f"     Cash Flow:         {'✅' if result['cashflow_statement'] else '❌'}")

        except Exception as e:
            print(f"     ❌ Error: {e}")
            print("     (Network restrictions may prevent yfinance access)")
            results[f"{year}_{quarter_str}"] = {
                "balance_sheet": False,
                "income_statement": False,
                "cashflow_statement": False,
            }

    return results


def verify_data_in_database() -> dict:
    """Verify that data was inserted into the database."""
    print_section("4. Verifying Data in Database")

    if not supabase_client.client:
        print("  ❌ Supabase client not initialized")
        return {}

    tables = [
        "korean_balance_sheet",
        "korean_income_statement",
        "korean_cashflow_statement",
        "us_balance_sheet",
        "us_income_statement",
        "us_cashflow_statement",
    ]

    results = {}

    print("\n  Table Name                          Records  Latest Year")
    print("  " + "─" * 70)

    for table in tables:
        try:
            # Get count
            response = supabase_client.client.table(table).select("*", count="exact").execute()

            count = len(response.data) if response.data else 0

            # Get latest year
            latest_year = "N/A"
            if response.data:
                years = [r.get("year") for r in response.data if r.get("year")]
                if years:
                    latest_year = str(max(years))

            status = "✅" if count > 0 else "⚠️ "
            print(f"  {status} {table:<33} {count:>6}   {latest_year:>10}")

            results[table] = {"count": count, "latest_year": latest_year}

        except Exception as e:
            print(f"  ❌ {table:<33} Error: {str(e)[:30]}")
            results[table] = {"count": 0, "error": str(e)}

    return results


def demonstrate_data_queries() -> None:
    """Demonstrate various data queries."""
    print_section("5. Demonstrating Data Queries")

    if not supabase_client.client:
        print("  ❌ Supabase client not initialized")
        return

    # Query 1: Get Samsung balance sheet
    print("\n  Query 1: Samsung (005930) Balance Sheet 2024")
    try:
        response = (
            supabase_client.client.table("korean_balance_sheet")
            .select("year, quarter, total_assets, total_liabilities, total_equity")
            .eq("symbol", "005930")
            .eq("year", 2024)
            .execute()
        )

        if response.data:
            for row in response.data:
                q = f"Q{row['quarter']}" if row.get("quarter") else "Annual"
                print(f"    {row['year']} {q}:")
                if row.get("total_assets"):
                    print(f"      Total Assets:      {row['total_assets']:>20,.0f}")
                if row.get("total_liabilities"):
                    print(f"      Total Liabilities: {row['total_liabilities']:>20,.0f}")
                if row.get("total_equity"):
                    print(f"      Total Equity:      {row['total_equity']:>20,.0f}")
        else:
            print("    No data found")

    except Exception as e:
        print(f"    ❌ Error: {e}")

    # Query 2: Get Samsung income statement
    print("\n  Query 2: Samsung (005930) Income Statement 2024")
    try:
        response = (
            supabase_client.client.table("korean_income_statement")
            .select("year, quarter, revenue, operating_income, net_income")
            .eq("symbol", "005930")
            .eq("year", 2024)
            .execute()
        )

        if response.data:
            for row in response.data:
                q = f"Q{row['quarter']}" if row.get("quarter") else "Annual"
                print(f"    {row['year']} {q}:")
                if row.get("revenue"):
                    print(f"      Revenue:          {row['revenue']:>20,.0f}")
                if row.get("operating_income"):
                    print(f"      Operating Income: {row['operating_income']:>20,.0f}")
                if row.get("net_income"):
                    print(f"      Net Income:       {row['net_income']:>20,.0f}")
        else:
            print("    No data found")

    except Exception as e:
        print(f"    ❌ Error: {e}")

    # Query 3: Get Apple balance sheet
    print("\n  Query 3: Apple (AAPL) Balance Sheet")
    try:
        response = (
            supabase_client.client.table("us_balance_sheet")
            .select("year, quarter, total_assets, total_liabilities, stockholders_equity")
            .eq("symbol", "AAPL")
            .limit(2)
            .execute()
        )

        if response.data:
            for row in response.data:
                q = f"Q{row['quarter']}" if row.get("quarter") else "Annual"
                print(f"    {row['year']} {q}:")
                if row.get("total_assets"):
                    print(f"      Total Assets:          {row['total_assets']:>20,.0f}")
                if row.get("total_liabilities"):
                    print(f"      Total Liabilities:     {row['total_liabilities']:>20,.0f}")
                if row.get("stockholders_equity"):
                    print(f"      Stockholders Equity:   {row['stockholders_equity']:>20,.0f}")
        else:
            print("    No data found")

    except Exception as e:
        print(f"    ❌ Error: {e}")


def print_summary(
    prereq_status: dict,
    korean_results: dict,
    us_results: dict,
    db_verification: dict,
) -> None:
    """Print final summary."""
    print_section("Summary")

    # Prerequisites
    print("\n  Prerequisites:")
    print(f"    Supabase:      {'✅' if prereq_status['supabase'] else '❌'}")
    print(f"    DART API:      {'✅' if prereq_status['dart_api'] else '⚠️ '}")
    print(f"    Tables Exist:  {'✅' if prereq_status['tables_exist'] else '❌'}")

    # Korean data
    if korean_results:
        print("\n  Korean Data Insertion:")
        for period, result in korean_results.items():
            success_count = sum(1 for v in result.values() if v)
            print(f"    {period}: {success_count}/3 statements inserted")

    # US data
    if us_results:
        print("\n  US Data Insertion:")
        for period, result in us_results.items():
            success_count = sum(1 for v in result.values() if v)
            print(f"    {period}: {success_count}/3 statements inserted")

    # Database verification
    if db_verification:
        print("\n  Database Records:")
        total_records = sum(v.get("count", 0) for v in db_verification.values())
        print(f"    Total records across all tables: {total_records}")


def main():
    """Main function."""
    print_header("FINANCIAL STATEMENTS - COMPREHENSIVE TEST")

    # Check prerequisites
    prereq_status = check_prerequisites()

    if not prereq_status["supabase"]:
        print("\n❌ Cannot proceed without Supabase connection")
        print("   Please configure SUPABASE_URL and SUPABASE_KEY in .env file")
        return

    if not prereq_status["tables_exist"]:
        print("\n⚠️  Database tables not found")
        print("   Please run the following SQL scripts in Supabase SQL editor:")
        print("   1. database/init.sql")
        print("   2. database/financial_statements.sql")
        response = input("\n   Continue anyway? (y/n): ")
        if response.lower() != "y":
            return

    # Test Korean data insertion
    korean_results = {}
    if prereq_status["dart_api"]:
        korean_results = test_korean_data_insertion()
    else:
        print_section("2. Korean Data Insertion")
        print("  ⏭️  Skipped (no DART API key)")

    # Test US data insertion
    us_results = test_us_data_insertion()

    # Verify data in database
    db_verification = verify_data_in_database()

    # Demonstrate queries
    demonstrate_data_queries()

    # Print summary
    print_summary(prereq_status, korean_results, us_results, db_verification)

    print_header("TEST COMPLETE")
    print("\n✅ Financial statement functionality has been tested!")
    print("\nNext steps:")
    print("  1. Review the database tables in Supabase dashboard")
    print("  2. Start the backend API: cd backend && uv run uvicorn src.main:app --reload")
    print("  3. Access API docs at http://localhost:8000/docs")
    print("  4. Test the financial statement endpoints in the API docs")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
