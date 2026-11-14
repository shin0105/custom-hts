"""Tests for futures/underlying pairing and basis calculations.

Broker payloads are trimmed copies of real responses captured on
2026-11-13/14, including the after-hours case where the stock quote
(209,000) had drifted from the regular-session close (206,000) that the
futures were priced against.
"""

from datetime import date
from types import SimpleNamespace

import pytest

from src.services.basis import (
    BasisService,
    annualised_carry,
    basis_stats,
    build_pairs,
    carry_days,
    fair_value,
)


def master_row(info_type, short_code, name, underlying, underlying_name, month="1"):
    return {
        "info_type": info_type,
        "short_code": short_code,
        "name_kr": name,
        "month_class_code": month,
        "underlying_short_code": underlying,
        "underlying_name_kr": underlying_name,
    }


INDEX_ROWS = [
    master_row("B", "A05612", "미니F 202612", "2001", "KOSPI200"),
    master_row("1", "A01703", "F 202703", "2001", "KOSPI200", "2"),
    master_row("1", "A01612", "F 202612", "2001", "KOSPI200", "1"),
    master_row("2", "A016S3", "SP 2612-2703", "2001", "KOSPI200"),
    master_row("5", "B0161Z", "C 202612   180.0", "2001", "KOSPI200"),
    master_row("3", "A06612", "코스닥150F 202612", "3003", "KSQ150"),
]
STOCK_ROWS = [
    master_row("1", "A11701", "삼성전자   F 202701 (  10)", "005930", "삼성전자", "2"),
    master_row("1", "A11612", "삼성전자   F 202612 (  10)", "005930", "삼성전자", "1"),
    master_row("1", "1GNW04", "금양       F 202504 (  10)", "001570", "금양"),
    master_row("2", "4GNW01", "삼성전자   SP 2612-2701 (  10)", "005930", "삼성전자"),
    master_row("5", "B11612", "삼성전자 C 202612   190,000(  10)", "005930", "삼성전자"),
]


class FakeMaster:
    def ensure_fresh(self, market):
        return True

    def get_local_master_file(self, market):
        return None

    def get_cached_rows(self, market):
        return {"index": INDEX_ROWS, "stock": STOCK_ROWS}[market]


SAMSUNG_FRONT = {
    "hts_kor_isnm": "삼성전자   F 202612 (  10)",
    "futs_prpr": "206000",
    "basis": "499",
    "mrkt_basis": "0",
    "hts_thpr": "206499",
    "dprt": "-0.24",
    "futs_last_tr_date": "20261210",
    "hts_rmnn_dynu": "28",
    "acml_vol": "1715443",
    "hts_otst_stpl_qty": "3911567",
}
SAMSUNG_NEXT = {
    "hts_kor_isnm": "삼성전자   F 202701 (  10)",
    "futs_prpr": "199300",
    "basis": "596",
    "mrkt_basis": "-6700",
    "hts_thpr": "206596",
    "dprt": "-3.53",
    "futs_last_tr_date": "20270114",
    "hts_rmnn_dynu": "63",
    "acml_vol": "18116",
    "hts_otst_stpl_qty": "7660",
}
KOSPI200_FRONT = {
    "hts_kor_isnm": "F 202612",
    "futs_prpr": "822.35",
    "basis": "1.77",
    "mrkt_basis": "-2.43",
    "hts_thpr": "826.55",
    "dprt": "-0.51",
    "futs_last_tr_date": "20261210",
    "hts_rmnn_dynu": "28",
    "acml_vol": "114342",
    "hts_otst_stpl_qty": "154085",
}


class FakeClient:
    def __init__(self):
        self.quotes = {
            "A11612": SAMSUNG_FRONT,
            "A11701": SAMSUNG_NEXT,
            "A01612": KOSPI200_FRONT,
        }
        self.books = {
            "A11612": {"futs_bidp1": "206000", "futs_askp1": "206500"},
            "A11701": {"futs_bidp1": "199200", "futs_askp1": "199900"},
            "A01612": {"futs_bidp1": "822.35", "futs_askp1": "822.90"},
        }
        self.stock_price = 209000.0  # after-hours print
        self.futures_daily = []
        self.stock_daily = []

    def get_quote(self, symbol):
        return SimpleNamespace(current_price=self.stock_price, change_percent=0.48)

    def get_index_price(self, code):
        return {"bstp_nmix_prpr": "824.78", "bstp_nmix_prdy_ctrt": "-1.05"}

    def get_future_option_quote(self, symbol, market_div_code="F"):
        output = self.quotes.get(symbol)
        return {"output1": output} if output else None

    def get_future_option_orderbook(self, symbol, market_div_code="F"):
        return {"output2": self.books.get(symbol, {})}

    def get_future_option_daily_candles(self, **kwargs):
        return {"output2": self.futures_daily}

    def get_stock_daily_chart(self, symbol, start, end):
        return self.stock_daily

    def get_index_daily_chart(self, code, start, end):
        return []


@pytest.fixture
def client():
    return FakeClient()


@pytest.fixture
def service(client):
    return BasisService(client=client, master=FakeMaster())


def test_build_pairs_links_futures_to_their_underlying():
    pairs = build_pairs({"index": INDEX_ROWS, "stock": STOCK_ROWS}, "202611")

    assert pairs["005930"].kind == "stock"
    assert pairs["005930"].market_div_code == "JF"
    assert [c.symbol for c in pairs["005930"].contracts] == ["A11612", "A11701"]
    assert pairs["005930"].contracts[0].name == "삼성전자 F 202612 ( 10)"
    assert pairs["3003"].kind == "index"
    assert pairs["3003"].market_div_code == "F"


def test_build_pairs_prefers_regular_futures_over_mini():
    pairs = build_pairs({"index": INDEX_ROWS, "stock": []}, "202611")
    assert [c.symbol for c in pairs["2001"].contracts] == ["A01612", "A01703"]


def test_build_pairs_drops_expired_months_spreads_and_options():
    pairs = build_pairs({"index": [], "stock": STOCK_ROWS}, "202611")
    assert "001570" not in pairs  # only an expired 202504 contract
    symbols = {c.symbol for c in pairs["005930"].contracts}
    assert symbols == {"A11612", "A11701"}


def test_carry_helpers():
    assert carry_days(date(2026, 12, 10), date(2026, 11, 13)) == 28
    assert fair_value(206000, 3.0, 28) == pytest.approx(206474.08, abs=0.01)
    assert fair_value(206000, 3.0, 28, dividend=361) == pytest.approx(
        206113.08, abs=0.01
    )
    assert annualised_carry(206474.08, 206000, 28) == pytest.approx(3.0, abs=1e-3)
    assert annualised_carry(206000, 206000, 0) is None
    assert annualised_carry(None, 206000, 28) is None


def test_basis_stats_scores_the_latest_value():
    stats = basis_stats([0.1, 0.2, 0.3, 0.4, -0.5])
    assert stats.count == 5
    assert stats.latest == -0.5
    assert stats.zscore < -1.5
    assert stats.percentile == pytest.approx(20.0)
    assert basis_stats([]) is None
    assert basis_stats([0.2]).zscore is None


def test_resolve_accepts_code_futures_symbol_or_name(service):
    assert service.resolve("005930").name == "삼성전자"
    assert service.resolve("a11612").code == "005930"
    assert service.resolve("KOSPI200").code == "2001"
    with pytest.raises(LookupError):
        service.resolve("999999")


def test_list_underlyings_filters_and_puts_indexes_first(service):
    everything = service.list_underlyings()
    assert [u.code for u in everything] == ["2001", "3003", "005930"]
    assert [u.code for u in service.list_underlyings("삼성")] == ["005930"]
    assert everything[0].front_symbol == "A01612"


def test_snapshot_measures_basis_against_the_futures_synced_spot(service):
    snapshot = service.snapshot("005930", months=2)

    assert snapshot.spot == 206000  # not the 209,000 after-hours quote
    assert snapshot.spot_source == "futures_synced"
    assert snapshot.live_spot == 209000
    assert snapshot.spot_gap_percent == pytest.approx(1.456, abs=1e-3)
    assert any("시간외" in note for note in snapshot.notes)

    front, following = snapshot.contracts
    assert front.basis == 0
    assert front.mid == 206250
    assert front.mid_basis == 250
    assert front.days_to_expiry == 28
    assert following.basis == -6700
    assert following.basis_percent == pytest.approx(-3.2524, abs=1e-4)


def test_snapshot_without_a_rate_uses_the_broker_theoretical_price(service):
    snapshot = service.snapshot("005930", months=1)
    front = snapshot.contracts[0]

    assert snapshot.rate_source == "broker"
    assert front.theoretical_price == 206499
    assert front.theoretical_basis == 499
    assert front.discrepancy_percent == pytest.approx(-0.2416, abs=1e-4)
    assert front.discrepancy_percent == pytest.approx(
        front.broker_discrepancy_rate, abs=0.005
    )
    assert front.carry_rate == pytest.approx(3.158, abs=1e-3)


def test_snapshot_with_a_rate_computes_its_own_fair_value(service):
    snapshot = service.snapshot("005930", rate=3.0, dividend=361, months=1)
    front = snapshot.contracts[0]

    assert snapshot.rate_source == "user"
    assert snapshot.dividend == 361
    assert front.carry_rate == 3.0
    assert front.theoretical_price == pytest.approx(206113.08, abs=0.01)
    assert front.broker_theoretical_price == 206499


def test_snapshot_for_an_index_matches_the_broker_market_basis(service):
    snapshot = service.snapshot("2001", months=1)
    front = snapshot.contracts[0]

    assert snapshot.kind == "index"
    assert snapshot.spot == pytest.approx(824.78)
    assert snapshot.notes == []
    assert front.basis == pytest.approx(front.broker_market_basis, abs=1e-6)
    assert front.implied_rate < 0  # futures below spot: backwardation


def test_snapshot_falls_back_to_the_live_quote(service, client):
    client.quotes["A11612"] = {**SAMSUNG_FRONT, "hts_thpr": "0", "basis": ""}
    client.stock_price = 206500.0
    snapshot = service.snapshot("005930", months=1)

    assert snapshot.spot == 206500
    assert snapshot.spot_source == "live_quote"
    assert snapshot.contracts[0].basis == -500
    assert snapshot.contracts[0].theoretical_price is None


def test_snapshot_fails_when_no_contract_can_be_quoted(service, client):
    client.quotes.clear()
    with pytest.raises(LookupError):
        service.snapshot("005930")


def test_history_joins_closes_and_skips_untraded_days(service, client):
    client.futures_daily = [
        {"stck_bsop_date": "20261113", "futs_prpr": "206000", "acml_vol": "1715443"},
        {"stck_bsop_date": "20261112", "futs_prpr": "207000", "acml_vol": "1939029"},
        {"stck_bsop_date": "20261111", "futs_prpr": "206500", "acml_vol": "0"},
        {"stck_bsop_date": "20261110", "futs_prpr": "198900", "acml_vol": "1216224"},
    ]
    client.stock_daily = [
        {"stck_bsop_date": "20261113", "stck_clpr": "209000"},
        {"stck_bsop_date": "20261112", "stck_clpr": "208000"},
        {"stck_bsop_date": "20261111", "stck_clpr": "206000"},
        {"stck_bsop_date": "20261110", "stck_clpr": "198900"},
    ]
    history = service.history("005930", days=30)

    assert [p.date for p in history.points] == ["20261110", "20261112", "20261113"]
    assert history.points[1].basis == -1000
    assert history.points[1].basis_percent == pytest.approx(-0.4808, abs=1e-4)
    assert history.stats.count == 3
    assert any("제외" in note for note in history.notes)


def test_history_replaces_an_after_hours_close_on_the_latest_day(service, client):
    client.futures_daily = [
        {"stck_bsop_date": "20261113", "futs_prpr": "206000", "acml_vol": "1715443"},
        {"stck_bsop_date": "20261112", "futs_prpr": "207000", "acml_vol": "1939029"},
    ]
    client.stock_daily = [
        {"stck_bsop_date": "20261113", "stck_clpr": "209000"},
        {"stck_bsop_date": "20261112", "stck_clpr": "208000"},
    ]
    history = service.history("005930", days=30)

    latest = history.points[-1]
    assert latest.spot == 206000
    assert latest.basis == 0
    assert history.stats.latest == 0
    assert any("대체" in note for note in history.notes)
