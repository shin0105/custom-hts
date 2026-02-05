#!/usr/bin/env python3
"""Quick database check to verify tables and data."""

import sys
from pathlib import Path

# Add src to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir / "src"))

from src.integrations.supabase_client import supabase_client


def check_database():
    """Check database tables and data."""
    if not supabase_client.client:
        print("❌ Supabase client not initialized")
        return

    print("\n" + "=" * 80)
    print("DATABASE CHECK")
    print("=" * 80)

    # Check Korean data
    print("\n📊 Korean Financial Data (005930 - Samsung):")
    tables = [
        "korean_balance_sheet",
        "korean_income_statement",
        "korean_cashflow_statement",
    ]

    for table in tables:
        try:
            response = (
                supabase_client.client.table(table)
                .select("*", count="exact")
                .eq("symbol", "005930")
                .order("year", desc=True)
                .order("quarter", desc=True)
                .limit(1)
                .execute()
            )

            count = (
                response.count
                if hasattr(response, "count")
                else len(response.data)
            )
            latest = response.data[0] if response.data else None

            if latest:
                q_str = (
                    f"Q{latest['quarter']}"
                    if latest.get("quarter")
                    else "Annual"
                )
                print(f"  ✅ {table}: {count} records")
                print(f"     Latest: {latest['year']} {q_str}")
            else:
                print(f"  ⚠️  {table}: 0 records")

        except Exception as e:
            print(f"  ❌ {table}: Error - {e}")

    # Check US data
    print("\n📊 US Financial Data (AAPL - Apple):")
    tables = [
        "us_balance_sheet",
        "us_income_statement",
        "us_cashflow_statement",
    ]

    for table in tables:
        try:
            response = (
                supabase_client.client.table(table)
                .select("*", count="exact")
                .eq("symbol", "AAPL")
                .order("year", desc=True)
                .order("quarter", desc=True)
                .limit(1)
                .execute()
            )

            count = (
                response.count
                if hasattr(response, "count")
                else len(response.data)
            )
            latest = response.data[0] if response.data else None

            if latest:
                q_str = (
                    f"Q{latest['quarter']}"
                    if latest.get("quarter")
                    else "Annual"
                )
                print(f"  ✅ {table}: {count} records")
                print(f"     Latest: {latest['year']} {q_str}")
            else:
                print(f"  ⚠️  {table}: 0 records")

        except Exception as e:
            print(f"  ❌ {table}: Error - {e}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    check_database()
