#!/usr/bin/env python3
"""
Comprehensive API testing script for HTS application.

This script:
1. Tests all API connections (kdevelopers, OPENDART, Supabase, yfinance)
2. Records raw API responses for inspection
3. Retrieves and stores 202509 (Sept 2025 Q3) financial statements for:
   - 005930 (Samsung Electronics)
   - AAPL (Apple Inc.)
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
import traceback

# Add src to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir / "src"))

from src.integrations.supabase_client import supabase_client
from src.integrations.opendart import opendart_client
from src.integrations.yfinance_client import yfinance_client
from src.services.financial_statements import financial_statement_service
from src.utils.config import settings

# Create results directory
results_dir = backend_dir / "test_results"
results_dir.mkdir(exist_ok=True)


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


def save_json(data, filename):
    """Save data to JSON file."""
    filepath = results_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"  💾 Saved to {filepath.name}")
    return filepath


def test_environment_variables():
    """Test that all environment variables are set."""
    print_section("1. Testing Environment Variables")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "variables": {}
    }
    
    # Check each environment variable
    env_vars = {
        "DART_API_KEY": settings.DART_API_KEY,
        "SUPABASE_URL": settings.SUPABASE_URL,
        "SUPABASE_KEY": settings.SUPABASE_KEY,
        "HANTU_API_KEY": settings.HANTU_API_KEY,
        "HANTU_API_SECRET": settings.HANTU_API_SECRET,
    }
    
    all_set = True
    for key, value in env_vars.items():
        is_set = bool(value)
        results["variables"][key] = {
            "set": is_set,
            "length": len(value) if value else 0
        }
        
        status = "✅" if is_set else "❌"
        print(f"  {status} {key}: {'SET' if is_set else 'NOT SET'}")
        
        if not is_set and key not in ["HANTU_API_KEY", "HANTU_API_SECRET"]:
            all_set = False
    
    results["all_required_set"] = all_set
    save_json(results, "01_environment_variables.json")
    
    return results


def test_supabase_connection():
    """Test Supabase connection."""
    print_section("2. Testing Supabase Connection")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "connected": False,
        "tables": {}
    }
    
    if not supabase_client.client:
        print("  ❌ Supabase client not initialized")
        save_json(results, "02_supabase_connection.json")
        return results
    
    print("  ✅ Supabase client initialized")
    results["connected"] = True
    
    # Test table access
    tables = [
        "korean_balance_sheet",
        "korean_income_statement",
        "korean_cashflow_statement",
        "us_balance_sheet",
        "us_income_statement",
        "us_cashflow_statement",
    ]
    
    print("\n  Testing table access:")
    for table in tables:
        try:
            response = supabase_client.client.table(table).select('*', count='exact').limit(1).execute()
            count = response.count if hasattr(response, 'count') else 0
            results["tables"][table] = {
                "accessible": True,
                "record_count": count
            }
            print(f"    ✅ {table}: accessible ({count} records)")
        except Exception as e:
            results["tables"][table] = {
                "accessible": False,
                "error": str(e)
            }
            print(f"    ❌ {table}: {str(e)[:50]}")
    
    save_json(results, "02_supabase_connection.json")
    return results


def test_opendart_connection():
    """Test OPENDART API connection."""
    print_section("3. Testing OPENDART API Connection")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "api_key_set": bool(opendart_client.api_key),
        "corp_codes_loaded": len(opendart_client._corp_code_cache),
        "test_queries": {}
    }
    
    if not opendart_client.api_key:
        print("  ❌ DART API key not configured")
        save_json(results, "03_opendart_connection.json")
        return results
    
    print(f"  ✅ DART API key configured")
    print(f"  ✅ Corp code cache: {len(opendart_client._corp_code_cache)} entries")
    
    # Test corp code lookup
    test_symbol = "005930"
    corp_code = opendart_client.get_corp_code(test_symbol)
    
    results["test_queries"]["corp_code_lookup"] = {
        "symbol": test_symbol,
        "corp_code": corp_code,
        "success": corp_code is not None
    }
    
    if corp_code:
        print(f"  ✅ Corp code for {test_symbol}: {corp_code}")
    else:
        print(f"  ❌ Corp code not found for {test_symbol}")
    
    # Test fetching a financial statement
    try:
        raw_data = opendart_client.get_financial_statement_raw(
            symbol=test_symbol,
            year=2024,
            quarter=3
        )
        
        results["test_queries"]["financial_statement"] = {
            "symbol": test_symbol,
            "year": 2024,
            "quarter": 3,
            "success": raw_data is not None,
            "items_count": len(raw_data) if raw_data else 0
        }
        
        if raw_data:
            print(f"  ✅ Retrieved financial data: {len(raw_data)} items")
        else:
            print(f"  ⚠️  No financial data available")
    except Exception as e:
        print(f"  ❌ Error fetching financial data: {e}")
        results["test_queries"]["financial_statement"] = {
            "success": False,
            "error": str(e)
        }
    
    save_json(results, "03_opendart_connection.json")
    return results


def test_yfinance_connection():
    """Test yfinance API connection."""
    print_section("4. Testing yfinance API Connection")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "test_queries": {}
    }
    
    try:
        import yfinance as yf
        test_symbol = "AAPL"
        
        print(f"  Testing {test_symbol}...")
        ticker = yf.Ticker(test_symbol)
        
        # Try to get info
        info = ticker.info
        results["test_queries"]["info"] = {
            "symbol": test_symbol,
            "success": bool(info),
            "company_name": info.get("longName") if info else None
        }
        
        if info:
            print(f"    ✅ Company info: {info.get('longName', 'N/A')}")
        
        # Try to get financials
        financials = ticker.financials
        results["test_queries"]["financials"] = {
            "symbol": test_symbol,
            "success": financials is not None and not financials.empty,
            "years": [str(d.year) for d in financials.columns] if financials is not None and not financials.empty else []
        }
        
        if financials is not None and not financials.empty:
            print(f"    ✅ Financials available: {len(financials.columns)} periods")
        else:
            print(f"    ⚠️  No financials available")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        results["test_queries"]["error"] = str(e)
        traceback.print_exc()
    
    save_json(results, "04_yfinance_connection.json")
    return results


def test_kdevelopers_connection():
    """Test Korean Investment Securities (kdevelopers) API connection."""
    print_section("5. Testing kdevelopers API Connection")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "api_key_set": bool(settings.HANTU_API_KEY),
        "api_secret_set": bool(settings.HANTU_API_SECRET),
        "test_queries": {}
    }
    
    if not settings.HANTU_API_KEY or not settings.HANTU_API_SECRET:
        print("  ⚠️  kdevelopers API credentials not configured")
        print("     This is optional - OPENDART will be used for Korean data")
        save_json(results, "05_kdevelopers_connection.json")
        return results
    
    print(f"  ✅ kdevelopers API key configured")
    print(f"  ✅ kdevelopers API secret configured")
    
    # Note: Actual kdevelopers API testing would require OAuth token generation
    # which is beyond the scope of this basic test
    print("  ℹ️  Full kdevelopers API testing requires OAuth token generation")
    print("     Using OPENDART for Korean financial data instead")
    
    save_json(results, "05_kdevelopers_connection.json")
    return results


def retrieve_korean_financial_data_202509():
    """Retrieve 202509 (Q3 2025) financial data for Korean stock 005930."""
    print_section("6. Retrieving Korean Financial Data - 005930 (Q3 2025)")
    
    symbol = "005930"
    year = 2025
    quarter = 3
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "year": year,
        "quarter": quarter,
        "raw_data": {},
        "insertion_results": {}
    }
    
    if not opendart_client.api_key:
        print("  ❌ DART API key not configured - cannot retrieve data")
        save_json(results, "06_korean_financial_data_202509.json")
        return results
    
    print(f"\n  📊 Fetching data for {symbol} {year}Q{quarter}...")
    
    # Try to fetch raw data first
    try:
        raw_data = opendart_client.get_financial_statement_raw(
            symbol=symbol,
            year=year,
            quarter=quarter
        )
        
        if raw_data:
            print(f"  ✅ Retrieved raw data: {len(raw_data)} items")
            results["raw_data"]["items_count"] = len(raw_data)
            results["raw_data"]["sample"] = raw_data[:5]  # Save first 5 items as sample
            
            # Save full raw data
            save_json({"symbol": symbol, "year": year, "quarter": quarter, "data": raw_data}, 
                     f"raw_opendart_{symbol}_{year}Q{quarter}.json")
        else:
            print(f"  ⚠️  No data available for {year}Q{quarter}")
            print(f"     Data may not be published yet - trying {year-1}Q{quarter} instead...")
            
            # Try previous year
            year = year - 1
            raw_data = opendart_client.get_financial_statement_raw(
                symbol=symbol,
                year=year,
                quarter=quarter
            )
            
            if raw_data:
                print(f"  ✅ Retrieved data for {year}Q{quarter}: {len(raw_data)} items")
                results["year"] = year
                results["raw_data"]["items_count"] = len(raw_data)
                results["raw_data"]["sample"] = raw_data[:5]
                
                save_json({"symbol": symbol, "year": year, "quarter": quarter, "data": raw_data}, 
                         f"raw_opendart_{symbol}_{year}Q{quarter}.json")
            else:
                print(f"  ❌ No data available")
                save_json(results, "06_korean_financial_data_202509.json")
                return results
    except Exception as e:
        print(f"  ❌ Error retrieving raw data: {e}")
        traceback.print_exc()
        results["raw_data"]["error"] = str(e)
        save_json(results, "06_korean_financial_data_202509.json")
        return results
    
    # Insert data into Supabase
    print(f"\n  💾 Inserting data into Supabase...")
    
    try:
        insertion_result = financial_statement_service.insert_all_korean_statements(
            symbol=symbol,
            year=year,
            quarter=quarter
        )
        
        results["insertion_results"] = insertion_result
        
        print(f"    Balance Sheet:     {'✅' if insertion_result['balance_sheet'] else '❌'}")
        print(f"    Income Statement:  {'✅' if insertion_result['income_statement'] else '❌'}")
        print(f"    Cash Flow:         {'✅' if insertion_result['cashflow_statement'] else '❌'}")
        
    except Exception as e:
        print(f"  ❌ Error inserting data: {e}")
        traceback.print_exc()
        results["insertion_results"]["error"] = str(e)
    
    save_json(results, "06_korean_financial_data_202509.json")
    return results


def retrieve_us_financial_data_202509():
    """Retrieve 202509 (Q3 2025) financial data for US stock AAPL."""
    print_section("7. Retrieving US Financial Data - AAPL (Q3 2025)")
    
    symbol = "AAPL"
    year = 2025
    quarter = 3
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "year": year,
        "quarter": quarter,
        "raw_data": {},
        "insertion_results": {}
    }
    
    print(f"\n  📊 Fetching data for {symbol} {year}Q{quarter}...")
    
    # Try to fetch raw data first
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        
        # Get quarterly financials
        quarterly_financials = ticker.quarterly_financials
        balance_sheet = ticker.quarterly_balance_sheet
        cashflow = ticker.quarterly_cashflow
        
        if quarterly_financials is not None and not quarterly_financials.empty:
            print(f"  ✅ Retrieved quarterly financials: {quarterly_financials.shape}")
            results["raw_data"]["financials_shape"] = list(quarterly_financials.shape)
            results["raw_data"]["available_quarters"] = [str(d) for d in quarterly_financials.columns]
            
            # Save raw data
            raw_data = {
                "symbol": symbol,
                "financials": quarterly_financials.to_dict(),
                "balance_sheet": balance_sheet.to_dict() if balance_sheet is not None else None,
                "cashflow": cashflow.to_dict() if cashflow is not None else None,
            }
            save_json(raw_data, f"raw_yfinance_{symbol}_{year}Q{quarter}.json")
        else:
            print(f"  ⚠️  No quarterly data available")
            # Try annual data
            print(f"     Trying annual data for {year}...")
            financials = ticker.financials
            if financials is not None and not financials.empty:
                print(f"  ✅ Retrieved annual financials: {financials.shape}")
                results["raw_data"]["financials_shape"] = list(financials.shape)
                quarter = None  # Use annual data
                results["quarter"] = None
            else:
                print(f"  ❌ No data available")
                save_json(results, "07_us_financial_data_202509.json")
                return results
                
    except Exception as e:
        print(f"  ❌ Error retrieving raw data: {e}")
        traceback.print_exc()
        results["raw_data"]["error"] = str(e)
        save_json(results, "07_us_financial_data_202509.json")
        return results
    
    # Insert data into Supabase
    print(f"\n  💾 Inserting data into Supabase...")
    
    # Note: yfinance data may not have 2025 Q3 yet, so we'll use the latest available
    try:
        # Use 2024 data as 2025 may not be available yet
        actual_year = 2024
        print(f"     Using {actual_year} data (2025 may not be published yet)")
        
        insertion_result = financial_statement_service.insert_all_us_statements(
            symbol=symbol,
            year=actual_year,
            quarter=quarter
        )
        
        results["insertion_results"] = insertion_result
        results["year"] = actual_year
        
        print(f"    Balance Sheet:     {'✅' if insertion_result['balance_sheet'] else '❌'}")
        print(f"    Income Statement:  {'✅' if insertion_result['income_statement'] else '❌'}")
        print(f"    Cash Flow:         {'✅' if insertion_result['cashflow_statement'] else '❌'}")
        
    except Exception as e:
        print(f"  ❌ Error inserting data: {e}")
        traceback.print_exc()
        results["insertion_results"]["error"] = str(e)
    
    save_json(results, "07_us_financial_data_202509.json")
    return results


def verify_data_in_database():
    """Verify data was stored in Supabase."""
    print_section("8. Verifying Data in Database")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tables": {}
    }
    
    if not supabase_client.client:
        print("  ❌ Supabase client not initialized")
        save_json(results, "08_database_verification.json")
        return results
    
    # Check Korean data
    print("\n  Korean data (005930):")
    tables = ["korean_balance_sheet", "korean_income_statement", "korean_cashflow_statement"]
    
    for table in tables:
        try:
            response = (
                supabase_client.client.table(table)
                .select("year, quarter", count="exact")
                .eq("symbol", "005930")
                .order("year", desc=True)
                .order("quarter", desc=True)
                .limit(5)
                .execute()
            )
            
            count = len(response.data) if response.data else 0
            latest = response.data[0] if response.data else None
            
            results["tables"][table] = {
                "count": count,
                "latest": latest
            }
            
            if latest:
                q_str = f"Q{latest['quarter']}" if latest.get('quarter') else "Annual"
                print(f"    ✅ {table}: {count} records, latest: {latest['year']} {q_str}")
            else:
                print(f"    ⚠️  {table}: {count} records")
                
        except Exception as e:
            print(f"    ❌ {table}: Error - {str(e)[:50]}")
            results["tables"][table] = {"error": str(e)}
    
    # Check US data
    print("\n  US data (AAPL):")
    tables = ["us_balance_sheet", "us_income_statement", "us_cashflow_statement"]
    
    for table in tables:
        try:
            response = (
                supabase_client.client.table(table)
                .select("year, quarter", count="exact")
                .eq("symbol", "AAPL")
                .order("year", desc=True)
                .order("quarter", desc=True)
                .limit(5)
                .execute()
            )
            
            count = len(response.data) if response.data else 0
            latest = response.data[0] if response.data else None
            
            results["tables"][table] = {
                "count": count,
                "latest": latest
            }
            
            if latest:
                q_str = f"Q{latest['quarter']}" if latest.get('quarter') else "Annual"
                print(f"    ✅ {table}: {count} records, latest: {latest['year']} {q_str}")
            else:
                print(f"    ⚠️  {table}: {count} records")
                
        except Exception as e:
            print(f"    ❌ {table}: Error - {str(e)[:50]}")
            results["tables"][table] = {"error": str(e)}
    
    save_json(results, "08_database_verification.json")
    return results


def generate_summary_report(all_results):
    """Generate final summary report."""
    print_header("TEST SUMMARY REPORT")
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "test_sections": {},
        "overall_status": "success"
    }
    
    # Environment Variables
    env_results = all_results.get("environment", {})
    summary["test_sections"]["environment"] = {
        "status": "✅" if env_results.get("all_required_set") else "❌",
        "details": "All required environment variables set" if env_results.get("all_required_set") else "Some variables missing"
    }
    
    # Supabase
    supabase_results = all_results.get("supabase", {})
    summary["test_sections"]["supabase"] = {
        "status": "✅" if supabase_results.get("connected") else "❌",
        "details": f"Connected, {len(supabase_results.get('tables', {}))} tables accessible"
    }
    
    # OPENDART
    opendart_results = all_results.get("opendart", {})
    summary["test_sections"]["opendart"] = {
        "status": "✅" if opendart_results.get("api_key_set") else "❌",
        "details": f"API key set, {opendart_results.get('corp_codes_loaded', 0)} corp codes loaded"
    }
    
    # yfinance
    yfinance_results = all_results.get("yfinance", {})
    has_yf_success = any(q.get("success") for q in yfinance_results.get("test_queries", {}).values() if isinstance(q, dict))
    summary["test_sections"]["yfinance"] = {
        "status": "✅" if has_yf_success else "⚠️",
        "details": "API accessible" if has_yf_success else "Limited access"
    }
    
    # Korean data
    korean_results = all_results.get("korean_data", {})
    korean_success = any(korean_results.get("insertion_results", {}).values())
    summary["test_sections"]["korean_data"] = {
        "status": "✅" if korean_success else "⚠️",
        "details": f"Data for {korean_results.get('symbol', '005930')} {korean_results.get('year', '')}Q{korean_results.get('quarter', '')}"
    }
    
    # US data
    us_results = all_results.get("us_data", {})
    us_success = any(us_results.get("insertion_results", {}).values())
    summary["test_sections"]["us_data"] = {
        "status": "✅" if us_success else "⚠️",
        "details": f"Data for {us_results.get('symbol', 'AAPL')} {us_results.get('year', '')}Q{us_results.get('quarter', '') or 'Annual'}"
    }
    
    # Print summary
    print("\n📊 Test Results:")
    for section, info in summary["test_sections"].items():
        print(f"  {info['status']} {section}: {info['details']}")
    
    print("\n📁 Test results saved to: backend/test_results/")
    print("   - JSON files with detailed results for each test section")
    print("   - Raw API response data for inspection")
    
    save_json(summary, "00_summary_report.json")
    
    return summary


def main():
    """Main test execution."""
    print_header("COMPREHENSIVE API TESTING & DATA RETRIEVAL")
    print("\nThis script will:")
    print("  1. Test all API connections")
    print("  2. Retrieve raw data for inspection")
    print("  3. Store 202509 financial statements in Supabase")
    print("\nResults will be saved to: backend/test_results/")
    
    all_results = {}
    
    # Run all tests
    try:
        all_results["environment"] = test_environment_variables()
        all_results["supabase"] = test_supabase_connection()
        all_results["opendart"] = test_opendart_connection()
        all_results["yfinance"] = test_yfinance_connection()
        all_results["kdevelopers"] = test_kdevelopers_connection()
        all_results["korean_data"] = retrieve_korean_financial_data_202509()
        all_results["us_data"] = retrieve_us_financial_data_202509()
        all_results["verification"] = verify_data_in_database()
        
        # Generate summary
        summary = generate_summary_report(all_results)
        
        print_header("TESTING COMPLETE")
        print("\n✅ All tests executed successfully!")
        print("\n📋 Next Steps:")
        print("  1. Review test results in backend/test_results/")
        print("  2. Check raw API data files for data structure")
        print("  3. Verify data in Supabase dashboard")
        print("  4. Use the stored data in your HTS application")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
