"""Yahoo Finance client for US market data."""

from typing import Optional, List
from datetime import datetime
import yfinance as yf
from ..models.us import (
    USStockQuote,
    USFinancialStatement,
    USCandleData,
    USValuationMetrics,
)
from ..utils.helpers import safe_float, safe_int, calculate_change_percent


class YFinanceClient:
    """Client for Yahoo Finance API."""

    def _optional_float(self, value: Optional[float]) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def get_quote(self, symbol: str) -> Optional[USStockQuote]:
        """
        Get real-time quote for a US stock.

        Args:
            symbol: Stock ticker symbol (e.g., AAPL)

        Returns:
            USStockQuote object or None if fetch fails
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info:
                return None

            current_price = safe_float(info.get("currentPrice"))
            previous_close = safe_float(info.get("previousClose"))
            change = current_price - previous_close
            change_percent = calculate_change_percent(
                current_price, previous_close
            )

            return USStockQuote(
                symbol=symbol.upper(),
                name=info.get("longName", symbol),
                current_price=current_price,
                change=change,
                change_percent=change_percent or 0.0,
                volume=safe_int(info.get("volume")),
                timestamp=datetime.now(),
                high=safe_float(info.get("dayHigh")),
                low=safe_float(info.get("dayLow")),
                open=safe_float(info.get("open")),
                previous_close=previous_close,
                market_cap=safe_float(info.get("marketCap")),
            )
        except Exception as e:
            print(f"Failed to get quote for {symbol}: {e}")
            return None

    def get_financials(
        self, symbol: str
    ) -> Optional[list[USFinancialStatement]]:
        """
        Get financial statements for a US company.

        Args:
            symbol: Stock ticker symbol

        Returns:
            List of USFinancialStatement objects or None if fetch fails
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            company_name = info.get("longName", symbol)

            # Get annual financials
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet

            if financials is None or financials.empty:
                return None

            statements = []

            # Process each year
            for date in financials.columns:
                year = date.year

                # Get income statement data
                revenue = safe_float(
                    financials.loc["Total Revenue", date]
                    if "Total Revenue" in financials.index
                    else None
                )
                operating_income = safe_float(
                    financials.loc["Operating Income", date]
                    if "Operating Income" in financials.index
                    else None
                )
                net_income = safe_float(
                    financials.loc["Net Income", date]
                    if "Net Income" in financials.index
                    else None
                )

                # Get balance sheet data
                total_assets = None
                total_liabilities = None
                total_equity = None
                if balance_sheet is not None and date in balance_sheet.columns:
                    total_assets = safe_float(
                        balance_sheet.loc["Total Assets", date]
                        if "Total Assets" in balance_sheet.index
                        else None
                    )
                    total_liabilities = safe_float(
                        balance_sheet.loc[
                            "Total Liabilities Net Minority Interest", date
                        ]
                        if "Total Liabilities Net Minority Interest"
                        in balance_sheet.index
                        else None
                    )
                    total_equity = safe_float(
                        balance_sheet.loc["Stockholders Equity", date]
                        if "Stockholders Equity" in balance_sheet.index
                        else None
                    )

                statement = USFinancialStatement(
                    symbol=symbol.upper(),
                    company_name=company_name,
                    year=year,
                    quarter=None,
                    revenue=revenue,
                    operating_income=operating_income,
                    net_income=net_income,
                    total_assets=total_assets,
                    total_liabilities=total_liabilities,
                    total_equity=total_equity,
                    eps=safe_float(info.get("trailingEps")),
                    pe_ratio=safe_float(info.get("trailingPE")),
                    updated_at=datetime.now(),
                )
                statements.append(statement)

            return statements
        except Exception as e:
            print(f"Failed to get financials for {symbol}: {e}")
            return None

    def get_historical_data(
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
            period: Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            interval: Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            start: Start date in YYYY-MM-DD format (optional)
            end: End date in YYYY-MM-DD format (optional)

        Returns:
            List of USCandleData objects or None if fetch fails
        """
        try:
            ticker = yf.Ticker(symbol)

            # Download historical data
            if start and end:
                hist = ticker.history(start=start, end=end, interval=interval)
            else:
                hist = ticker.history(period=period, interval=interval)

            if hist is None or hist.empty:
                return None

            candles = []
            for index, row in hist.iterrows():
                # Format date based on interval
                if interval in [
                    "1m",
                    "2m",
                    "5m",
                    "15m",
                    "30m",
                    "60m",
                    "90m",
                    "1h",
                ]:
                    # For intraday, use datetime format
                    date_str = index.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    # For daily and above, use date format
                    date_str = index.strftime("%Y-%m-%d")

                open_price = safe_float(row.get("Open", 0))
                close_price = safe_float(row.get("Close", 0))
                change = close_price - open_price
                change_percent = calculate_change_percent(
                    close_price, open_price
                )

                candle = USCandleData(
                    symbol=symbol.upper(),
                    date=date_str,
                    open=open_price,
                    high=safe_float(row.get("High", 0)),
                    low=safe_float(row.get("Low", 0)),
                    close=close_price,
                    volume=safe_int(row.get("Volume", 0)),
                    change=change,
                    change_percent=change_percent or 0.0,
                )
                candles.append(candle)

            return candles
        except Exception as e:
            print(f"Failed to get historical data for {symbol}: {e}")
            return None

    def get_valuation_metrics(
        self, symbol: str
    ) -> Optional[USValuationMetrics]:
        """
        Get valuation metrics for a US stock using Yahoo Finance.
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info:
                return None

            price = self._optional_float(info.get("currentPrice"))
            if price is None:
                return None

            eps = self._optional_float(info.get("trailingEps"))
            per = self._optional_float(info.get("trailingPE"))
            bps = self._optional_float(info.get("bookValue"))
            pbr = self._optional_float(info.get("priceToBook"))
            shares_outstanding = self._optional_float(
                info.get("sharesOutstanding")
            )
            market_cap = self._optional_float(info.get("marketCap"))

            if per is None and eps not in (None, 0):
                per = price / eps

            if pbr is None and bps not in (None, 0):
                pbr = price / bps

            return USValuationMetrics(
                symbol=symbol.upper(),
                price=price,
                eps=eps,
                bps=bps,
                per=per,
                pbr=pbr,
                shares_outstanding=shares_outstanding,
                market_cap=market_cap,
                as_of=datetime.now(),
            )
        except Exception as e:
            print(f"Failed to get valuation metrics for {symbol}: {e}")
            return None


# Global instance
yfinance_client = YFinanceClient()
