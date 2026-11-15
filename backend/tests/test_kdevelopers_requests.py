"""Offline tests for KIS request parameters and paging (no network)."""

from collections import namedtuple

import pytest

from src.integrations.kdevelopers import KDevelopersClient


class FakeResponse:
    """Minimal stand-in for APIResponse."""

    def __init__(self, body, tr_cont="", ok=True):
        self._body = namedtuple("body", body.keys())(**body)
        self._header = namedtuple("header", ["tr_cont"])(tr_cont)
        self._ok = ok

    def is_ok(self):
        return self._ok

    def get_body(self):
        return self._body

    def get_header(self):
        return self._header

    def print_error(self, url):
        pass


@pytest.fixture()
def client():
    return KDevelopersClient()


def _record_fetches(monkeypatch, client, responses):
    calls = []
    queue = list(responses)

    def fake_fetch(api_url, tr_id, tr_cont, params, post_flag=False):
        calls.append({"url": api_url, "tr_cont": tr_cont, **params})
        return queue.pop(0)

    monkeypatch.setattr(client, "_url_fetch", fake_fetch)
    return calls


@pytest.mark.parametrize("adjust,expected", [(True, "1"), (False, "0")])
def test_daily_candle_adjusted_price_flag(monkeypatch, client, adjust, expected):
    """inquire-daily-price: 0 = 수정주가 미반영, 1 = 수정주가 반영."""
    calls = _record_fetches(
        monkeypatch, client, [FakeResponse({"rt_cd": "0", "output": []})]
    )

    assert client.get_daily_candle("005930", adjust_price=adjust) == []
    assert calls[0]["FID_ORG_ADJ_PRC"] == expected


def _holdings(start, count):
    return [
        {"pdno": f"{n:06d}", "prdt_name": f"종목{n}", "hldg_qty": "1"}
        for n in range(start, start + count)
    ]


SUMMARY = [{"tot_evlu_amt": "1000", "dnca_tot_amt": "10"}]


def test_account_balance_follows_continuation_keys(monkeypatch, client):
    calls = _record_fetches(
        monkeypatch,
        client,
        [
            FakeResponse(
                {
                    "rt_cd": "0",
                    "output1": _holdings(0, 50),
                    "output2": SUMMARY,
                    "ctx_area_fk100": "FK-1",
                    "ctx_area_nk100": "NK-1",
                },
                tr_cont="M",
            ),
            FakeResponse(
                {
                    "rt_cd": "0",
                    "output1": _holdings(50, 12),
                    "output2": SUMMARY,
                    "ctx_area_fk100": "FK-2",
                    "ctx_area_nk100": "NK-2",
                },
                tr_cont="D",
            ),
        ],
    )

    result = client.get_account_balance("12345678")

    assert [p.symbol for p in result["positions"]] == [
        f"{n:06d}" for n in range(62)
    ]
    assert result["balance"].total_evaluation == 1000.0
    assert len(calls) == 2
    assert calls[0]["tr_cont"] == ""
    assert calls[0]["CTX_AREA_FK100"] == ""
    assert calls[0]["CTX_AREA_NK100"] == ""
    assert calls[1]["tr_cont"] == "N"
    assert calls[1]["CTX_AREA_FK100"] == "FK-1"
    assert calls[1]["CTX_AREA_NK100"] == "NK-1"


def test_account_balance_single_page(monkeypatch, client):
    calls = _record_fetches(
        monkeypatch,
        client,
        [
            FakeResponse(
                {
                    "rt_cd": "0",
                    "output1": _holdings(0, 3),
                    "output2": SUMMARY,
                    "ctx_area_fk100": "",
                    "ctx_area_nk100": "",
                },
                tr_cont="D",
            )
        ],
    )

    result = client.get_account_balance("12345678")

    assert len(result["positions"]) == 3
    assert len(calls) == 1


def test_account_balance_failed_continuation_is_not_truncated(
    monkeypatch, client
):
    _record_fetches(
        monkeypatch,
        client,
        [
            FakeResponse(
                {
                    "rt_cd": "0",
                    "output1": _holdings(0, 50),
                    "output2": SUMMARY,
                    "ctx_area_fk100": "FK-1",
                    "ctx_area_nk100": "NK-1",
                },
                tr_cont="M",
            ),
            FakeResponse({"rt_cd": "1"}, ok=False),
        ],
    )

    assert client.get_account_balance("12345678") is None
