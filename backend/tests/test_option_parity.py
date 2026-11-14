"""Tests for put-call parity against futures and spot.

Option books are trimmed copies of the KOSPI200 December 2026 chain as it
stood after the close on 2026-11-13: one strike quoted tightly on both
sides, others with a lone resting bid or a wide book.
"""

import pytest

from src.services.basis import BasisService
from src.services.option_parity import (
    FuturesQuote,
    LegQuote,
    OptionParityService,
    OptionStrike,
    build_option_chains,
    growth_factor,
    leg_quote,
    parity_row,
    select_strikes,
    summarise,
    synthetic_futures,
)


def master_row(info_type, short_code, name, strike, underlying, underlying_name):
    return {
        "info_type": info_type,
        "short_code": short_code,
        "name_kr": name,
        "strike_price": strike,
        "month_class_code": "1",
        "underlying_short_code": underlying,
        "underlying_name_kr": underlying_name,
    }


def kospi200_option(side, month, strike):
    info_type, prefix = ("5", "B") if side == "C" else ("6", "C")
    return master_row(
        info_type,
        f"{prefix}01{month[3:]}{int(strike)}",
        f"{side} {month}   {strike:.1f}",
        f"{strike:08.2f}",
        "2001",
        "KOSPI200",
    )


DECEMBER_STRIKES = (815.0, 817.5, 820.0, 822.5, 825.0, 827.5, 830.0)
INDEX_ROWS = [
    master_row("1", "A01612", "F 202612", "00000.00", "2001", "KOSPI200"),
    master_row("1", "A01703", "F 202703", "00000.00", "2001", "KOSPI200"),
    master_row("B", "A05612", "미니F 202612", "00000.00", "2001", "KOSPI200"),
    master_row("B", "A05701", "미니F 202701", "00000.00", "2001", "KOSPI200"),
    master_row("3", "A06612", "코스닥150F 202612", "00000.00", "3003", "KSQ150"),
    *[kospi200_option(side, "202612", k) for k in DECEMBER_STRIKES for side in "CP"],
    kospi200_option("C", "202701", 825.0),
    kospi200_option("P", "202701", 825.0),
    kospi200_option("C", "202702", 825.0),
    kospi200_option("P", "202702", 825.0),
    kospi200_option("C", "202610", 825.0),  # expired
    kospi200_option("P", "202610", 825.0),
    kospi200_option("C", "202612", 900.0),  # no matching put
    master_row("D", "B05612825", "미니C 202612   825.0", "00825.00", "2001", "KOSPI200"),
    master_row("L", "B09FLW825", "위클리C 2611W3   825.0", "00825.00", "2001", "KOSPI200"),
    master_row("J", "B06612001", "코스닥150C 202612 1,150", "01150.00", "3003", "KSQ150"),
    master_row("K", "C06612001", "코스닥150P 202612 1,150", "01150.00", "3003", "KSQ150"),
]
STOCK_ROWS = [
    master_row("1", "A11612", "삼성전자   F 202612 (  10)", "00000.00", "005930", "삼성전자"),
    master_row("5", "B11612092", "삼성전자   C 202612   210,000(  10)", "00210000", "005930", "삼성전자"),
    master_row("6", "C11612092", "삼성전자   P 202612   210,000(  10)", "00210000", "005930", "삼성전자"),
    master_row("1", "A56612", "NAVER      F 202612 (  10)", "00000.00", "035420", "NAVER"),
]


class FakeMaster:
    def ensure_fresh(self, market):
        return True

    def get_local_master_file(self, market):
        return None

    def get_cached_rows(self, market):
        return {"index": INDEX_ROWS, "stock": STOCK_ROWS}[market]


KOSPI200_FRONT = {
    "hts_kor_isnm": "F 202612",
    "futs_prpr": "822.35",
    "basis": "1.77",
    "hts_thpr": "826.55",
    "futs_last_tr_date": "20261210",
    "hts_rmnn_dynu": "28",
}
MINI_JANUARY = {
    "hts_kor_isnm": "미니F 202701",
    "futs_prpr": "815.66",
    "basis": "2.75",
    "hts_thpr": "827.53",
    "futs_last_tr_date": "20270114",
    "hts_rmnn_dynu": "63",
}


def book(last, bid, ask, volume):
    return {
        "output1": {"futs_prpr": last, "acml_vol": volume},
        "output2": {"futs_bidp1": bid, "futs_askp1": ask},
    }


# strike -> (call book, put book)
DECEMBER_BOOKS = {
    815.0: (book("48.90", "43.75", "50.85", "1"), book("38.50", "38.00", "0.00", "27")),
    817.5: (book("50.55", "1.79", "0.00", "0"), book("26.65", "37.25", "42.05", "1")),
    820.0: (book("43.65", "41.10", "46.05", "13"), book("40.65", "40.35", "41.75", "110")),
    822.5: (book("50.50", "1.77", "0.00", "1"), book("39.25", "40.40", "44.40", "0")),
    825.0: (book("41.00", "38.60", "46.45", "6"), book("43.40", "2.31", "0.00", "22")),
    827.5: (book("40.40", "1.75", "0.00", "82"), book("44.05", "42.40", "0.00", "46")),
    830.0: (book("39.15", "36.70", "40.80", "102"), book("45.40", "44.50", "57.80", "95")),
}


class FakeClient:
    def __init__(self):
        self.quotes = {"A01612": KOSPI200_FRONT, "A05701": MINI_JANUARY}
        self.futures_books = {
            "A01612": {"futs_bidp1": "822.35", "futs_askp1": "822.90"},
            "A05701": {"futs_bidp1": "810.28", "futs_askp1": "817.00"},
        }
        self.option_books = {}
        for strike, (call, put) in DECEMBER_BOOKS.items():
            self.option_books[f"B01612{int(strike)}"] = call
            self.option_books[f"C01612{int(strike)}"] = put
        self.option_quotes = {}
        self.book_calls = []

    def get_index_price(self, code):
        return {"bstp_nmix_prpr": "824.78", "bstp_nmix_prdy_ctrt": "-1.05"}

    def get_future_option_quote(self, symbol, market_div_code="F"):
        output = self.quotes.get(symbol) or self.option_quotes.get(symbol)
        return {"output1": output} if output else None

    def get_future_option_orderbook(self, symbol, market_div_code="F"):
        self.book_calls.append((symbol, market_div_code))
        if symbol in self.futures_books:
            return {"output2": self.futures_books[symbol]}
        return self.option_books.get(symbol)


@pytest.fixture
def client():
    return FakeClient()


@pytest.fixture
def service(client):
    master = FakeMaster()
    return OptionParityService(
        client=client, master=master, basis=BasisService(client=client, master=master)
    )


FUTURES = FuturesQuote(price=822.625, bid=822.35, ask=822.90)


def test_synthetic_futures_is_strike_plus_carried_net_premium():
    assert synthetic_futures(820, 43.575, 41.05) == pytest.approx(822.525)
    assert growth_factor(3.65, 100) == pytest.approx(1.01)
    assert synthetic_futures(800, 30, 10, growth=1.01) == pytest.approx(820.2)
    # No rate or no time left: the premium is taken as is.
    assert growth_factor(None, 28) == 1.0
    assert growth_factor(3.0, 0) == 1.0


def test_parity_holds_for_options_priced_off_the_same_forward():
    """Any call/put pair worth max(F - K, 0) and max(K - F, 0) plus the same
    time value recovers F, whatever the strike."""
    forward, time_value = 822.35, 12.5
    for strike in (780.0, 820.0, 860.0):
        call = max(forward - strike, 0.0) + time_value
        put = max(strike - forward, 0.0) + time_value
        assert synthetic_futures(strike, call, put) == pytest.approx(forward)


def test_build_option_chains_pairs_calls_with_puts_by_month():
    chains = build_option_chains({"index": INDEX_ROWS, "stock": STOCK_ROWS}, "202611")

    assert sorted(chains["2001"]) == ["202612", "202701", "202702"]  # 202610 expired
    december = chains["2001"]["202612"]
    assert [s.strike for s in december] == list(DECEMBER_STRIKES)  # 900 has no put
    assert december[2] == OptionStrike(820.0, "B01612820", "C01612820")
    # Mini and weekly options are not part of the chain.
    assert all(s.call_symbol.startswith("B016") for s in december)
    assert chains["3003"]["202612"] == [OptionStrike(1150.0, "B06612001", "C06612001")]
    assert chains["005930"]["202612"] == [
        OptionStrike(210000.0, "B11612092", "C11612092")
    ]
    assert "035420" not in chains


def test_select_strikes_takes_the_nearest_in_ascending_order():
    strikes = [OptionStrike(k, f"C{k}", f"P{k}") for k in DECEMBER_STRIKES]
    chosen = select_strikes(strikes, 822.625, 3)
    assert [s.strike for s in chosen] == [820.0, 822.5, 825.0]
    assert len(select_strikes(strikes, 822.625, 50)) == len(strikes)


def test_leg_quote_treats_zero_as_missing():
    leg = leg_quote(book("41.00", "2.31", "0.00", "22"))
    assert (leg.last, leg.bid, leg.ask, leg.volume) == (41.0, 2.31, None, 22)
    assert not leg.two_sided
    assert leg.traded
    assert not leg_quote(book("50.55", "1.79", "0.00", "0")).traded
    assert leg_quote(None) == LegQuote()


def test_tight_two_sided_quotes_give_an_executable_band():
    call, put = (leg_quote(b) for b in DECEMBER_BOOKS[820.0])
    row = parity_row(
        OptionStrike(820.0, "C", "P"), call, put, 1.0, FUTURES, 824.78, 28
    )

    assert row.source == "quote"
    assert row.synthetic == pytest.approx(822.525)
    assert row.synthetic_bid == pytest.approx(820 + 41.10 - 41.75)  # sell call, buy put
    assert row.synthetic_ask == pytest.approx(820 + 46.05 - 40.35)  # buy call, sell put
    assert row.futures_gap == pytest.approx(-0.10)
    assert row.spot_basis == pytest.approx(-2.255)
    # Selling the synthetic at 819.35 and buying futures at 822.90 loses money.
    assert row.conversion_edge == pytest.approx(819.35 - 822.90)
    assert row.reversal_edge == pytest.approx(822.35 - 825.70)
    assert row.implied_rate == pytest.approx(-3.564, abs=1e-3)


def test_a_wide_book_falls_back_to_last_trades():
    call, put = (leg_quote(b) for b in DECEMBER_BOOKS[830.0])
    row = parity_row(OptionStrike(830.0, "C", "P"), call, put, 1.0, FUTURES, 824.78, 28)

    assert row.source == "last"  # band of 17.4 points is over 1% of the strike
    assert row.synthetic == pytest.approx(830 + 39.15 - 45.40)
    assert row.synthetic_bid is not None  # still shown as executable prices


def test_a_lone_resting_bid_is_not_an_executable_price():
    call, put = (leg_quote(b) for b in DECEMBER_BOOKS[825.0])
    row = parity_row(OptionStrike(825.0, "C", "P"), call, put, 1.0, FUTURES, 824.78, 28)

    assert row.source == "last"
    assert row.synthetic == pytest.approx(822.6)
    assert row.synthetic_bid is None and row.synthetic_ask is None
    assert row.conversion_edge is None and row.reversal_edge is None


def test_an_untraded_one_sided_strike_has_no_synthetic():
    call, put = (leg_quote(b) for b in DECEMBER_BOOKS[817.5])
    row = parity_row(OptionStrike(817.5, "C", "P"), call, put, 1.0, FUTURES, 824.78, 28)
    assert row.synthetic is None and row.source is None
    assert row.futures_gap is None


def test_wide_quotes_without_trades_are_marked_as_such():
    row = parity_row(
        OptionStrike(830.0, "C", "P"),
        LegQuote(last=39.15, bid=30.0, ask=45.0, volume=0),
        LegQuote(last=45.40, bid=40.0, ask=60.0, volume=0),
        1.0,
        FUTURES,
        824.78,
        28,
    )
    assert row.source == "wide_quote"
    assert row.synthetic == pytest.approx(830 + 37.5 - 50.0)


def test_summary_prefers_quoted_rows_and_reports_the_best_edges():
    rows = [
        parity_row(
            OptionStrike(k, "C", "P"),
            leg_quote(DECEMBER_BOOKS[k][0]),
            leg_quote(DECEMBER_BOOKS[k][1]),
            1.0,
            FUTURES,
            824.78,
            28,
        )
        for k in DECEMBER_STRIKES
    ]
    summary = summarise(rows, FUTURES, 824.78, 28)

    assert summary.source == "quote"
    assert summary.strike_count == 1
    assert summary.synthetic == pytest.approx(822.525)
    assert summary.futures_gap_percent == pytest.approx(-0.01216, abs=1e-4)
    assert summary.conversion_strike == 820.0
    assert summary.conversion_edge == pytest.approx(-3.55)
    assert summary.reversal_strike == 820.0


def test_summary_takes_the_median_of_last_trades_when_nothing_is_quoted():
    rows = [
        parity_row(
            OptionStrike(k, "C", "P"),
            LegQuote(last=call, volume=10),
            LegQuote(last=put, volume=10),
            1.0,
            FuturesQuote(),
            824.78,
            28,
        )
        for k, call, put in (
            (815.0, 48.90, 38.50),  # 825.40
            (825.0, 41.00, 43.40),  # 822.60
            (830.0, 39.15, 45.40),  # 823.75
            (805.0, 71.70, 34.00),  # 842.70: a stale call print
        )
    ]
    summary = summarise(rows, FuturesQuote(), 824.78, 28)

    assert summary.source == "last"
    assert summary.strike_count == 4
    assert summary.synthetic == pytest.approx((823.75 + 825.40) / 2)
    assert summary.futures_gap is None  # no futures to compare with
    assert summary.conversion_edge is None
    assert summarise([], FuturesQuote(), 824.78, 28).synthetic is None


def test_parity_compares_the_nearest_month_with_its_futures(service, client):
    result = service.parity("2001", strikes=7)

    assert result.expiries == ["202612", "202701", "202702"]
    assert result.expiry == "202612"
    assert result.futures_symbol == "A01612"
    assert result.futures_price == pytest.approx(822.625)  # bid/ask midpoint
    assert result.spot == pytest.approx(824.78)
    assert result.spot_source == "futures_synced"
    assert result.days_to_expiry == 28
    assert result.last_trade_date == "20261210"
    assert [row.strike for row in result.rows] == list(DECEMBER_STRIKES)
    assert [row.strike for row in result.rows if row.is_atm] == [822.5]
    # Options are quoted on the index option market, not the futures one.
    assert ("B01612820", "O") in client.book_calls

    # Net premium is carried at the rate behind the broker's fair value.
    assert result.rate_source == "futures_carry"
    assert result.rate == pytest.approx(2.7975, abs=1e-4)
    growth = 1 + result.rate / 100 * 28 / 365
    assert result.summary.synthetic == pytest.approx(820 + 2.525 * growth)
    assert result.summary.futures_gap == pytest.approx(-0.0946, abs=1e-4)
    assert result.summary.spot_basis == pytest.approx(-2.2496, abs=1e-4)


def test_parity_uses_the_given_rate_and_strike_count(service):
    result = service.parity("2001", rate=0.0, strikes=3)

    assert result.rate_source == "user"
    assert result.rate == 0.0
    assert [row.strike for row in result.rows] == [820.0, 822.5, 825.0]
    assert result.summary.synthetic == pytest.approx(822.525)
    assert result.notes == []


def test_parity_without_any_rate_takes_the_premium_as_is(service, client):
    client.quotes["A01612"] = {**KOSPI200_FRONT, "hts_thpr": "0", "basis": ""}
    result = service.parity("2001", strikes=3)

    assert result.rate is None
    assert result.rate_source == "none"
    assert result.spot_source == "live_quote"
    assert result.spot == pytest.approx(824.78)
    assert result.summary.synthetic == pytest.approx(822.525)
    assert any("이자 없이" in note for note in result.notes)


def test_parity_matches_an_off_quarter_month_with_the_mini_futures(service, client):
    client.option_books["B01701825"] = book("60.00", "58.00", "60.00", "5")
    client.option_books["C01701825"] = book("68.00", "67.00", "69.00", "5")
    result = service.parity("2001", expiry="202701")

    assert result.futures_symbol == "A05701"
    assert result.days_to_expiry == 63
    assert result.spot == pytest.approx(827.53 - 2.75)
    assert result.futures_price == pytest.approx(813.64)
    assert result.rows[0].source == "quote"


def test_parity_without_a_futures_month_compares_with_spot_only(service, client):
    client.option_books["B01702825"] = book("70.00", "0", "0", "3")
    client.option_books["C01702825"] = book("71.00", "0", "0", "4")
    client.option_quotes["B01702825"] = {
        "futs_last_tr_date": "20270211",
        "hts_rmnn_dynu": "91",
    }
    result = service.parity("2001", expiry="202702")

    assert result.futures_symbol is None
    assert result.futures_price is None
    assert result.days_to_expiry == 91  # read from the option itself
    assert result.last_trade_date == "20270211"
    assert result.spot == pytest.approx(824.78)  # from the front futures
    assert result.summary.source == "last"
    assert result.summary.futures_gap is None
    assert result.summary.spot_basis is not None
    assert any("현물과만" in note for note in result.notes)
    assert any("체결가" in note for note in result.notes)


def test_parity_for_an_underlying_without_options_is_empty(service):
    result = service.parity("035420")

    assert result.underlying_name == "NAVER"
    assert result.expiries == []
    assert result.rows == []
    assert result.summary is None


def test_parity_rejects_an_unlisted_month_or_unknown_underlying(service):
    with pytest.raises(LookupError):
        service.parity("2001", expiry="203001")
    with pytest.raises(LookupError):
        service.parity("999999")


def test_parity_reports_when_no_strike_can_be_priced(service, client):
    client.option_books.clear()
    result = service.parity("2001", strikes=3)

    assert result.summary.synthetic is None
    assert all(row.synthetic is None for row in result.rows)
    assert any("없습니다" in note for note in result.notes)
