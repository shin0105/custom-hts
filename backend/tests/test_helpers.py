"""Tests for utility helper functions."""

import pytest
from src.utils.helpers import (
    format_currency,
    safe_float,
    safe_int,
    calculate_change_percent,
)


def test_format_currency_usd() -> None:
    """Test USD currency formatting."""
    assert format_currency(1234.56, "USD") == "$1,234.56"
    assert format_currency(1000000, "USD") == "$1,000,000.00"


def test_format_currency_krw() -> None:
    """Test KRW currency formatting."""
    assert format_currency(1234567, "KRW") == "₩1,234,567"
    assert format_currency(1000000, "KRW") == "₩1,000,000"


def test_safe_float() -> None:
    """Test safe float conversion."""
    assert safe_float("123.45") == 123.45
    assert safe_float("invalid", 0.0) == 0.0
    assert safe_float(None, 10.0) == 10.0
    assert safe_float(100) == 100.0


def test_safe_int() -> None:
    """Test safe int conversion."""
    assert safe_int("123") == 123
    assert safe_int("invalid", 0) == 0
    assert safe_int(None, 10) == 10
    assert safe_int(100.5) == 100


def test_calculate_change_percent() -> None:
    """Test percentage change calculation."""
    assert calculate_change_percent(110, 100) == 10.0
    assert calculate_change_percent(90, 100) == -10.0
    assert calculate_change_percent(100, 0) is None
    assert calculate_change_percent(None, 100) is None
