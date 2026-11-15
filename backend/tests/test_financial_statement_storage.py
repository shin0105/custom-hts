"""Offline tests for storing financial statements in Supabase."""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.services.financial_statements import (
    FinancialStatementService,
    financial_statement_service,
)


class FakeQuery:
    def __init__(self, calls, table):
        self.calls = calls
        self.table = table

    def upsert(self, row, **kwargs):
        self.calls.append((self.table, row, kwargs))
        return self

    def execute(self):
        return None


class FakeClient:
    def __init__(self):
        self.calls = []

    def table(self, name):
        return FakeQuery(self.calls, name)


class FakeSupabase:
    def __init__(self, client):
        self.client = client


class FakeDart:
    """OpenDART stand-in: BS and IS rows only, like the real API."""

    def __init__(self, symbols_with_data=("005930",)):
        self.symbols_with_data = set(symbols_with_data)
        self.requests = []

    def _statement(self, symbol, rows):
        self.requests.append(symbol)
        return rows if symbol in self.symbols_with_data else {}

    def get_balance_sheet(self, symbol, year, quarter=None):
        return self._statement(symbol, {"자산총계": 100.0})

    def get_income_statement(self, symbol, year, quarter=None):
        return self._statement(symbol, {"매출액": 10.0})

    def get_cash_flow(self, symbol, year, quarter=None):
        return self._statement(symbol, {})

    def get_corp_code(self, symbol):
        return "00126380"

    def get_company_info(self, symbol):
        return {"corp_name": "삼성전자"}


@pytest.fixture()
def service():
    instance = FinancialStatementService()
    instance.supabase = FakeSupabase(FakeClient())
    instance.opendart = FakeDart()
    return instance


def test_upsert_targets_the_unique_key(service):
    assert service.insert_korean_balance_sheet("005930", 2024) is True

    [(table, row, kwargs)] = service.supabase.client.calls
    assert table == "korean_balance_sheet"
    assert kwargs == {"on_conflict": "symbol,year,quarter"}
    assert row["quarter"] is None
    assert row["total_assets"] == 100.0


def test_unconfigured_supabase_skips_the_source_fetch(service):
    service.supabase = FakeSupabase(None)

    assert service.is_configured is False
    assert service.insert_korean_balance_sheet("005930", 2024) is False
    assert service.opendart.requests == []


def test_batch_reports_failure_when_a_symbol_stores_nothing(service):
    result = service.batch_insert_korean_statements(
        ["005930", "999999"], 2024, None
    )

    assert result["success"] is False
    assert result["failed"] == ["999999 2024"]
    assert result["stored"] == 2  # balance sheet + income statement
    assert result["attempted"] == 6
    assert result["results"]["005930"]["2024"]["balance_sheet"] is True


def test_batch_reports_success_when_every_period_stores_something(service):
    result = service.batch_insert_korean_statements(["005930"], 2024, [1, 2])

    assert result["success"] is True
    assert result["failed"] == []
    assert set(result["results"]["005930"]) == {"2024Q1", "2024Q2"}


def test_batch_with_no_symbols_is_not_a_success(service):
    result = service.batch_insert_korean_statements([], 2024, None)

    assert result["success"] is False


@pytest.mark.parametrize(
    "path,body",
    [
        ("/api/financials/korean/statements/insert", {"symbol": "005930", "year": 2024}),
        ("/api/financials/us/statements/insert", {"symbol": "AAPL", "year": 2024}),
        ("/api/financials/korean/statements/batch-insert", {"symbols": ["005930"], "year": 2024}),
        ("/api/financials/us/statements/batch-insert", {"symbols": ["AAPL"], "year": 2024}),
    ],
)
def test_insert_routes_return_503_without_supabase(monkeypatch, path, body):
    monkeypatch.setattr(
        financial_statement_service, "supabase", FakeSupabase(None)
    )

    response = TestClient(app).post(path, json=body)

    assert response.status_code == 503
    assert response.json()["detail"] == "Database connection not available"
