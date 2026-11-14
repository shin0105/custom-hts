"""Yield, risk and relative-value analytics for KRX-listed bonds.

The broker gives a yield only for today's last trade. This service turns
the bond's terms into a ``BondSpec`` so yields can be computed for any
price (bids, asks, past closes), then compares the market yield with the
pricing agencies' valuation yield - an independent benchmark, unlike
discounting at the market's own yield.
"""

from __future__ import annotations

import logging
import statistics
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from ..integrations.kdevelopers import kdevelopers_client
from ..models.korean_analytics import (
    KoreanBondAgencyValuation,
    KoreanBondAnalytics,
    KoreanBondOrderbookLevel,
    KoreanBondScenario,
    KoreanBondYieldHistory,
    KoreanBondYieldPoint,
)
from ..utils.concurrency import TTLCache, run_blocking
from . import bond_math
from .bond_math import BondSpec

logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))

# bond_int_dfrm_mthd_cd -> kind handled by bond_math
KIND_BY_METHOD = {
    "01": bond_math.KIND_DISCOUNT,
    "02": bond_math.KIND_COMPOUND,
    "03": bond_math.KIND_COUPON,
    "06": bond_math.KIND_SIMPLE,
}
KIND_LABEL = {
    bond_math.KIND_COUPON: "이표채",
    bond_math.KIND_COMPOUND: "복리채",
    bond_math.KIND_SIMPLE: "단리채",
    bond_math.KIND_DISCOUNT: "할인채",
}
UNSUPPORTED_METHOD = {
    "04": "금리연동 이표채",
    "05": "변동금리 이표채",
    "07": "분할상환채",
    "09": "복5단2",
    "29": "변동금리 채권",
}
# (label, price field, yield field, credit rating field)
AGENCY_FIELDS = (
    ("KIS", "kis_unpr", "kis_erng_rt", "kis_crdt_grad_text"),
    ("KBP", "kbp_unpr", "kbp_erng_rt", "kbp_crdt_grad_text"),
    ("NICE", "nice_evlu_unpr", "nice_evlu_erng_rt", "nice_crdt_grad_text"),
    ("FnP", "fnp_unpr", "fnp_erng_rt", "fnp_crdt_grad_text"),
)

WIDE_SPREAD_BP = 50.0
YIELD_MISMATCH = 0.01  # percentage points
MAX_HISTORY_DAYS = 365


def to_number(value: Any) -> Optional[float]:
    if value is None:
        return None
    text = str(value).replace(",", "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def positive(value: Any) -> Optional[float]:
    """Prices and quantities: the broker sends 0 for 'no value'."""
    number = to_number(value)
    return number if number is not None and number > 0 else None


def nonzero(value: Any) -> Optional[float]:
    """Yields: 0.000 means 'not available', but negatives are real."""
    number = to_number(value)
    return number if number else None


def parse_yyyymmdd(value: Any) -> Optional[date]:
    text = str(value or "").strip()
    if len(text) != 8 or not text.isdigit() or text == "00000000":
        return None
    try:
        return datetime.strptime(text, "%Y%m%d").date()
    except ValueError:
        return None


def settlement_date(now: Optional[datetime] = None) -> date:
    """KRX bonds settle same-day; weekends roll back to Friday so yields
    match the quotes left over from the last session."""
    day = (now or datetime.now(KST)).date()
    while day.weekday() >= 5:
        day -= timedelta(days=1)
    return day


def spec_from_info(
    info: Dict[str, Any],
) -> Tuple[Optional[BondSpec], Optional[str], List[str]]:
    """Build a BondSpec from the broker's bond basic info.

    Returns:
        (spec, reason, warnings). ``spec`` is None, with a ``reason``,
        for structures a fixed cash-flow yield does not describe.
    """
    warnings: List[str] = []
    method = str(info.get("bond_int_dfrm_mthd_cd") or "").strip()
    maturity = parse_yyyymmdd(info.get("rdpt_dt"))
    issue = parse_yyyymmdd(info.get("issu_dt"))

    if maturity is None:
        return None, "만기일 정보가 없습니다.", warnings
    if method in UNSUPPORTED_METHOD:
        return None, f"{UNSUPPORTED_METHOD[method]}는 수익률 계산을 지원하지 않습니다.", warnings
    if str(info.get("ksd_prcm_lnkg_gvbd_yn") or "").strip().upper() == "Y":
        return None, "물가연동국고채는 수익률 계산을 지원하지 않습니다.", warnings
    if str(info.get("csbd_yn") or "").strip().upper() == "Y":
        return None, "영구채는 만기수익률을 계산할 수 없습니다.", warnings
    if (to_number(info.get("splt_rdpt_rcnt")) or 0) > 0:
        return None, "분할상환채는 수익률 계산을 지원하지 않습니다.", warnings
    if (to_number(info.get("frn_intr")) or 0) != 0:
        return None, "변동금리채(FRN)는 수익률 계산을 지원하지 않습니다.", warnings

    kind = KIND_BY_METHOD.get(method)
    if kind is None:
        return None, f"이자지급방법 코드 '{method or '-'}'는 지원하지 않습니다.", warnings

    coupon_rate = to_number(info.get("ksd_rcvg_bond_srfc_inrt")) or 0.0
    interval = int(to_number(info.get("int_caltm_mcnt")) or 0)
    if kind == bond_math.KIND_DISCOUNT:
        coupon_rate = 0.0
    if kind == bond_math.KIND_COUPON and interval <= 0:
        return None, "이자지급주기 정보가 없습니다.", warnings
    if interval <= 0:
        interval = 12
    if kind in (bond_math.KIND_COMPOUND, bond_math.KIND_SIMPLE) and issue is None:
        return None, "발행일 정보가 없어 만기상환금액을 계산할 수 없습니다.", warnings

    redemption = (
        positive(info.get("bond_expd_rdpt_rt"))
        or positive(info.get("expd_rdpt_rt"))
        or 100.0
    )

    if str(info.get("ksd_opcb_yn") or "").strip().upper() == "Y":
        warnings.append("옵션부사채: 콜·풋 행사는 반영하지 않은 만기 기준 수익률입니다.")
    if str(info.get("ksd_cbbw_dvsn_cd") or "").strip() not in ("", "9"):
        warnings.append("주식관련사채: 전환·신주인수권 가치는 반영하지 않았습니다.")
    if str(info.get("ksd_sodn_yn") or "").strip().upper() == "Y":
        warnings.append("후순위채권입니다.")

    spec = BondSpec(
        kind=kind,
        coupon_rate=coupon_rate,
        maturity_date=maturity,
        issue_date=issue,
        interval_months=interval,
        redemption_ratio=redemption,
    )
    return spec, None, warnings


def latest_agency_row(rows: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Most recent agency valuation that carries an average yield."""
    dated = [
        row
        for row in rows
        if row.get("evlu_dt") and nonzero(row.get("avg_evlu_erng_rt")) is not None
    ]
    return max(dated, key=lambda row: row["evlu_dt"]) if dated else None


class BondAnalyticsService:
    """Builds yield analytics from the broker's bond APIs."""

    def __init__(self, client: Any = kdevelopers_client) -> None:
        self._client = client
        self._analytics_cache = TTLCache(ttl_seconds=5)
        self._history_cache = TTLCache(ttl_seconds=300)

    def analytics(
        self, pdno: str, now: Optional[datetime] = None
    ) -> KoreanBondAnalytics:
        cached = self._analytics_cache.get(pdno) if now is None else None
        if cached is not None:
            return cached

        info = self._client.get_bond_basic_info(pdno) or {}
        price = self._client.get_bond_price(pdno) or {}
        asking = self._client.get_bond_asking_price(pdno) or {}
        # An unknown code comes back as a payload of blanks, not an error.
        if not str(info.get("ksd_bond_item_name") or "").strip() and not positive(
            price.get("bond_prpr")
        ):
            raise LookupError(f"채권 {pdno} 정보를 찾지 못했습니다.")

        current = now or datetime.now(KST)
        settle = settlement_date(current)
        spec, reason, notes = spec_from_info(info)
        if spec is not None and settle >= spec.maturity_date:
            spec, reason = None, "만기가 지난 채권입니다."

        def ytm(value: Optional[float]) -> Optional[float]:
            if spec is None or not value:
                return None
            return bond_math.yield_from_price(spec, settle, value)

        last_price = positive(price.get("bond_prpr"))
        volume = int(to_number(price.get("acml_vol")) or 0)
        traded_today = volume > 0
        broker_yield = nonzero(price.get("ernn_rate"))
        computed_yield = ytm(last_price)

        levels: List[KoreanBondOrderbookLevel] = []
        for level in range(1, 6):
            ask_price = positive(asking.get(f"bond_askp{level}"))
            bid_price = positive(asking.get(f"bond_bidp{level}"))
            if ask_price is None and bid_price is None:
                continue
            ask_quantity = to_number(asking.get(f"askp_rsqn{level}"))
            bid_quantity = to_number(asking.get(f"bidp_rsqn{level}"))
            levels.append(
                KoreanBondOrderbookLevel(
                    level=level,
                    ask_price=ask_price,
                    ask_quantity=int(ask_quantity) if ask_price and ask_quantity else None,
                    ask_yield=(
                        nonzero(asking.get(f"seln_ernn_rate{level}"))
                        or ytm(ask_price)
                    )
                    if ask_price
                    else None,
                    bid_price=bid_price,
                    bid_quantity=int(bid_quantity) if bid_price and bid_quantity else None,
                    bid_yield=(
                        nonzero(asking.get(f"shnu_ernn_rate{level}"))
                        or ytm(bid_price)
                    )
                    if bid_price
                    else None,
                )
            )
        best = next((lv for lv in levels if lv.level == 1), None)
        best_bid_yield = best.bid_yield if best else None
        best_ask_yield = best.ask_yield if best else None
        spread_bp = (
            (best_bid_yield - best_ask_yield) * 100.0
            if best_bid_yield is not None and best_ask_yield is not None
            else None
        )

        agency_rows = self._client.get_bond_avg_unit(
            pdno,
            (settle - timedelta(days=10)).strftime("%Y%m%d"),
            current.strftime("%Y%m%d"),
            max_pages=1,
        )
        agency = latest_agency_row(agency_rows)
        agency_yield = nonzero(agency.get("avg_evlu_erng_rt")) if agency else None

        # Pick the yield everything else is measured from.
        reference_yield: Optional[float] = None
        reference_source: Optional[str] = None
        traded_yield = computed_yield if computed_yield is not None else broker_yield
        if traded_today and traded_yield is not None:
            reference_yield = traded_yield
            reference_source = "last_trade"
        elif best_bid_yield is not None and best_ask_yield is not None:
            reference_yield = (best_bid_yield + best_ask_yield) / 2.0
            reference_source = "quote_mid"
            notes.append(
                "오늘 체결이 없어 최우선 매수·매도 호가 수익률의 중간값을 "
                "기준으로 계산했습니다."
            )
        elif computed_yield is not None:
            reference_yield = computed_yield
            reference_source = "last_price"
            notes.append(
                "오늘 체결과 양방향 호가가 없어 직전 체결가 기준으로 "
                "계산했습니다."
            )
        elif agency_yield is not None and spec is not None:
            reference_yield = agency_yield
            reference_source = "agency"
            notes.append("시장 가격이 없어 민평 수익률 기준으로 계산했습니다.")

        if (
            traded_today
            and broker_yield is not None
            and computed_yield is not None
            and abs(broker_yield - computed_yield) > YIELD_MISMATCH
        ):
            notes.append(
                f"증권사 수익률({broker_yield:.3f}%)과 자체 계산"
                f"({computed_yield:.3f}%)이 다릅니다. 채권 조건을 확인하세요."
            )
        if spread_bp is not None and spread_bp >= WIDE_SPREAD_BP:
            notes.append(
                f"호가 스프레드가 {spread_bp:.0f}bp로 넓어 체결 수익률이 "
                "호가에 크게 좌우됩니다."
            )
        if reason:
            notes.insert(0, reason)

        result = KoreanBondAnalytics(
            pdno=pdno,
            name=(
                str(info.get("ksd_bond_item_name") or "").strip()
                or str(price.get("hts_kor_isnm") or "").strip()
                or pdno
            ),
            as_of=current,
            settlement_date=settle.strftime("%Y%m%d"),
            kind=spec.kind if spec else None,
            kind_label=KIND_LABEL.get(spec.kind) if spec else None,
            supported=spec is not None,
            unsupported_reason=reason,
            coupon_rate=to_number(info.get("ksd_rcvg_bond_srfc_inrt")),
            interval_months=spec.interval_months if spec else None,
            issue_date=str(info.get("issu_dt") or "").strip() or None,
            maturity_date=str(info.get("rdpt_dt") or "").strip() or None,
            last_price=last_price,
            last_yield=broker_yield,
            computed_yield=computed_yield,
            traded_today=traded_today,
            volume=volume,
            day_open_yield=nonzero(price.get("oprc_ert")),
            day_high_price_yield=nonzero(price.get("hgpr_ert")),
            day_low_price_yield=nonzero(price.get("lwpr_ert")),
            best_bid_price=best.bid_price if best else None,
            best_bid_yield=best_bid_yield,
            best_ask_price=best.ask_price if best else None,
            best_ask_yield=best_ask_yield,
            bid_ask_spread_bp=spread_bp,
            levels=levels,
            reference_yield=reference_yield,
            reference_source=reference_source,
            notes=notes,
        )

        if agency is not None:
            result.agency_date = agency.get("evlu_dt")
            result.agency_yield = agency_yield
            result.agency_price = positive(agency.get("avg_evlu_unpr"))
            result.agencies = [
                KoreanBondAgencyValuation(
                    agency=label,
                    price=positive(agency.get(price_field)),
                    yield_rate=nonzero(agency.get(yield_field)),
                    credit_rating=str(agency.get(rating_field) or "").strip() or None,
                )
                for label, price_field, yield_field, rating_field in AGENCY_FIELDS
            ]
            if reference_yield is not None and reference_source != "agency":
                result.agency_spread_bp = (reference_yield - agency_yield) * 100.0

        if spec is not None:
            result.remaining_years = (spec.maturity_date - settle).days / 365.0
            if spec.kind == bond_math.KIND_COUPON:
                _, upcoming = bond_math.coupon_schedule(spec, settle)
                result.next_coupon_date = upcoming[0].strftime("%Y%m%d")

        if spec is not None and reference_yield is not None:
            try:
                self._add_risk(result, spec, settle, reference_yield, agency_yield)
            except ValueError as error:
                result.notes.append(f"위험지표를 계산하지 못했습니다: {error}")

        if now is None:
            self._analytics_cache.set(pdno, result)
        return result

    def _add_risk(
        self,
        result: KoreanBondAnalytics,
        spec: BondSpec,
        settle: date,
        reference_yield: float,
        agency_yield: Optional[float],
    ) -> None:
        reference_price = bond_math.price_from_yield(spec, settle, reference_yield)
        accrued = bond_math.accrued_interest(spec, settle)
        risk = bond_math.risk_measures(spec, settle, reference_yield)

        result.reference_price = reference_price
        result.accrued_interest = accrued
        if spec.kind == bond_math.KIND_COUPON:
            result.clean_price = reference_price - accrued
        result.after_tax_yield = bond_math.after_tax_yield(
            spec, settle, reference_price
        )
        result.tax_rate = bond_math.DEFAULT_TAX_RATE * 100.0
        result.macaulay_duration = risk["macaulay_duration"]
        result.modified_duration = risk["modified_duration"]
        result.convexity = risk["convexity"]
        result.dv01 = risk["dv01"]
        result.scenarios = [
            KoreanBondScenario(**row)
            for row in bond_math.scenario_table(spec, settle, reference_yield)
        ]
        if agency_yield is not None and result.reference_source != "agency":
            result.agency_implied_price = bond_math.price_from_yield(
                spec, settle, agency_yield
            )
            result.price_vs_agency = reference_price - result.agency_implied_price

    def yield_history(self, pdno: str, days: int = 120) -> KoreanBondYieldHistory:
        """Daily market yield (from closes) against the agency yield."""
        days = max(10, min(days, MAX_HISTORY_DAYS))
        cache_key = (pdno, days)
        cached = self._history_cache.get(cache_key)
        if cached is not None:
            return cached

        info = self._client.get_bond_basic_info(pdno) or {}
        candles = self._client.get_bond_daily_price(pdno) or []
        if not str(info.get("ksd_bond_item_name") or "").strip() and not candles:
            raise LookupError(f"채권 {pdno} 정보를 찾지 못했습니다.")

        spec, reason, notes = spec_from_info(info)
        today = datetime.now(KST).date()
        start = (today - timedelta(days=days)).strftime("%Y%m%d")
        end = today.strftime("%Y%m%d")
        agency_rows = self._client.get_bond_avg_unit(
            pdno, start, end, max_pages=days // 20 + 2
        )

        points: Dict[str, KoreanBondYieldPoint] = {}
        for candle in candles:
            if not start <= candle.date <= end or not candle.close:
                continue
            point = KoreanBondYieldPoint(
                date=candle.date, close=candle.close, volume=candle.volume
            )
            day = parse_yyyymmdd(candle.date)
            # A close without volume is carried forward, so its yield would
            # drift for no reason other than the passing days.
            if spec and day and candle.volume > 0 and day < spec.maturity_date:
                point.market_yield = bond_math.yield_from_price(
                    spec, day, candle.close
                )
            points[candle.date] = point

        for row in agency_rows:
            day = parse_yyyymmdd(row.get("evlu_dt"))
            agency_yield = nonzero(row.get("avg_evlu_erng_rt"))
            if day is None or day.weekday() >= 5 or agency_yield is None:
                continue
            key = row["evlu_dt"]
            point = points.setdefault(key, KoreanBondYieldPoint(date=key))
            point.agency_yield = agency_yield
            point.agency_price = positive(row.get("avg_evlu_unpr"))

        ordered = [points[key] for key in sorted(points)]
        spreads = []
        for point in ordered:
            if point.market_yield is not None and point.agency_yield is not None:
                point.spread_bp = (point.market_yield - point.agency_yield) * 100.0
                spreads.append(point.spread_bp)

        traded_days = sum(1 for p in ordered if p.market_yield is not None)
        if reason:
            notes.insert(0, reason)
        elif traded_days:
            notes.append(
                f"거래가 있던 {traded_days}일만 시장수익률을 계산했습니다."
            )
        else:
            notes.append("조회 기간에 거래가 없어 시장수익률이 없습니다.")

        result = KoreanBondYieldHistory(
            pdno=pdno,
            name=str(info.get("ksd_bond_item_name") or "").strip() or pdno,
            points=ordered,
            traded_days=traded_days,
            average_spread_bp=statistics.fmean(spreads) if spreads else None,
            latest_spread_bp=spreads[-1] if spreads else None,
            notes=notes,
        )
        self._history_cache.set(cache_key, result)
        return result

    async def get_analytics(self, pdno: str) -> KoreanBondAnalytics:
        return await run_blocking(self.analytics, pdno)

    async def get_yield_history(
        self, pdno: str, days: int = 120
    ) -> KoreanBondYieldHistory:
        return await run_blocking(self.yield_history, pdno, days)


bond_analytics_service = BondAnalyticsService()
