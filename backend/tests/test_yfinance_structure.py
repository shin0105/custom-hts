#!/usr/bin/env python3
"""Test script to examine yfinance data structure in detail."""

import sys
from pathlib import Path
import json

# Add src to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir / "src"))

import yfinance as yf
import pandas as pd


def explore_ticker_methods():
    """Explore available methods and data structure of yfinance Ticker."""
    print("\n" + "=" * 80)
    print("YFINANCE DATA STRUCTURE EXPLORATION")
    print("=" * 80)

    symbol = "AAPL"
    print(f"\nTesting with: {symbol}")

    ticker = yf.Ticker(symbol)

    # List all available attributes
    print("\n" + "-" * 80)
    print("AVAILABLE TICKER ATTRIBUTES")
    print("-" * 80)

    attributes = [attr for attr in dir(ticker) if not attr.startswith("_")]
    financial_attrs = [
        attr
        for attr in attributes
        if any(
            keyword in attr.lower()
            for keyword in [
                "financial",
                "balance",
                "income",
                "cash",
                "statement",
                "earnings",
            ]
        )
    ]

    for attr in sorted(financial_attrs):
        print(f"  • {attr}")

    return ticker, symbol


def test_balance_sheet(ticker, symbol):
    """Test balance sheet data structure."""
    print("\n" + "=" * 80)
    print("BALANCE SHEET DATA")
    print("=" * 80)

    # Annual balance sheet
    print("\n📊 Annual Balance Sheet:")
    bs_annual = ticker.balance_sheet
    if bs_annual is not None and not bs_annual.empty:
        print(f"  Shape: {bs_annual.shape}")
        print(f"  Columns (dates): {[str(d) for d in bs_annual.columns]}")
        print(f"  Row count: {len(bs_annual.index)}")
        print(f"\n  Available fields:")
        for idx in bs_annual.index[:20]:  # First 20 fields
            print(f"    - {idx}")
        if len(bs_annual.index) > 20:
            print(f"    ... and {len(bs_annual.index) - 20} more")

    # Quarterly balance sheet
    print("\n📊 Quarterly Balance Sheet:")
    bs_quarterly = ticker.quarterly_balance_sheet
    if bs_quarterly is not None and not bs_quarterly.empty:
        print(f"  Shape: {bs_quarterly.shape}")
        print(f"  Columns (dates): {[str(d) for d in bs_quarterly.columns]}")
        print(f"  Row count: {len(bs_quarterly.index)}")

        # Show sample data for most recent quarter
        if len(bs_quarterly.columns) > 0:
            latest = bs_quarterly.columns[0]
            print(f"\n  Sample data for {latest}:")
            sample_fields = [
                "Total Assets",
                "Current Assets",
                "Cash And Cash Equivalents",
                "Total Liabilities Net Minority Interest",
                "Current Liabilities",
                "Stockholders Equity",
                "Total Debt",
                "Net Debt",
            ]
            for field in sample_fields:
                if field in bs_quarterly.index:
                    value = bs_quarterly.loc[field, latest]
                    print(
                        f"    {field}: {value:,.0f}"
                        if pd.notna(value)
                        else f"    {field}: N/A"
                    )

    return bs_quarterly


def test_income_statement(ticker, symbol):
    """Test income statement data structure."""
    print("\n" + "=" * 80)
    print("INCOME STATEMENT DATA")
    print("=" * 80)

    # Annual
    print("\n📊 Annual Income Statement:")
    is_annual = ticker.financials
    if is_annual is not None and not is_annual.empty:
        print(f"  Shape: {is_annual.shape}")
        print(f"  Columns (dates): {[str(d) for d in is_annual.columns]}")
        print(f"\n  Available fields:")
        for idx in is_annual.index[:20]:
            print(f"    - {idx}")
        if len(is_annual.index) > 20:
            print(f"    ... and {len(is_annual.index) - 20} more")

    # Quarterly
    print("\n📊 Quarterly Income Statement:")
    is_quarterly = ticker.quarterly_financials
    if is_quarterly is not None and not is_quarterly.empty:
        print(f"  Shape: {is_quarterly.shape}")
        print(f"  Columns (dates): {[str(d) for d in is_quarterly.columns]}")

        # Show sample data
        if len(is_quarterly.columns) > 0:
            latest = is_quarterly.columns[0]
            print(f"\n  Sample data for {latest}:")
            sample_fields = [
                "Total Revenue",
                "Cost Of Revenue",
                "Gross Profit",
                "Operating Income",
                "Operating Expense",
                "Net Income",
                "EBITDA",
                "Basic EPS",
                "Diluted EPS",
            ]
            for field in sample_fields:
                if field in is_quarterly.index:
                    value = is_quarterly.loc[field, latest]
                    print(
                        f"    {field}: {value:,.2f}"
                        if pd.notna(value)
                        else f"    {field}: N/A"
                    )

    return is_quarterly


def test_cash_flow(ticker, symbol):
    """Test cash flow statement data structure."""
    print("\n" + "=" * 80)
    print("CASH FLOW STATEMENT DATA")
    print("=" * 80)

    # Annual
    print("\n📊 Annual Cash Flow:")
    cf_annual = ticker.cashflow
    if cf_annual is not None and not cf_annual.empty:
        print(f"  Shape: {cf_annual.shape}")
        print(f"  Columns (dates): {[str(d) for d in cf_annual.columns]}")
        print(f"\n  Available fields:")
        for idx in cf_annual.index[:20]:
            print(f"    - {idx}")
        if len(cf_annual.index) > 20:
            print(f"    ... and {len(cf_annual.index) - 20} more")

    # Quarterly
    print("\n📊 Quarterly Cash Flow:")
    cf_quarterly = ticker.quarterly_cashflow
    if cf_quarterly is not None and not cf_quarterly.empty:
        print(f"  Shape: {cf_quarterly.shape}")
        print(f"  Columns (dates): {[str(d) for d in cf_quarterly.columns]}")

        # Show sample data
        if len(cf_quarterly.columns) > 0:
            latest = cf_quarterly.columns[0]
            print(f"\n  Sample data for {latest}:")
            sample_fields = [
                "Operating Cash Flow",
                "Investing Cash Flow",
                "Financing Cash Flow",
                "Free Cash Flow",
                "Capital Expenditure",
                "Repurchase Of Capital Stock",
                "Cash Dividends Paid",
                "Change In Cash",
            ]
            for field in sample_fields:
                if field in cf_quarterly.index:
                    value = cf_quarterly.loc[field, latest]
                    print(
                        f"    {field}: {value:,.0f}"
                        if pd.notna(value)
                        else f"    {field}: N/A"
                    )

    return cf_quarterly


def compare_with_db_schema():
    """Compare yfinance fields with database schema."""
    print("\n" + "=" * 80)
    print("MAPPING TO DATABASE SCHEMA")
    print("=" * 80)

    print("\n📋 Balance Sheet Mapping:")
    print("  yfinance field → database column")
    print("  " + "-" * 70)
    mappings = {
        "Total Assets": "total_assets",
        "Current Assets": "current_assets",
        "Cash And Cash Equivalents": "cash_and_cash_equivalents",
        "Short Term Investments": "short_term_investments",
        "Receivables": "receivables",
        "Inventory": "inventory",
        "Total Liabilities Net Minority Interest": "total_liabilities",
        "Current Liabilities": "current_liabilities",
        "Accounts Payable": "accounts_payable",
        "Current Debt": "short_term_debt",
        "Long Term Debt": "long_term_debt",
        "Stockholders Equity": "stockholders_equity",
        "Common Stock": "common_stock",
        "Retained Earnings": "retained_earnings",
        "Treasury Stock": "treasury_stock",
    }
    for yf_field, db_col in mappings.items():
        print(f"  {yf_field:45} → {db_col}")

    print("\n📋 Income Statement Mapping:")
    print("  yfinance field → database column")
    print("  " + "-" * 70)
    mappings = {
        "Total Revenue": "total_revenue",
        "Cost Of Revenue": "cost_of_revenue",
        "Gross Profit": "gross_profit",
        "Operating Expense": "operating_expense",
        "Selling General And Administration": "selling_general_admin",
        "Research And Development": "research_development",
        "Operating Income": "operating_income",
        "Interest Income": "interest_income",
        "Interest Expense": "interest_expense",
        "Other Income Expense": "other_income_expense",
        "Pretax Income": "pretax_income",
        "Tax Provision": "tax_provision",
        "Net Income": "net_income",
        "EBITDA": "ebitda",
        "Basic EPS": "basic_eps",
        "Diluted EPS": "diluted_eps",
    }
    for yf_field, db_col in mappings.items():
        print(f"  {yf_field:45} → {db_col}")

    print("\n📋 Cash Flow Mapping:")
    print("  yfinance field → database column")
    print("  " + "-" * 70)
    mappings = {
        "Operating Cash Flow": "operating_cash_flow",
        "Investing Cash Flow": "investing_cash_flow",
        "Financing Cash Flow": "financing_cash_flow",
        "Free Cash Flow": "free_cash_flow",
        "Net Income From Continuing Operations": "net_income_from_continuing_ops",
        "Depreciation And Amortization": "depreciation_amortization",
        "Deferred Income Tax": "deferred_income_tax",
        "Stock Based Compensation": "stock_based_compensation",
        "Change In Working Capital": "change_working_capital",
        "Capital Expenditure": "capital_expenditure",
        "Cash Dividends Paid": "cash_dividends_paid",
        "Repurchase Of Capital Stock": "repurchase_capital_stock",
        "Change In Cash": "net_change_cash",
    }
    for yf_field, db_col in mappings.items():
        print(f"  {yf_field:45} → {db_col}")


def main():
    """Main execution."""
    try:
        # Explore structure
        ticker, symbol = explore_ticker_methods()

        # Test each statement type
        bs_quarterly = test_balance_sheet(ticker, symbol)
        is_quarterly = test_income_statement(ticker, symbol)
        cf_quarterly = test_cash_flow(ticker, symbol)

        # Compare with database schema
        compare_with_db_schema()

        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print("\n✅ yfinance provides:")
        print("  • Quarterly and annual financial statements")
        print("  • Balance sheet, income statement, cash flow")
        print("  • Data as pandas DataFrame with Timestamp columns")
        print("  • Field names are descriptive and well-structured")

        print("\n💡 Key Observations:")
        print(
            "  • Column names are Timestamps (not strings) → need conversion"
        )
        print("  • Row index contains field names (e.g., 'Total Assets')")
        print("  • Values are numeric (float64)")
        print("  • Most recent quarter is in column 0")
        print("  • Typically has 4 quarters of data available")

        print("\n🔧 Implementation Requirements:")
        print("  • Convert Timestamp columns to year/quarter")
        print("  • Map yfinance field names to database columns")
        print("  • Handle None/NaN values appropriately")
        print("  • Store raw DataFrame as JSONB for completeness")
        print("  • Use Python package (not REST API) ✓ Already implemented")

        print("\n" + "=" * 80 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
