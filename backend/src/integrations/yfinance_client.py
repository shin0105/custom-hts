"""Yahoo Finance client for US market data."""

import yfinance as yf
from typing import Optional
from datetime import datetime
import pandas as pd
from ..models.us import USStockQuote, USFinancialStatement
from ..utils.helpers import safe_float, safe_int, calculate_change_percent


class YFinanceClient:
    """Client for Yahoo Finance API."""

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
                        balance_sheet.loc["Total Liabilities Net Minority Interest", date]
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


# Global instance
yfinance_client = YFinanceClient()
