"""API routes for Korean market endpoints."""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional, Dict, Any
from ..models.korean import KoreanStockQuote, KoreanFinancialStatement
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
    year: int = Query(
        datetime.now().year, description="Fiscal year"
    ),
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


@router.get("/financials/{symbol}/balance-sheet")
async def get_balance_sheet(
    symbol: str,
    year: int = Query(
        datetime.now().year - 1, description="Fiscal year"
    ),
    quarter: Optional[int] = Query(
        None, ge=1, le=4, description="Quarter (1-4 for quarterly, None for annual)"
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
        "data": balance_sheet
    }


@router.get("/financials/{symbol}/income-statement")
async def get_income_statement(
    symbol: str,
    year: int = Query(
        datetime.now().year - 1, description="Fiscal year"
    ),
    quarter: Optional[int] = Query(
        None, ge=1, le=4, description="Quarter (1-4 for quarterly, None for annual)"
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
    income_statement = opendart_client.get_income_statement(symbol, year, quarter)
    
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
        "data": income_statement
    }


@router.get("/financials/{symbol}/cash-flow")
async def get_cash_flow(
    symbol: str,
    year: int = Query(
        datetime.now().year - 1, description="Fiscal year"
    ),
    quarter: Optional[int] = Query(
        None, ge=1, le=4, description="Quarter (1-4 for quarterly, None for annual)"
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
        "data": cash_flow
    }
