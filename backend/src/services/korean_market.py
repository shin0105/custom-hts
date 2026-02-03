"""Service layer for Korean market operations."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.korean import (
    KoreanStockQuote,
    KoreanFinancialStatement,
    KoreanCandleData,
    KoreanAccountBalance,
    KoreanStockPosition,
)
from ..integrations.kdevelopers import kdevelopers_client
from ..integrations.opendart import opendart_client
from ..integrations.supabase_client import supabase_client


class KoreanMarketService:
    """Service for Korean market data operations."""

    async def get_quote(self, symbol: str) -> Optional[KoreanStockQuote]:
        """
        Get real-time quote for a Korean stock.

        Args:
            symbol: Stock code (e.g., "005930")

        Returns:
            KoreanStockQuote or None
        """
        return kdevelopers_client.get_quote(symbol)

    async def get_financials(
        self, symbol: str, year: int, quarter: Optional[int] = None, use_cache: bool = True
    ) -> Optional[KoreanFinancialStatement]:
        """
        Get financial statement for a Korean company.

        Args:
            symbol: Stock code
            year: Fiscal year
            quarter: Optional quarter (1-4)
            use_cache: Whether to use cached data

        Returns:
            KoreanFinancialStatement or None
        """
        # Try to get from cache first if enabled
        if use_cache:
            cached = await supabase_client.get_financial_statement(
                "korean_financials", symbol, year, quarter
            )
            if cached:
                return KoreanFinancialStatement(**cached)

        # Fetch from OPENDART
        statement = opendart_client.get_financial_statement(
            symbol, year, quarter
        )

        # Cache the data if fetched successfully
        if statement and supabase_client.client:
            await supabase_client.save_financial_statement(
                "korean_financials", statement.model_dump()
            )

        return statement


    async def get_daily_candle(
        self,
        symbol: str,
        period: str = "D",
        adjust_price: bool = True,
        limit: int = 100,
    ) -> Optional[List[KoreanCandleData]]:
        """
        Get daily/period candle chart data for a Korean stock.

        Args:
            symbol: Stock code
            period: Period type - "D" (daily), "W" (weekly), "M" (monthly)
            adjust_price: Whether to adjust for stock splits
            limit: Number of candles to retrieve

        Returns:
            List of KoreanCandleData or None
        """
        return kdevelopers_client.get_daily_candle(
            symbol, period, adjust_price, limit
        )

    async def get_minute_candle(
        self, symbol: str, interval: int = 1, limit: int = 100
    ) -> Optional[List[KoreanCandleData]]:
        """
        Get minute candle chart data for a Korean stock.

        Args:
            symbol: Stock code
            interval: Minute interval (1, 3, 5, 10, 15, 30, 60)
            limit: Number of candles to retrieve

        Returns:
            List of KoreanCandleData or None
        """
        return kdevelopers_client.get_minute_candle(symbol, interval, limit)

    async def get_account_balance(
        self, account_number: str, account_product_code: str = "01"
    ) -> Optional[Dict[str, Any]]:
        """
        Get account balance and positions.

        Args:
            account_number: Account number (8 digits)
            account_product_code: Account product code

        Returns:
            Dictionary containing balance and positions, or None
        """
        return kdevelopers_client.get_account_balance(
            account_number, account_product_code
        )


korean_market_service = KoreanMarketService()
