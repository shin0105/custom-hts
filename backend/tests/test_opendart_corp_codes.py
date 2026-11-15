"""Offline tests for the OpenDART stock-code → corp-code lookup."""

import json
from datetime import datetime, timedelta, timezone

import pytest

from src.integrations.opendart import OpenDartClient


def _write_snapshot(path, codes, age):
    timestamp = datetime.now(timezone.utc) - age
    path.write_text(
        json.dumps({"timestamp": timestamp.isoformat(), "codes": codes}),
        encoding="utf-8",
    )


@pytest.fixture()
def no_download(monkeypatch):
    """Make every download attempt fail and count the attempts."""
    calls = []

    def fake_download(self):
        calls.append(self)
        return False

    monkeypatch.setattr(OpenDartClient, "download_corp_code_list", fake_download)
    return calls


@pytest.mark.parametrize(
    "stock_code,corp_code",
    [
        ("005930", "00126380"),  # 삼성전자
        ("000660", "00164779"),  # SK하이닉스
        ("005380", "00164742"),  # 현대차
        ("035420", "00266961"),  # NAVER
        ("035720", "00258801"),  # 카카오
        ("051910", "00356361"),  # LG화학
        ("006400", "00126362"),  # 삼성SDI
        ("207940", "00877059"),  # 삼성바이오로직스
        ("068270", "00413046"),  # 셀트리온
        ("028260", "00149655"),  # 삼성물산
        ("012330", "00164788"),  # 현대모비스
    ],
)
def test_committed_snapshot_maps_frequent_stocks(
    no_download, stock_code, corp_code
):
    """The 자주 찾는 종목 chips resolve to their own company's corp code."""
    client = OpenDartClient()
    assert client.get_corp_code(stock_code) == corp_code
    assert no_download == []


def test_stale_snapshot_is_still_used(tmp_path, no_download):
    path = tmp_path / "corp_codes.json"
    _write_snapshot(path, {"005930": "00126380"}, timedelta(days=400))

    client = OpenDartClient(corp_code_cache_path=path)

    assert client.get_corp_code("005930") == "00126380"
    assert client.get_corp_code("5930") == "00126380"
    assert no_download == []


def test_stale_snapshot_miss_tries_a_download(tmp_path, no_download):
    path = tmp_path / "corp_codes.json"
    _write_snapshot(path, {"005930": "00126380"}, timedelta(days=400))

    client = OpenDartClient(corp_code_cache_path=path)

    assert client.get_corp_code("999999") is None
    assert len(no_download) == 1
    # The failed download leaves the stale entries usable.
    assert client.get_corp_code("005930") == "00126380"


def test_fresh_snapshot_miss_does_not_download(tmp_path, no_download):
    path = tmp_path / "corp_codes.json"
    _write_snapshot(path, {"005930": "00126380"}, timedelta(hours=1))

    client = OpenDartClient(corp_code_cache_path=path)

    assert client.get_corp_code("999999") is None
    assert no_download == []


def test_missing_snapshot_tries_a_download(tmp_path, no_download):
    client = OpenDartClient(corp_code_cache_path=tmp_path / "none.json")

    assert client.get_corp_code("005930") is None
    assert len(no_download) == 1
