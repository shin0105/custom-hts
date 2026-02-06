"""
Live API testing for KDevelopers Integration.

This script tests all implemented KDevelopers APIs with actual API calls
and saves the raw JSON responses to files for documentation and analysis.

Before running:
1. Ensure environment variables are set in .env:
   - HANTU_API_KEY
   - HANTU_API_SECRET
   - HANTU_BASE_URL
   - HANTU_ACCOUNT_NUMBER (optional, for account balance test)

Usage:
    cd backend
    uv run python tests/test_kdevelopers_live_api.py
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from src.integrations.kdevelopers import kdevelopers_client
from src.utils.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Output directory for JSON responses
OUTPUT_DIR = Path(__file__).parent / "test-results" / "kdevelopers_responses"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_json_response(filename: str, data: dict, description: str = ""):
    """Save response data to JSON file."""
    filepath = OUTPUT_DIR / filename
    output = {
        "timestamp": datetime.now().isoformat(),
        "description": description,
        "data": data,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    logger.info(f"✓ Saved response to: {filepath}")


def test_get_quote():
    """Test 1: Real-time Stock Quote API (주식현재가 시세)."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 1: get_quote() - Real-time Stock Quote")
    logger.info("API: [국내주식] 기본시세 > 주식현재가 시세[v1_국내주식-008]")
    logger.info("=" * 70)

    test_symbols = [
        ("005930", "Samsung Electronics"),
        ("000660", "SK Hynix"),
        ("035420", "NAVER"),
    ]

    results = {}
    for symbol, name in test_symbols:
        logger.info(f"\nTesting: {symbol} ({name})")
        try:
            quote = kdevelopers_client.get_quote(symbol)
            if quote:
                quote_dict = {
                    "symbol": quote.symbol,
                    "name": quote.name,
                    "current_price": quote.current_price,
                    "change": quote.change,
                    "change_percent": quote.change_percent,
                    "volume": quote.volume,
                    "high": quote.high,
                    "low": quote.low,
                    "open": quote.open,
                    "previous_close": quote.previous_close,
                    "timestamp": (
                        quote.timestamp.isoformat()
                        if quote.timestamp
                        else None
                    ),
                }
                results[symbol] = {"success": True, "data": quote_dict}
                logger.info(
                    f"  ✓ Success: {quote.name} - {quote.current_price:,.0f} KRW ({quote.change_percent:+.2f}%)"
                )
            else:
                results[symbol] = {
                    "success": False,
                    "error": "No data returned",
                }
                logger.error(f"  ✗ Failed to fetch quote")
        except Exception as e:
            results[symbol] = {"success": False, "error": str(e)}
            logger.error(f"  ✗ Exception: {e}")

    save_json_response(
        "01_get_quote.json",
        results,
        "Real-time stock quote for multiple stocks",
    )


def test_get_daily_candle():
    """Test 2: Daily Candle Data API (국내주식기간별시세)."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 2: get_daily_candle() - Daily Candle Data")
    logger.info(
        "API: [국내주식] 기본시세 > 국내주식기간별시세(일/주/월/년)[v1_국내주식-016]"
    )
    logger.info("=" * 70)

    symbol = "005930"
    test_configs = [
        ("D", "Daily", 10),
        ("W", "Weekly", 5),
        ("M", "Monthly", 3),
    ]

    results = {}
    for period, period_name, limit in test_configs:
        logger.info(f"\nTesting: {period_name} candles (limit={limit})")
        try:
            candles = kdevelopers_client.get_daily_candle(
                symbol=symbol, period=period, adjust_price=True, limit=limit
            )

            if candles:
                candles_list = []
                for candle in candles:
                    candles_list.append(
                        {
                            "symbol": candle.symbol,
                            "date": candle.date,
                            "open": candle.open,
                            "high": candle.high,
                            "low": candle.low,
                            "close": candle.close,
                            "volume": candle.volume,
                            "change": candle.change,
                            "change_percent": candle.change_percent,
                        }
                    )

                results[period_name.lower()] = {
                    "success": True,
                    "count": len(candles),
                    "data": candles_list,
                }
                logger.info(
                    f"  ✓ Success: Retrieved {len(candles)} {period_name.lower()} candles"
                )
                logger.info(
                    f"    Latest: {candles[0].date} - Close: {candles[0].close:,.0f} KRW"
                )
            else:
                results[period_name.lower()] = {
                    "success": False,
                    "error": "No data returned",
                }
                logger.error(f"  ✗ Failed to fetch candles")
        except Exception as e:
            results[period_name.lower()] = {"success": False, "error": str(e)}
            logger.error(f"  ✗ Exception: {e}")

    save_json_response(
        "02_get_daily_candle.json",
        results,
        f"Daily, weekly, and monthly candle data for {symbol}",
    )


def test_get_minute_candle():
    """Test 3: Minute Candle Data API (국내주식분봉조회)."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 3: get_minute_candle() - Minute Candle Data")
    logger.info("API: [국내주식] 기본시세 > 주식일별분봉조회[국내주식-213]")
    logger.info("=" * 70)

    symbol = "005930"
    test_intervals = [1, 5, 10, 30]
    minute_date = os.getenv("HANTU_MINUTE_CANDLE_DATE")

    results = {}
    for interval in test_intervals:
        logger.info(f"\nTesting: {interval}-minute candles")
        try:
            candles = kdevelopers_client.get_minute_candle(
                symbol=symbol, interval=interval, limit=5, date=minute_date
            )

            if candles:
                candles_list = []
                for candle in candles:
                    candles_list.append(
                        {
                            "symbol": candle.symbol,
                            "time": candle.date,
                            "open": candle.open,
                            "high": candle.high,
                            "low": candle.low,
                            "close": candle.close,
                            "volume": candle.volume,
                            "change": candle.change,
                            "change_percent": candle.change_percent,
                        }
                    )

                results[f"{interval}_minute"] = {
                    "success": True,
                    "count": len(candles),
                    "data": candles_list,
                }
                logger.info(f"  ✓ Success: Retrieved {len(candles)} candles")
                logger.info(
                    f"    Latest: {candles[0].date} - Close: {candles[0].close:,.0f} KRW"
                )
            else:
                results[f"{interval}_minute"] = {
                    "success": False,
                    "error": "No data returned",
                }
                logger.error(f"  ✗ Failed to fetch candles")
        except Exception as e:
            results[f"{interval}_minute"] = {"success": False, "error": str(e)}
            logger.error(f"  ✗ Exception: {e}")

    save_json_response(
        "03_get_minute_candle.json",
        results,
        f"Minute candle data with different intervals for {symbol}",
    )


def test_get_account_balance():
    """Test 5: Account Balance API (주식잔고조회)."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 5: get_account_balance() - Account Balance")
    logger.info("API: [국내주식] 계좌/잔고 > 주식잔고조회[v1_국내주식-006]")
    logger.info("=" * 70)

    account_number = os.getenv("HANTU_ACCOUNT_NUMBER", "")

    if not account_number:
        logger.warning("⚠ HANTU_ACCOUNT_NUMBER not set in environment")
        logger.info("  Skipping account balance test")
        save_json_response(
            "05_get_account_balance.json",
            {
                "success": False,
                "error": "Account number not configured",
                "message": "Set HANTU_ACCOUNT_NUMBER in .env to test this API",
            },
            "Account balance and positions (requires account number)",
        )
        return

    logger.info(f"Testing with account: {account_number[:4]}****")
    try:
        result = kdevelopers_client.get_account_balance(account_number)

        if result:
            balance = result.get("balance")
            positions = result.get("positions", [])

            balance_dict = {
                "account_number": balance.account_number,
                "total_evaluation": balance.total_evaluation,
                "cash_balance": balance.cash_balance,
                "investment_amount": balance.investment_amount,
                "profit_loss": balance.profit_loss,
                "profit_loss_percent": balance.profit_loss_percent,
                "timestamp": (
                    balance.timestamp.isoformat()
                    if balance.timestamp
                    else None
                ),
            }

            positions_list = []
            for pos in positions:
                positions_list.append(
                    {
                        "symbol": pos.symbol,
                        "name": pos.name,
                        "quantity": pos.quantity,
                        "average_price": pos.average_price,
                        "current_price": pos.current_price,
                        "evaluation_amount": pos.evaluation_amount,
                        "profit_loss": pos.profit_loss,
                        "profit_loss_percent": pos.profit_loss_percent,
                    }
                )

            response_data = {
                "success": True,
                "balance": balance_dict,
                "positions": positions_list,
                "position_count": len(positions),
            }

            logger.info(f"  ✓ Success:")
            logger.info(
                f"    Total Evaluation: {balance.total_evaluation:,.0f} KRW"
            )
            logger.info(f"    Cash Balance: {balance.cash_balance:,.0f} KRW")
            logger.info(
                f"    Profit/Loss: {balance.profit_loss:,.0f} KRW ({balance.profit_loss_percent:+.2f}%)"
            )
            logger.info(f"    Positions: {len(positions)}")
        else:
            response_data = {"success": False, "error": "No data returned"}
            logger.error("  ✗ Failed to fetch account balance")

        save_json_response(
            "05_get_account_balance.json",
            response_data,
            "Account balance and stock positions",
        )
    except Exception as e:
        logger.error(f"  ✗ Exception: {e}")
        save_json_response(
            "05_get_account_balance.json",
            {"success": False, "error": str(e)},
            "Account balance test failed with exception",
        )


def test_search_stock_info():
    """Test 4: Stock Basic Info API (주식기본조회)."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 4: search_stock_info() - Stock Basic Info")
    logger.info("API: [국내주식] 종목정보 > 주식기본조회[v1_국내주식-067]")
    logger.info("=" * 70)

    prdt_type_cd = "300"
    pdno = "005930"

    try:
        results = kdevelopers_client.search_stock_info(prdt_type_cd, pdno)
        success = bool(results)
        payload = {
            "success": success,
            "count": len(results),
            "data": results,
        }
        if success:
            logger.info(f"  ✓ Success: Retrieved {len(results)} records")
        else:
            logger.error("  ✗ No data returned")
    except Exception as e:
        payload = {"success": False, "error": str(e)}
        logger.error(f"  ✗ Exception: {e}")

    save_json_response(
        "04_search_stock_info.json",
        payload,
        f"Stock basic info for {pdno}",
    )


def generate_summary_report():
    """Generate summary report of all tests."""
    logger.info("\n" + "=" * 70)
    logger.info("Generating Summary Report")
    logger.info("=" * 70)

    api_list = [
        {
            "name": "get_quote()",
            "description": "주식현재가 시세 - Real-time Stock Quote",
            "api_path": "/uapi/domestic-stock/v1/quotations/inquire-price",
            "tr_id": "FHKST01010100",
            "file": "01_get_quote.json",
            "parameters": ["symbol"],
            "returns": "KoreanStockQuote object",
        },
        {
            "name": "get_daily_candle()",
            "description": "국내주식기간별시세 - Daily/Weekly/Monthly Candle Data",
            "api_path": "/uapi/domestic-stock/v1/quotations/inquire-daily-price",
            "tr_id": "FHKST01010400",
            "file": "02_get_daily_candle.json",
            "parameters": ["symbol", "period", "adjust_price", "limit"],
            "returns": "List[KoreanCandleData]",
        },
        {
            "name": "get_minute_candle()",
            "description": "주식일별분봉조회 - Minute Candle Data",
            "api_path": "/uapi/domestic-stock/v1/quotations/inquire-time-dailychartprice",
            "tr_id": "FHKST03010230",
            "file": "03_get_minute_candle.json",
            "parameters": ["symbol", "interval", "limit", "date", "time_str"],
            "returns": "List[KoreanCandleData]",
        },
        {
            "name": "search_stock_info()",
            "description": "주식기본조회 - Stock Basic Info",
            "api_path": "/uapi/domestic-stock/v1/quotations/search-stock-info",
            "tr_id": "CTPF1002R",
            "file": "04_search_stock_info.json",
            "parameters": ["prdt_type_cd", "pdno"],
            "returns": "List[Dict[str, Any]]",
        },
        {
            "name": "get_account_balance()",
            "description": "주식잔고조회 - Account Balance and Positions",
            "api_path": "/uapi/domestic-stock/v1/trading/inquire-balance",
            "tr_id": "TTTC8434R / VTTC8434R",
            "file": "05_get_account_balance.json",
            "parameters": ["account_number", "account_product_code"],
            "returns": "Dict with balance and positions",
        },
    ]

    summary = {
        "test_date": datetime.now().isoformat(),
        "total_apis": len(api_list),
        "apis": api_list,
        "output_directory": str(OUTPUT_DIR),
        "documentation": {
            "base_url": settings.HANTU_BASE_URL,
            "reference": "https://github.com/koreainvestment/open-trading-api",
            "implementation": "backend/src/integrations/kdevelopers.py",
        },
    }

    save_json_response(
        "00_summary.json",
        summary,
        "Summary of all KDevelopers API implementations and test results",
    )

    logger.info("\n" + "=" * 70)
    logger.info("KDEVELOPERS API IMPLEMENTATION SUMMARY")
    logger.info("=" * 70)
    logger.info(f"\nTotal APIs Implemented: {len(api_list)}")
    logger.info("\nAPI List:")
    for i, api in enumerate(api_list, 1):
        logger.info(f"\n{i}. {api['name']}")
        logger.info(f"   Description: {api['description']}")
        logger.info(f"   API Path: {api['api_path']}")
        logger.info(f"   TR ID: {api['tr_id']}")
        logger.info(f"   Parameters: {', '.join(api['parameters'])}")
        logger.info(f"   Returns: {api['returns']}")
        logger.info(f"   Response File: {api['file']}")


def main():
    """Run all API tests."""
    logger.info("\n" + "=" * 70)
    logger.info("KDEVELOPERS API LIVE TESTING")
    logger.info("=" * 70)
    logger.info(f"Output Directory: {OUTPUT_DIR}")
    logger.info(f"Base URL: {settings.HANTU_BASE_URL}")
    logger.info("=" * 70)

    # Generate summary first
    generate_summary_report()

    # Run all tests
    test_get_quote()
    test_get_daily_candle()
    test_get_minute_candle()
    test_search_stock_info()
    test_get_account_balance()

    logger.info("\n" + "=" * 70)
    logger.info("ALL TESTS COMPLETED")
    logger.info("=" * 70)
    logger.info(f"\n✓ All response files saved to: {OUTPUT_DIR}")
    logger.info("\nFiles created:")
    logger.info("  - 00_summary.json (API implementation summary)")
    logger.info("  - 01_get_quote.json (Real-time quotes)")
    logger.info("  - 02_get_daily_candle.json (Daily/weekly/monthly candles)")
    logger.info("  - 03_get_minute_candle.json (Minute candles)")
    logger.info("  - 04_search_stock_info.json (Stock basic info)")
    logger.info("  - 05_get_account_balance.json (Account balance)")


if __name__ == "__main__":
    main()
