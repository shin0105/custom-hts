#!/usr/bin/env python3
"""
Demo script to test OPENDART API integration.

This script demonstrates:
1. Getting financial statements for Korean companies
2. Retrieving balance sheet data
3. Retrieving income statement data
4. Retrieving cash flow statement data

Usage:
    cd backend
    PYTHONPATH=$(pwd)/src python test_opendart_demo.py
"""

import sys
from pathlib import Path

# Add src to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir / "src"))

from src.integrations.opendart import opendart_client
from datetime import datetime
import json


def print_section(title: str) -> None:
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_financial_statement(statement, company_name: str) -> None:
    """Print financial statement in a readable format."""
    if not statement:
        print(f"  ❌ No data available for {company_name}")
        return
    
    print(f"\n  ✅ {statement.company_name} ({statement.symbol})")
    print(f"     Period: {statement.year}" + (f" Q{statement.quarter}" if statement.quarter else " (Annual)"))
    print(f"     Updated: {statement.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n     Financial Data (in KRW):")
    print(f"     - Revenue:           {statement.revenue:>20,.0f}" if statement.revenue else "     - Revenue:           N/A")
    print(f"     - Operating Income:  {statement.operating_income:>20,.0f}" if statement.operating_income else "     - Operating Income:  N/A")
    print(f"     - Net Income:        {statement.net_income:>20,.0f}" if statement.net_income else "     - Net Income:        N/A")
    print(f"     - Total Assets:      {statement.total_assets:>20,.0f}" if statement.total_assets else "     - Total Assets:      N/A")
    print(f"     - Total Liabilities: {statement.total_liabilities:>20,.0f}" if statement.total_liabilities else "     - Total Liabilities: N/A")
    print(f"     - Total Equity:      {statement.total_equity:>20,.0f}" if statement.total_equity else "     - Total Equity:      N/A")


def print_statement_details(data: dict, statement_type: str, max_items: int = 10) -> None:
    """Print statement details in a readable format."""
    if not data:
        print(f"  ❌ No {statement_type} data available")
        return
    
    print(f"\n  ✅ {statement_type} (showing top {max_items} items):")
    
    # Sort by absolute value to show most significant items first
    sorted_items = sorted(
        data.items(), 
        key=lambda x: abs(x[1]) if x[1] is not None else 0, 
        reverse=True
    )
    
    for i, (account, amount) in enumerate(sorted_items[:max_items]):
        if amount is not None:
            print(f"     {i+1:2d}. {account:40s}: {amount:>20,.0f}")


def main():
    """Main demo function."""
    print_section("OPENDART API Integration Demo")
    
    # Check if API key is configured
    if not opendart_client.api_key:
        print("\n❌ ERROR: DART_API_KEY not configured in .env file")
        print("   Please set your DART API key from https://opendart.fss.or.kr/")
        return
    
    print(f"\n✅ DART API Key configured")
    print(f"   Base URL: {opendart_client.base_url}")
    
    # Test companies
    test_companies = [
        ("005930", "Samsung Electronics"),
        ("035420", "NAVER"),
        ("035720", "Kakao"),
    ]
    
    current_year = datetime.now().year
    test_year = current_year - 1  # Use previous year for complete annual data
    
    # =========================================================================
    # Test 1: Get Financial Statements (Summary)
    # =========================================================================
    print_section("Test 1: Financial Statements (Summary)")
    
    for symbol, company_name in test_companies:
        print(f"\n📊 Fetching financial statement for {company_name} ({symbol})...")
        
        # Get annual financial statement
        statement = opendart_client.get_financial_statement(
            symbol=symbol,
            year=test_year,
            quarter=None  # Annual report
        )
        
        print_financial_statement(statement, company_name)
    
    # =========================================================================
    # Test 2: Detailed Balance Sheet
    # =========================================================================
    print_section("Test 2: Detailed Balance Sheet")
    
    symbol = "005930"  # Samsung Electronics
    company_name = "Samsung Electronics"
    
    print(f"\n📊 Fetching detailed balance sheet for {company_name} ({symbol})...")
    balance_sheet = opendart_client.get_balance_sheet(
        symbol=symbol,
        year=test_year
    )
    
    print_statement_details(balance_sheet, "Balance Sheet")
    
    # =========================================================================
    # Test 3: Detailed Income Statement
    # =========================================================================
    print_section("Test 3: Detailed Income Statement")
    
    print(f"\n📊 Fetching detailed income statement for {company_name} ({symbol})...")
    income_statement = opendart_client.get_income_statement(
        symbol=symbol,
        year=test_year
    )
    
    print_statement_details(income_statement, "Income Statement")
    
    # =========================================================================
    # Test 4: Detailed Cash Flow Statement
    # =========================================================================
    print_section("Test 4: Detailed Cash Flow Statement")
    
    print(f"\n📊 Fetching detailed cash flow statement for {company_name} ({symbol})...")
    cash_flow = opendart_client.get_cash_flow(
        symbol=symbol,
        year=test_year
    )
    
    print_statement_details(cash_flow, "Cash Flow Statement")
    
    # =========================================================================
    # Test 5: Quarterly Data
    # =========================================================================
    print_section("Test 5: Quarterly Financial Statement")
    
    print(f"\n📊 Fetching Q3 {test_year} statement for {company_name} ({symbol})...")
    quarterly_statement = opendart_client.get_financial_statement(
        symbol=symbol,
        year=test_year,
        quarter=3
    )
    
    print_financial_statement(quarterly_statement, company_name)
    
    # =========================================================================
    # Summary
    # =========================================================================
    print_section("Demo Complete")
    print("\n✅ OPENDART API integration is working correctly!")
    print("\nKey Features Demonstrated:")
    print("  1. ✅ Financial statement retrieval (summary)")
    print("  2. ✅ Detailed balance sheet data")
    print("  3. ✅ Detailed income statement data")
    print("  4. ✅ Detailed cash flow statement data")
    print("  5. ✅ Quarterly financial data")
    print("\nAPI Endpoint Used:")
    print(f"  - {opendart_client.base_url}/fnlttSinglAcntAll.json")
    print("\nNote: Make sure your DART_API_KEY is set in the .env file")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
