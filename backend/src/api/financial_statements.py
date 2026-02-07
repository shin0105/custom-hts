"""API routes for financial statement endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from ..services.financial_statements import financial_statement_service
from ..integrations.supabase_client import supabase_client

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================


class FinancialStatementInsertRequest(BaseModel):
    """Request model for inserting financial statements."""

    symbol: str
    year: int
    quarter: Optional[int] = None


class FinancialStatementInsertResponse(BaseModel):
    """Response model for financial statement insertion."""

    success: bool
    message: str
    inserted: Dict[str, bool]


class FinancialDataResponse(BaseModel):
    """Response model for financial data queries."""

    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    count: int = 0
    message: Optional[str] = None


class BatchInsertRequest(BaseModel):
    """Request model for batch insertion endpoints."""

    symbols: List[str]
    year: int
    quarters: Optional[List[int]] = None


# ============================================================================
# Korean Financial Statement Endpoints
# ============================================================================


@router.post("/korean/statements/insert", response_model=FinancialStatementInsertResponse)
async def insert_korean_financial_statements(
    request: FinancialStatementInsertRequest,
) -> FinancialStatementInsertResponse:
    """
    Insert all financial statements for a Korean company.

    This endpoint fetches data from OPENDART and inserts into:
    - korean_balance_sheet
    - korean_income_statement
    - korean_cashflow_statement

    Args:
        request: Contains symbol, year, and optional quarter

    Returns:
        Success status and details of what was inserted
    """
    try:
        results = financial_statement_service.insert_all_korean_statements(
            symbol=request.symbol, year=request.year, quarter=request.quarter
        )

        success = any(results.values())
        period = f"{request.year}Q{request.quarter}" if request.quarter else str(request.year)

        if success:
            message = f"Successfully inserted financial statements for {request.symbol} ({period})"
        else:
            message = f"No data available for {request.symbol} ({period})"

        return FinancialStatementInsertResponse(
            success=success, message=message, inserted=results
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/korean/balance-sheet/{symbol}", response_model=FinancialDataResponse)
async def get_korean_balance_sheet(
    symbol: str,
    year: Optional[int] = Query(None, description="Filter by year"),
    quarter: Optional[int] = Query(None, description="Filter by quarter (1-4)"),
) -> FinancialDataResponse:
    """
    Get balance sheet data for a Korean company.

    Args:
        symbol: Korean stock code (e.g., "005930")
        year: Optional year filter
        quarter: Optional quarter filter

    Returns:
        Balance sheet data
    """
    try:
        if not supabase_client.client:
            raise HTTPException(
                status_code=503, detail="Database connection not available"
            )

        query = supabase_client.client.table("korean_balance_sheet").select("*").eq("symbol", symbol)

        if year is not None:
            query = query.eq("year", year)

        if quarter is not None:
            query = query.eq("quarter", quarter)

        response = query.order("year", desc=True).order("quarter", desc=True).execute()

        return FinancialDataResponse(
            success=True, data=response.data, count=len(response.data)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/korean/income-statement/{symbol}", response_model=FinancialDataResponse)
async def get_korean_income_statement(
    symbol: str,
    year: Optional[int] = Query(None, description="Filter by year"),
    quarter: Optional[int] = Query(None, description="Filter by quarter (1-4)"),
) -> FinancialDataResponse:
    """
    Get income statement data for a Korean company.

    Args:
        symbol: Korean stock code
        year: Optional year filter
        quarter: Optional quarter filter

    Returns:
        Income statement data
    """
    try:
        if not supabase_client.client:
            raise HTTPException(
                status_code=503, detail="Database connection not available"
            )

        query = supabase_client.client.table("korean_income_statement").select("*").eq("symbol", symbol)

        if year is not None:
            query = query.eq("year", year)

        if quarter is not None:
            query = query.eq("quarter", quarter)

        response = query.order("year", desc=True).order("quarter", desc=True).execute()

        return FinancialDataResponse(
            success=True, data=response.data, count=len(response.data)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/korean/cashflow/{symbol}", response_model=FinancialDataResponse)
async def get_korean_cashflow(
    symbol: str,
    year: Optional[int] = Query(None, description="Filter by year"),
    quarter: Optional[int] = Query(None, description="Filter by quarter (1-4)"),
) -> FinancialDataResponse:
    """
    Get cash flow statement data for a Korean company.

    Args:
        symbol: Korean stock code
        year: Optional year filter
        quarter: Optional quarter filter

    Returns:
        Cash flow data
    """
    try:
        if not supabase_client.client:
            raise HTTPException(
                status_code=503, detail="Database connection not available"
            )

        query = supabase_client.client.table("korean_cashflow_statement").select("*").eq("symbol", symbol)

        if year is not None:
            query = query.eq("year", year)

        if quarter is not None:
            query = query.eq("quarter", quarter)

        response = query.order("year", desc=True).order("quarter", desc=True).execute()

        return FinancialDataResponse(
            success=True, data=response.data, count=len(response.data)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# US Financial Statement Endpoints
# ============================================================================


@router.post("/us/statements/insert", response_model=FinancialStatementInsertResponse)
async def insert_us_financial_statements(
    request: FinancialStatementInsertRequest,
) -> FinancialStatementInsertResponse:
    """
    Insert all financial statements for a US company.

    This endpoint fetches data from yfinance and inserts into:
    - us_balance_sheet
    - us_income_statement
    - us_cashflow_statement

    Args:
        request: Contains symbol, year, and optional quarter

    Returns:
        Success status and details of what was inserted
    """
    try:
        results = financial_statement_service.insert_all_us_statements(
            symbol=request.symbol, year=request.year, quarter=request.quarter
        )

        success = any(results.values())
        period = f"{request.year}Q{request.quarter}" if request.quarter else str(request.year)

        if success:
            message = f"Successfully inserted financial statements for {request.symbol} ({period})"
        else:
            message = f"No data available for {request.symbol} ({period})"

        return FinancialStatementInsertResponse(
            success=success, message=message, inserted=results
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/us/balance-sheet/{symbol}", response_model=FinancialDataResponse)
async def get_us_balance_sheet(
    symbol: str,
    year: Optional[int] = Query(None, description="Filter by year"),
    quarter: Optional[int] = Query(None, description="Filter by quarter (1-4)"),
) -> FinancialDataResponse:
    """
    Get balance sheet data for a US company.

    Args:
        symbol: US stock ticker (e.g., "AAPL")
        year: Optional year filter
        quarter: Optional quarter filter

    Returns:
        Balance sheet data
    """
    try:
        if not supabase_client.client:
            raise HTTPException(
                status_code=503, detail="Database connection not available"
            )

        query = supabase_client.client.table("us_balance_sheet").select("*").eq("symbol", symbol)

        if year is not None:
            query = query.eq("year", year)

        if quarter is not None:
            query = query.eq("quarter", quarter)

        response = query.order("year", desc=True).order("quarter", desc=True).execute()

        return FinancialDataResponse(
            success=True, data=response.data, count=len(response.data)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/us/income-statement/{symbol}", response_model=FinancialDataResponse)
async def get_us_income_statement(
    symbol: str,
    year: Optional[int] = Query(None, description="Filter by year"),
    quarter: Optional[int] = Query(None, description="Filter by quarter (1-4)"),
) -> FinancialDataResponse:
    """
    Get income statement data for a US company.

    Args:
        symbol: US stock ticker
        year: Optional year filter
        quarter: Optional quarter filter

    Returns:
        Income statement data
    """
    try:
        if not supabase_client.client:
            raise HTTPException(
                status_code=503, detail="Database connection not available"
            )

        query = supabase_client.client.table("us_income_statement").select("*").eq("symbol", symbol)

        if year is not None:
            query = query.eq("year", year)

        if quarter is not None:
            query = query.eq("quarter", quarter)

        response = query.order("year", desc=True).order("quarter", desc=True).execute()

        return FinancialDataResponse(
            success=True, data=response.data, count=len(response.data)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/us/cashflow/{symbol}", response_model=FinancialDataResponse)
async def get_us_cashflow(
    symbol: str,
    year: Optional[int] = Query(None, description="Filter by year"),
    quarter: Optional[int] = Query(None, description="Filter by quarter (1-4)"),
) -> FinancialDataResponse:
    """
    Get cash flow statement data for a US company.

    Args:
        symbol: US stock ticker
        year: Optional year filter
        quarter: Optional quarter filter

    Returns:
        Cash flow data
    """
    try:
        if not supabase_client.client:
            raise HTTPException(
                status_code=503, detail="Database connection not available"
            )

        query = supabase_client.client.table("us_cashflow_statement").select("*").eq("symbol", symbol)

        if year is not None:
            query = query.eq("year", year)

        if quarter is not None:
            query = query.eq("quarter", quarter)

        response = query.order("year", desc=True).order("quarter", desc=True).execute()

        return FinancialDataResponse(
            success=True, data=response.data, count=len(response.data)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Batch Operations
# ============================================================================


@router.post("/korean/statements/batch-insert")
async def batch_insert_korean_statements(
    request: BatchInsertRequest,
) -> Dict[str, Any]:
    """
    Insert financial statements for multiple Korean companies.

    Args:
        symbols: List of Korean stock codes
        year: Fiscal year
        quarters: Optional list of quarters to insert (defaults to annual only)

    Returns:
        Summary of insertions
    """
    try:
        if request.quarters is None:
            quarters = [None]  # Annual only
        else:
            quarters = request.quarters

        results = {}
        for symbol in request.symbols:
            symbol_results = {}
            for quarter in quarters:
                period_key = f"{request.year}Q{quarter}" if quarter else str(request.year)
                symbol_results[period_key] = (
                    financial_statement_service.insert_all_korean_statements(
                        symbol, request.year, quarter
                    )
                )
            results[symbol] = symbol_results

        return {"success": True, "results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/us/statements/batch-insert")
async def batch_insert_us_statements(
    request: BatchInsertRequest,
) -> Dict[str, Any]:
    """
    Insert financial statements for multiple US companies.

    Args:
        symbols: List of US stock tickers
        year: Fiscal year
        quarters: Optional list of quarters to insert (defaults to annual only)

    Returns:
        Summary of insertions
    """
    try:
        if request.quarters is None:
            quarters = [None]  # Annual only
        else:
            quarters = request.quarters

        results = {}
        for symbol in request.symbols:
            symbol_results = {}
            for quarter in quarters:
                period_key = f"{request.year}Q{quarter}" if quarter else str(request.year)
                symbol_results[period_key] = (
                    financial_statement_service.insert_all_us_statements(
                        symbol, request.year, quarter
                    )
                )
            results[symbol] = symbol_results

        return {"success": True, "results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
