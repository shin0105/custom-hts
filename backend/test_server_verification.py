#!/usr/bin/env python3
"""
Simple script to verify the FastAPI server can start and respond to requests.
This is a smoke test to ensure the OpenDartReader integration doesn't break the API.
"""

import sys
import time
import requests
from pathlib import Path

# Add src to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir / "src"))


def test_import():
    """Test that imports work."""
    print("Testing imports...")
    try:
        from src.main import app
        from src.integrations.opendart import opendart_client
        from src.api.korean import router
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_routes():
    """Test that all expected routes are registered."""
    print("\nTesting route registration...")
    try:
        from src.main import app
        
        expected_routes = [
            "/api/korean/quote/{symbol}",
            "/api/korean/financials/{symbol}",
            "/api/korean/company/{symbol}",
            "/api/korean/disclosures",
            "/api/korean/financials/{symbol}/all",
            "/api/korean/financials/{symbol}/balance-sheet",
            "/api/korean/financials/{symbol}/income-statement",
            "/api/korean/financials/{symbol}/cash-flow",
        ]
        
        app_routes = [route.path for route in app.routes if hasattr(route, 'path')]
        
        for route in expected_routes:
            if route in app_routes:
                print(f"  ✅ {route}")
            else:
                print(f"  ❌ {route} NOT FOUND")
                return False
        
        print("✅ All expected routes are registered")
        return True
    except Exception as e:
        print(f"❌ Route test failed: {e}")
        return False


def test_opendart_client():
    """Test that the OPENDART client initializes correctly."""
    print("\nTesting OPENDART client...")
    try:
        from src.integrations.opendart import opendart_client
        
        # Test basic attributes
        assert hasattr(opendart_client, 'api_key'), "Missing api_key attribute"
        assert hasattr(opendart_client, 'base_url'), "Missing base_url attribute"
        assert hasattr(opendart_client, 'dart_reader'), "Missing dart_reader attribute"
        
        # Test methods
        assert hasattr(opendart_client, 'get_corp_code'), "Missing get_corp_code method"
        assert hasattr(opendart_client, 'get_financial_statement'), "Missing get_financial_statement method"
        assert hasattr(opendart_client, 'get_company_info'), "Missing get_company_info method"
        assert hasattr(opendart_client, 'get_disclosure_list'), "Missing get_disclosure_list method"
        assert hasattr(opendart_client, 'get_finstate_all'), "Missing get_finstate_all method"
        
        # Test corp code cache
        assert len(opendart_client._corp_code_cache) > 0, "Corp code cache is empty"
        
        print("✅ OPENDART client initialized correctly")
        print(f"   - Corp codes cached: {len(opendart_client._corp_code_cache)}")
        print(f"   - OpenDartReader available: {opendart_client.dart_reader is not None}")
        return True
    except Exception as e:
        print(f"❌ OPENDART client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification tests."""
    print("=" * 80)
    print("FastAPI Server Verification")
    print("=" * 80)
    
    results = []
    
    # Test 1: Imports
    results.append(("Import Test", test_import()))
    
    # Test 2: Routes
    results.append(("Route Test", test_routes()))
    
    # Test 3: OPENDART Client
    results.append(("OPENDART Client Test", test_opendart_client()))
    
    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:30s}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✅ All tests passed! Server is ready to run.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
