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
    bond_type: Optional[str] = Field(
        None, description="Bond type code (A0/F9/C0)"
    )
    bond_class_code: Optional[str] = Field(
        None, description="Bond class code"
    )
    bond_interest_class_code: Optional[str] = Field(
        None, description="Bond interest class code"
    )
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


class KoreanStockMasterItem(BaseModel):
    """One row of the Korean stock master file (KOSPI/KOSDAQ/KONEX)."""

    symbol: str = Field(..., description="Short code (단축코드, 6 digits)")
    name: Optional[str] = Field(None, description="Korean company name")
    market: str = Field(..., description="Market: kospi/kosdaq/konex")
    standard_code: Optional[str] = Field(
        None, description="Standard code (표준코드)"
    )
    security_group_code: Optional[str] = Field(
        None, description="Security group code (증권그룹구분코드)"
    )
    market_cap_100m: Optional[float] = Field(
        None, description="Market capitalisation in 억 KRW"
    )
    listing_date: Optional[str] = Field(
        None, description="Listing date (상장일자, YYYYMMDD)"
    )


class KoreanStockMasterResponse(BaseModel):
    """Korean stock master search response."""

    items: List[KoreanStockMasterItem] = Field(
        ..., description="Matched stock master rows"
    )
    total_loaded: int = Field(
        ..., description="Total rows loaded from the searched markets"
    )
    total_matched: int = Field(
        ..., description="Number of rows matching the query"
    )
    total_returned: int = Field(..., description="Number of rows returned")
    offset: int = Field(..., description="Applied offset")
    limit: int = Field(..., description="Applied limit")
    query: Optional[str] = Field(None, description="Applied search query")
    markets: List[str] = Field(..., description="Markets that were searched")


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
    bond_type: Optional[str] = Field(None, description="Bond type filter")
    bond_class_code: Optional[str] = Field(
        None, description="Bond class code filter"
    )
    bond_interest_class_code: Optional[str] = Field(
        None, description="Bond interest class code filter"
    )
    listed_date_from: Optional[str] = Field(
        None, description="Listed date from (YYYYMMDD)"
    )
    listed_date_to: Optional[str] = Field(
        None, description="Listed date to (YYYYMMDD)"
    )
    issue_date_from: Optional[str] = Field(
        None, description="Issue date from (YYYYMMDD)"
    )
    issue_date_to: Optional[str] = Field(
        None, description="Issue date to (YYYYMMDD)"
    )
    maturity_date_from: Optional[str] = Field(
        None, description="Maturity date from (YYYYMMDD)"
    )
    maturity_date_to: Optional[str] = Field(
        None, description="Maturity date to (YYYYMMDD)"
    )
    available_bond_types: Dict[str, int] = Field(
        default_factory=dict, description="Available bond type counts from source file"
    )
    available_bond_class_codes_by_type: Dict[str, Dict[str, int]] = Field(
        default_factory=dict,
        description="Available bond class code counts grouped by bond type",
    )
    available_bond_interest_class_codes_by_type: Dict[str, Dict[str, int]] = Field(
        default_factory=dict,
        description=(
            "Available bond interest class code counts grouped by bond type"
        ),
    )
    items: List[KoreanBondMasterItem] = Field(
        default_factory=list, description="Bond master rows"
    )


class KoreanFuturesOptionsMasterItem(BaseModel):
    """Domestic futures/options master row."""

    market: str = Field(..., description="Master market type: index/stock/commodity")
    commodity_type: Optional[str] = Field(
        None, description="Commodity type code (commodity market only)"
    )
    info_type: Optional[str] = Field(None, description="Product/info type code")
    short_code: Optional[str] = Field(None, description="Short code")
    standard_code: Optional[str] = Field(None, description="Standard code")
    name_kr: Optional[str] = Field(None, description="Korean product name")
    atm_class_code: Optional[str] = Field(None, description="ATM class code")
    strike_price: Optional[str] = Field(None, description="Strike price")
    month_class_code: Optional[str] = Field(None, description="Month class code")
    underlying_short_code: Optional[str] = Field(
        None, description="Underlying short code"
    )
    underlying_name_kr: Optional[str] = Field(
        None, description="Underlying Korean name"
    )


class KoreanFuturesOptionsMasterResponse(BaseModel):
    """Domestic futures/options master response."""

    market: str = Field(..., description="Requested market: all/index/stock/commodity")
    source_files: Dict[str, Optional[str]] = Field(
        default_factory=dict, description="Local master source file per market"
    )
    total_loaded: int = Field(..., description="Total loaded rows after filtering")
    total_returned: int = Field(..., description="Number of rows returned")
    offset: int = Field(..., description="Applied offset")
    limit: int = Field(..., description="Applied limit")
    query: Optional[str] = Field(None, description="Optional search query")
    info_type: Optional[str] = Field(None, description="Info type filter")
    underlying_short_code: Optional[str] = Field(
        None, description="Underlying short code filter"
    )
    available_markets: Dict[str, int] = Field(
        default_factory=dict, description="Available row counts by market"
    )
    available_info_types_by_market: Dict[str, Dict[str, int]] = Field(
        default_factory=dict, description="Available info type counts grouped by market"
    )
    items: List[KoreanFuturesOptionsMasterItem] = Field(
        default_factory=list, description="Futures/options master rows"
    )


class KoreanFuturesOptionReferenceIndex(BaseModel):
    """Reference index data bundled with futures/options quote."""

    code: Optional[str] = Field(None, description="Index classification code")
    name: Optional[str] = Field(None, description="Index name")
    current_price: Optional[float] = Field(None, description="Current index value")
    change_sign: Optional[str] = Field(None, description="Change sign code")
    change: Optional[float] = Field(None, description="Change vs previous close")
    change_percent: Optional[float] = Field(None, description="Change percentage")


class KoreanFuturesOptionQuote(BaseModel):
    """Normalized domestic futures/options quote."""

    symbol: str = Field(..., description="Futures/options short code")
    market_div_code: str = Field(..., description="Market division code")
    name: Optional[str] = Field(None, description="Korean instrument name")
    current_price: Optional[float] = Field(None, description="Current price")
    change_sign: Optional[str] = Field(None, description="Change sign code")
    change: Optional[float] = Field(None, description="Change vs previous close")
    change_percent: Optional[float] = Field(None, description="Change percentage")
    previous_close: Optional[float] = Field(None, description="Previous close")
    volume: Optional[int] = Field(None, description="Accumulated volume")
    trading_value: Optional[float] = Field(None, description="Accumulated trading value")
    open_interest: Optional[int] = Field(None, description="Open interest")
    open_interest_change: Optional[int] = Field(
        None, description="Open interest change"
    )
    open: Optional[float] = Field(None, description="Open price")
    high: Optional[float] = Field(None, description="High price")
    low: Optional[float] = Field(None, description="Low price")
    upper_limit: Optional[float] = Field(None, description="Price upper limit")
    lower_limit: Optional[float] = Field(None, description="Price lower limit")
    theoretical_price: Optional[float] = Field(
        None, description="Theoretical price"
    )
    basis: Optional[float] = Field(None, description="Theoretical basis")
    market_basis: Optional[float] = Field(None, description="Market basis")
    discrepancy_rate: Optional[float] = Field(None, description="Discrepancy rate")
    strike_price: Optional[float] = Field(None, description="Strike price")
    delta: Optional[float] = Field(None, description="Option delta")
    gamma: Optional[float] = Field(None, description="Option gamma")
    theta: Optional[float] = Field(None, description="Option theta")
    vega: Optional[float] = Field(None, description="Option vega")
    rho: Optional[float] = Field(None, description="Option rho")
    historical_volatility: Optional[float] = Field(
        None, description="Historical volatility"
    )
    implied_volatility: Optional[float] = Field(None, description="Implied volatility")
    last_trade_date: Optional[str] = Field(
        None, description="Last trade date (YYYYMMDD)"
    )
    remaining_days: Optional[int] = Field(None, description="Remaining days")
    reference_indices: List[KoreanFuturesOptionReferenceIndex] = Field(
        default_factory=list, description="Related reference indices"
    )


class KoreanFuturesOptionOrderbookLevel(BaseModel):
    """Single futures/options orderbook level."""

    level: int = Field(..., description="Orderbook level (1~5)")
    ask_price: Optional[float] = Field(None, description="Ask price")
    ask_quantity: Optional[int] = Field(None, description="Ask quantity")
    ask_orders: Optional[int] = Field(None, description="Ask order count")
    bid_price: Optional[float] = Field(None, description="Bid price")
    bid_quantity: Optional[int] = Field(None, description="Bid quantity")
    bid_orders: Optional[int] = Field(None, description="Bid order count")


class KoreanFuturesOptionOrderbook(BaseModel):
    """Normalized domestic futures/options orderbook."""

    symbol: str = Field(..., description="Futures/options short code")
    market_div_code: str = Field(..., description="Market division code")
    name: Optional[str] = Field(None, description="Korean instrument name")
    current_price: Optional[float] = Field(None, description="Current price")
    change_sign: Optional[str] = Field(None, description="Change sign code")
    change: Optional[float] = Field(None, description="Change vs previous close")
    change_percent: Optional[float] = Field(None, description="Change percentage")
    previous_close: Optional[float] = Field(None, description="Previous close")
    volume: Optional[int] = Field(None, description="Accumulated volume")
    as_of_time: Optional[str] = Field(None, description="Orderbook as-of time (HHMMSS)")
    total_ask_quantity: Optional[int] = Field(
        None, description="Total ask quantity (L1~L5)"
    )
    total_bid_quantity: Optional[int] = Field(
        None, description="Total bid quantity (L1~L5)"
    )
    total_ask_orders: Optional[int] = Field(
        None, description="Total ask order count (L1~L5)"
    )
    total_bid_orders: Optional[int] = Field(
        None, description="Total bid order count (L1~L5)"
    )
    levels: List[KoreanFuturesOptionOrderbookLevel] = Field(
        default_factory=list, description="5-level orderbook"
    )


class KoreanFuturesOptionMinuteCandle(BaseModel):
    """Single domestic futures/options intraday candle."""

    symbol: str = Field(..., description="Futures/options short code")
    market_div_code: str = Field(..., description="Market division code")
    date: Optional[str] = Field(None, description="Trading date (YYYYMMDD)")
    time: Optional[str] = Field(None, description="Trading time (HHMMSS)")
    timestamp: Optional[str] = Field(
        None, description="Combined timestamp (YYYYMMDDHHMMSS)"
    )
    open: Optional[float] = Field(None, description="Open")
    high: Optional[float] = Field(None, description="High")
    low: Optional[float] = Field(None, description="Low")
    close: Optional[float] = Field(None, description="Close")
    volume: Optional[int] = Field(None, description="Executed volume")
    cumulative_trading_value: Optional[float] = Field(
        None, description="Accumulated trading value"
    )


class KoreanFuturesOptionMinuteCandleResponse(BaseModel):
    """Normalized domestic futures/options intraday candle response."""

    symbol: str = Field(..., description="Futures/options short code")
    market_div_code: str = Field(..., description="Market division code")
    timeframe_sec: int = Field(..., description="Candle timeframe in seconds")
    date: Optional[str] = Field(None, description="Cursor date (YYYYMMDD)")
    time: Optional[str] = Field(None, description="Cursor time (HHMMSS)")
    name: Optional[str] = Field(None, description="Korean instrument name")
    current_price: Optional[float] = Field(None, description="Current price")
    change: Optional[float] = Field(None, description="Change vs previous close")
    change_sign: Optional[str] = Field(None, description="Change sign code")
    change_percent: Optional[float] = Field(None, description="Change percentage")
    volume: Optional[int] = Field(None, description="Accumulated volume")
    open_interest: Optional[int] = Field(None, description="Open interest")
    open_interest_change: Optional[int] = Field(
        None, description="Open interest change"
    )
    candles: List[KoreanFuturesOptionMinuteCandle] = Field(
        default_factory=list, description="Intraday candles"
    )


class KoreanFuturesOptionChainRow(BaseModel):
    """Single option chain row for call/put side."""

    option_code: Optional[str] = Field(None, description="Option short code")
    strike_price: Optional[float] = Field(None, description="Strike price")
    current_price: Optional[float] = Field(None, description="Current price")
    change_sign: Optional[str] = Field(None, description="Change sign code")
    change: Optional[float] = Field(None, description="Change vs previous close")
    change_percent: Optional[float] = Field(None, description="Change percentage")
    bid_price: Optional[float] = Field(None, description="Best bid")
    ask_price: Optional[float] = Field(None, description="Best ask")
    volume: Optional[int] = Field(None, description="Accumulated volume")
    trading_value: Optional[float] = Field(None, description="Accumulated trading value")
    open_interest: Optional[int] = Field(None, description="Open interest")
    open_interest_change: Optional[int] = Field(
        None, description="Open interest change"
    )
    delta: Optional[float] = Field(None, description="Delta")
    gamma: Optional[float] = Field(None, description="Gamma")
    theta: Optional[float] = Field(None, description="Theta")
    vega: Optional[float] = Field(None, description="Vega")
    rho: Optional[float] = Field(None, description="Rho")
    implied_volatility: Optional[float] = Field(None, description="Implied volatility")
    historical_volatility: Optional[float] = Field(
        None, description="Historical volatility"
    )
    theoretical_price: Optional[float] = Field(
        None, description="Theoretical price"
    )
    intrinsic_value: Optional[float] = Field(None, description="Intrinsic value")
    time_value: Optional[float] = Field(None, description="Time value")
    moneyness: Optional[str] = Field(None, description="Moneyness classification")


class KoreanFuturesOptionChainResponse(BaseModel):
    """Normalized domestic option chain response."""

    expiry: str = Field(..., description="Expiry in YYYYMM")
    market_class: str = Field(..., description="Market class code")
    fetched_at: datetime = Field(..., description="Fetch timestamp")
    total_calls: int = Field(..., description="Number of call rows")
    total_puts: int = Field(..., description="Number of put rows")
    calls: List[KoreanFuturesOptionChainRow] = Field(
        default_factory=list, description="Call option rows"
    )
    puts: List[KoreanFuturesOptionChainRow] = Field(
        default_factory=list, description="Put option rows"
    )
