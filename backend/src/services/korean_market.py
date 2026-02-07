"""Service layer for Korean market operations."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.korean import (
    KoreanStockQuote,
    KoreanFinancialStatement,
    KoreanCandleData,
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
            use_cache: Whether to use cached data (parameter kept for API compatibility but not used)

        Returns:
            KoreanFinancialStatement or None
        """
        # Fetch directly from OPENDART without database caching
        statement = opendart_client.get_financial_statement(
            symbol, year, quarter
        )

        return statement


    async def get_daily_candle(
        self,
        symbol: str,
        period: str = "D",
        adjust_price: bool = True,
        limit: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
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
            symbol,
            period,
            adjust_price,
            limit,
            start_date=start_date,
            end_date=end_date,
        )

    async def get_minute_candle(
        self,
        symbol: str,
        interval: int = 1,
        limit: Optional[int] = None,
        date: Optional[str] = None,
        time_str: str = "",
    ) -> Optional[List[KoreanCandleData]]:
        """
        Get minute candle chart data for a Korean stock.

        Args:
            symbol: Stock code
            interval: Minute interval (1, 5, 10, 30, 60)
            limit: Number of candles to retrieve

        Returns:
            List of KoreanCandleData or None
        """
        max_per_day = 390 // interval if interval else 390
        include_previous = limit is not None and limit > max_per_day
        return kdevelopers_client.get_minute_candle(
            symbol,
            interval,
            limit,
            date=date,
            time_str=time_str,
            include_previous=include_previous,
        )

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

    async def get_stock_info(
        self, prdt_type_cd: str, pdno: str
    ) -> List[Dict[str, Any]]:
        """
        Get stock basic information from KDevelopers.

        Args:
            prdt_type_cd: Product type code
            pdno: Product number (stock code)

        Returns:
            Raw output list from search-stock-info API
        """
        return kdevelopers_client.search_stock_info(prdt_type_cd, pdno)


korean_market_service = KoreanMarketService()
