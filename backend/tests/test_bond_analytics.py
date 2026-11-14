"""Tests for bond yield analytics built on broker payloads.

Payloads are trimmed copies of real responses captured on 2026-11-14 (a
Saturday), so quotes belong to the 2026-11-13 session.
"""

from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from src.services import bond_math
from src.services.bond_analytics import (
    BondAnalyticsService,
    latest_agency_row,
    settlement_date,
    spec_from_info,
)

KST = timezone(timedelta(hours=9))
NOW = datetime(2026, 11, 14, 21, 0, tzinfo=KST)

KTB_INFO = {
    "ksd_bond_item_name": "국고채권 03250-3512(25-11)",
    "issu_dt": "20251210",
    "rdpt_dt": "20351210",
    "ksd_rcvg_bond_srfc_inrt": "3.250000000000",
    "int_caltm_mcnt": "6",
    "bond_expd_rdpt_rt": "100.000000000000",
    "bond_int_dfrm_mthd_cd": "03",
    "ksd_prcm_lnkg_gvbd_yn": "N",
    "csbd_yn": "N",
    "ksd_opcb_yn": "N",
    "splt_rdpt_rcnt": "0",
    "frn_intr": "0.000000000000",
    "ksd_cbbw_dvsn_cd": "9",
    "ksd_sodn_yn": "N",
}
KTB_PRICE = {
    "hts_kor_isnm": "국고03250-3512(25-11)",
    "bond_prpr": "9604.00",
    "acml_vol": "1020",
    "ernn_rate": "3.956",
    "oprc_ert": "3.956",
    "hgpr_ert": "3.956",
    "lwpr_ert": "3.956",
}
KTB_ASKING = {
    "bond_askp1": "9602.50",
    "bond_askp2": "9638.50",
    "bond_askp3": "0.00",
    "bond_bidp1": "9543.50",
    "bond_bidp2": "0.00",
    "askp_rsqn1": "1393740",
    "askp_rsqn2": "1020",
    "bidp_rsqn1": "430000",
    "seln_ernn_rate1": "3.958",
    "seln_ernn_rate2": "3.909",
    "shnu_ernn_rate1": "4.039",
    "shnu_ernn_rate2": "0.000",
}
KTB_AGENCY = [
    {
        "evlu_dt": "20261114",
        "kis_unpr": "9576.32",
        "kbp_unpr": "9576.32",
        "nice_evlu_unpr": "9576.32",
        "fnp_unpr": "9576.32",
        "avg_evlu_unpr": "9576.32",
        "kis_erng_rt": "3.997",
        "kbp_erng_rt": "3.997",
        "nice_evlu_erng_rt": "3.997",
        "fnp_erng_rt": "3.997",
        "avg_evlu_erng_rt": "3.997",
        "kis_crdt_grad_text": "",
    },
    {"evlu_dt": "20261113", "avg_evlu_unpr": "9575.28", "avg_evlu_erng_rt": "3.997"},
    {"evlu_dt": "20261112", "avg_evlu_unpr": "9615.95", "avg_evlu_erng_rt": "3.940"},
    {"evlu_dt": "20261110", "avg_evlu_unpr": "9680.22", "avg_evlu_erng_rt": "3.850"},
]

HOUSING_INFO = {
    "ksd_bond_item_name": "국민주택1종채권 21-11",
    "issu_dt": "20211130",
    "rdpt_dt": "20261130",
    "ksd_rcvg_bond_srfc_inrt": "1.000000000000",
    "int_caltm_mcnt": "12",
    "bond_expd_rdpt_rt": "100.000000000000",
    "bond_int_dfrm_mthd_cd": "02",
    "frn_intr": "0.000000000000",
    "ksd_cbbw_dvsn_cd": "9",
}
HOUSING_PRICE = {"bond_prpr": "10480.00", "acml_vol": "0", "ernn_rate": "0.000"}
HOUSING_ASKING = {
    "bond_askp1": "10514.50",
    "bond_bidp1": "10489.50",
    "bond_bidp2": "10479.40",
    "seln_ernn_rate1": "-0.918",
    "shnu_ernn_rate1": "4.196",
    "shnu_ernn_rate2": "0.000",  # missing: computed instead
}


class FakeClient:
    def __init__(self, info, price, asking, agency=None, candles=None):
        self.info, self.price, self.asking = info, price, asking
        self.agency = agency or []
        self.candles = candles or []

    def get_bond_basic_info(self, pdno):
        return self.info

    def get_bond_price(self, pdno):
        return self.price

    def get_bond_asking_price(self, pdno):
        return self.asking

    def get_bond_avg_unit(self, pdno, start, end, max_pages=10):
        return self.agency

    def get_bond_daily_price(self, pdno, limit=None):
        return self.candles


def candle(day, close, volume):
    return SimpleNamespace(date=day, close=close, volume=volume)


def test_settlement_rolls_weekends_back_to_friday():
    assert settlement_date(NOW) == date(2026, 11, 13)
    assert settlement_date(datetime(2026, 11, 16, 9, 0, tzinfo=KST)) == date(
        2026, 11, 16
    )


def test_spec_from_info_reads_a_coupon_bond():
    spec, reason, warnings = spec_from_info(KTB_INFO)
    assert reason is None and warnings == []
    assert spec.kind == bond_math.KIND_COUPON
    assert spec.coupon_rate == 3.25
    assert spec.interval_months == 6
    assert spec.maturity_date == date(2035, 12, 10)


def test_spec_from_info_reads_a_compound_bond():
    spec, reason, _ = spec_from_info(HOUSING_INFO)
    assert reason is None
    assert spec.kind == bond_math.KIND_COMPOUND
    assert spec.issue_date == date(2021, 11, 30)


@pytest.mark.parametrize(
    "override, fragment",
    [
        ({"bond_int_dfrm_mthd_cd": "05"}, "변동금리"),
        ({"frn_intr": "3.1"}, "FRN"),
        ({"csbd_yn": "Y"}, "영구채"),
        ({"ksd_prcm_lnkg_gvbd_yn": "Y"}, "물가연동"),
        ({"splt_rdpt_rcnt": "4"}, "분할상환"),
        ({"int_caltm_mcnt": "0"}, "이자지급주기"),
        ({"rdpt_dt": ""}, "만기일"),
        ({"bond_int_dfrm_mthd_cd": "99"}, "지원하지"),
    ],
)
def test_spec_from_info_rejects_structures_it_cannot_price(override, fragment):
    spec, reason, _ = spec_from_info({**KTB_INFO, **override})
    assert spec is None
    assert fragment in reason


def test_spec_from_info_warns_about_embedded_options():
    spec, _, warnings = spec_from_info(
        {**KTB_INFO, "ksd_opcb_yn": "Y", "ksd_cbbw_dvsn_cd": "1"}
    )
    assert spec is not None
    assert len(warnings) == 2


def test_latest_agency_row_ignores_rows_without_a_yield():
    rows = [
        {"evlu_dt": "20261114", "avg_evlu_erng_rt": "0.000"},
        {"evlu_dt": "20261112", "avg_evlu_erng_rt": "3.94"},
        {"evlu_dt": "20261113", "avg_evlu_erng_rt": "3.997"},
    ]
    assert latest_agency_row(rows)["evlu_dt"] == "20261113"
    assert latest_agency_row([]) is None


def test_analytics_for_a_traded_coupon_bond():
    service = BondAnalyticsService(
        FakeClient(KTB_INFO, KTB_PRICE, KTB_ASKING, KTB_AGENCY)
    )
    result = service.analytics("KR103502GFC1", now=NOW)

    assert result.supported and result.kind_label == "이표채"
    assert result.settlement_date == "20261113"
    assert result.traded_today
    assert result.computed_yield == pytest.approx(result.last_yield, abs=0.0015)
    assert result.reference_source == "last_trade"
    assert result.reference_price == pytest.approx(9604.0, abs=0.01)
    assert result.next_coupon_date == "20261210"

    assert result.best_ask_yield == 3.958
    assert result.best_bid_yield == 4.039
    assert result.bid_ask_spread_bp == pytest.approx(8.1)
    assert [lv.level for lv in result.levels] == [1, 2]

    assert result.accrued_interest == pytest.approx(138.52, abs=0.01)
    assert result.clean_price == pytest.approx(9465.48, abs=0.01)
    assert 7.0 < result.modified_duration < 8.5
    assert result.after_tax_yield < result.reference_yield
    assert [s.shift_bp for s in result.scenarios] == [-100, -50, -25, 25, 50, 100]

    # Market yield below the agencies' 3.997%: the bond trades rich.
    assert result.agency_yield == 3.997
    assert result.agency_spread_bp == pytest.approx(-4.07, abs=0.05)
    assert result.price_vs_agency > 0
    assert [a.agency for a in result.agencies] == ["KIS", "KBP", "NICE", "FnP"]
    assert result.notes == []


def test_analytics_uses_the_quote_mid_when_nothing_traded_today():
    service = BondAnalyticsService(
        FakeClient(HOUSING_INFO, HOUSING_PRICE, HOUSING_ASKING)
    )
    result = service.analytics("KR101501DBB3", now=NOW)

    assert not result.traded_today
    assert result.last_yield is None  # broker sends 0.000 without a trade
    assert result.computed_yield == pytest.approx(6.146, abs=0.002)
    assert result.reference_source == "quote_mid"
    assert result.reference_yield == pytest.approx((4.196 - 0.918) / 2)
    assert result.clean_price is None  # only meaningful for coupon bonds
    # The second bid has no broker yield, so ours fills in.
    assert result.levels[1].bid_yield == pytest.approx(6.269, abs=0.002)
    assert result.bid_ask_spread_bp == pytest.approx(511.4)
    assert any("스프레드" in note for note in result.notes)
    assert result.agency_yield is None and result.agency_spread_bp is None


def test_analytics_reports_unsupported_bonds_without_yields():
    info = {**KTB_INFO, "bond_int_dfrm_mthd_cd": "05"}
    service = BondAnalyticsService(FakeClient(info, KTB_PRICE, {}, KTB_AGENCY))
    result = service.analytics("KRXXXXXXXXXX", now=NOW)

    assert not result.supported
    assert "변동금리" in result.unsupported_reason
    assert result.computed_yield is None
    assert result.modified_duration is None
    assert result.scenarios == []
    # The broker's own figures still come through.
    assert result.last_yield == 3.956
    assert result.agency_yield == 3.997


def test_analytics_rejects_matured_bonds():
    info = {**HOUSING_INFO, "rdpt_dt": "20261113"}
    service = BondAnalyticsService(FakeClient(info, HOUSING_PRICE, {}))
    result = service.analytics("KR101501DBB3", now=NOW)
    assert not result.supported
    assert "만기" in result.unsupported_reason


@pytest.mark.parametrize(
    "info, price",
    [
        ({}, {}),
        # The broker answers an unknown code with blank fields, not an error.
        ({"ksd_bond_item_name": "", "rdpt_dt": ""}, {"bond_prpr": "0.00"}),
    ],
)
def test_analytics_raises_when_the_bond_is_unknown(info, price):
    service = BondAnalyticsService(FakeClient(info, price, {}))
    with pytest.raises(LookupError):
        service.analytics("KR0000000000", now=NOW)
    with pytest.raises(LookupError):
        service.yield_history("KR0000000000")


def test_yield_history_prices_only_days_that_traded():
    today = datetime.now(KST).date()
    days = []
    cursor = today
    while len(days) < 3:
        if cursor.weekday() < 5:
            days.append(cursor.strftime("%Y%m%d"))
        cursor -= timedelta(days=1)
    latest, middle, oldest = days
    weekend = today
    while weekend.weekday() != 5:
        weekend -= timedelta(days=1)

    service = BondAnalyticsService(
        FakeClient(
            KTB_INFO,
            {},
            {},
            agency=[
                {"evlu_dt": latest, "avg_evlu_erng_rt": "3.997", "avg_evlu_unpr": "9575"},
                {"evlu_dt": middle, "avg_evlu_erng_rt": "3.940", "avg_evlu_unpr": "9615"},
                {
                    "evlu_dt": weekend.strftime("%Y%m%d"),
                    "avg_evlu_erng_rt": "3.997",
                    "avg_evlu_unpr": "9576",
                },
            ],
            candles=[
                candle(latest, 9604.0, 1020),
                candle(middle, 9604.0, 0),  # carried-forward close
                candle(oldest, 9644.0, 500),
                candle("20200102", 9000.0, 10),  # outside the window
            ],
        )
    )
    history = service.yield_history("KR103502GFC1", days=30)

    by_date = {p.date: p for p in history.points}
    assert set(by_date) == {latest, middle, oldest}
    assert by_date[latest].market_yield is not None
    assert by_date[middle].market_yield is None
    assert by_date[middle].agency_yield == 3.94
    assert by_date[oldest].agency_yield is None
    assert history.traded_days == 2
    assert history.latest_spread_bp == pytest.approx(
        (by_date[latest].market_yield - 3.997) * 100
    )
    assert history.points == sorted(history.points, key=lambda p: p.date)
