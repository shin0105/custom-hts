"""Price/yield maths for KRX-listed bonds, using Korean market convention.

Everything here is a pure function of a ``BondSpec`` and a settlement date,
so it can be unit-tested without the broker API.

Conventions (checked against live KRX quotes, see tests/test_bond_math.py):

* Prices are per 10,000 KRW face and are *dirty* prices: the quoted KRX
  price already includes accrued interest.
* Coupon bonds discount whole coupon periods with compound interest at
  ``y / f`` and the partial first period with simple interest::

      P = sum(CF_k / (1 + y/f)^k) / (1 + (y/f) * d/t)

  where ``d`` is the days to the next coupon and ``t`` the days in the
  current coupon period.
* Bonds paying everything at maturity (compound, simple-interest and
  discount bonds) discount whole years with annual compounding and the
  remaining days with simple interest on an actual/365 basis::

      P = S / ((1 + y)^n * (1 + y * d/365))

* The maturity amount of compound and simple-interest bonds is truncated
  to whole won per 10,000 face.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Tuple

FACE = 10_000.0

KIND_COUPON = "coupon"
KIND_COMPOUND = "compound"
KIND_SIMPLE = "simple"
KIND_DISCOUNT = "discount"
BULLET_KINDS = {KIND_COMPOUND, KIND_SIMPLE, KIND_DISCOUNT}

DEFAULT_TAX_RATE = 0.154
DEFAULT_SHIFTS_BP = (-100, -50, -25, 25, 50, 100)


@dataclass(frozen=True)
class BondSpec:
    """Static terms of a fixed-rate bond."""

    kind: str
    coupon_rate: float  # annual, percent
    maturity_date: date
    issue_date: Optional[date] = None
    interval_months: int = 12  # coupon (or compounding) interval
    redemption_ratio: float = 100.0  # percent of face repaid at maturity

    @property
    def frequency(self) -> float:
        """Coupon payments (or compounding periods) per year."""
        return 12.0 / self.interval_months


def add_months(source: date, months: int) -> date:
    """Shift a date by whole months, clamping to the month's last day."""
    month_index = (source.month - 1) + months
    year = source.year + month_index // 12
    month = month_index % 12 + 1
    leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    month_days = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return date(year, month, min(source.day, month_days[month - 1]))


def _check(spec: BondSpec, settle: date) -> None:
    if spec.interval_months <= 0:
        raise ValueError("interval_months must be positive")
    if settle >= spec.maturity_date:
        raise ValueError("bond has matured")


def coupon_schedule(spec: BondSpec, settle: date) -> Tuple[date, List[date]]:
    """Return (previous coupon date, coupon dates after ``settle``).

    Dates are generated backwards from maturity so they stay anchored to
    the maturity day-of-month. The previous date is floored at the issue
    date, which makes a short first period accrue from issuance.
    """
    _check(spec, settle)
    upcoming: List[date] = []
    step = 0
    cursor = spec.maturity_date
    while cursor > settle:
        upcoming.append(cursor)
        step += 1
        cursor = add_months(spec.maturity_date, -step * spec.interval_months)
    previous = cursor
    if spec.issue_date and previous < spec.issue_date <= settle:
        previous = spec.issue_date
    upcoming.reverse()
    return previous, upcoming


def _years_between(start: date, end: date) -> float:
    """Whole years plus an actual/365 fraction."""
    years = 0
    while add_months(start, 12 * (years + 1)) <= end:
        years += 1
    rest = (end - add_months(start, 12 * years)).days
    return years + rest / 365.0


def maturity_amount(spec: BondSpec) -> float:
    """Amount repaid at maturity per 10,000 face (principal + interest)."""
    redemption = FACE * spec.redemption_ratio / 100.0
    if spec.kind == KIND_COUPON:
        return redemption + FACE * spec.coupon_rate / 100.0 / spec.frequency
    if spec.kind == KIND_DISCOUNT:
        return redemption
    if spec.issue_date is None:
        raise ValueError("issue_date is required for compound/simple bonds")
    term = _years_between(spec.issue_date, spec.maturity_date)
    rate = spec.coupon_rate / 100.0
    if spec.kind == KIND_COMPOUND:
        grown = (1.0 + rate / spec.frequency) ** (spec.frequency * term)
    elif spec.kind == KIND_SIMPLE:
        grown = 1.0 + rate * term
    else:
        raise ValueError(f"unknown bond kind: {spec.kind}")
    # Small epsilon so 10510.0999999 style float noise is not truncated down.
    return math.floor(redemption * grown + 1e-6)


def cash_flows(spec: BondSpec, settle: date) -> List[Tuple[date, float]]:
    """Future cash flows per 10,000 face, strictly after ``settle``."""
    _check(spec, settle)
    if spec.kind in BULLET_KINDS:
        return [(spec.maturity_date, maturity_amount(spec))]
    if spec.kind != KIND_COUPON:
        raise ValueError(f"unknown bond kind: {spec.kind}")
    _, dates = coupon_schedule(spec, settle)
    coupon = FACE * spec.coupon_rate / 100.0 / spec.frequency
    flows = [(d, coupon) for d in dates]
    flows[-1] = (dates[-1], coupon + FACE * spec.redemption_ratio / 100.0)
    return flows


def _bullet_periods(spec: BondSpec, settle: date) -> Tuple[int, int]:
    """Whole years and leftover days from ``settle`` to maturity."""
    years = 0
    while add_months(spec.maturity_date, -12 * (years + 1)) >= settle:
        years += 1
    days = (add_months(spec.maturity_date, -12 * years) - settle).days
    return years, days


def _pv(spec: BondSpec, settle: date, amounts: List[float], y: float) -> float:
    """Present value of ``amounts`` (aligned to cash_flows) at yield ``y``."""
    if spec.kind in BULLET_KINDS:
        years, days = _bullet_periods(spec, settle)
        if 1.0 + y <= 0 or 1.0 + y * days / 365.0 <= 0:
            raise ValueError("yield out of range")
        return amounts[0] / ((1.0 + y) ** years * (1.0 + y * days / 365.0))

    previous, dates = coupon_schedule(spec, settle)
    per = y / spec.frequency
    stub = (dates[0] - settle).days / (dates[0] - previous).days
    if 1.0 + per <= 0 or 1.0 + per * stub <= 0:
        raise ValueError("yield out of range")
    total = sum(amount / (1.0 + per) ** k for k, amount in enumerate(amounts))
    return total / (1.0 + per * stub)


def price_from_yield(spec: BondSpec, settle: date, yield_pct: float) -> float:
    """Dirty price per 10,000 face for an annual yield in percent."""
    amounts = [amount for _, amount in cash_flows(spec, settle)]
    return _pv(spec, settle, amounts, yield_pct / 100.0)


def _solve_yield(
    spec: BondSpec, settle: date, amounts: List[float], price: float
) -> Optional[float]:
    """Bisection on yield; PV falls monotonically as yield rises.

    Yields outside -50%..500% are treated as bad input (usually a price in
    the wrong unit) rather than solved.
    """
    if price <= 0:
        return None
    low, high = -0.5, 5.0
    try:
        if _pv(spec, settle, amounts, low) < price:
            return None
        if _pv(spec, settle, amounts, high) > price:
            return None
    except ValueError:
        return None
    for _ in range(200):
        mid = (low + high) / 2.0
        if _pv(spec, settle, amounts, mid) > price:
            low = mid
        else:
            high = mid
        if high - low < 1e-12:
            break
    return (low + high) / 2.0 * 100.0


def yield_from_price(
    spec: BondSpec, settle: date, price: float
) -> Optional[float]:
    """Yield to maturity (percent) for a dirty price per 10,000 face."""
    amounts = [amount for _, amount in cash_flows(spec, settle)]
    return _solve_yield(spec, settle, amounts, price)


def accrued_interest(spec: BondSpec, settle: date) -> float:
    """Interest earned but not yet paid, per 10,000 face."""
    _check(spec, settle)
    rate = spec.coupon_rate / 100.0
    if spec.kind == KIND_COUPON:
        previous, dates = coupon_schedule(spec, settle)
        coupon = FACE * rate / spec.frequency
        elapsed = (settle - previous).days / (dates[0] - previous).days
        return coupon * max(0.0, min(1.0, elapsed))
    if spec.kind == KIND_DISCOUNT or spec.issue_date is None:
        return 0.0
    held = _years_between(spec.issue_date, max(settle, spec.issue_date))
    if spec.kind == KIND_COMPOUND:
        return FACE * ((1.0 + rate / spec.frequency) ** (spec.frequency * held) - 1.0)
    return FACE * rate * held


def risk_measures(spec: BondSpec, settle: date, yield_pct: float) -> dict:
    """Duration, convexity and DV01 by bumping the yield one basis point."""
    bump = 0.01  # percent, i.e. 1bp
    base = price_from_yield(spec, settle, yield_pct)
    up = price_from_yield(spec, settle, yield_pct + bump)
    down = price_from_yield(spec, settle, yield_pct - bump)
    step = bump / 100.0
    modified = -(up - down) / (2.0 * step * base)
    compounding = spec.frequency if spec.kind == KIND_COUPON else 1.0
    return {
        "modified_duration": modified,
        "macaulay_duration": modified * (1.0 + yield_pct / 100.0 / compounding),
        "convexity": (up + down - 2.0 * base) / (base * step * step),
        "dv01": (down - up) / 2.0,
    }


def scenario_table(
    spec: BondSpec,
    settle: date,
    yield_pct: float,
    shifts_bp: Tuple[int, ...] = DEFAULT_SHIFTS_BP,
) -> List[dict]:
    """Price impact of parallel yield shifts, in basis points."""
    base = price_from_yield(spec, settle, yield_pct)
    rows = []
    for shift in shifts_bp:
        shifted_yield = yield_pct + shift / 100.0
        price = price_from_yield(spec, settle, shifted_yield)
        rows.append(
            {
                "shift_bp": shift,
                "yield_rate": shifted_yield,
                "price": price,
                "price_change": price - base,
                "price_change_percent": (price - base) / base * 100.0,
            }
        )
    return rows


def after_tax_yield(
    spec: BondSpec,
    settle: date,
    price: float,
    tax_rate: float = DEFAULT_TAX_RATE,
) -> Optional[float]:
    """Yield to maturity after interest income tax, for a buy-and-hold retail
    investor.

    Tax is charged only on interest accrued while the bond is held (capital
    gains on bonds are untaxed), so the first coupon is taxed pro rata.
    Discount bonds are not handled and return None.
    """
    flows = cash_flows(spec, settle)
    amounts = [amount for _, amount in flows]
    if spec.kind == KIND_COUPON:
        previous, dates = coupon_schedule(spec, settle)
        coupon = FACE * spec.coupon_rate / 100.0 / spec.frequency
        held = (dates[0] - settle).days / (dates[0] - previous).days
        amounts = [amount - coupon * tax_rate for amount in amounts]
        amounts[0] += coupon * tax_rate * (1.0 - held)
    elif spec.kind in (KIND_COMPOUND, KIND_SIMPLE):
        redemption = FACE * spec.redemption_ratio / 100.0
        interest_at_maturity = amounts[0] - redemption
        taxable = interest_at_maturity - accrued_interest(spec, settle)
        amounts = [amounts[0] - max(0.0, taxable) * tax_rate]
    else:
        return None
    return _solve_yield(spec, settle, amounts, price)
