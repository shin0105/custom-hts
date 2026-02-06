"""
Live API testing script for KDEVELOPERS API.

This script tests the actual API functions with real credentials.
Results will be documented for verification.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.integrations.kdevelopers import kdevelopers_client
from src.utils.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_environment():
    """Test if environment variables are set."""
    logger.info("=" * 70)
    logger.info("Testing Environment Configuration")
    logger.info("=" * 70)
    
    has_key = bool(settings.HANTU_API_KEY and settings.HANTU_API_KEY != "your_hantu_api_key_here")
    has_secret = bool(settings.HANTU_API_SECRET and settings.HANTU_API_SECRET != "your_hantu_api_secret_here")
    has_url = bool(settings.HANTU_BASE_URL)
    
    logger.info(f"API Key configured: {has_key}")
    logger.info(f"API Secret configured: {has_secret}")
    logger.info(f"Base URL: {settings.HANTU_BASE_URL}")
    
    if has_key and has_secret:
        logger.info("✓ Environment is properly configured for testing")
        return True
    else:
        logger.warning("✗ Environment variables not configured")
        logger.warning("Please set HANTU_API_KEY and HANTU_API_SECRET in .env file")
        return False


def test_get_quote():
    """Test getting stock quote."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 1: Get Stock Quote (get_quote)")
    logger.info("=" * 70)
    
    symbol = "005930"  # Samsung Electronics
    
    try:
        logger.info(f"Requesting quote for {symbol} (Samsung Electronics)...")
        quote = kdevelopers_client.get_quote(symbol)
        
        if quote:
            logger.info("✓ SUCCESS - Quote retrieved")
            logger.info(f"  Symbol: {quote.symbol}")
            logger.info(f"  Name: {quote.name}")
            logger.info(f"  Current Price: {quote.current_price:,.0f} KRW")
            logger.info(f"  Change: {quote.change:+,.0f} ({quote.change_percent:+.2f}%)")
            logger.info(f"  Volume: {quote.volume:,}")
            logger.info(f"  High: {quote.high:,.0f} KRW")
            logger.info(f"  Low: {quote.low:,.0f} KRW")
            logger.info(f"  Open: {quote.open:,.0f} KRW")
            logger.info(f"  Previous Close: {quote.previous_close:,.0f} KRW")
            logger.info(f"  Timestamp: {quote.timestamp}")
            return True
        else:
            logger.error("✗ FAILED - Quote is None")
            return False
            
    except Exception as e:
        logger.error(f"✗ EXCEPTION - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_daily_candle():
    """Test getting daily candle data."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 2: Get Daily Candle Data (get_daily_candle)")
    logger.info("=" * 70)
    
    symbol = "005930"
    limit = 5
    
    try:
        logger.info(f"Requesting last {limit} daily candles for {symbol}...")
        candles = kdevelopers_client.get_daily_candle(
            symbol=symbol,
            period="D",
            adjust_price=True,
            limit=limit
        )
        
        if candles and len(candles) > 0:
            logger.info(f"✓ SUCCESS - Retrieved {len(candles)} candles")
            for i, candle in enumerate(candles[:limit], 1):
                logger.info(
                    f"  {i}. Date: {candle.date} | "
                    f"O: {candle.open:,.0f} | "
                    f"H: {candle.high:,.0f} | "
                    f"L: {candle.low:,.0f} | "
                    f"C: {candle.close:,.0f} | "
                    f"V: {candle.volume:,}"
                )
            return True
        else:
            logger.error("✗ FAILED - No candles retrieved")
            return False
            
    except Exception as e:
        logger.error(f"✗ EXCEPTION - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_minute_candle():
    """Test getting minute candle data."""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 3: Get Minute Candle Data (get_minute_candle)")
    logger.info("=" * 70)
    
    symbol = "005930"
    interval = 1
    limit = 5
    minute_date = os.getenv("HANTU_MINUTE_CANDLE_DATE")
    
    try:
        logger.info(f"Requesting last {limit} {interval}-minute candles for {symbol}...")
        candles = kdevelopers_client.get_minute_candle(
            symbol=symbol,
            interval=interval,
            limit=limit,
            date=minute_date,
        )
        
        if candles and len(candles) > 0:
            logger.info(f"✓ SUCCESS - Retrieved {len(candles)} candles")
            for i, candle in enumerate(candles[:limit], 1):
                logger.info(
                    f"  {i}. Time: {candle.date} | "
                    f"O: {candle.open:,.0f} | "
                    f"H: {candle.high:,.0f} | "
                    f"L: {candle.low:,.0f} | "
                    f"C: {candle.close:,.0f} | "
                    f"V: {candle.volume:,}"
                )
            return True
        else:
            logger.error("✗ FAILED - No candles retrieved")
            return False
            
    except Exception as e:
        logger.error(f"✗ EXCEPTION - {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests and generate report."""
    logger.info("\n" + "=" * 70)
    logger.info("KDEVELOPERS API Live Testing")
    logger.info(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # Check environment
    if not test_environment():
        logger.error("\n" + "=" * 70)
        logger.error("Cannot proceed with tests - environment not configured")
        logger.error("=" * 70)
        return
    
    # Run tests
    results = {
        "get_quote": test_get_quote(),
        "get_daily_candle": test_get_daily_candle(),
        "get_minute_candle": test_get_minute_candle(),
    }
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    logger.info(f"Tests Passed: {passed}/{total}")
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"  {test_name}: {status}")
    
    logger.info("=" * 70)
    
    # Save results to file
    results_file = "backend/API_TEST_RESULTS.md"
    with open(results_file, "w") as f:
        f.write("# KDEVELOPERS API Live Test Results\n\n")
        f.write(f"**Test Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Tests Passed**: {passed}/{total}\n\n")
        f.write("## Test Results\n\n")
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            f.write(f"- **{test_name}**: {status}\n")
        f.write("\n## Notes\n\n")
        if passed == total:
            f.write("All API functions are working correctly with live credentials.\n")
        else:
            f.write("Some tests failed. Check logs for details.\n")
    
    logger.info(f"Results saved to {results_file}")


if __name__ == "__main__":
    main()
