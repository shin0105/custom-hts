"""Pydantic models for US market data."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class USStockQuote(BaseModel):
    """US stock quote data."""

    symbol: str = Field(..., description="Stock ticker symbol (e.g., AAPL)")
    name: str = Field(..., description="Company name")
    current_price: float = Field(..., description="Current price in USD")
    change: float = Field(..., description="Price change in USD")
    change_percent: float = Field(..., description="Price change percentage")
    volume: int = Field(..., description="Trading volume")
    timestamp: datetime = Field(..., description="Quote timestamp")
    high: Optional[float] = Field(None, description="Day high")
    low: Optional[float] = Field(None, description="Day low")
    open: Optional[float] = Field(None, description="Opening price")
    previous_close: Optional[float] = Field(None, description="Previous close")
    market_cap: Optional[float] = Field(None, description="Market cap in USD")


class USFinancialStatement(BaseModel):
    """US company financial statement data."""

    symbol: str = Field(..., description="Stock ticker symbol")
    company_name: str = Field(..., description="Company name")
    year: int = Field(..., description="Fiscal year")
    quarter: Optional[int] = Field(None, description="Quarter (1-4)")
    revenue: Optional[float] = Field(None, description="Revenue in USD")
    operating_income: Optional[float] = Field(
        None, description="Operating income in USD"
    )
    net_income: Optional[float] = Field(None, description="Net income in USD")
    total_assets: Optional[float] = Field(
        None, description="Total assets in USD"
    )
    total_liabilities: Optional[float] = Field(
        None, description="Total liabilities in USD"
    )
    total_equity: Optional[float] = Field(
        None, description="Total equity in USD"
    )
    eps: Optional[float] = Field(None, description="Earnings per share")
    pe_ratio: Optional[float] = Field(None, description="P/E ratio")
    updated_at: datetime = Field(..., description="Data update timestamp")


class USValuationMetrics(BaseModel):
    """US stock valuation metrics."""

    symbol: str = Field(..., description="Stock ticker symbol")
    price: float = Field(..., description="Current price in USD")
    eps: Optional[float] = Field(None, description="Earnings per share")
    bps: Optional[float] = Field(None, description="Book value per share")
    per: Optional[float] = Field(None, description="Price-to-earnings ratio")
    pbr: Optional[float] = Field(None, description="Price-to-book ratio")
    eps_ttm: Optional[float] = Field(
        None, description="Trailing twelve-month EPS (aggregated 4Q)"
    )
    bps_ttm: Optional[float] = Field(
        None, description="Trailing twelve-month BPS (average equity per share)"
    )
    per_ttm: Optional[float] = Field(
        None, description="Trailing twelve-month PER (price / EPS TTM)"
    )
    pbr_ttm: Optional[float] = Field(
        None, description="Trailing twelve-month PBR (price / BPS TTM)"
    )
    shares_outstanding: Optional[float] = Field(
        None, description="Shares outstanding"
    )
    market_cap: Optional[float] = Field(
        None, description="Market capitalization in USD"
    )
    as_of: datetime = Field(..., description="Valuation timestamp")


class USSearchResult(BaseModel):
    """US stock search result."""

    symbol: str = Field(..., description="Stock ticker symbol")
    name: str = Field(..., description="Company name")
    exchange: str = Field(..., description="Exchange (NYSE, NASDAQ, etc.)")


class USCandleData(BaseModel):
    """US stock candle/OHLCV data."""

    symbol: str = Field(..., description="Stock ticker symbol")
    date: str = Field(
        ..., description="Candle date in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format"
    )
    open: float = Field(..., description="Opening price in USD")
    high: float = Field(..., description="High price in USD")
    low: float = Field(..., description="Low price in USD")
    close: float = Field(..., description="Closing price in USD")
    volume: int = Field(..., description="Trading volume")
    change: Optional[float] = Field(None, description="Price change in USD")
    change_percent: Optional[float] = Field(
        None, description="Price change percentage"
    )
