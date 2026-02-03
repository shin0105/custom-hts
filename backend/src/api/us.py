"""API routes for US market endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from ..models.us import USStockQuote, USFinancialStatement
from ..services.us_market import us_market_service

router = APIRouter(prefix="/us", tags=["US Market"])


@router.get("/quote/{symbol}", response_model=USStockQuote)
async def get_us_quote(symbol: str) -> USStockQuote:
    """
    Get real-time quote for a US stock.

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)

    Returns:
        Real-time stock quote data
    """
    quote = await us_market_service.get_quote(symbol.upper())
    if not quote:
        raise HTTPException(
            status_code=404, detail=f"Quote not found for symbol {symbol}"
        )
    return quote


@router.get("/financials/{symbol}", response_model=List[USFinancialStatement])
async def get_us_financials(
    symbol: str,
    use_cache: bool = Query(True, description="Use cached data if available"),
) -> List[USFinancialStatement]:
    """
    Get financial statements for a US company.

    Args:
        symbol: Stock ticker symbol
        use_cache: Whether to use cached data

    Returns:
        List of financial statements
    """
    financials = await us_market_service.get_financials(
        symbol.upper(), use_cache
    )
    if not financials:
        raise HTTPException(
            status_code=404,
            detail=f"Financials not found for symbol {symbol}",
        )
    return financials


@router.get("/health")
async def us_market_health() -> dict:
    """Health check endpoint for US market API."""
    return {"status": "healthy", "market": "US"}
