"""Offline tests for OpenDART disclosures and statement routes."""

import pytest
from fastapi.testclient import TestClient

from src.api import korean
from src.integrations import opendart
from src.integrations.opendart import OpenDartClient
from src.main import app


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


@pytest.fixture()
def dart(monkeypatch):
    """A client with a stub key whose HTTP calls are recorded."""
    client = OpenDartClient()
    client.api_key = "your_dart_key"
    monkeypatch.setattr(
        OpenDartClient, "download_corp_code_list", lambda self: False
    )
    calls = []

    def fake_get(url, params=None, timeout=None):
        calls.append(params)
        return FakeResponse({"status": "000", "list": [{"rcept_no": "1"}]})

    monkeypatch.setattr(opendart.requests, "get", fake_get)
    return client, calls


def test_disclosures_for_unknown_company_raise(dart):
    client, calls = dart

    with pytest.raises(LookupError):
        client.get_disclosure_list(corp="없는회사")
    assert calls == []  # never asks DART for every company's filings


def test_disclosures_for_stock_code_send_corp_code(dart):
    client, calls = dart

    assert client.get_disclosure_list(corp="005930") == [{"rcept_no": "1"}]
    assert calls[0]["corp_code"] == "00126380"


def test_disclosures_without_corp_list_everything(dart):
    client, calls = dart

    client.get_disclosure_list()
    assert "corp_code" not in calls[0]


def test_disclosures_route_returns_404_for_unknown_company(monkeypatch):
    def raise_lookup(**kwargs):
        raise LookupError("Company not found: 없는회사")

    monkeypatch.setattr(
        korean.opendart_client, "get_disclosure_list", raise_lookup
    )

    response = TestClient(app).get(
        "/api/korean/disclosures", params={"corp": "없는회사"}
    )

    assert response.status_code == 404
    assert "없는회사" in response.json()["detail"]


def test_cash_flow_route_is_not_implemented():
    response = TestClient(app).get("/api/korean/financials/005930/cash-flow")

    assert response.status_code == 501
