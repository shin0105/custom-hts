"""Tests for bond price/yield maths.

The quote fixtures are real KRX prices and broker-reported yields captured
on 2026-11-13 (same-day settlement), so they pin the market convention
rather than a textbook formula.
"""

from datetime import date

import pytest

from src.services import bond_math
from src.services.bond_math import BondSpec

SETTLE = date(2026, 11, 13)

# 국고03250-3512(25-11): 3.25% semi-annual coupon bond.
KTB_10Y = BondSpec(
    kind=bond_math.KIND_COUPON,
    coupon_rate=3.25,
    maturity_date=date(2035, 12, 10),
    issue_date=date(2025, 12, 10),
    interval_months=6,
)

# 국민주택1종21-11: 1.0% annually compounded, paid at maturity.
HOUSING = BondSpec(
    kind=bond_math.KIND_COMPOUND,
    coupon_rate=1.0,
    maturity_date=date(2026, 11, 30),
    issue_date=date(2021, 11, 30),
    interval_months=12,
)


@pytest.mark.parametrize(
    "price, broker_yield",
    [
        (9604.00, 3.956),  # last trade
        (9602.50, 3.958),  # best ask
        (9638.50, 3.909),  # second ask
        (9543.50, 4.039),  # best bid
    ],
)
def test_coupon_bond_yield_matches_broker(price, broker_yield):
    assert bond_math.yield_from_price(KTB_10Y, SETTLE, price) == pytest.approx(
        broker_yield, abs=0.0015
    )


@pytest.mark.parametrize(
    "price, broker_yield",
    [
        (10489.50, 4.196),
        (10479.40, 6.269),
        (10450.40, 12.244),
        (10450.00, 12.327),
        (10514.50, -0.918),  # priced above the maturity amount
    ],
)
def test_compound_bond_yield_matches_broker(price, broker_yield):
    assert bond_math.yield_from_price(HOUSING, SETTLE, price) == pytest.approx(
        broker_yield, abs=0.0015
    )


def test_compound_maturity_amount_is_truncated_to_won():
    # 10,000 * 1.01^5 = 10,510.10 -> 10,510
    assert bond_math.maturity_amount(HOUSING) == 10510


def test_price_and_yield_round_trip():
    for spec in (KTB_10Y, HOUSING):
        price = bond_math.price_from_yield(spec, SETTLE, 3.7)
        assert bond_math.yield_from_price(spec, SETTLE, price) == pytest.approx(
            3.7, abs=1e-6
        )


def test_coupon_schedule_is_anchored_to_maturity():
    previous, upcoming = bond_math.coupon_schedule(KTB_10Y, SETTLE)
    assert previous == date(2026, 6, 10)
    assert upcoming[0] == date(2026, 12, 10)
    assert upcoming[-1] == date(2035, 12, 10)
    assert len(upcoming) == 19


def test_coupon_schedule_first_period_starts_at_issue():
    previous, upcoming = bond_math.coupon_schedule(KTB_10Y, date(2026, 1, 15))
    assert previous == date(2025, 12, 10)
    assert upcoming[0] == date(2026, 6, 10)


def test_accrued_interest_is_pro_rata_within_the_period():
    # 156 of 183 days into a 162.5 coupon.
    assert bond_math.accrued_interest(KTB_10Y, SETTLE) == pytest.approx(
        162.5 * 156 / 183
    )


def test_par_bond_on_coupon_date_prices_at_par():
    spec = BondSpec(
        kind=bond_math.KIND_COUPON,
        coupon_rate=4.0,
        maturity_date=date(2030, 6, 10),
        issue_date=date(2025, 6, 10),
        interval_months=6,
    )
    assert bond_math.price_from_yield(spec, date(2026, 6, 10), 4.0) == pytest.approx(
        10000.0
    )


def test_discount_bond_under_a_year_uses_simple_interest():
    spec = BondSpec(
        kind=bond_math.KIND_DISCOUNT,
        coupon_rate=0.0,
        maturity_date=date(2027, 5, 13),
    )
    days = (spec.maturity_date - SETTLE).days
    assert bond_math.price_from_yield(spec, SETTLE, 3.0) == pytest.approx(
        10000.0 / (1 + 0.03 * days / 365)
    )


def test_risk_measures_are_consistent_with_repricing():
    risk = bond_math.risk_measures(KTB_10Y, SETTLE, 3.956)
    assert 7.0 < risk["modified_duration"] < 8.5
    assert risk["macaulay_duration"] > risk["modified_duration"]
    assert risk["convexity"] > 0
    base = bond_math.price_from_yield(KTB_10Y, SETTLE, 3.956)
    bumped = bond_math.price_from_yield(KTB_10Y, SETTLE, 3.966)
    assert base - bumped == pytest.approx(risk["dv01"], rel=1e-3)


def test_scenario_table_moves_against_yield():
    rows = bond_math.scenario_table(KTB_10Y, SETTLE, 3.956)
    by_shift = {row["shift_bp"]: row for row in rows}
    assert by_shift[-100]["price_change"] > 0 > by_shift[100]["price_change"]
    # Convexity: a fall in yield gains more than an equal rise loses.
    assert by_shift[-100]["price_change"] > -by_shift[100]["price_change"]


def test_after_tax_yield_is_below_pre_tax_yield():
    for spec, price in ((KTB_10Y, 9604.0), (HOUSING, 10489.5)):
        pre_tax = bond_math.yield_from_price(spec, SETTLE, price)
        post_tax = bond_math.after_tax_yield(spec, SETTLE, price)
        assert post_tax is not None and post_tax < pre_tax


def test_after_tax_yield_only_taxes_interest_earned_while_held():
    # Bought 17 days before maturity: tax applies to ~17 days of accrual,
    # not to all five years of compounded interest.
    pre_tax = bond_math.yield_from_price(HOUSING, SETTLE, 10489.5)
    post_tax = bond_math.after_tax_yield(HOUSING, SETTLE, 10489.5)
    assert pre_tax - post_tax < 0.2


def test_matured_bond_is_rejected():
    with pytest.raises(ValueError):
        bond_math.price_from_yield(KTB_10Y, date(2035, 12, 10), 3.0)


def test_yield_from_price_returns_none_when_unsolvable():
    assert bond_math.yield_from_price(KTB_10Y, SETTLE, 0) is None
    assert bond_math.yield_from_price(KTB_10Y, SETTLE, 10**9) is None
