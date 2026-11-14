"""Pydantic models for basis and bond yield analytics."""

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_serializer


class RoundedModel(BaseModel):
    """Serialises floats to 6 decimals, hiding binary float noise such as
    -2.42999999999995 without touching the values used in calculations."""

    @field_serializer("*", mode="wrap")
    def _round_floats(self, value: Any, handler: Any) -> Any:
        serialised = handler(value)
        if isinstance(serialised, float):
            return round(serialised, 6)
        return serialised


# --------------------------------------------------------------------------
# Futures vs underlying basis
# --------------------------------------------------------------------------


class KoreanBasisUnderlying(RoundedModel):
    """An underlying that has listed futures."""

    code: str = Field(..., description="Stock code or index code")
    name: str = Field(..., description="Underlying name")
    kind: str = Field(..., description="'stock' or 'index'")
    contract_count: int = Field(..., description="Listed futures months")
    front_symbol: Optional[str] = Field(
        None, description="Short code of the nearest futures month"
    )


class KoreanBasisContract(RoundedModel):
    """One futures month compared with its underlying."""

    symbol: str = Field(..., description="Futures short code")
    name: Optional[str] = Field(None, description="Futures name")
    expiry_month: Optional[str] = Field(None, description="Expiry (YYYYMM)")
    last_trade_date: Optional[str] = Field(
        None, description="Last trading date (YYYYMMDD)"
    )
    days_to_expiry: Optional[int] = Field(
        None, description="Remaining days used for carry calculations"
    )
    price: Optional[float] = Field(None, description="Last traded price")
    bid: Optional[float] = Field(None, description="Best bid")
    ask: Optional[float] = Field(None, description="Best ask")
    mid: Optional[float] = Field(None, description="Bid/ask midpoint")
    volume: Optional[int] = Field(None, description="Accumulated volume")
    open_interest: Optional[int] = Field(None, description="Open interest")
    basis: Optional[float] = Field(None, description="Last price - spot")
    basis_percent: Optional[float] = Field(
        None, description="Basis as a percentage of spot"
    )
    mid_basis: Optional[float] = Field(None, description="Midpoint - spot")
    implied_rate: Optional[float] = Field(
        None,
        description="Annualised carry implied by the futures price (%)",
    )
    theoretical_price: Optional[float] = Field(
        None, description="Fair futures price used for the discrepancy"
    )
    theoretical_basis: Optional[float] = Field(
        None, description="Theoretical price - spot"
    )
    discrepancy_percent: Optional[float] = Field(
        None, description="(price - theoretical) / theoretical, in percent"
    )
    carry_rate: Optional[float] = Field(
        None, description="Annual rate behind the theoretical price (%)"
    )
    broker_theoretical_price: Optional[float] = Field(
        None, description="Theoretical price reported by the broker"
    )
    broker_basis: Optional[float] = Field(
        None, description="Theoretical basis reported by the broker"
    )
    broker_market_basis: Optional[float] = Field(
        None, description="Market basis reported by the broker"
    )
    broker_discrepancy_rate: Optional[float] = Field(
        None, description="Discrepancy rate reported by the broker (%)"
    )


class KoreanBasisSnapshot(RoundedModel):
    """Term structure of basis for one underlying."""

    underlying_code: str = Field(..., description="Stock or index code")
    underlying_name: str = Field(..., description="Underlying name")
    kind: str = Field(..., description="'stock' or 'index'")
    as_of: datetime = Field(..., description="Snapshot timestamp")
    spot: Optional[float] = Field(
        None, description="Spot price the basis is measured against"
    )
    spot_source: Optional[str] = Field(
        None,
        description=(
            "'futures_synced' (spot behind the broker's futures analytics) "
            "or 'live_quote'"
        ),
    )
    live_spot: Optional[float] = Field(
        None, description="Spot from the stock/index quote API"
    )
    live_spot_change_percent: Optional[float] = Field(
        None, description="Live spot change vs previous close (%)"
    )
    spot_gap_percent: Optional[float] = Field(
        None, description="(live spot - synced spot) / synced spot, percent"
    )
    rate: Optional[float] = Field(
        None, description="User-supplied annual rate (%), if any"
    )
    rate_source: str = Field(
        ..., description="'user' or 'broker' (broker's theoretical price)"
    )
    dividend: float = Field(
        0.0, description="Expected dividend before expiry, in price units"
    )
    contracts: List[KoreanBasisContract] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class KoreanBasisHistoryPoint(RoundedModel):
    """Daily close of spot and futures."""

    date: str = Field(..., description="YYYYMMDD")
    spot: float
    futures: float
    basis: float
    basis_percent: float
    implied_rate: Optional[float] = Field(
        None, description="Annualised carry implied on that day (%)"
    )
    volume: Optional[int] = Field(None, description="Futures volume")


class KoreanBasisStats(RoundedModel):
    """Distribution of daily basis (percent of spot) over the window."""

    count: int
    mean: float
    std: float
    min: float
    max: float
    latest: float
    zscore: Optional[float] = Field(
        None, description="(latest - mean) / std"
    )
    percentile: float = Field(
        ..., description="Share of days at or below the latest value (%)"
    )


class KoreanBasisHistory(RoundedModel):
    """Daily basis history for one futures contract."""

    underlying_code: str
    underlying_name: str
    kind: str
    symbol: str = Field(..., description="Futures short code")
    contract_name: Optional[str] = None
    points: List[KoreanBasisHistoryPoint] = Field(default_factory=list)
    stats: Optional[KoreanBasisStats] = None
    notes: List[str] = Field(default_factory=list)


# --------------------------------------------------------------------------
# Options vs futures and spot (put-call parity)
# --------------------------------------------------------------------------


class KoreanOptionParityRow(RoundedModel):
    """One strike: the futures price its call and put imply together."""

    strike: float
    is_atm: bool = Field(False, description="Strike nearest the futures price")
    call_symbol: str
    put_symbol: str
    call_last: Optional[float] = None
    call_bid: Optional[float] = None
    call_ask: Optional[float] = None
    call_volume: int = 0
    put_last: Optional[float] = None
    put_bid: Optional[float] = None
    put_ask: Optional[float] = None
    put_volume: int = 0
    synthetic: Optional[float] = Field(
        None, description="Synthetic futures price (see `source`)"
    )
    source: Optional[str] = Field(
        None,
        description=(
            "'quote' (midpoint of tight two-sided quotes), 'last' (last "
            "trades of both legs) or 'wide_quote' (midpoint of wide quotes)"
        ),
    )
    synthetic_bid: Optional[float] = Field(
        None, description="Price to sell it: sell call at bid, buy put at ask"
    )
    synthetic_ask: Optional[float] = Field(
        None, description="Price to buy it: buy call at ask, sell put at bid"
    )
    futures_gap: Optional[float] = Field(
        None, description="Synthetic - listed futures"
    )
    futures_gap_percent: Optional[float] = None
    spot_basis: Optional[float] = Field(None, description="Synthetic - spot")
    spot_basis_percent: Optional[float] = None
    implied_rate: Optional[float] = Field(
        None, description="Annualised carry the synthetic implies (%)"
    )
    conversion_edge: Optional[float] = Field(
        None,
        description="Sell synthetic, buy futures at the ask: profit before costs",
    )
    reversal_edge: Optional[float] = Field(
        None,
        description="Buy synthetic, sell futures at the bid: profit before costs",
    )


class KoreanOptionParitySummary(RoundedModel):
    """The option market's futures price across the quoted strikes."""

    synthetic: Optional[float] = Field(
        None, description="Median synthetic futures over the best-quoted rows"
    )
    source: Optional[str] = Field(
        None, description="Row source the median was taken over"
    )
    strike_count: int = Field(0, description="Rows behind the median")
    futures_gap: Optional[float] = None
    futures_gap_percent: Optional[float] = None
    spot_basis: Optional[float] = None
    spot_basis_percent: Optional[float] = None
    implied_rate: Optional[float] = None
    conversion_edge: Optional[float] = Field(
        None, description="Best conversion edge over the rows"
    )
    conversion_strike: Optional[float] = None
    reversal_edge: Optional[float] = Field(
        None, description="Best reversal edge over the rows"
    )
    reversal_strike: Optional[float] = None


class KoreanOptionParity(RoundedModel):
    """Synthetic futures from one option expiry against futures and spot."""

    underlying_code: str
    underlying_name: str
    kind: str = Field(..., description="'stock' or 'index'")
    as_of: datetime
    expiries: List[str] = Field(
        default_factory=list, description="Listed option months (YYYYMM)"
    )
    expiry: Optional[str] = Field(None, description="Month shown (YYYYMM)")
    last_trade_date: Optional[str] = None
    days_to_expiry: Optional[int] = None
    spot: Optional[float] = None
    spot_source: Optional[str] = Field(
        None, description="'futures_synced' or 'live_quote'"
    )
    futures_symbol: Optional[str] = Field(
        None, description="Futures of the same expiry, if one is listed"
    )
    futures_name: Optional[str] = None
    futures_price: Optional[float] = Field(
        None, description="Bid/ask midpoint, else last trade"
    )
    futures_last: Optional[float] = None
    futures_bid: Optional[float] = None
    futures_ask: Optional[float] = None
    rate: Optional[float] = Field(
        None, description="Annual rate (%) used to carry the net premium"
    )
    rate_source: str = Field(
        "none", description="'user', 'futures_carry' or 'none'"
    )
    summary: Optional[KoreanOptionParitySummary] = None
    rows: List[KoreanOptionParityRow] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


# --------------------------------------------------------------------------
# Bond yield analytics
# --------------------------------------------------------------------------


class KoreanBondOrderbookLevel(RoundedModel):
    """One bid/ask level with its yield."""

    level: int
    ask_price: Optional[float] = None
    ask_quantity: Optional[int] = None
    ask_yield: Optional[float] = None
    bid_price: Optional[float] = None
    bid_quantity: Optional[int] = None
    bid_yield: Optional[float] = None


class KoreanBondAgencyValuation(RoundedModel):
    """Valuation from one bond pricing agency."""

    agency: str
    price: Optional[float] = None
    yield_rate: Optional[float] = None
    credit_rating: Optional[str] = None


class KoreanBondScenario(RoundedModel):
    """Price impact of a parallel yield shift."""

    shift_bp: int
    yield_rate: float
    price: float
    price_change: float
    price_change_percent: float


class KoreanBondAnalytics(RoundedModel):
    """Yield, risk and relative-value view of a listed bond.

    Prices are per 10,000 KRW face and include accrued interest, as quoted
    on KRX.
    """

    pdno: str
    name: str
    as_of: datetime
    settlement_date: str = Field(..., description="YYYYMMDD used for yields")

    kind: Optional[str] = Field(
        None, description="coupon / compound / simple / discount"
    )
    kind_label: Optional[str] = Field(None, description="Korean label")
    supported: bool = Field(
        ..., description="False when yield maths does not apply to this bond"
    )
    unsupported_reason: Optional[str] = None
    coupon_rate: Optional[float] = None
    interval_months: Optional[int] = None
    issue_date: Optional[str] = None
    maturity_date: Optional[str] = None
    remaining_years: Optional[float] = None
    next_coupon_date: Optional[str] = None

    last_price: Optional[float] = None
    last_yield: Optional[float] = Field(
        None, description="Yield reported by the broker for the last trade"
    )
    computed_yield: Optional[float] = Field(
        None, description="Our yield to maturity at the last price"
    )
    traded_today: bool = False
    volume: Optional[int] = None
    day_open_yield: Optional[float] = None
    day_high_price_yield: Optional[float] = Field(
        None, description="Yield at the day's high price"
    )
    day_low_price_yield: Optional[float] = Field(
        None, description="Yield at the day's low price"
    )

    best_bid_price: Optional[float] = None
    best_bid_yield: Optional[float] = None
    best_ask_price: Optional[float] = None
    best_ask_yield: Optional[float] = None
    bid_ask_spread_bp: Optional[float] = None
    levels: List[KoreanBondOrderbookLevel] = Field(default_factory=list)

    reference_yield: Optional[float] = Field(
        None, description="Yield used for risk and relative value"
    )
    reference_price: Optional[float] = None
    reference_source: Optional[str] = Field(
        None, description="last_trade / quote_mid / last_price / agency"
    )
    accrued_interest: Optional[float] = None
    clean_price: Optional[float] = None
    after_tax_yield: Optional[float] = None
    tax_rate: Optional[float] = None
    macaulay_duration: Optional[float] = None
    modified_duration: Optional[float] = None
    convexity: Optional[float] = None
    dv01: Optional[float] = Field(
        None, description="Price change per 1bp, per 10,000 face"
    )
    scenarios: List[KoreanBondScenario] = Field(default_factory=list)

    agency_date: Optional[str] = Field(
        None, description="Pricing agency valuation date (YYYYMMDD)"
    )
    agency_yield: Optional[float] = Field(
        None, description="Average pricing agency yield (%)"
    )
    agency_price: Optional[float] = None
    agency_spread_bp: Optional[float] = Field(
        None, description="Reference yield - agency yield, in bp"
    )
    agency_implied_price: Optional[float] = Field(
        None, description="Our price at the agency yield, for settlement date"
    )
    price_vs_agency: Optional[float] = Field(
        None, description="Reference price - agency implied price"
    )
    agencies: List[KoreanBondAgencyValuation] = Field(default_factory=list)

    notes: List[str] = Field(default_factory=list)


class KoreanBondYieldPoint(RoundedModel):
    """One day of market and pricing-agency yield."""

    date: str = Field(..., description="YYYYMMDD")
    close: Optional[float] = None
    volume: Optional[int] = None
    market_yield: Optional[float] = Field(
        None, description="Yield at the close, on days the bond traded"
    )
    agency_yield: Optional[float] = None
    agency_price: Optional[float] = None
    spread_bp: Optional[float] = Field(
        None, description="Market yield - agency yield, in bp"
    )


class KoreanBondYieldHistory(RoundedModel):
    """Daily yield history for a listed bond."""

    pdno: str
    name: str
    points: List[KoreanBondYieldPoint] = Field(default_factory=list)
    traded_days: int = 0
    average_spread_bp: Optional[float] = None
    latest_spread_bp: Optional[float] = None
    notes: List[str] = Field(default_factory=list)
