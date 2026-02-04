"""API routes for Korean market endpoints."""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from ..models.korean import (
    KoreanStockQuote,
    KoreanFinancialStatement,
    KoreanCandleData,
)
from ..services.korean_market import korean_market_service
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
    limit: int = Query(100, ge=1, le=500, description="Number of candles"),
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
        symbol, period.value, adjust_price, limit
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
    limit: int = Query(100, ge=1, le=500, description="Number of candles"),
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
        symbol, interval.value, limit
    )
    if not candles:
        raise HTTPException(
            status_code=404,
            detail=f"Minute candle data not found for symbol {symbol}",
        )
    return candles


@router.get("/account/{account_number}")
async def get_korean_account_balance(
    account_number: str,
    account_product_code: str = Query(
        "01", description="Account product code"
    ),
) -> Dict[str, Any]:
    """
    Get account balance and stock positions.

    WARNING: This endpoint currently lacks authentication and authorization.
    In production, this should be protected with user authentication and
    the account_number should be derived from the authenticated user context
    rather than being a path parameter accessible by anyone.

    Args:
        account_number: Account number (8 digits)
        account_product_code: Account product code (default: "01")

    Returns:
        Account balance and list of stock positions
    """
    result = await korean_market_service.get_account_balance(
        account_number, account_product_code
    )
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Account balance not found for account {account_number}",
        )
    return result


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
    corp: Optional[str] = Query(None, description="Stock code or company name (optional)"),
    start: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    kind: Optional[str] = Query(
        None,
        description="Disclosure type (A=regular, B=major, C=issue, etc.)",
    ),
    final: bool = Query(True, description="Only final reports (exclude corrections)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
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
    fs_div: str = Query("CFS", description="Financial statement division (CFS/OFS)"),
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

    financials = opendart_client.get_finstate_all(symbol, year, reprt_code, fs_div)

    if financials is None or not financials:
        raise HTTPException(
            status_code=404,
            detail=f"Financial data not found for {symbol} (year: {year}, quarter: {quarter})",
        )

    return {
        "symbol": symbol,
        "year": year,
        "quarter": quarter,
        "fs_div": fs_div,
        "count": len(financials),
        "data": financials,
    }
