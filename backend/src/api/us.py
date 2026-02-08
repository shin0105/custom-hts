"""API routes for US market endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..models.us import (
    USStockQuote,
    USFinancialStatement,
    USCandleData,
    USValuationMetrics,
)
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


@router.get("/valuation/{symbol}", response_model=USValuationMetrics)
async def get_us_valuation(symbol: str) -> USValuationMetrics:
    """
    Get valuation metrics (PER/PBR/EPS/BPS) for a US stock.
    """
    metrics = await us_market_service.get_valuation_metrics(symbol.upper())
    if not metrics:
        raise HTTPException(
            status_code=404,
            detail=f"Valuation metrics not found for symbol {symbol}",
        )
    return metrics


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


@router.get("/candle/{symbol}", response_model=List[USCandleData])
async def get_us_candle(
    symbol: str,
    period: str = Query(
        "1mo",
        description="Time period: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max",
    ),
    interval: str = Query(
        "1d", description="Interval: 1m,5m,15m,30m,60m,1d,1wk,1mo"
    ),
    start: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
) -> List[USCandleData]:
    """
    Get historical candle data for a US stock.

    Args:
        symbol: Stock ticker symbol (e.g., AAPL)
        period: Time period for data
        interval: Data interval
        start: Optional start date
        end: Optional end date

    Returns:
        List of candle data (OHLCV)
    """
    candles = await us_market_service.get_historical_data(
        symbol.upper(), period, interval, start, end
    )
    if not candles:
        raise HTTPException(
            status_code=404,
            detail=f"Candle data not found for symbol {symbol}",
        )
    return candles


@router.get("/health")
async def us_market_health() -> dict:
    """Health check endpoint for US market API."""
    return {"status": "healthy", "market": "US"}
