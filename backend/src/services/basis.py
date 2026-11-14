"""Basis between listed futures and their underlying stock or index.

Three pieces:

* pairing - the futures master names each contract's underlying, so a
  stock or index code resolves to its futures months without any lookup
  table of our own;
* snapshot - spot against every listed month, with fair value and the
  carry the market price implies;
* history - daily closes of one contract joined to the underlying.

The spot used for the basis is, by default, the one behind the broker's
own futures analytics (theoretical price minus theoretical basis). It is
taken at the same instant as the futures price, whereas the stock quote
API keeps moving after the regular session with after-hours prints.
"""

from __future__ import annotations

import logging
import re
import statistics
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from ..integrations.futures_options_master import (
    futures_options_master_file_manager,
)
from ..integrations.kdevelopers import kdevelopers_client
from ..models.korean_analytics import (
    KoreanBasisContract,
    KoreanBasisHistory,
    KoreanBasisHistoryPoint,
    KoreanBasisSnapshot,
    KoreanBasisStats,
    KoreanBasisUnderlying,
)
from ..utils.concurrency import TTLCache, run_blocking

logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))

# Outright futures in each master, in order of preference when one
# underlying has several products (regular KOSPI200 before the mini).
FUTURES_INFO_TYPES: Dict[str, Tuple[str, ...]] = {
    "index": ("1", "3", "H", "7", "9", "B"),
    "stock": ("1", "3", "7"),
}
MARKET_DIV_CODE = {"index": "F", "stock": "JF"}
_EXPIRY_PATTERN = re.compile(r"F\s+(\d{6})")

# Flag a live quote that has drifted this far from the futures-synced spot.
SPOT_GAP_NOTE_PERCENT = 0.2
MAX_SNAPSHOT_MONTHS = 8
MAX_HISTORY_DAYS = 365


@dataclass
class FuturesContract:
    symbol: str
    name: str
    expiry_month: str


@dataclass
class BasisPair:
    code: str
    name: str
    kind: str  # "stock" or "index"
    contracts: List[FuturesContract] = field(default_factory=list)
    # Futures of the other products on the same underlying (the mini, when
    # ``contracts`` holds the regular KOSPI200 futures).
    alternates: List[FuturesContract] = field(default_factory=list)

    @property
    def market_div_code(self) -> str:
        return MARKET_DIV_CODE[self.kind]

    def contract_for_month(self, expiry_month: str) -> Optional[FuturesContract]:
        """The futures expiring in ``expiry_month``, main product first."""
        return next(
            (
                contract
                for contract in (*self.contracts, *self.alternates)
                if contract.expiry_month == expiry_month
            ),
            None,
        )


def to_number(value: Any) -> Optional[float]:
    """Parse a broker numeric string; blank or malformed gives None."""
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
    """Parse a price-like field where the broker sends 0 for 'no value'."""
    number = to_number(value)
    return number if number is not None and number > 0 else None


def synced_spot(output: Dict[str, Any]) -> Optional[float]:
    """Spot behind a futures quote: theoretical price less theoretical basis.

    It is taken at the same instant as the futures price, unlike the stock
    quote, which keeps moving with after-hours prints.
    """
    theoretical = positive(output.get("hts_thpr"))
    broker_basis = to_number(output.get("basis"))
    if theoretical is None or broker_basis is None:
        return None
    return theoretical - broker_basis


def master_version(master: Any) -> Tuple[Any, ...]:
    """Refresh today's futures/options masters and return a key that
    changes whenever the listed contracts may have."""
    stamps = []
    for market in ("stock", "index"):
        master.ensure_fresh(market)
        master_file = master.get_local_master_file(market)
        stamps.append(master_file.stat().st_mtime if master_file else None)
    return (datetime.now(KST).strftime("%Y%m"), *stamps)


def carry_days(last_trade_date: date, as_of: date) -> int:
    """Days of carry left: through final settlement, the day after the last
    trading day. This matches the broker's remaining-day count."""
    return (last_trade_date - as_of).days + 1


def annualised_carry(
    futures: Optional[float], spot: Optional[float], days: Optional[int]
) -> Optional[float]:
    """Simple annual rate (%) that turns ``spot`` into ``futures`` in ``days``."""
    if not futures or not spot or not days or days <= 0:
        return None
    return (futures / spot - 1.0) * 365.0 / days * 100.0


def fair_value(
    spot: float, rate_percent: float, days: int, dividend: float = 0.0
) -> float:
    """Cost-of-carry futures price: spot plus interest, less dividends."""
    return spot * (1.0 + rate_percent / 100.0 * days / 365.0) - dividend


def build_pairs(
    rows_by_market: Dict[str, List[Dict[str, Any]]], current_month: str
) -> Dict[str, BasisPair]:
    """Group unexpired outright futures by underlying code."""
    pairs: Dict[str, BasisPair] = {}
    for kind, rows in rows_by_market.items():
        preference = FUTURES_INFO_TYPES[kind]
        grouped: Dict[str, Dict[str, List[Tuple[str, FuturesContract]]]] = {}
        names: Dict[str, str] = {}
        for row in rows:
            info_type = str(row.get("info_type") or "").strip().upper()
            if info_type not in preference:
                continue
            code = str(row.get("underlying_short_code") or "").strip()
            symbol = str(row.get("short_code") or "").strip()
            name = str(row.get("name_kr") or "").strip()
            match = _EXPIRY_PATTERN.search(name)
            if not code or not symbol or not match:
                continue
            expiry_month = match.group(1)
            if expiry_month < current_month:
                continue
            names.setdefault(
                code, str(row.get("underlying_name_kr") or "").strip() or code
            )
            grouped.setdefault(code, {}).setdefault(info_type, []).append(
                (
                    str(row.get("month_class_code") or ""),
                    FuturesContract(symbol, " ".join(name.split()), expiry_month),
                )
            )

        def in_expiry_order(
            items: List[Tuple[str, FuturesContract]]
        ) -> List[FuturesContract]:
            return [
                contract
                for _, contract in sorted(
                    items, key=lambda item: (item[1].expiry_month, item[0])
                )
            ]

        for code, by_type in grouped.items():
            chosen = next(t for t in preference if t in by_type)
            alternates = [
                contract
                for info_type in preference
                if info_type in by_type and info_type != chosen
                for contract in in_expiry_order(by_type[info_type])
            ]
            pairs[code] = BasisPair(
                code,
                names[code],
                kind,
                in_expiry_order(by_type[chosen]),
                alternates,
            )
    return pairs


def basis_stats(values: List[float]) -> Optional[KoreanBasisStats]:
    """Summary of a basis series; the last value is the latest day."""
    if not values:
        return None
    latest = values[-1]
    mean = statistics.fmean(values)
    std = statistics.pstdev(values) if len(values) > 1 else 0.0
    return KoreanBasisStats(
        count=len(values),
        mean=mean,
        std=std,
        min=min(values),
        max=max(values),
        latest=latest,
        zscore=(latest - mean) / std if std > 0 else None,
        percentile=sum(1 for v in values if v <= latest) / len(values) * 100.0,
    )


class BasisService:
    """Resolves futures/underlying pairs and measures their basis."""

    def __init__(
        self,
        client: Any = kdevelopers_client,
        master: Any = futures_options_master_file_manager,
    ) -> None:
        self._client = client
        self._master = master
        self._pairs_key: Optional[Tuple[Any, ...]] = None
        self._pairs: Dict[str, BasisPair] = {}
        self._symbol_to_code: Dict[str, str] = {}
        self._snapshot_cache = TTLCache(ttl_seconds=3)
        self._history_cache = TTLCache(ttl_seconds=120)

    # ------------------------------------------------------------------
    # Pairing
    # ------------------------------------------------------------------

    def _load_pairs(self) -> Dict[str, BasisPair]:
        key = master_version(self._master)
        if key != self._pairs_key:
            self._pairs = build_pairs(
                {
                    market: self._master.get_cached_rows(market)
                    for market in ("stock", "index")
                },
                key[0],
            )
            self._symbol_to_code = {
                contract.symbol.upper(): pair.code
                for pair in self._pairs.values()
                for contract in pair.contracts
            }
            self._pairs_key = key
        return self._pairs

    def list_underlyings(
        self, query: Optional[str] = None
    ) -> List[KoreanBasisUnderlying]:
        """Underlyings with listed futures: indexes first, then by name."""
        needle = (query or "").strip().lower()
        pairs = [
            pair
            for pair in self._load_pairs().values()
            if not needle
            or needle in pair.code.lower()
            or needle in pair.name.lower()
        ]
        pairs.sort(key=lambda pair: (pair.kind != "index", pair.name))
        return [
            KoreanBasisUnderlying(
                code=pair.code,
                name=pair.name,
                kind=pair.kind,
                contract_count=len(pair.contracts),
                front_symbol=pair.contracts[0].symbol,
            )
            for pair in pairs
        ]

    def resolve(self, key: str) -> BasisPair:
        """Find a pair by underlying code, futures short code, or name."""
        pairs = self._load_pairs()
        text = (key or "").strip()
        if text in pairs:
            return pairs[text]
        code = self._symbol_to_code.get(text.upper())
        if code:
            return pairs[code]
        for pair in pairs.values():
            if pair.name == text:
                return pair
        raise LookupError(f"'{key}'에 해당하는 선물 기초자산을 찾지 못했습니다.")

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def live_spot(
        self, pair: BasisPair
    ) -> Tuple[Optional[float], Optional[float]]:
        """(price, change percent) from the stock or index quote API."""
        if pair.kind == "stock":
            quote = self._client.get_quote(pair.code)
            if quote is None:
                return None, None
            return quote.current_price or None, quote.change_percent
        output = self._client.get_index_price(pair.code) or {}
        return (
            positive(output.get("bstp_nmix_prpr")),
            to_number(output.get("bstp_nmix_prdy_ctrt")),
        )

    def quote_contract(
        self, pair: BasisPair, contract: FuturesContract
    ) -> Optional[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """(quote, best bid/ask) of one futures contract, or None."""
        raw = self._client.get_future_option_quote(
            contract.symbol, pair.market_div_code
        )
        output = (raw or {}).get("output1") or {}
        if not output:
            return None
        book = self._client.get_future_option_orderbook(
            contract.symbol, pair.market_div_code
        )
        return output, (book or {}).get("output2") or {}

    def days_to_expiry(self, output: Dict[str, Any]) -> Optional[int]:
        """Broker's remaining-day count, else calendar days to last trade.

        Futures and option quotes share these fields."""
        remaining = to_number(output.get("hts_rmnn_dynu"))
        if remaining is not None and remaining > 0:
            return int(remaining)
        last_trade = str(output.get("futs_last_tr_date") or "").strip()
        try:
            expiry = datetime.strptime(last_trade, "%Y%m%d").date()
        except ValueError:
            return None
        days = carry_days(expiry, datetime.now(KST).date())
        return days if days > 0 else None

    def snapshot(
        self,
        key: str,
        rate: Optional[float] = None,
        dividend: float = 0.0,
        months: int = 4,
    ) -> KoreanBasisSnapshot:
        """Compare spot with the nearest ``months`` futures contracts.

        Args:
            key: Underlying code, futures short code, or underlying name
            rate: Annual financing rate (%). When omitted, the broker's
                theoretical price is used as fair value.
            dividend: Dividends expected before expiry, in price units.
                Only applied together with ``rate``.
            months: How many contract months to quote
        """
        months = max(1, min(months, MAX_SNAPSHOT_MONTHS))
        cache_key = (key, rate, dividend, months)
        cached = self._snapshot_cache.get(cache_key)
        if cached is not None:
            return cached

        pair = self.resolve(key)
        live_spot, live_change = self.live_spot(pair)

        quoted: List[Tuple[FuturesContract, Dict[str, Any], Dict[str, Any]]] = []
        for contract in pair.contracts[:months]:
            quote = self.quote_contract(pair, contract)
            if quote is not None:
                quoted.append((contract, *quote))

        if not quoted:
            raise LookupError(
                f"{pair.name} 선물 시세를 가져오지 못했습니다."
            )

        futures_spot = next(
            (
                value
                for value in (synced_spot(output) for _, output, _ in quoted)
                if value
            ),
            None,
        )

        notes: List[str] = []
        if futures_spot:
            spot, spot_source = futures_spot, "futures_synced"
        else:
            spot, spot_source = live_spot, "live_quote"
            notes.append(
                "선물 시세에 이론가·베이시스가 없어 현물 현재가를 기준으로 "
                "계산했습니다."
            )

        spot_gap = None
        if futures_spot and live_spot:
            spot_gap = (live_spot - futures_spot) / futures_spot * 100.0
            if abs(spot_gap) >= SPOT_GAP_NOTE_PERCENT:
                notes.append(
                    f"현물 현재가({live_spot:,.2f})가 선물 기준 현물가"
                    f"({futures_spot:,.2f})와 {spot_gap:+.2f}% 다릅니다. "
                    "정규장 마감 후에는 현물 현재가에 시간외 가격이 반영되므로 "
                    "선물 기준 현물가로 베이시스를 계산했습니다."
                )
        if rate is not None and dividend:
            notes.append(
                f"예상 배당 {dividend:,.2f}을(를) 모든 월물의 이론가에서 "
                "차감했습니다."
            )

        contracts = [
            self.contract_row(contract, output, book, spot, rate, dividend)
            for contract, output, book in quoted
        ]
        result = KoreanBasisSnapshot(
            underlying_code=pair.code,
            underlying_name=pair.name,
            kind=pair.kind,
            as_of=datetime.now(KST),
            spot=spot,
            spot_source=spot_source if spot else None,
            live_spot=live_spot,
            live_spot_change_percent=live_change,
            spot_gap_percent=spot_gap,
            rate=rate,
            rate_source="user" if rate is not None else "broker",
            dividend=dividend if rate is not None else 0.0,
            contracts=contracts,
            notes=notes,
        )
        self._snapshot_cache.set(cache_key, result)
        return result

    def contract_row(
        self,
        contract: FuturesContract,
        output: Dict[str, Any],
        book: Dict[str, Any],
        spot: Optional[float],
        rate: Optional[float],
        dividend: float,
    ) -> KoreanBasisContract:
        price = positive(output.get("futs_prpr"))
        bid = positive(book.get("futs_bidp1"))
        ask = positive(book.get("futs_askp1"))
        mid = (bid + ask) / 2.0 if bid and ask else None
        days = self.days_to_expiry(output)
        broker_theoretical = positive(output.get("hts_thpr"))
        broker_basis = to_number(output.get("basis"))

        if rate is not None:
            carry_rate = rate
            theoretical = (
                fair_value(spot, rate, days, dividend) if spot and days else None
            )
        else:
            theoretical = broker_theoretical
            # The broker's own spot keeps its carry rate self-consistent.
            broker_spot = (
                broker_theoretical - broker_basis
                if broker_theoretical is not None and broker_basis is not None
                else spot
            )
            carry_rate = annualised_carry(broker_theoretical, broker_spot, days)

        volume = to_number(output.get("acml_vol"))
        open_interest = to_number(output.get("hts_otst_stpl_qty"))
        return KoreanBasisContract(
            symbol=contract.symbol,
            name=" ".join(str(output.get("hts_kor_isnm") or "").split())
            or contract.name,
            expiry_month=contract.expiry_month,
            last_trade_date=str(output.get("futs_last_tr_date") or "").strip()
            or None,
            days_to_expiry=days,
            price=price,
            bid=bid,
            ask=ask,
            mid=mid,
            volume=int(volume) if volume is not None else None,
            open_interest=int(open_interest) if open_interest is not None else None,
            basis=price - spot if price and spot else None,
            basis_percent=(price - spot) / spot * 100.0 if price and spot else None,
            mid_basis=mid - spot if mid and spot else None,
            implied_rate=annualised_carry(price, spot, days),
            theoretical_price=theoretical,
            theoretical_basis=theoretical - spot if theoretical and spot else None,
            discrepancy_percent=(price - theoretical) / theoretical * 100.0
            if price and theoretical
            else None,
            carry_rate=carry_rate,
            broker_theoretical_price=broker_theoretical,
            broker_basis=broker_basis,
            broker_market_basis=to_number(output.get("mrkt_basis")),
            broker_discrepancy_rate=to_number(output.get("dprt")),
        )

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def _futures_daily(
        self, symbol: str, market_div_code: str, start: str, end: str
    ) -> Dict[str, Tuple[float, int]]:
        """date -> (close, volume), paging back until ``start`` is covered."""
        closes: Dict[str, Tuple[float, int]] = {}
        cursor_end = end
        for _ in range(4):
            raw = self._client.get_future_option_daily_candles(
                symbol=symbol,
                market_div_code=market_div_code,
                period_code="D",
                input_date=start,
                input_date_to=cursor_end,
            )
            page = [
                row
                for row in (raw or {}).get("output2") or []
                if row.get("stck_bsop_date")
                and row["stck_bsop_date"] not in closes
            ]
            if not page:
                break
            for row in page:
                close = positive(row.get("futs_prpr"))
                if close is not None:
                    closes[row["stck_bsop_date"]] = (
                        close,
                        int(to_number(row.get("acml_vol")) or 0),
                    )
            oldest = min(row["stck_bsop_date"] for row in page)
            if oldest <= start or len(page) < 90:
                break
            cursor_end = (
                datetime.strptime(oldest, "%Y%m%d") - timedelta(days=1)
            ).strftime("%Y%m%d")
        return closes

    def _spot_daily(self, pair: BasisPair, start: str, end: str) -> Dict[str, float]:
        if pair.kind == "stock":
            rows = self._client.get_stock_daily_chart(pair.code, start, end)
            field_name = "stck_clpr"
        else:
            rows = self._client.get_index_daily_chart(pair.code, start, end)
            field_name = "bstp_nmix_prpr"
        closes = {}
        for row in rows:
            close = positive(row.get(field_name))
            if close is not None:
                closes[row["stck_bsop_date"]] = close
        return closes

    def history(
        self, key: str, symbol: Optional[str] = None, days: int = 90
    ) -> KoreanBasisHistory:
        """Daily basis of one contract (default: the front month).

        Days on which the futures did not trade are skipped, since their
        close is a stale carry-forward.
        """
        days = max(5, min(days, MAX_HISTORY_DAYS))
        cache_key = (key, symbol, days)
        cached = self._history_cache.get(cache_key)
        if cached is not None:
            return cached

        pair = self.resolve(key)
        wanted = (symbol or "").strip().upper()
        contract = next(
            (c for c in pair.contracts if c.symbol.upper() == wanted),
            pair.contracts[0],
        )
        today = datetime.now(KST).date()
        start = (today - timedelta(days=days)).strftime("%Y%m%d")
        end = today.strftime("%Y%m%d")

        futures = self._futures_daily(
            contract.symbol, pair.market_div_code, start, end
        )
        spots = self._spot_daily(pair, start, end)
        raw = self._client.get_future_option_quote(
            contract.symbol, pair.market_div_code
        )
        output = (raw or {}).get("output1") or {}
        notes: List[str] = []

        dates = sorted(d for d in futures if d in spots and futures[d][1] > 0)

        # The latest daily stock close can carry an after-hours print; the
        # spot behind the futures quote is the regular-session value.
        futures_spot = synced_spot(output)
        if dates and futures_spot:
            latest = dates[-1]
            same_session = futures[latest][0] == positive(output.get("futs_prpr"))
            drift = abs(spots[latest] - futures_spot) / futures_spot * 100.0
            if same_session and drift >= SPOT_GAP_NOTE_PERCENT:
                notes.append(
                    f"최근일({latest}) 현물 종가 {spots[latest]:,.2f}에 시간외 "
                    f"가격이 반영되어 선물 기준 현물가 {futures_spot:,.2f}로 "
                    "대체했습니다."
                )
                spots[latest] = futures_spot

        try:
            expiry = datetime.strptime(
                str(output.get("futs_last_tr_date") or ""), "%Y%m%d"
            ).date()
        except ValueError:
            expiry = None

        points = []
        for day in dates:
            spot = spots[day]
            close, volume = futures[day]
            remaining = (
                carry_days(expiry, datetime.strptime(day, "%Y%m%d").date())
                if expiry
                else None
            )
            points.append(
                KoreanBasisHistoryPoint(
                    date=day,
                    spot=spot,
                    futures=close,
                    basis=close - spot,
                    basis_percent=(close - spot) / spot * 100.0,
                    implied_rate=annualised_carry(close, spot, remaining),
                    volume=volume,
                )
            )

        skipped = len([d for d in futures if d in spots]) - len(dates)
        if skipped:
            notes.append(f"선물 거래가 없던 {skipped}일은 제외했습니다.")
        if pair.kind == "stock":
            notes.append(
                "선물 종가(15:45)와 현물 종가(15:30)는 시각이 달라 일별 "
                "베이시스에 장 마감 후 15분의 움직임이 섞입니다."
            )

        result = KoreanBasisHistory(
            underlying_code=pair.code,
            underlying_name=pair.name,
            kind=pair.kind,
            symbol=contract.symbol,
            contract_name=contract.name,
            points=points,
            stats=basis_stats([point.basis_percent for point in points]),
            notes=notes,
        )
        self._history_cache.set(cache_key, result)
        return result

    # ------------------------------------------------------------------
    # Async entry points
    # ------------------------------------------------------------------

    async def get_underlyings(
        self, query: Optional[str] = None
    ) -> List[KoreanBasisUnderlying]:
        return await run_blocking(self.list_underlyings, query)

    async def get_snapshot(
        self,
        key: str,
        rate: Optional[float] = None,
        dividend: float = 0.0,
        months: int = 4,
    ) -> KoreanBasisSnapshot:
        return await run_blocking(self.snapshot, key, rate, dividend, months)

    async def get_history(
        self, key: str, symbol: Optional[str] = None, days: int = 90
    ) -> KoreanBasisHistory:
        return await run_blocking(self.history, key, symbol, days)


basis_service = BasisService()
