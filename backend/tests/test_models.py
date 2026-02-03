"""Tests for data models."""

from datetime import datetime
from src.models.korean import KoreanStockQuote, KoreanFinancialStatement
from src.models.us import USStockQuote, USFinancialStatement


def test_korean_stock_quote_creation() -> None:
    """Test Korean stock quote model creation."""
    quote = KoreanStockQuote(
        symbol="005930",
        name="삼성전자",
        current_price=70000,
        change=1000,
        change_percent=1.45,
        volume=10000000,
        timestamp=datetime.now(),
    )
    
    assert quote.symbol == "005930"
    assert quote.name == "삼성전자"
    assert quote.current_price == 70000
    assert quote.change == 1000


def test_us_stock_quote_creation() -> None:
    """Test US stock quote model creation."""
    quote = USStockQuote(
        symbol="AAPL",
        name="Apple Inc.",
        current_price=175.50,
        change=2.50,
        change_percent=1.45,
        volume=50000000,
        timestamp=datetime.now(),
        market_cap=2800000000000,
    )
    
    assert quote.symbol == "AAPL"
    assert quote.name == "Apple Inc."
    assert quote.current_price == 175.50
    assert quote.market_cap == 2800000000000


def test_korean_financial_statement_creation() -> None:
    """Test Korean financial statement model creation."""
    statement = KoreanFinancialStatement(
        symbol="005930",
        company_name="삼성전자",
        year=2024,
        revenue=1000000000000,
        net_income=50000000000,
        updated_at=datetime.now(),
    )
    
    assert statement.symbol == "005930"
    assert statement.year == 2024
    assert statement.revenue == 1000000000000


def test_us_financial_statement_creation() -> None:
    """Test US financial statement model creation."""
    statement = USFinancialStatement(
        symbol="AAPL",
        company_name="Apple Inc.",
        year=2024,
        revenue=394000000000,
        net_income=97000000000,
        eps=6.13,
        pe_ratio=28.5,
        updated_at=datetime.now(),
    )
    
    assert statement.symbol == "AAPL"
    assert statement.year == 2024
    assert statement.eps == 6.13
    assert statement.pe_ratio == 28.5
