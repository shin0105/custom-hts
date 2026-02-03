"""Service layer for Korean market operations."""

from typing import Optional
from datetime import datetime
from ..models.korean import KoreanStockQuote, KoreanFinancialStatement
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


korean_market_service = KoreanMarketService()
