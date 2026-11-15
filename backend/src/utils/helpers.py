"""Utility helper functions for the HTS backend."""

from typing import Any, Optional
from datetime import datetime, timedelta, timezone
import pandas as pd

KST = timezone(timedelta(hours=9))


def current_year_kst() -> int:
    """Return the current calendar year in Korea (evaluated per call)."""
    return datetime.now(KST).year


def format_currency(
    amount: float, currency: str = "USD", decimals: int = 2
) -> str:
    """
    Format a number as currency.

    Args:
        amount: The amount to format
        currency: Currency code (USD, KRW, etc.)
        decimals: Number of decimal places

    Returns:
        Formatted currency string
    """
    if currency == "KRW":
        # Korean Won typically doesn't use decimals
        return f"₩{amount:,.0f}"
    elif currency == "USD":
        return f"${amount:,.{decimals}f}"
    else:
        return f"{amount:,.{decimals}f} {currency}"


def parse_date(date_str: str, format: str = "%Y%m%d") -> Optional[datetime]:
    """
    Parse a date string into a datetime object.

    Args:
        date_str: Date string to parse
        format: Expected date format

    Returns:
        datetime object or None if parsing fails
    """
    try:
        return datetime.strptime(date_str, format)
    except (ValueError, TypeError):
        return None


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to float.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Float value or default
    """
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert a value to int.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Int value or default
    """
    try:
        if pd.isna(value):
            return default
        return int(value)
    except (ValueError, TypeError):
        return default


def calculate_change_percent(
    current: float, previous: float
) -> Optional[float]:
    """
    Calculate percentage change between two values.

    Args:
        current: Current value
        previous: Previous value

    Returns:
        Percentage change or None if calculation not possible
    """
    if previous == 0 or pd.isna(previous) or pd.isna(current):
        return None
    return ((current - previous) / previous) * 100
