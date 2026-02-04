#!/usr/bin/env python3
"""
Test script to record raw API data from OPENDART and yfinance.

This script will:
1. Fetch raw data for stock 005930 from OPENDART
2. Fetch raw data for AAPL from yfinance
3. Save results to JSON files for analysis
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir / "src"))

from src.integrations.opendart import opendart_client
import yfinance as yf


def save_json(data, filename):
    """Save data to JSON file."""
    output_dir = backend_dir / "data"
    output_dir.mkdir(exist_ok=True)
    
    filepath = output_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✅ Saved to {filepath}")
    return filepath


def test_opendart_005930():
    """Test OPENDART API with Samsung (005930)."""
    print("\n" + "="*80)
    print("Testing OPENDART API - Samsung Electronics (005930)")
    print("="*80)
    
    symbol = "005930"
    year = 2024
    quarters = [None, 1, 2, 3]  # None = Annual, 1-3 = Q1-Q3
    
    results = {}
    
    for quarter in quarters:
        quarter_str = f"Q{quarter}" if quarter else "Annual"
        print(f"\n📊 Fetching {year} {quarter_str} data for {symbol}...")
        
        try:
            # Get raw financial statement data
            raw_data = opendart_client.get_financial_statement_raw(
                symbol=symbol,
                year=year,
                quarter=quarter
            )
            
            if raw_data:
                print(f"  ✅ Retrieved {len(raw_data)} line items")
                results[quarter_str] = raw_data
                
                # Show a few examples
                print(f"  Sample data (first 3 items):")
                for item in raw_data[:3]:
                    print(f"    - {item.get('sj_div')}: {item.get('account_nm')} = {item.get('thstrm_amount')}")
            else:
                print(f"  ❌ No data available")
                results[quarter_str] = None
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results[quarter_str] = None
    
    # Save to file
    if any(results.values()):
        filename = f"opendart_005930_{year}_raw.json"
        filepath = save_json(results, filename)
        
        # Print summary
        print(f"\n📈 Summary:")
        for quarter_str, data in results.items():
            if data:
                print(f"  - {quarter_str}: {len(data)} items")
        
        return results
    else:
        print("\n❌ No data retrieved")
        return None


def test_yfinance_aapl():
    """Test yfinance API with Apple (AAPL)."""
    print("\n" + "="*80)
    print("Testing yfinance API - Apple Inc. (AAPL)")
    print("="*80)
    
    symbol = "AAPL"
    
    results = {}
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Get financials
        print(f"\n📊 Fetching financial data for {symbol}...")
        
        # Annual financials
        financials = ticker.financials
        if financials is not None and not financials.empty:
            print(f"  ✅ Retrieved financials: {financials.shape}")
            results['financials'] = financials.to_dict()
            
            # Show columns
            print(f"  Available years: {[str(d.year) for d in financials.columns]}")
            print(f"  Line items ({len(financials.index)}):")
            for idx in list(financials.index)[:10]:
                print(f"    - {idx}")
        
        # Balance sheet
        balance_sheet = ticker.balance_sheet
        if balance_sheet is not None and not balance_sheet.empty:
            print(f"\n  ✅ Retrieved balance sheet: {balance_sheet.shape}")
            results['balance_sheet'] = balance_sheet.to_dict()
            
            print(f"  Line items ({len(balance_sheet.index)}):")
            for idx in list(balance_sheet.index)[:10]:
                print(f"    - {idx}")
        
        # Cash flow
        cashflow = ticker.cashflow
        if cashflow is not None and not cashflow.empty:
            print(f"\n  ✅ Retrieved cash flow: {cashflow.shape}")
            results['cashflow'] = cashflow.to_dict()
            
            print(f"  Line items ({len(cashflow.index)}):")
            for idx in list(cashflow.index)[:10]:
                print(f"    - {idx}")
        
        # Quarterly financials
        quarterly_financials = ticker.quarterly_financials
        if quarterly_financials is not None and not quarterly_financials.empty:
            print(f"\n  ✅ Retrieved quarterly financials: {quarterly_financials.shape}")
            results['quarterly_financials'] = quarterly_financials.to_dict()
        
        # Company info
        info = ticker.info
        if info:
            print(f"\n  ✅ Retrieved company info")
            # Filter to only include JSON-serializable data
            safe_info = {k: v for k, v in info.items() if isinstance(v, (str, int, float, bool, type(None)))}
            results['info'] = safe_info
        
        # Save to file
        if results:
            filename = f"yfinance_AAPL_raw.json"
            filepath = save_json(results, filename)
            
            print(f"\n📈 Summary:")
            for key, data in results.items():
                if isinstance(data, dict):
                    print(f"  - {key}: {len(data)} items")
                else:
                    print(f"  - {key}: available")
            
            return results
        else:
            print("\n❌ No data retrieved")
            return None
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function."""
    print("\n" + "="*80)
    print("RAW API DATA RECORDING")
    print("="*80)
    
    # Check if DART API key is configured
    if not opendart_client.api_key:
        print("\n⚠️  WARNING: DART_API_KEY not configured")
        print("   OPENDART tests will be skipped")
        print("   Please set DART_API_KEY in .env file")
    else:
        print(f"\n✅ DART API Key configured")
        # Test OPENDART
        opendart_results = test_opendart_005930()
    
    # Test yfinance (doesn't require API key)
    yfinance_results = test_yfinance_aapl()
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
    print("\nRaw data has been saved to the data/ directory")
    print("Review the JSON files to understand the data structure")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
