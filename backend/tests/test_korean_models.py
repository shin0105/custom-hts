"""Tests for Korean market models."""

from datetime import datetime
from src.models.korean import (
    KoreanStockQuote,
    KoreanCandleData,
    KoreanAccountBalance,
    KoreanStockPosition,
)


def test_korean_candle_data_creation() -> None:
    """Test Korean candle data model creation."""
    candle = KoreanCandleData(
        symbol="005930",
        date="20240101",
        open=70000,
        high=71000,
        low=69000,
        close=70500,
        volume=10000000,
        change=500,
        change_percent=0.71,
    )

    assert candle.symbol == "005930"
    assert candle.date == "20240101"
    assert candle.open == 70000
    assert candle.high == 71000
    assert candle.low == 69000
    assert candle.close == 70500
    assert candle.volume == 10000000


def test_korean_account_balance_creation() -> None:
    """Test Korean account balance model creation."""
    balance = KoreanAccountBalance(
        account_number="12345678",
        total_evaluation=100000000,
        cash_balance=20000000,
        investment_amount=80000000,
        profit_loss=5000000,
        profit_loss_percent=6.25,
        timestamp=datetime.now(),
    )

    assert balance.account_number == "12345678"
    assert balance.total_evaluation == 100000000
    assert balance.cash_balance == 20000000
    assert balance.investment_amount == 80000000
    assert balance.profit_loss == 5000000
    assert balance.profit_loss_percent == 6.25


def test_korean_stock_position_creation() -> None:
    """Test Korean stock position model creation."""
    position = KoreanStockPosition(
        symbol="005930",
        name="삼성전자",
        quantity=100,
        average_price=70000,
        current_price=72000,
        evaluation_amount=7200000,
        profit_loss=200000,
        profit_loss_percent=2.86,
    )

    assert position.symbol == "005930"
    assert position.name == "삼성전자"
    assert position.quantity == 100
    assert position.average_price == 70000
    assert position.current_price == 72000
    assert position.evaluation_amount == 7200000
    assert position.profit_loss == 200000


def test_korean_candle_data_with_optional_fields() -> None:
    """Test Korean candle data with optional fields."""
    candle = KoreanCandleData(
        symbol="005930",
        date="20240101",
        open=70000,
        high=71000,
        low=69000,
        close=70500,
        volume=10000000,
    )

    assert candle.symbol == "005930"
    assert candle.change is None
    assert candle.change_percent is None


def test_korean_stock_quote_with_full_data() -> None:
    """Test Korean stock quote with all fields."""
    quote = KoreanStockQuote(
        symbol="005930",
        name="삼성전자",
        current_price=70000,
        change=1000,
        change_percent=1.45,
        volume=10000000,
        timestamp=datetime.now(),
        high=71000,
        low=69000,
        open=69500,
        previous_close=69000,
    )

    assert quote.symbol == "005930"
    assert quote.current_price == 70000
    assert quote.high == 71000
    assert quote.low == 69000
    assert quote.open == 69500
    assert quote.previous_close == 69000
