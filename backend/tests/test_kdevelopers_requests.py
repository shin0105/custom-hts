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
