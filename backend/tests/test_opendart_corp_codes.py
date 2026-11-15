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


# ---------------------------------------------------------------------------
# Lookups by company name (used by /api/korean/disclosures?corp=...)
# ---------------------------------------------------------------------------


def _write_named_snapshot(path, age=timedelta(hours=1)):
    timestamp = datetime.now(timezone.utc) - age
    path.write_text(
        json.dumps(
            {
                "timestamp": timestamp.isoformat(),
                "codes": {"005930": "00126380", "035420": "00266961"},
                "names": {"삼성전자": "00126380", "NAVER": "00266961"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    "query,expected",
    [
        ("삼성전자", "00126380"),
        (" 삼성 전자 ", "00126380"),
        ("(주)삼성전자", "00126380"),
        ("naver", "00266961"),
        ("005930", "00126380"),
        ("5930", "00126380"),
        ("00126380", "00126380"),
    ],
)
def test_find_corp_code_by_name_or_code(tmp_path, no_download, query, expected):
    path = tmp_path / "corp_codes.json"
    _write_named_snapshot(path)

    client = OpenDartClient(corp_code_cache_path=path)

    assert client.find_corp_code(query) == expected
    assert no_download == []


def test_find_corp_code_unknown_name(tmp_path, no_download):
    path = tmp_path / "corp_codes.json"
    _write_named_snapshot(path)

    client = OpenDartClient(corp_code_cache_path=path)

    assert client.find_corp_code("없는회사") is None
    assert no_download == []  # fresh snapshot with names: no download


def test_snapshot_without_names_downloads_for_a_name(tmp_path, no_download):
    path = tmp_path / "corp_codes.json"
    _write_snapshot(path, {"005930": "00126380"}, timedelta(hours=1))

    client = OpenDartClient(corp_code_cache_path=path)

    assert client.find_corp_code("삼성전자") is None
    assert len(no_download) == 1


CORPCODE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<result>
  <list>
    <corp_code>00126380</corp_code>
    <corp_name>삼성전자</corp_name>
    <stock_code>005930</stock_code>
  </list>
  <list>
    <corp_code>00999999</corp_code>
    <corp_name>비상장회사</corp_name>
    <stock_code> </stock_code>
  </list>
</result>
"""


def test_download_stores_codes_and_names(tmp_path, monkeypatch):
    import io
    import zipfile

    from src.integrations import opendart

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("CORPCODE.xml", CORPCODE_XML.encode("utf-8"))

    class FakeResponse:
        content = buffer.getvalue()

        def raise_for_status(self):
            pass

    monkeypatch.setattr(
        opendart.requests, "get", lambda *args, **kwargs: FakeResponse()
    )
    path = tmp_path / "corp_codes.json"
    client = OpenDartClient(corp_code_cache_path=path)
    client.api_key = "your_dart_key"

    assert client.download_corp_code_list() is True

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["codes"] == {"005930": "00126380"}
    assert payload["names"] == {"삼성전자": "00126380"}
    assert client.find_corp_code("삼성전자") == "00126380"
    assert client.find_corp_code("비상장회사") is None
