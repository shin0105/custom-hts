"""Default fiscal years are resolved per request, not at import time."""

import pytest
from fastapi.testclient import TestClient

from src.api import korean
from src.main import app


@pytest.fixture()
def year_2031(monkeypatch):
    monkeypatch.setattr(korean, "current_year_kst", lambda: 2031)


def test_statement_routes_default_to_last_year(monkeypatch, year_2031):
    seen = []

    def fake_balance_sheet(symbol, year, quarter):
        seen.append(year)
        return {"자산총계": 1.0}

    monkeypatch.setattr(
        korean.opendart_client, "get_balance_sheet", fake_balance_sheet
    )

    response = TestClient(app).get(
        "/api/korean/financials/005930/balance-sheet"
    )

    assert response.status_code == 200
    assert response.json()["year"] == 2030
    assert seen == [2030]


def test_explicit_year_is_kept(monkeypatch, year_2031):
    seen = []

    def fake_income_statement(symbol, year, quarter):
        seen.append(year)
        return {"매출액": 1.0}

    monkeypatch.setattr(
        korean.opendart_client, "get_income_statement", fake_income_statement
    )

    TestClient(app).get(
        "/api/korean/financials/005930/income-statement", params={"year": 2024}
    )

    assert seen == [2024]


def test_summary_defaults_to_this_year(monkeypatch, year_2031):
    seen = []

    async def fake_get_financials(symbol, year, quarter, use_cache):
        seen.append(year)
        return None

    monkeypatch.setattr(
        korean.korean_market_service, "get_financials", fake_get_financials
    )

    TestClient(app).get("/api/korean/financials/005930")

    assert seen == [2031]


def test_openapi_has_no_baked_in_year():
    schema = TestClient(app).get("/openapi.json").json()
    params = schema["paths"]["/api/korean/financials/{symbol}/all"]["get"][
        "parameters"
    ]
    year = next(p for p in params if p["name"] == "year")

    assert year["schema"].get("default") is None
