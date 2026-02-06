"""
Example script demonstrating KDEVELOPERS API usage.

This script shows how to use the enhanced kdevelopers.py implementation
based on the reference repository from:
https://github.com/koreainvestment/open-trading-api

Before running this script, make sure you have:
1. Set up environment variables in .env file:
   - HANTU_API_KEY: Your KIS Developers app key
   - HANTU_API_SECRET: Your KIS Developers app secret
   - HANTU_BASE_URL: API base URL (e.g., https://openapi.koreainvestment.com:9443)

2. Installed all dependencies: uv pip install -e .

Usage:
    cd backend
    uv run python examples/kdevelopers_example.py
"""

import sys
import os
from datetime import datetime

# Add parent directory to path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.integrations.kdevelopers import kdevelopers_client
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_get_quote():
    """Example: Get real-time stock quote."""
    logger.info("=" * 60)
    logger.info("Example 1: Getting Stock Quote")
    logger.info("=" * 60)
    
    # Samsung Electronics stock code
    symbol = "005930"
    
    logger.info(f"Fetching quote for {symbol} (Samsung Electronics)...")
    quote = kdevelopers_client.get_quote(symbol)
    
    if quote:
        logger.info(f"\n✓ Successfully fetched quote:")
        logger.info(f"  Symbol: {quote.symbol}")
        logger.info(f"  Name: {quote.name}")
        logger.info(f"  Current Price: {quote.current_price:,.0f} KRW")
        logger.info(f"  Change: {quote.change:+,.0f} ({quote.change_percent:+.2f}%)")
        logger.info(f"  Volume: {quote.volume:,}")
        logger.info(f"  High: {quote.high:,.0f} KRW")
        logger.info(f"  Low: {quote.low:,.0f} KRW")
        logger.info(f"  Open: {quote.open:,.0f} KRW")
        logger.info(f"  Timestamp: {quote.timestamp}")
    else:
        logger.error("✗ Failed to fetch quote")
    
    logger.info("")


def example_get_daily_candles():
    """Example: Get daily candle data."""
    logger.info("=" * 60)
    logger.info("Example 2: Getting Daily Candle Data")
    logger.info("=" * 60)
    
    symbol = "005930"
    limit = 5
    
    logger.info(f"Fetching last {limit} daily candles for {symbol}...")
    candles = kdevelopers_client.get_daily_candle(
        symbol=symbol,
        period="D",  # Daily
        adjust_price=True,
        limit=limit
    )
    
    if candles:
        logger.info(f"\n✓ Successfully fetched {len(candles)} candles:")
        for i, candle in enumerate(candles[:limit], 1):
            logger.info(
                f"  {i}. Date: {candle.date} | "
                f"O: {candle.open:,.0f} | "
                f"H: {candle.high:,.0f} | "
                f"L: {candle.low:,.0f} | "
                f"C: {candle.close:,.0f} | "
                f"V: {candle.volume:,}"
            )
    else:
        logger.error("✗ Failed to fetch candles")
    
    logger.info("")


def example_get_minute_candles():
    """Example: Get minute candle data."""
    logger.info("=" * 60)
    logger.info("Example 3: Getting Minute Candle Data")
    logger.info("=" * 60)
    
    symbol = "005930"
    interval = 1  # 1-minute candles
    limit = 5
    minute_date = datetime.now().strftime("%Y%m%d")
    
    logger.info(f"Fetching last {limit} {interval}-minute candles for {symbol}...")
    candles = kdevelopers_client.get_minute_candle(
        symbol=symbol,
        interval=interval,
        limit=limit,
        date=minute_date,
    )
    
    if candles:
        logger.info(f"\n✓ Successfully fetched {len(candles)} candles:")
        for i, candle in enumerate(candles[:limit], 1):
            logger.info(
                f"  {i}. Time: {candle.date} | "
                f"O: {candle.open:,.0f} | "
                f"H: {candle.high:,.0f} | "
                f"L: {candle.low:,.0f} | "
                f"C: {candle.close:,.0f} | "
                f"V: {candle.volume:,}"
            )
    else:
        logger.error("✗ Failed to fetch minute candles")
    
    logger.info("")


def main():
    """Run all examples."""
    logger.info("\n" + "=" * 60)
    logger.info("KDEVELOPERS API Examples")
    logger.info("Based on: https://github.com/koreainvestment/open-trading-api")
    logger.info("=" * 60 + "\n")
    
    try:
        # Example 1: Get stock quote
        example_get_quote()
        
        # Example 2: Get daily candles
        example_get_daily_candles()
        
        # Example 3: Get minute candles
        example_get_minute_candles()
        
        logger.info("=" * 60)
        logger.info("All examples completed!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
