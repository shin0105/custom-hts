#!/usr/bin/env python3
"""Test script for GitHub Actions workflow."""

import sys
from pathlib import Path

# Add backend src to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir / "src"))

def test_supabase_connection():
    """Test Supabase connection."""
    from src.integrations.supabase_client import supabase_client
    
    if supabase_client.client:
        print('✅ Supabase client initialized successfully')
        try:
            # Test connection by listing tables
            response = supabase_client.client.table('korean_financials').select('*', count='exact').limit(1).execute()
            print('✅ Successfully connected to Supabase database')
            print('   korean_financials table accessible')
            return True
        except Exception as e:
            print(f'⚠️  Connection test failed: {e}')
            return False
    else:
        print('❌ Supabase client not initialized')
        return False

def test_opendart_connection():
    """Test OPENDART API connection."""
    from src.integrations.opendart import opendart_client
    
    if opendart_client.api_key:
        print('✅ DART API key configured')
        print(f'   Corp code cache loaded: {len(opendart_client._corp_code_cache)} entries')
        
        # Test with Samsung (005930)
        corp_code = opendart_client.get_corp_code('005930')
        if corp_code:
            print(f'✅ Successfully retrieved corp code for 005930: {corp_code}')
            return True
        else:
            print('⚠️  Corp code not found for 005930')
            return False
    else:
        print('⚠️  DART API key not configured - Korean data tests will be skipped')
        return False

def test_service_methods():
    """Test that service methods are available."""
    from src.services.financial_statements import financial_statement_service
    from src.integrations.supabase_client import supabase_client
    from src.integrations.opendart import opendart_client
    
    print('Testing Financial Statement Service...')
    print('=' * 80)
    
    # Check prerequisites
    has_supabase = bool(supabase_client.client)
    has_dart = bool(opendart_client.api_key)
    
    print(f'Supabase: {"✅" if has_supabase else "❌"}')
    print(f'DART API: {"✅" if has_dart else "⚠️ "}')
    
    if not has_supabase:
        print('\n❌ Cannot test without Supabase connection')
        return False
    
    # Test service methods exist
    print('\nVerifying service methods:')
    methods = [
        'insert_korean_balance_sheet',
        'insert_korean_income_statement',
        'insert_korean_cashflow_statement',
        'insert_us_balance_sheet',
        'insert_us_income_statement',
        'insert_us_cashflow_statement'
    ]
    
    all_present = True
    for method in methods:
        has_method = hasattr(financial_statement_service, method)
        print(f'  {method}: {"✅" if has_method else "❌"}')
        if not has_method:
            all_present = False
    
    if all_present:
        print('\n✅ All service methods available')
    else:
        print('\n❌ Some service methods are missing')
    
    return all_present

if __name__ == "__main__":
    print("Running GitHub Actions Tests")
    print("=" * 80)
    
    # Run tests
    results = []
    
    print("\n1. Testing Supabase Connection")
    print("-" * 80)
    results.append(test_supabase_connection())
    
    print("\n2. Testing OPENDART Connection")
    print("-" * 80)
    results.append(test_opendart_connection())
    
    print("\n3. Testing Service Methods")
    print("-" * 80)
    results.append(test_service_methods())
    
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed")
        sys.exit(1)
