#!/usr/bin/env python3
"""Test API endpoints for GitHub Actions workflow."""

import requests
import sys

def test_api_endpoints():
    """Test all financial statement API endpoints."""
    base_url = 'http://localhost:8000/api/financials'
    
    print("Testing Financial Statements API Endpoints...")
    print("=" * 80)
    
    tests = [
        ("GET /api/financials/korean/balance-sheet/005930", 
         f"{base_url}/korean/balance-sheet/005930"),
        ("GET /api/financials/us/balance-sheet/AAPL", 
         f"{base_url}/us/balance-sheet/AAPL"),
        ("GET /api/financials/korean/income-statement/005930", 
         f"{base_url}/korean/income-statement/005930"),
        ("GET /api/financials/us/income-statement/AAPL", 
         f"{base_url}/us/income-statement/AAPL"),
        ("GET /api/financials/korean/cashflow/005930", 
         f"{base_url}/korean/cashflow/005930"),
        ("GET /api/financials/us/cashflow/AAPL", 
         f"{base_url}/us/cashflow/AAPL"),
    ]
    
    results = []
    
    for i, (name, url) in enumerate(tests, 1):
        print(f"\n{i}. Testing {name}")
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                count = data.get("count", 0)
                print(f"   ✅ Success - Retrieved {count} records")
                results.append(True)
            elif response.status_code == 503:
                print(f"   ⚠️  Service unavailable (may need database setup)")
                results.append(False)
            else:
                print(f"   ⚠️  Unexpected status: {response.text[:200]}")
                results.append(False)
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection error - API server may not be running")
            results.append(False)
        except requests.exceptions.Timeout:
            print(f"   ⚠️  Request timeout")
            results.append(False)
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            results.append(False)
    
    print("\n" + "=" * 80)
    print(f"✅ API endpoint tests completed: {sum(results)}/{len(results)} passed")
    
    return all(results)

if __name__ == "__main__":
    success = test_api_endpoints()
    sys.exit(0 if success else 1)
