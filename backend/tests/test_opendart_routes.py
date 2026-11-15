"""Offline tests for OpenDART statement routes."""

from fastapi.testclient import TestClient

from src.main import app


def test_cash_flow_route_is_not_implemented():
    response = TestClient(app).get("/api/korean/financials/005930/cash-flow")

    assert response.status_code == 501
