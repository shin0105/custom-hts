"""Pydantic models for Korean market data."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class KoreanStockQuote(BaseModel):
    """Korean stock quote data."""

    symbol: str = Field(..., description="Stock symbol (e.g., 005930)")
    name: str = Field(..., description="Company name in Korean")
    current_price: float = Field(..., description="Current price in KRW")
    change: float = Field(..., description="Price change in KRW")
    change_percent: float = Field(..., description="Price change percentage")
    volume: int = Field(..., description="Trading volume")
    timestamp: datetime = Field(..., description="Quote timestamp")
    high: Optional[float] = Field(None, description="Day high")
    low: Optional[float] = Field(None, description="Day low")
    open: Optional[float] = Field(None, description="Opening price")
    previous_close: Optional[float] = Field(None, description="Previous close")


class KoreanFinancialStatement(BaseModel):
    """Korean company financial statement data."""

    symbol: str = Field(..., description="Stock symbol")
    company_name: str = Field(..., description="Company name")
    year: int = Field(..., description="Fiscal year")
    quarter: Optional[int] = Field(None, description="Quarter (1-4)")
    revenue: Optional[float] = Field(None, description="Revenue in KRW")
    operating_income: Optional[float] = Field(
        None, description="Operating income in KRW"
    )
    net_income: Optional[float] = Field(None, description="Net income in KRW")
    total_assets: Optional[float] = Field(
        None, description="Total assets in KRW"
    )
    total_liabilities: Optional[float] = Field(
        None, description="Total liabilities in KRW"
    )
    total_equity: Optional[float] = Field(
        None, description="Total equity in KRW"
    )
    eps: Optional[float] = Field(None, description="Earnings per share")
    updated_at: datetime = Field(..., description="Data update timestamp")


class KoreanSearchResult(BaseModel):
    """Korean stock search result."""

    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company name in Korean")
    market: str = Field(..., description="Market (KOSPI, KOSDAQ, etc.)")
