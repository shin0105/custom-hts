"""Put-call parity: what the option market says the futures should cost.

Buying a call and selling a put at the same strike pays ``S_T - K`` at
expiry, exactly like a futures position entered at ``K``. The net premium
is paid today rather than at expiry, so the futures price the two options
imply together is

    synthetic = K + (call - put) * (1 + r * days / 365)

KOSPI200, KOSDAQ150 and single-stock options are European and expire with
the futures of the same month, so comparing ``synthetic`` with the listed
futures needs no dividend estimate: any gap is a pricing difference
between the two markets. Against spot, ``synthetic`` gives a second
reading of the basis.

The broker's option board stops at 100 rows from the highest strike and
often never reaches the money, so strikes are chosen from the master file
and quoted one by one.
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ..integrations.futures_options_master import (
    futures_options_master_file_manager,
)
from ..integrations.kdevelopers import kdevelopers_client
from ..models.korean_analytics import (
    KoreanOptionParity,
    KoreanOptionParityRow,
    KoreanOptionParitySummary,
)
from ..utils.concurrency import TTLCache, run_blocking
from .basis import (
    KST,
    BasisService,
    annualised_carry,
    basis_service,
    master_version,
    positive,
    synced_spot,
    to_number,
)

# Monthly options that share an expiry with listed futures. Mini and
# weekly options are left out: they repeat the same underlying, and the
# weeklies have no futures expiring with them.
OPTION_INFO_TYPES: Dict[str, Dict[str, str]] = {
    "index": {"5": "C", "6": "P", "J": "C", "K": "P"},
    "stock": {"5": "C", "6": "P"},
}
OPTION_MARKET_DIV_CODE = {"index": "O", "stock": "JO"}
_EXPIRY_PATTERN = re.compile(r"[CP]\s+(\d{6})\b")

# A quoted synthetic is trusted when its bid/ask band is at most this
# share of the strike; wider than that, the last trades say more.
MAX_QUOTE_BAND_PERCENT = 1.0
DEFAULT_STRIKES = 9
MIN_STRIKES = 3
MAX_STRIKES = 15

SOURCE_QUOTE = "quote"
SOURCE_LAST = "last"
SOURCE_WIDE_QUOTE = "wide_quote"
# Most to least reliable.
SOURCE_ORDER = (SOURCE_QUOTE, SOURCE_LAST, SOURCE_WIDE_QUOTE)


@dataclass(frozen=True)
class OptionStrike:
    """A strike with both its call and its put listed."""

    strike: float
    call_symbol: str
    put_symbol: str


@dataclass(frozen=True)
class LegQuote:
    """Last trade and best bid/ask of one option."""

    last: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume: int = 0

    @property
    def two_sided(self) -> bool:
        return bool(self.bid and self.ask and self.ask >= self.bid)

    @property
    def traded(self) -> bool:
        """Traded today, so ``last`` is not yesterday's close."""
        return bool(self.last and self.volume > 0)


@dataclass(frozen=True)
class FuturesQuote:
    """The listed futures the synthetic is compared with."""

    price: Optional[float] = None  # bid/ask midpoint, else last trade
    bid: Optional[float] = None
    ask: Optional[float] = None


# Underlying code -> expiry month -> strikes in ascending order.
OptionChains = Dict[str, Dict[str, List[OptionStrike]]]


def build_option_chains(
    rows_by_market: Dict[str, List[Dict[str, Any]]], current_month: str
) -> OptionChains:
    """Group unexpired monthly options into call/put pairs per strike."""
    legs: Dict[str, Dict[str, Dict[float, Dict[str, str]]]] = {}
    for kind, rows in rows_by_market.items():
        sides = OPTION_INFO_TYPES[kind]
        for row in rows:
            side = sides.get(str(row.get("info_type") or "").strip().upper())
            if side is None:
                continue
            code = str(row.get("underlying_short_code") or "").strip()
            symbol = str(row.get("short_code") or "").strip()
            strike = positive(row.get("strike_price"))
            match = _EXPIRY_PATTERN.search(str(row.get("name_kr") or ""))
            if not code or not symbol or strike is None or not match:
                continue
            if match.group(1) < current_month:
                continue
            (
                legs.setdefault(code, {})
                .setdefault(match.group(1), {})
                .setdefault(strike, {})
                .setdefault(side, symbol)
            )

    chains: OptionChains = {}
    for code, by_expiry in legs.items():
        for expiry, by_strike in by_expiry.items():
            strikes = [
                OptionStrike(strike, sides["C"], sides["P"])
                for strike, sides in sorted(by_strike.items())
                if "C" in sides and "P" in sides
            ]
            if strikes:
                chains.setdefault(code, {})[expiry] = strikes
    return chains


def select_strikes(
    strikes: List[OptionStrike], reference: float, count: int
) -> List[OptionStrike]:
    """The ``count`` strikes nearest ``reference``, in ascending order."""
    nearest = sorted(
        strikes, key=lambda item: (abs(item.strike - reference), item.strike)
    )[:count]
    return sorted(nearest, key=lambda item: item.strike)


def growth_factor(rate_percent: Optional[float], days: Optional[int]) -> float:
    """What 1 paid today is worth at expiry, at simple interest."""
    if not rate_percent or not days or days <= 0:
        return 1.0
    return 1.0 + rate_percent / 100.0 * days / 365.0


def synthetic_futures(
    strike: float, call: float, put: float, growth: float = 1.0
) -> float:
    """Futures price implied by a call and a put at the same strike."""
    return strike + (call - put) * growth


def leg_quote(book: Optional[Dict[str, Any]]) -> LegQuote:
    """Read one option's order book response."""
    summary = (book or {}).get("output1") or {}
    levels = (book or {}).get("output2") or {}
    return LegQuote(
        last=positive(summary.get("futs_prpr")),
        bid=positive(levels.get("futs_bidp1")),
        ask=positive(levels.get("futs_askp1")),
        volume=int(to_number(summary.get("acml_vol")) or 0),
    )


def parity_row(
    strike: OptionStrike,
    call: LegQuote,
    put: LegQuote,
    growth: float,
    futures: FuturesQuote,
    spot: Optional[float],
    days: Optional[int],
    is_atm: bool = False,
) -> KoreanOptionParityRow:
    """Synthetic futures at one strike, against the futures and spot.

    Executable prices need a two-sided book on both options: a lone bid
    is usually a resting order far from the market, and pairing it with
    the other option's quote gives a price nobody would trade at.
    """
    k = strike.strike
    sell = buy = mid = None
    if call.two_sided and put.two_sided:
        # Selling the synthetic sells the call at its bid and buys the put
        # at its ask; buying it does the opposite.
        sell = synthetic_futures(k, call.bid, put.ask, growth)
        buy = synthetic_futures(k, call.ask, put.bid, growth)
        mid = (sell + buy) / 2.0
    last = (
        synthetic_futures(k, call.last, put.last, growth)
        if call.traded and put.traded
        else None
    )
    tight = mid is not None and (buy - sell) <= k * MAX_QUOTE_BAND_PERCENT / 100.0

    if tight:
        synthetic, source = mid, SOURCE_QUOTE
    elif last is not None:
        synthetic, source = last, SOURCE_LAST
    elif mid is not None:
        synthetic, source = mid, SOURCE_WIDE_QUOTE
    else:
        synthetic, source = None, None

    return KoreanOptionParityRow(
        strike=k,
        is_atm=is_atm,
        call_symbol=strike.call_symbol,
        put_symbol=strike.put_symbol,
        call_last=call.last,
        call_bid=call.bid,
        call_ask=call.ask,
        call_volume=call.volume,
        put_last=put.last,
        put_bid=put.bid,
        put_ask=put.ask,
        put_volume=put.volume,
        synthetic=synthetic,
        source=source,
        synthetic_bid=sell,
        synthetic_ask=buy,
        conversion_edge=sell - futures.ask
        if sell is not None and futures.ask
        else None,
        reversal_edge=futures.bid - buy if buy is not None and futures.bid else None,
        **_comparison(synthetic, futures, spot, days),
    )


def _comparison(
    synthetic: Optional[float],
    futures: FuturesQuote,
    spot: Optional[float],
    days: Optional[int],
) -> Dict[str, Optional[float]]:
    """A synthetic price measured against the listed futures and spot."""
    against_futures = synthetic is not None and bool(futures.price)
    against_spot = synthetic is not None and bool(spot)
    return {
        "futures_gap": synthetic - futures.price if against_futures else None,
        "futures_gap_percent": (synthetic - futures.price) / futures.price * 100.0
        if against_futures
        else None,
        "spot_basis": synthetic - spot if against_spot else None,
        "spot_basis_percent": (synthetic - spot) / spot * 100.0
        if against_spot
        else None,
        "implied_rate": annualised_carry(synthetic, spot, days),
    }


def summarise(
    rows: List[KoreanOptionParityRow],
    futures: FuturesQuote,
    spot: Optional[float],
    days: Optional[int],
) -> KoreanOptionParitySummary:
    """Median synthetic over the most reliable rows, plus the best edges.

    The median shrugs off a strike whose last trades are hours apart.
    """
    synthetic, source, count = None, None, 0
    for candidate in SOURCE_ORDER:
        values = [
            row.synthetic
            for row in rows
            if row.source == candidate and row.synthetic is not None
        ]
        if values:
            synthetic, source, count = statistics.median(values), candidate, len(values)
            break

    def best(field: str) -> Tuple[Optional[float], Optional[float]]:
        candidates = [
            (getattr(row, field), row.strike)
            for row in rows
            if getattr(row, field) is not None
        ]
        return max(candidates) if candidates else (None, None)

    conversion_edge, conversion_strike = best("conversion_edge")
    reversal_edge, reversal_strike = best("reversal_edge")
    return KoreanOptionParitySummary(
        synthetic=synthetic,
        source=source,
        strike_count=count,
        conversion_edge=conversion_edge,
        conversion_strike=conversion_strike,
        reversal_edge=reversal_edge,
        reversal_strike=reversal_strike,
        **_comparison(synthetic, futures, spot, days),
    )


class OptionParityService:
    """Quotes the options around the money and prices the synthetic futures."""

    def __init__(
        self,
        client: Any = kdevelopers_client,
        master: Any = futures_options_master_file_manager,
        basis: BasisService = basis_service,
    ) -> None:
        self._client = client
        self._master = master
        self._basis = basis
        self._chains_key: Optional[Tuple[Any, ...]] = None
        self._chains: OptionChains = {}
        self._cache = TTLCache(ttl_seconds=5)

    def _load_chains(self) -> OptionChains:
        key = master_version(self._master)
        if key != self._chains_key:
            self._chains = build_option_chains(
                {
                    market: self._master.get_cached_rows(market)
                    for market in ("stock", "index")
                },
                key[0],
            )
            self._chains_key = key
        return self._chains

    def _leg(self, symbol: str, kind: str) -> LegQuote:
        return leg_quote(
            self._client.get_future_option_orderbook(
                symbol, OPTION_MARKET_DIV_CODE[kind]
            )
        )

    def parity(
        self,
        key: str,
        expiry: Optional[str] = None,
        rate: Optional[float] = None,
        strikes: int = DEFAULT_STRIKES,
    ) -> KoreanOptionParity:
        """Synthetic futures of one option month against futures and spot.

        Args:
            key: Underlying code, futures short code, or underlying name
            expiry: Option month (YYYYMM); the nearest one when omitted
            rate: Annual rate (%) for carrying the net premium to expiry.
                When omitted, the carry rate behind the broker's
                theoretical futures price is used.
            strikes: How many strikes around the money to quote
        """
        strikes = max(MIN_STRIKES, min(strikes, MAX_STRIKES))
        cache_key = (key, expiry, rate, strikes)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        pair = self._basis.resolve(key)
        chain = self._load_chains().get(pair.code, {})
        expiries = sorted(chain)
        if not expiries:
            return KoreanOptionParity(
                underlying_code=pair.code,
                underlying_name=pair.name,
                kind=pair.kind,
                as_of=datetime.now(KST),
            )
        if expiry and expiry not in chain:
            raise LookupError(
                f"{pair.name}에 {expiry} 만기 옵션이 상장되어 있지 않습니다."
            )
        expiry = expiry or expiries[0]
        notes: List[str] = []

        # The futures of the same month if there is one; otherwise the
        # front month still supplies the spot and a carry rate.
        matched = pair.contract_for_month(expiry)
        anchor = matched or pair.contracts[0]
        anchor_quote, anchor_book = self._basis.quote_contract(pair, anchor) or ({}, {})

        spot, spot_source = synced_spot(anchor_quote), "futures_synced"
        if not spot:
            spot, spot_source = self._basis.live_spot(pair)[0], "live_quote"

        futures = FuturesQuote()
        futures_last = None
        if matched is None:
            notes.append(
                f"{expiry} 만기 선물이 상장되어 있지 않아 현물과만 비교했습니다."
            )
        elif not anchor_quote:
            notes.append(
                f"{matched.name} 시세를 가져오지 못해 현물과만 비교했습니다."
            )
        else:
            futures_last = positive(anchor_quote.get("futs_prpr"))
            bid = positive(anchor_book.get("futs_bidp1"))
            ask = positive(anchor_book.get("futs_askp1"))
            futures = FuturesQuote(
                price=(bid + ask) / 2.0 if bid and ask and ask >= bid else futures_last,
                bid=bid,
                ask=ask,
            )

        reference = futures.price or spot
        if not reference:
            raise LookupError(f"{pair.name} 시세를 가져오지 못했습니다.")
        chosen = select_strikes(chain[expiry], reference, strikes)
        atm = min(chosen, key=lambda item: abs(item.strike - reference))

        # Days to expiry come from the futures of that month, or failing
        # that from one of the options, which carry the same fields.
        expiry_quote = anchor_quote if matched else {}
        if not expiry_quote:
            raw = self._client.get_future_option_quote(
                atm.call_symbol, OPTION_MARKET_DIV_CODE[pair.kind]
            )
            expiry_quote = (raw or {}).get("output1") or {}
        days = self._basis.days_to_expiry(expiry_quote)

        if rate is not None:
            discount_rate, rate_source = rate, "user"
        else:
            # Net of dividends, so it can understate the interest rate; a
            # negative carry is certainly not one.
            carry = annualised_carry(
                positive(anchor_quote.get("hts_thpr")),
                synced_spot(anchor_quote),
                self._basis.days_to_expiry(anchor_quote),
            )
            discount_rate = max(carry, 0.0) if carry is not None else None
            rate_source = "futures_carry" if discount_rate is not None else "none"
            if discount_rate is None:
                notes.append(
                    "금리 정보가 없어 옵션 순프리미엄을 이자 없이 계산했습니다."
                )
        growth = growth_factor(discount_rate, days)

        rows = [
            parity_row(
                strike,
                self._leg(strike.call_symbol, pair.kind),
                self._leg(strike.put_symbol, pair.kind),
                growth,
                futures,
                spot,
                days,
                is_atm=strike is atm,
            )
            for strike in chosen
        ]
        summary = summarise(rows, futures, spot, days)

        if summary.source == SOURCE_LAST:
            notes.append(
                "호가가 한쪽뿐이거나 넓어 콜·풋 체결가로 계산했습니다. 두 옵션의 "
                "체결 시각이 달라 오차가 있을 수 있습니다."
            )
        elif summary.source == SOURCE_WIDE_QUOTE:
            notes.append(
                "오늘 체결이 없고 호가 간격이 넓어 합성선물 가격은 참고용입니다."
            )
        elif summary.source is None:
            notes.append("콜과 풋이 함께 호가되거나 체결된 행사가가 없습니다.")

        result = KoreanOptionParity(
            underlying_code=pair.code,
            underlying_name=pair.name,
            kind=pair.kind,
            as_of=datetime.now(KST),
            expiries=expiries,
            expiry=expiry,
            last_trade_date=str(expiry_quote.get("futs_last_tr_date") or "").strip()
            or None,
            days_to_expiry=days,
            spot=spot,
            spot_source=spot_source if spot else None,
            futures_symbol=matched.symbol if matched else None,
            futures_name=matched.name if matched else None,
            futures_price=futures.price,
            futures_last=futures_last,
            futures_bid=futures.bid,
            futures_ask=futures.ask,
            rate=discount_rate,
            rate_source=rate_source,
            summary=summary,
            rows=rows,
            notes=notes,
        )
        self._cache.set(cache_key, result)
        return result

    async def get_parity(
        self,
        key: str,
        expiry: Optional[str] = None,
        rate: Optional[float] = None,
        strikes: int = DEFAULT_STRIKES,
    ) -> KoreanOptionParity:
        return await run_blocking(self.parity, key, expiry, rate, strikes)


option_parity_service = OptionParityService()
