"""API routes for Korean market endpoints."""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from ..models.korean import (
    KoreanStockQuote,
    KoreanFinancialStatement,
    KoreanCandleData,
    KoreanValuationMetrics,
    KoreanEstimatePerform,
    KoreanBondQuote,
    KoreanBondValuation,
    KoreanBondMasterResponse,
    KoreanFuturesOptionsMasterResponse,
    KoreanFuturesOptionQuote,
    KoreanFuturesOptionOrderbook,
    KoreanFuturesOptionMinuteCandleResponse,
    KoreanFuturesOptionChainResponse,
)
from ..services.korean_market import korean_market_service
from ..utils.config import settings
from ..integrations.opendart import opendart_client


class PeriodType(str, Enum):
    """Valid period types for candle data."""

    DAILY = "D"
    WEEKLY = "W"
    MONTHLY = "M"


class MinuteInterval(int, Enum):
    """Valid minute intervals for candle data."""

    ONE = 1
    FIVE = 5
    TEN = 10
    THIRTY = 30
    SIXTY = 60


class FuturesMinuteInterval(int, Enum):
    """Valid futures/options timeframe in seconds."""

    THIRTY_SEC = 30
    ONE_MIN = 60
    ONE_HOUR = 3600


router = APIRouter(prefix="/korean", tags=["Korean Market"])


@router.get("/quote/{symbol}", response_model=KoreanStockQuote)
async def get_korean_quote(symbol: str) -> KoreanStockQuote:
    """
    Get real-time quote for a Korean stock.

    Args:
        symbol: Stock code (e.g., 005930 for Samsung Electronics)

    Returns:
        Real-time stock quote data
    """
    quote = await korean_market_service.get_quote(symbol)
    if not quote:
        raise HTTPException(
            status_code=404, detail=f"Quote not found for symbol {symbol}"
        )
    return quote


@router.get("/valuation/{symbol}", response_model=KoreanValuationMetrics)
async def get_korean_valuation(
    symbol: str,
    year: int = Query(datetime.now().year - 1, description="Fiscal year"),
    quarter: Optional[int] = Query(
        None, ge=1, le=4, description="Quarter (1-4)"
    ),
    fs_div: str = Query(
        "CFS", description="Financial statement division (CFS/OFS)"
    ),
) -> KoreanValuationMetrics:
    """
    Get valuation metrics (PER/PBR/EPS/BPS) for a Korean stock.

    Uses KDevelopers for price and OpenDART for financials.
    """
    metrics = await korean_market_service.get_valuation_metrics(
        symbol, year, quarter, fs_div
    )
    if not metrics:
        raise HTTPException(
            status_code=404,
            detail=f"Valuation metrics not found for symbol {symbol}",
        )
    return metrics


@router.get("/financials/{symbol}", response_model=KoreanFinancialStatement)
async def get_korean_financials(
    symbol: str,
    year: int = Query(datetime.now().year, description="Fiscal year"),
    quarter: Optional[int] = Query(
        None, ge=1, le=4, description="Quarter (1-4)"
    ),
    use_cache: bool = Query(True, description="Use cached data if available"),
) -> KoreanFinancialStatement:
    """
    Get financial statement for a Korean company.

    Args:
        symbol: Stock code
        year: Fiscal year (defaults to current year)
        quarter: Optional quarter (1-4)
        use_cache: Whether to use cached data

    Returns:
        Financial statement data
    """
    financials = await korean_market_service.get_financials(
        symbol, year, quarter, use_cache
    )
    if not financials:
        raise HTTPException(
            status_code=404,
            detail=f"Financials not found for symbol {symbol}",
        )
    return financials


@router.get("/health")
async def korean_market_health() -> dict:
    """Health check endpoint for Korean market API."""
    return {"status": "healthy", "market": "Korean"}


@router.get("/candle/{symbol}", response_model=List[KoreanCandleData])
async def get_korean_candle(
    symbol: str,
    period: PeriodType = Query(
        PeriodType.DAILY,
        description="Period type (D: daily, W: weekly, M: monthly)",
    ),
    adjust_price: bool = Query(True, description="Adjust for stock splits"),
    limit: Optional[int] = Query(
        None, ge=1, le=500, description="Number of candles (optional)"
    ),
    start_date: Optional[str] = Query(
        None, description="Start date in YYYYMMDD (optional)"
    ),
    end_date: Optional[str] = Query(
        None, description="End date in YYYYMMDD (optional)"
    ),
) -> List[KoreanCandleData]:
    """
    Get candle chart data for a Korean stock.

    Args:
        symbol: Stock code (e.g., 005930 for Samsung Electronics)
        period: Period type (D/W/M for daily/weekly/monthly)
        adjust_price: Whether to adjust for stock splits
        limit: Number of candles to retrieve (1-500)

    Returns:
        List of candle data (OHLCV)
    """
    candles = await korean_market_service.get_daily_candle(
        symbol,
        period.value,
        adjust_price,
        limit,
        start_date=start_date,
        end_date=end_date,
    )
    if not candles:
        raise HTTPException(
            status_code=404,
            detail=f"Candle data not found for symbol {symbol}",
        )
    return candles


@router.get("/candle-minute/{symbol}", response_model=List[KoreanCandleData])
async def get_korean_minute_candle(
    symbol: str,
    interval: MinuteInterval = Query(
        MinuteInterval.ONE, description="Minute interval (1, 5, 10, 30, 60)"
    ),
    limit: Optional[int] = Query(
        None, ge=1, le=500, description="Number of candles (optional)"
    ),
    date: Optional[str] = Query(
        None, description="Trading date in YYYYMMDD (defaults to today in KST)"
    ),
    time_str: str = Query(
        "", description="Time filter in HHMMSS (empty defaults to 09:00:00)"
    ),
) -> List[KoreanCandleData]:
    """
    Get minute candle chart data for a Korean stock.

    Args:
        symbol: Stock code
        interval: Minute interval (1, 5, 10, 30, or 60 minutes)
        limit: Number of candles to retrieve (1-500)

    Returns:
        List of minute candle data (OHLCV)
    """
    candles = await korean_market_service.get_minute_candle(
        symbol, interval.value, limit, date=date, time_str=time_str
    )
    if not candles:
        raise HTTPException(
            status_code=404,
            detail=f"Minute candle data not found for symbol {symbol}",
        )
    return candles


@router.get("/account")
async def get_korean_account_balance(
    account_product_code: str = Query(
        "01", description="Account product code"
    ),
) -> Dict[str, Any]:
    """
    Get account balance and stock positions.

    Args:
        account_product_code: Account product code (default: "01")

    Returns:
        Account balance and list of stock positions
    """
    account_number = settings.HANTU_ACCOUNT_NUMBER.strip()
    if not (account_number.isdigit() and len(account_number) == 8):
        raise HTTPException(
            status_code=500,
            detail="HANTU_ACCOUNT_NUMBER (or HANTU_BANK_ACCOUNT) is not configured correctly",
        )
    result = await korean_market_service.get_account_balance(
        account_number, account_product_code
    )
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Account balance not found for account {account_number}",
        )
    return result


@router.get("/stock-info/{pdno}", response_model=List[Dict[str, Any]])
async def get_korean_stock_info(
    pdno: str,
    prdt_type_cd: str = Query(
        "300",
        description="300: 주식/ETF/ETN/ELW, 301: 선물옵션, 302: 채권, 306: ELS",
    ),
) -> List[Dict[str, Any]]:
    """
    Get stock basic information (주식기본조회).

    Args:
        pdno: 종목번호 (6자리) ETN의 경우 Q로 시작 (EX. Q500001)
        prdt_type_cd: 상품유형코드

    Returns:
        Raw output list from KDevelopers search-stock-info API
    """
    result = await korean_market_service.get_stock_info(prdt_type_cd, pdno)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Stock info not found for pdno {pdno}",
        )
    return result


@router.get("/estimate-perform/{symbol}", response_model=KoreanEstimatePerform)
async def get_korean_estimate_perform(symbol: str) -> KoreanEstimatePerform:
    """
    Get estimated performance data for a Korean stock.

    Args:
        symbol: Stock code (e.g., 005930)

    Returns:
        Estimate performance data from KDevelopers
    """
    result = await korean_market_service.get_estimate_perform(symbol)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Estimate performance not found for symbol {symbol}",
        )
    return result


@router.get("/bonds/master", response_model=KoreanBondMasterResponse)
async def get_korean_bond_master(
    query: Optional[str] = Query(
        None, description="Filter by bond code/name (case-insensitive)"
    ),
    bond_type: Optional[str] = Query(
        None, alias="type", description="Bond type code (A0/F9/C0)"
    ),
    bond_class_code: Optional[str] = Query(
        None, description="Bond class code"
    ),
    bond_interest_class_code: Optional[str] = Query(
        None, description="Bond interest class code"
    ),
    listed_date_from: Optional[str] = Query(
        None, description="Listed date from (YYYYMMDD)"
    ),
    listed_date_to: Optional[str] = Query(
        None, description="Listed date to (YYYYMMDD)"
    ),
    issue_date_from: Optional[str] = Query(
        None, description="Issue date from (YYYYMMDD)"
    ),
    issue_date_to: Optional[str] = Query(
        None, description="Issue date to (YYYYMMDD)"
    ),
    maturity_date_from: Optional[str] = Query(
        None, description="Maturity date from (YYYYMMDD)"
    ),
    maturity_date_to: Optional[str] = Query(
        None, description="Maturity date to (YYYYMMDD)"
    ),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=500, description="Pagination limit"),
    enrich: bool = Query(
        False,
        description="Enrich rows with search-bond-info fields",
    ),
    include_quotes: bool = Query(
        False,
        description="Include price fields via inquire-price per row",
    ),
) -> KoreanBondMasterResponse:
    """
    Get domestic listed bond master list from local bond code master file.

    Master source file should exist at one of:
    - backend/data/kr_bond_master/bond_codes.csv
    - backend/data/kr_bond_master/bond_codes.tsv
    - backend/data/kr_bond_master/bond_codes.txt
    """
    result = await korean_market_service.get_bond_master(
        query=query,
        bond_type=bond_type,
        bond_class_code=bond_class_code,
        bond_interest_class_code=bond_interest_class_code,
        listed_date_from=listed_date_from,
        listed_date_to=listed_date_to,
        issue_date_from=issue_date_from,
        issue_date_to=issue_date_to,
        maturity_date_from=maturity_date_from,
        maturity_date_to=maturity_date_to,
        offset=offset,
        limit=limit,
        enrich=enrich,
        include_quotes=include_quotes,
    )
    return KoreanBondMasterResponse(**result)


@router.get("/bonds/{pdno}/price", response_model=KoreanBondQuote)
async def get_korean_bond_price(pdno: str) -> KoreanBondQuote:
    """Get domestic listed bond current quote."""
    quote = await korean_market_service.get_bond_price(pdno)
    if not quote:
        raise HTTPException(
            status_code=404, detail=f"Bond price not found for {pdno}"
        )
    return quote


@router.get("/bonds/{pdno}/valuation", response_model=KoreanBondValuation)
async def get_korean_bond_valuation(pdno: str) -> KoreanBondValuation:
    """Get domestic listed bond valuation using basic info + price data."""
    valuation = await korean_market_service.get_bond_valuation(pdno)
    if not valuation:
        raise HTTPException(
            status_code=404, detail=f"Bond valuation not found for {pdno}"
        )
    return valuation


@router.get("/bonds/{pdno}/daily-price", response_model=List[KoreanCandleData])
async def get_korean_bond_daily_price(
    pdno: str,
    limit: Optional[int] = Query(
        None, ge=1, le=100, description="Number of daily rows to return (max 100)"
    ),
) -> List[KoreanCandleData]:
    """Get domestic listed bond daily prices."""
    rows = await korean_market_service.get_bond_daily_price(pdno, limit=limit)
    if not rows:
        raise HTTPException(
            status_code=404, detail=f"Bond daily prices not found for {pdno}"
        )
    return rows


@router.get("/bonds/{pdno}/info")
async def get_korean_bond_info(pdno: str) -> Dict[str, Any]:
    """Get domestic listed bond basic information."""
    info = await korean_market_service.get_bond_basic_info(pdno)
    if not info:
        raise HTTPException(
            status_code=404, detail=f"Bond basic info not found for {pdno}"
        )
    return info


@router.get("/bonds/{pdno}/issue")
async def get_korean_bond_issue_info(pdno: str) -> Dict[str, Any]:
    """Get domestic listed bond issue information."""
    info = await korean_market_service.get_bond_issue_info(pdno)
    if not info:
        raise HTTPException(
            status_code=404, detail=f"Bond issue info not found for {pdno}"
        )
    return info


@router.post("/bonds/master/refresh")
async def refresh_korean_bond_master(
    output_format: str = Query(
        "csv", description="Export format: csv or json"
    ),
    force: bool = Query(
        False, description="Force re-download from source URL"
    ),
    source_url: Optional[str] = Query(
        None,
        description=(
            "Optional override URL for bond master zip "
            "(defaults to KIS bond_code.mst.zip)"
        ),
    ),
) -> Dict[str, Any]:
    """Refresh/download bond master and export as CSV or JSON."""
    fmt = output_format.lower().strip()
    if fmt not in {"csv", "json"}:
        raise HTTPException(
            status_code=400, detail="output_format must be 'csv' or 'json'"
        )

    result = await korean_market_service.refresh_bond_master(
        output_format=fmt, force=force, source_url=source_url
    )
    if not result.get("ok"):
        raise HTTPException(
            status_code=500,
            detail="Failed to refresh/export bond master file",
    )
    return result


@router.get(
    "/futures-options/master",
    response_model=KoreanFuturesOptionsMasterResponse,
)
async def get_korean_futures_options_master(
    market: str = Query(
        "all", description="Target market: all/index/stock/commodity"
    ),
    query: Optional[str] = Query(
        None, description="Filter by code/name (case-insensitive)"
    ),
    info_type: Optional[str] = Query(
        None, description="Info type code filter (e.g. 1,2,5,6...)"
    ),
    underlying_short_code: Optional[str] = Query(
        None, description="Underlying short code filter"
    ),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=2000, description="Pagination limit"),
    auto_download: bool = Query(
        False,
        description="Auto-download master file if local file is missing",
    ),
    force_download: bool = Query(
        False, description="Force re-download before parsing"
    ),
) -> KoreanFuturesOptionsMasterResponse:
    """Get domestic futures/options master rows (index/stock/commodity)."""
    market_normalized = market.strip().lower()
    if market_normalized not in {"all", "index", "stock", "commodity"}:
        raise HTTPException(
            status_code=400,
            detail="market must be one of: all/index/stock/commodity",
        )

    result = await korean_market_service.get_futures_options_master(
        market=market_normalized,
        query=query,
        info_type=info_type,
        underlying_short_code=underlying_short_code,
        offset=offset,
        limit=limit,
        auto_download=auto_download,
        force_download=force_download,
    )
    return KoreanFuturesOptionsMasterResponse(**result)


@router.post("/futures-options/master/refresh")
async def refresh_korean_futures_options_master(
    market: str = Query(
        "all", description="Target market: all/index/stock/commodity"
    ),
    output_format: str = Query(
        "csv", description="Export format: csv or json"
    ),
    force: bool = Query(False, description="Force re-download from source URL"),
) -> Dict[str, Any]:
    """Refresh/download domestic futures/options master files and export."""
    market_normalized = market.strip().lower()
    if market_normalized not in {"all", "index", "stock", "commodity"}:
        raise HTTPException(
            status_code=400,
            detail="market must be one of: all/index/stock/commodity",
        )

    fmt = output_format.lower().strip()
    if fmt not in {"csv", "json"}:
        raise HTTPException(
            status_code=400, detail="output_format must be 'csv' or 'json'"
        )

    result = await korean_market_service.refresh_futures_options_master(
        market=market_normalized,
        output_format=fmt,
        force=force,
    )
    if not result.get("ok"):
        raise HTTPException(
            status_code=500,
            detail="Failed to refresh/export futures-options master file",
        )
    return result


@router.get(
    "/futures-options/quote",
    response_model=KoreanFuturesOptionQuote,
)
async def get_korean_futures_options_quote(
    symbol: str = Query(..., min_length=3, max_length=12),
    market_div_code: str = Query(
        "F",
        description="F: 지수선물, O: 지수옵션, JF: 주식선물, JO: 주식옵션",
    ),
) -> KoreanFuturesOptionQuote:
    """Get domestic futures/options normalized quote."""
    market_code = market_div_code.strip().upper()
    if market_code not in {"F", "O", "JF", "JO", "CF", "CM", "EU"}:
        raise HTTPException(
            status_code=400,
            detail="market_div_code must be one of F/O/JF/JO/CF/CM/EU",
        )
    quote = await korean_market_service.get_futures_option_quote(
        symbol=symbol.strip().upper(),
        market_div_code=market_code,
    )
    if not quote:
        raise HTTPException(
            status_code=404, detail=f"Futures/options quote not found for {symbol}"
        )
    return quote


@router.get(
    "/futures-options/orderbook",
    response_model=KoreanFuturesOptionOrderbook,
)
async def get_korean_futures_options_orderbook(
    symbol: str = Query(..., min_length=3, max_length=12),
    market_div_code: str = Query(
        "F",
        description="F: 지수선물, O: 지수옵션, JF: 주식선물, JO: 주식옵션",
    ),
) -> KoreanFuturesOptionOrderbook:
    """Get domestic futures/options normalized 5-level orderbook."""
    market_code = market_div_code.strip().upper()
    if market_code not in {"F", "O", "JF", "JO", "CF", "CM", "EU"}:
        raise HTTPException(
            status_code=400,
            detail="market_div_code must be one of F/O/JF/JO/CF/CM/EU",
        )
    orderbook = await korean_market_service.get_futures_option_orderbook(
        symbol=symbol.strip().upper(),
        market_div_code=market_code,
    )
    if not orderbook:
        raise HTTPException(
            status_code=404,
            detail=f"Futures/options orderbook not found for {symbol}",
        )
    return orderbook


@router.get(
    "/futures-options/minute-candles",
    response_model=KoreanFuturesOptionMinuteCandleResponse,
)
async def get_korean_futures_options_minute_candles(
    symbol: str = Query(..., min_length=3, max_length=12),
    market_div_code: str = Query(
        "F",
        description="F: 지수선물, O: 지수옵션, JF: 주식선물, JO: 주식옵션",
    ),
    timeframe_sec: FuturesMinuteInterval = Query(
        FuturesMinuteInterval.ONE_MIN,
        description="Timeframe in seconds (30, 60, 3600)",
    ),
    date: Optional[str] = Query(
        None, description="Cursor date in YYYYMMDD"
    ),
    time: Optional[str] = Query(
        None, description="Cursor time in HHMMSS"
    ),
    include_previous: bool = Query(
        True, description="Include previous-day data"
    ),
    include_fake_tick: bool = Query(
        False, description="Include fake tick candles"
    ),
    limit: Optional[int] = Query(
        None, ge=1, le=200, description="Max candle rows to return"
    ),
) -> KoreanFuturesOptionMinuteCandleResponse:
    """Get domestic futures/options normalized intraday candles."""
    market_code = market_div_code.strip().upper()
    if market_code not in {"F", "O", "JF", "JO", "CF", "CM", "EU"}:
        raise HTTPException(
            status_code=400,
            detail="market_div_code must be one of F/O/JF/JO/CF/CM/EU",
        )
    if date and (len(date) != 8 or not date.isdigit()):
        raise HTTPException(status_code=400, detail="date must be YYYYMMDD")
    if time and (len(time) != 6 or not time.isdigit()):
        raise HTTPException(status_code=400, detail="time must be HHMMSS")

    candles = await korean_market_service.get_futures_option_minute_candles(
        symbol=symbol.strip().upper(),
        market_div_code=market_code,
        timeframe_sec=timeframe_sec.value,
        date_value=date,
        time_value=time,
        include_previous=include_previous,
        include_fake_tick=include_fake_tick,
        limit=limit,
    )
    if not candles:
        raise HTTPException(
            status_code=404,
            detail=f"Futures/options minute candles not found for {symbol}",
        )
    return candles


@router.get(
    "/futures-options/option-chain",
    response_model=KoreanFuturesOptionChainResponse,
)
async def get_korean_futures_options_option_chain(
    expiry: str = Query(..., min_length=6, max_length=6, description="YYYYMM"),
    market_class: str = Query(
        "",
        description="KOSPI200: '' (blank), MKI: 미니, KQI: 코스닥150, WKM/WKI: 위클리",
    ),
) -> KoreanFuturesOptionChainResponse:
    """Get domestic futures/options normalized option chain (call/put)."""
    if len(expiry) != 6 or not expiry.isdigit():
        raise HTTPException(status_code=400, detail="expiry must be YYYYMM")
    market_class_normalized = market_class.strip().upper()
    if market_class_normalized not in {"", "MKI", "KQI", "WKM", "WKI"}:
        raise HTTPException(
            status_code=400,
            detail="market_class must be one of: '', MKI, KQI, WKM, WKI",
        )

    chain = await korean_market_service.get_futures_option_chain(
        expiry=expiry,
        market_class=market_class_normalized,
    )
    if not chain:
        raise HTTPException(
            status_code=404,
            detail=f"Futures/options option-chain not found for expiry {expiry}",
        )
    return chain


@router.get("/financials/{symbol}/balance-sheet")
async def get_balance_sheet(
    symbol: str,
    year: int = Query(datetime.now().year - 1, description="Fiscal year"),
    quarter: Optional[int] = Query(
        None,
        ge=1,
        le=4,
        description="Quarter (1-4 for quarterly, None for annual)",
    ),
) -> Dict[str, Any]:
    """
    Get detailed balance sheet for a Korean company.

    Returns all balance sheet line items including:
    - Current assets
    - Non-current assets
    - Total assets
    - Current liabilities
    - Non-current liabilities
    - Total liabilities
    - Total equity

    Args:
        symbol: Stock code (e.g., 005930 for Samsung Electronics)
        year: Fiscal year (defaults to previous year)
        quarter: Optional quarter (1-4)

    Returns:
        Dictionary with all balance sheet line items
    """
    balance_sheet = opendart_client.get_balance_sheet(symbol, year, quarter)

    if not balance_sheet:
        raise HTTPException(
            status_code=404,
            detail=f"Balance sheet not found for {symbol} (year: {year}, quarter: {quarter})",
        )

    return {
        "symbol": symbol,
        "year": year,
        "quarter": quarter,
        "statement_type": "balance_sheet",
        "data": balance_sheet,
    }


@router.get("/financials/{symbol}/income-statement")
async def get_income_statement(
    symbol: str,
    year: int = Query(datetime.now().year - 1, description="Fiscal year"),
    quarter: Optional[int] = Query(
        None,
        ge=1,
        le=4,
        description="Quarter (1-4 for quarterly, None for annual)",
    ),
) -> Dict[str, Any]:
    """
    Get detailed income statement for a Korean company.

    Returns all income statement line items including:
    - Revenue (by segment if available)
    - Cost of sales
    - Gross profit
    - Operating expenses
    - Operating income
    - Non-operating income/expenses
    - Income tax
    - Net income

    Args:
        symbol: Stock code (e.g., 005930 for Samsung Electronics)
        year: Fiscal year (defaults to previous year)
        quarter: Optional quarter (1-4)

    Returns:
        Dictionary with all income statement line items
    """
    income_statement = opendart_client.get_income_statement(
        symbol, year, quarter
    )

    if not income_statement:
        raise HTTPException(
            status_code=404,
            detail=f"Income statement not found for {symbol} (year: {year}, quarter: {quarter})",
        )

    return {
        "symbol": symbol,
        "year": year,
        "quarter": quarter,
        "statement_type": "income_statement",
        "data": income_statement,
    }


@router.get("/financials/{symbol}/cash-flow")
async def get_cash_flow(
    symbol: str,
    year: int = Query(datetime.now().year - 1, description="Fiscal year"),
    quarter: Optional[int] = Query(
        None,
        ge=1,
        le=4,
        description="Quarter (1-4 for quarterly, None for annual)",
    ),
) -> Dict[str, Any]:
    """
    Get detailed cash flow statement for a Korean company.

    Returns all cash flow statement line items including:
    - Operating activities
    - Investing activities
    - Financing activities
    - Net change in cash

    Args:
        symbol: Stock code (e.g., 005930 for Samsung Electronics)
        year: Fiscal year (defaults to previous year)
        quarter: Optional quarter (1-4)

    Returns:
        Dictionary with all cash flow line items
    """
    cash_flow = opendart_client.get_cash_flow(symbol, year, quarter)

    if not cash_flow:
        raise HTTPException(
            status_code=404,
            detail=f"Cash flow statement not found for {symbol} (year: {year}, quarter: {quarter})",
        )

    return {
        "symbol": symbol,
        "year": year,
        "quarter": quarter,
        "statement_type": "cash_flow",
        "data": cash_flow,
    }


@router.get("/company/{symbol}")
async def get_company_info(symbol: str) -> Dict[str, Any]:
    """
    Get detailed company information for a Korean company.

    Returns comprehensive company profile including:
    - Company name (Korean and English)
    - CEO name
    - Address
    - Industry code
    - Website URL
    - Establishment date
    - And more...

    Args:
        symbol: Stock code (e.g., 005930 for Samsung Electronics)

    Returns:
        Dictionary with company information
    """
    company_info = opendart_client.get_company_info(symbol)

    if not company_info:
        raise HTTPException(
            status_code=404,
            detail=f"Company information not found for {symbol}",
        )

    return {
        "symbol": symbol,
        "data": company_info,
    }


@router.get("/disclosures")
async def get_disclosures(
    corp: Optional[str] = Query(
        None, description="Stock code or company name (optional)"
    ),
    start: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    kind: Optional[str] = Query(
        None,
        description="Disclosure type (A=regular, B=major, C=issue, etc.)",
    ),
    final: bool = Query(
        True, description="Only final reports (exclude corrections)"
    ),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of results"
    ),
) -> Dict[str, Any]:
    """
    Get list of corporate disclosures.

    Retrieves disclosure listings from OPENDART. Can filter by company,
    date range, and disclosure type.

    Args:
        corp: Stock code or company name (optional, if omitted returns all companies)
        start: Start date (YYYY-MM-DD or YYYYMMDD)
        end: End date (YYYY-MM-DD or YYYYMMDD)
        kind: Disclosure type code (A-J)
        final: If True, only return final reports
        limit: Maximum number of results to return

    Returns:
        Dictionary with disclosure listings
    """
    disclosures = opendart_client.get_disclosure_list(
        corp=corp, start=start, end=end, kind=kind, final=final
    )

    if disclosures is None:
        raise HTTPException(
            status_code=404,
            detail="No disclosures found for the specified criteria",
        )

    # Limit results
    limited_disclosures = disclosures[:limit] if disclosures else []

    return {
        "corp": corp,
        "start": start,
        "end": end,
        "kind": kind,
        "count": len(limited_disclosures),
        "data": limited_disclosures,
    }


@router.get("/financials/{symbol}/all")
async def get_all_financials(
    symbol: str,
    year: int = Query(datetime.now().year - 1, description="Fiscal year"),
    quarter: Optional[int] = Query(
        None,
        ge=1,
        le=4,
        description="Quarter (1-4 for quarterly, None for annual)",
    ),
    fs_div: str = Query(
        "CFS", description="Financial statement division (CFS/OFS)"
    ),
) -> Dict[str, Any]:
    """
    Get comprehensive financial statements with all line items.

    Returns complete financial data including all accounts from:
    - Balance Sheet
    - Income Statement
    - Cash Flow Statement

    This is more comprehensive than the summary endpoint.

    Args:
        symbol: Stock code (e.g., 005930 for Samsung Electronics)
        year: Fiscal year (defaults to previous year)
        quarter: Optional quarter (1-4)
        fs_div: Financial statement division (CFS for consolidated, OFS for separate)

    Returns:
        Dictionary with comprehensive financial data
    """
    # Determine report code
    if quarter:
        quarter_codes = {1: "11013", 2: "11012", 3: "11014", 4: "11011"}
        reprt_code = quarter_codes.get(quarter, "11011")
    else:
        reprt_code = "11011"

    requested_year = year
    financials = opendart_client.get_finstate_all(
        symbol, year, reprt_code, fs_div
    )

    if financials is None:
        raise HTTPException(
            status_code=404,
            detail=f"Financial data not found for {symbol} (year: {year}, quarter: {quarter})",
        )

    if not financials:
        return {
            "symbol": symbol,
            "year": requested_year,
            "requested_year": requested_year,
            "quarter": quarter,
            "fs_div": fs_div,
            "count": 0,
            "data": [],
            "note": f"DART API no data for {symbol} (year: {year}, quarter: {quarter}).",
        }

    return {
        "symbol": symbol,
        "year": year,
        "quarter": quarter,
        "fs_div": fs_div,
        "count": len(financials),
        "data": financials,
    }
