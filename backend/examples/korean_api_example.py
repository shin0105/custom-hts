"""
Example usage of Korean Investment Securities API integration.

This script demonstrates how to use the KDevelopers API client
to fetch stock quotes, candle charts, and account balance.
"""

import asyncio
from src.services.korean_market import korean_market_service


async def main():
    """Main example function demonstrating API usage."""
    
    # Example stock symbol (Samsung Electronics)
    symbol = "005930"
    
    print("=" * 60)
    print("Korean Investment Securities API Example")
    print("=" * 60)
    
    # 1. Get real-time stock quote
    print(f"\n1. Getting real-time quote for {symbol}...")
    quote = await korean_market_service.get_quote(symbol)
    if quote:
        print(f"   Company: {quote.name}")
        print(f"   Current Price: {quote.current_price:,.0f} KRW")
        print(f"   Change: {quote.change:+,.0f} KRW ({quote.change_percent:+.2f}%)")
        print(f"   Volume: {quote.volume:,}")
        print(f"   High: {quote.high:,.0f} KRW")
        print(f"   Low: {quote.low:,.0f} KRW")
    else:
        print("   Failed to fetch quote (check API credentials)")
    
    # 2. Get daily candle data
    print(f"\n2. Getting daily candle data for {symbol}...")
    candles = await korean_market_service.get_daily_candle(
        symbol=symbol,
        period="D",  # Daily
        adjust_price=True,
        limit=5  # Last 5 days
    )
    if candles:
        print(f"   Retrieved {len(candles)} candles:")
        for candle in candles[:5]:  # Show first 5
            print(f"   - {candle.date}: O={candle.open:,.0f} "
                  f"H={candle.high:,.0f} L={candle.low:,.0f} "
                  f"C={candle.close:,.0f} V={candle.volume:,}")
    else:
        print("   Failed to fetch candle data (check API credentials)")
    
    # 3. Get minute candle data
    print(f"\n3. Getting minute candle data for {symbol}...")
    minute_candles = await korean_market_service.get_minute_candle(
        symbol=symbol,
        interval=5,  # 5-minute intervals
        limit=5  # Last 5 candles
    )
    if minute_candles:
        print(f"   Retrieved {len(minute_candles)} minute candles:")
        for candle in minute_candles[:5]:  # Show first 5
            print(f"   - {candle.date}: Close={candle.close:,.0f} "
                  f"Volume={candle.volume:,}")
    else:
        print("   Failed to fetch minute candle data (check API credentials)")
    
    # 4. Get account balance (requires valid account number)
    print("\n4. Getting account balance...")
    print("   Note: This requires a valid account number and will fail")
    print("   with demo credentials.")
    print("   WARNING: This endpoint lacks authentication in current implementation.")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
