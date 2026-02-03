"""Service layer for US market operations."""

from typing import Optional, List
from datetime import datetime
from ..models.us import USStockQuote, USFinancialStatement
from ..integrations.yfinance_client import yfinance_client
from ..integrations.supabase_client import supabase_client


class USMarketService:
    """Service for US market data operations."""

    async def get_quote(self, symbol: str) -> Optional[USStockQuote]:
        """
        Get real-time quote for a US stock.

        Args:
            symbol: Stock ticker symbol

        Returns:
            USStockQuote or None
        """
        return yfinance_client.get_quote(symbol)

    async def get_financials(
        self, symbol: str, use_cache: bool = True
    ) -> Optional[List[USFinancialStatement]]:
        """
        Get financial statements for a US company.

        Args:
            symbol: Stock ticker symbol
            use_cache: Whether to use cached data

        Returns:
            List of USFinancialStatement or None
        """
        # Try to get from cache first if enabled
        if use_cache:
            cached = await supabase_client.get_financial_statement(
                "us_financials", symbol, datetime.now().year
            )
            if cached:
                # Return cached data as list
                return [USFinancialStatement(**cached)]

        # Fetch from Yahoo Finance
        statements = yfinance_client.get_financials(symbol)

        # Cache the data if fetched successfully
        if statements and supabase_client.client:
            for statement in statements:
                await supabase_client.save_financial_statement(
                    "us_financials", statement.model_dump()
                )

        return statements


us_market_service = USMarketService()
