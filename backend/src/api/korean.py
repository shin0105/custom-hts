"""API routes for Korean market endpoints."""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional
from ..models.korean import KoreanStockQuote, KoreanFinancialStatement
from ..services.korean_market import korean_market_service

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
