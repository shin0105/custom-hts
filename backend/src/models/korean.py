"""Pydantic models for Korean market data."""

from typing import Optional, List, Dict, Any
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
    bps: Optional[float] = Field(None, description="Book value per share")
    updated_at: datetime = Field(..., description="Data update timestamp")


class KoreanValuationMetrics(BaseModel):
    """Korean stock valuation metrics."""

    symbol: str = Field(..., description="Stock symbol")
    price: float = Field(..., description="Current price in KRW")
    fiscal_year: Optional[int] = Field(
        None, description="Fiscal year used for base EPS/BPS calculations"
    )
    fiscal_quarter: Optional[int] = Field(
        None, description="Fiscal quarter used for base EPS/BPS calculations"
    )
    eps: Optional[float] = Field(None, description="Earnings per share")
    eps_12mf: Optional[float] = Field(
        None, description="Forward 12-month EPS (projection-weighted)"
    )
    bps: Optional[float] = Field(None, description="Book value per share")
    per: Optional[float] = Field(None, description="Price-to-earnings ratio")
    per_12mf: Optional[float] = Field(
        None, description="Forward 12-month PER (projection-weighted)"
    )
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
    ttm_quarters: Optional[List[Dict[str, int]]] = Field(
        None, description="Quarters used for TTM calculations"
    )
    estimate_12mf_labels: Optional[List[str]] = Field(
        None, description="Estimate labels used for 12MF calculations"
    )
    shares_outstanding: Optional[float] = Field(
        None, description="Shares outstanding"
    )
    market_cap: Optional[float] = Field(
        None, description="Market capitalization in KRW"
    )
    notes: Optional[List[str]] = Field(
        None, description="Warnings or data availability notes"
    )
    as_of: datetime = Field(..., description="Valuation timestamp")


class KoreanEstimatePerform(BaseModel):
    """Korean stock estimate performance data from KDevelopers."""

    symbol: str = Field(..., description="Stock symbol")
    output1: List[Dict[str, Any]] = Field(
        default_factory=list, description="Estimate performance summary"
    )
    output2: List[Dict[str, Any]] = Field(
        default_factory=list, description="Estimate performance detail (set 1)"
    )
    output3: List[Dict[str, Any]] = Field(
        default_factory=list, description="Estimate performance detail (set 2)"
    )
    output4: List[str] = Field(
        default_factory=list,
        description="Estimate performance year labels (e.g., 2023.12, 2025.12E)",
    )
    units: Dict[str, Any] = Field(
        default_factory=dict,
        description="Unit metadata for estimate outputs (e.g., 억원 for monetary values).",
    )
    unit_notes: Optional[str] = Field(
        None,
        description="Notes about estimate units and conversions (e.g., 억원 to KRW).",
    )


class KoreanSearchResult(BaseModel):
    """Korean stock search result."""

    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company name in Korean")
    market: str = Field(..., description="Market (KOSPI, KOSDAQ, etc.)")


class KoreanCandleData(BaseModel):
    """Korean stock candle/OHLCV data."""

    symbol: str = Field(..., description="Stock symbol")
    date: str = Field(
        ...,
        description=(
            "Candle date/time (YYYYMMDD for daily/period candles, "
            "YYYYMMDDHHMMSS for minute candles)"
        ),
    )
    open: float = Field(..., description="Opening price in KRW")
    high: float = Field(..., description="High price in KRW")
    low: float = Field(..., description="Low price in KRW")
    close: float = Field(..., description="Closing price in KRW")
    volume: int = Field(..., description="Trading volume")
    change: Optional[float] = Field(None, description="Price change in KRW")
    change_percent: Optional[float] = Field(
        None, description="Price change percentage"
    )


class KoreanAccountBalance(BaseModel):
    """Korean stock account balance information."""

    account_number: str = Field(..., description="Account number")
    total_evaluation: float = Field(
        ..., description="Total evaluation amount in KRW"
    )
    cash_balance: float = Field(..., description="Cash balance in KRW")
    investment_amount: float = Field(
        ..., description="Total investment amount in KRW"
    )
    profit_loss: float = Field(..., description="Total profit/loss in KRW")
    profit_loss_percent: float = Field(
        ..., description="Total profit/loss percentage"
    )
    timestamp: datetime = Field(..., description="Balance timestamp")


class KoreanStockPosition(BaseModel):
    """Korean stock position in account."""

    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company name in Korean")
    quantity: int = Field(..., description="Number of shares held")
    average_price: float = Field(..., description="Average purchase price")
    current_price: float = Field(..., description="Current market price")
    evaluation_amount: float = Field(
        ..., description="Current evaluation amount"
    )
    profit_loss: float = Field(..., description="Profit/loss in KRW")
    profit_loss_percent: float = Field(
        ..., description="Profit/loss percentage"
    )


class KoreanBondQuote(BaseModel):
    """Domestic listed bond quote data."""

    pdno: str = Field(..., description="Bond standard code (e.g., KR2033022D33)")
    name: str = Field(..., description="Bond name")
    current_price: Optional[float] = Field(
        None, description="Current bond price"
    )
    change: Optional[float] = Field(None, description="Change vs previous close")
    change_percent: Optional[float] = Field(
        None, description="Change percentage vs previous close"
    )
    volume: Optional[int] = Field(None, description="Accumulated volume")
    high: Optional[float] = Field(None, description="Day high")
    low: Optional[float] = Field(None, description="Day low")
    open: Optional[float] = Field(None, description="Day open")
    previous_close: Optional[float] = Field(
        None, description="Previous close price"
    )
    earning_rate: Optional[float] = Field(
        None, description="Yield/earning rate from API response"
    )
    best_ask: Optional[float] = Field(
        None, description="Best ask price from bond asking-price API"
    )
    best_bid: Optional[float] = Field(
        None, description="Best bid price from bond asking-price API"
    )
    middle_price: Optional[float] = Field(
        None, description="Current middle price ((best ask + best bid) / 2)"
    )


class KoreanBondValuation(BaseModel):
    """Domestic listed bond valuation output."""

    pdno: str = Field(..., description="Bond standard code")
    name: str = Field(..., description="Bond name")
    as_of: datetime = Field(..., description="Valuation timestamp")
    raw_market_price: Optional[float] = Field(
        None, description="Raw observed market price from quote API"
    )
    market_price: Optional[float] = Field(
        None, description="Normalized market price on face=100 basis"
    )
    market_price_source: Optional[str] = Field(
        None, description="Source of market price (middle/current/daily_close)"
    )
    theoretical_dirty_price: Optional[float] = Field(
        None, description="Discounted dirty price from future cashflows"
    )
    accrued_interest: Optional[float] = Field(
        None, description="Estimated accrued interest"
    )
    theoretical_clean_price: Optional[float] = Field(
        None, description="Theoretical clean price (dirty - accrued)"
    )
    mispricing: Optional[float] = Field(
        None, description="Market - theoretical clean price"
    )
    mispricing_percent: Optional[float] = Field(
        None, description="Mispricing percentage vs theoretical clean price"
    )
    annual_coupon_rate: Optional[float] = Field(
        None, description="Annual coupon rate used in valuation (%)"
    )
    annual_yield_rate: Optional[float] = Field(
        None, description="Annual yield used in valuation (%)"
    )
    payment_interval_months: Optional[int] = Field(
        None, description="Coupon payment interval in months"
    )
    remaining_periods: Optional[int] = Field(
        None, description="Remaining coupon periods until maturity"
    )
    face_value: float = Field(
        100.0, description="Face value assumption for valuation"
    )
    redemption_ratio: Optional[float] = Field(
        None, description="Maturity redemption ratio (%)"
    )
    next_coupon_date: Optional[str] = Field(
        None, description="Next coupon date (YYYYMMDD)"
    )
    maturity_date: Optional[str] = Field(
        None, description="Maturity/redemption date (YYYYMMDD)"
    )
    notes: List[str] = Field(
        default_factory=list, description="Assumptions or data availability notes"
    )


class KoreanBondMasterItem(BaseModel):
    """Domestic listed bond master row."""

    pdno: str = Field(..., description="Bond standard code")
    name: Optional[str] = Field(None, description="Bond name")
    english_name: Optional[str] = Field(None, description="Bond English name")
    bond_class_name: Optional[str] = Field(
        None, description="Bond classification name"
    )
    issue_date: Optional[str] = Field(None, description="Issue date (YYYYMMDD)")
    maturity_date: Optional[str] = Field(
        None, description="Maturity/redemption date (YYYYMMDD)"
    )
    listed_date: Optional[str] = Field(None, description="Listed date (YYYYMMDD)")
    delisted_date: Optional[str] = Field(
        None, description="Delisted date (YYYYMMDD)"
    )
    currency: Optional[str] = Field(None, description="Currency code")
    surface_interest_rate: Optional[float] = Field(
        None, description="Surface/coupon interest rate"
    )
    total_issue_amount: Optional[float] = Field(
        None, description="Total issue amount"
    )
    current_price: Optional[float] = Field(
        None, description="Current bond price (optional enrichment)"
    )
    change_percent: Optional[float] = Field(
        None, description="Price change percentage (optional enrichment)"
    )
    volume: Optional[int] = Field(
        None, description="Accumulated volume (optional enrichment)"
    )


class KoreanBondMasterResponse(BaseModel):
    """Domestic listed bond master response."""

    source_file: Optional[str] = Field(
        None, description="Local bond master file used"
    )
    total_loaded: int = Field(
        ..., description="Total number of bond codes loaded from source"
    )
    total_returned: int = Field(..., description="Number of rows returned")
    offset: int = Field(..., description="Applied offset")
    limit: int = Field(..., description="Applied limit")
    query: Optional[str] = Field(None, description="Optional search query")
    items: List[KoreanBondMasterItem] = Field(
        default_factory=list, description="Bond master rows"
    )
