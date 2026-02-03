"""API routes for Korean market endpoints."""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional, List, Dict, Any
from ..models.korean import (
    KoreanStockQuote,
    KoreanFinancialStatement,
    KoreanCandleData,
    KoreanAccountBalance,
    KoreanStockPosition,
)
from ..services.korean_market import korean_market_service
from ..integrations.opendart import opendart_client

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
    period: str = Query(
        "D", description="Period type (D: daily, W: weekly, M: monthly)"
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
        symbol, period, adjust_price, limit
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
    interval: int = Query(1, description="Minute interval (1, 5, 10, 30, 60)"),
    limit: int = Query(100, ge=1, le=500, description="Number of candles"),
) -> List[KoreanCandleData]:
    """
    Get minute candle chart data for a Korean stock.

    Args:
        symbol: Stock code
        interval: Minute interval
        limit: Number of candles to retrieve (1-500)

    Returns:
        List of minute candle data (OHLCV)
    """
    candles = await korean_market_service.get_minute_candle(
        symbol, interval, limit
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
