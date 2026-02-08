"""Service layer for US market operations."""

from typing import Optional, List
from starlette.concurrency import run_in_threadpool
from datetime import datetime
from ..models.us import (
    USStockQuote,
    USFinancialStatement,
    USCandleData,
    USValuationMetrics,
)
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
            cached = await run_in_threadpool(
                supabase_client.get_financial_statement,
                "us_financials",
                symbol,
                datetime.now().year,
            )
            if cached:
                # Return cached data as list
                return [USFinancialStatement(**cached)]

        # Fetch from Yahoo Finance
        statements = yfinance_client.get_financials(symbol)

        # Cache the data if fetched successfully
        if statements and supabase_client.client:
            for statement in statements:
                await run_in_threadpool(
                    supabase_client.save_financial_statement,
                    "us_financials",
                    statement.model_dump(),
                )

        return statements

    async def get_historical_data(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d",
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> Optional[List[USCandleData]]:
        """
        Get historical OHLCV data for a US stock.

        Args:
            symbol: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)
            start: Start date in YYYY-MM-DD format (optional)
            end: End date in YYYY-MM-DD format (optional)

        Returns:
            List of USCandleData or None
        """
        return yfinance_client.get_historical_data(
            symbol, period, interval, start, end
        )

    async def get_valuation_metrics(
        self, symbol: str
    ) -> Optional[USValuationMetrics]:
        """
        Get valuation metrics for a US stock using Yahoo Finance.
        """
        return yfinance_client.get_valuation_metrics(symbol)


us_market_service = USMarketService()
