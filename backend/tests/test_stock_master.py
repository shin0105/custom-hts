"""Tests for the Korean stock master search used by symbol typeahead."""

import asyncio

import pytest

from src.integrations.stock_master import StockMasterFileManager


@pytest.fixture()
def manager(tmp_path):
    """A manager backed by a temp dir with a stubbed parse step."""
    instance = StockMasterFileManager(data_dir=str(tmp_path))
    return instance


def _stub_rows(manager, rows_by_market):
    """Seed the row cache directly so tests never hit the network."""
    import time

    for market, rows in rows_by_market.items():
        manager._rows_cache[market] = (time.time(), rows)


def _row(symbol, name, market="kospi", market_cap=None):
    return {
        "market": market,
        "symbol": symbol,
        "name": name,
        "standard_code": f"KR7{symbol}001",
        "security_group_code": "ST",
        "market_cap_100m": market_cap,
        "listing_date": "20000101",
    }


def test_search_ranks_exact_code_first(manager):
    _stub_rows(
        manager,
        {
            "kospi": [
                _row("005930", "삼성전자", market_cap=15697258.0),
                _row("005935", "삼성전자우", market_cap=1510864.0),
            ],
            "kosdaq": [],
            "konex": [],
        },
    )

    results = manager.search_stocks("005935", markets=["kospi", "kosdaq", "konex"])

    assert results[0]["symbol"] == "005935"


def test_search_ranks_larger_company_first_on_name_prefix(manager):
    """Typing 삼성 should surface 삼성전자 ahead of smaller 삼성 names."""
    _stub_rows(
        manager,
        {
            "kospi": [
                _row("000810", "삼성화재", market_cap=270000.0),
                _row("001360", "삼성제약", market_cap=1193.0),
                _row("005930", "삼성전자", market_cap=15697258.0),
            ],
            "kosdaq": [],
            "konex": [],
        },
    )

    results = manager.search_stocks("삼성", markets=["kospi", "kosdaq", "konex"])

    assert [row["name"] for row in results][:3] == [
        "삼성전자",
        "삼성화재",
        "삼성제약",
    ]


def test_search_matches_substring(manager):
    _stub_rows(
        manager,
        {
            "kospi": [_row("035420", "NAVER", market_cap=300000.0)],
            "kosdaq": [_row("293490", "카카오게임즈", market_cap=20000.0)],
            "konex": [],
        },
    )

    results = manager.search_stocks("게임", markets=["kospi", "kosdaq", "konex"])

    assert len(results) == 1
    assert results[0]["symbol"] == "293490"


def test_search_without_query_returns_all_rows(manager):
    _stub_rows(
        manager,
        {
            "kospi": [_row("005930", "삼성전자")],
            "kosdaq": [_row("293490", "카카오게임즈", market="kosdaq")],
            "konex": [],
        },
    )

    results = manager.search_stocks(None, markets=["kospi", "kosdaq", "konex"])

    assert len(results) == 2


def test_search_returns_empty_for_no_match(manager):
    _stub_rows(
        manager,
        {"kospi": [_row("005930", "삼성전자")], "kosdaq": [], "konex": []},
    )

    assert manager.search_stocks("존재하지않는종목", markets=["kospi"]) == []


def test_normalize_rows_maps_per_market_column_names(manager):
    """Each market file names the same fields differently."""
    import pandas as pd

    kosdaq = pd.DataFrame(
        [
            {
                "단축코드": "293490",
                "표준코드": "KR7293490005",
                "한글종목명": "카카오게임즈",
                "증권그룹구분코드": "ST",
                "전일기준 시가총액 (억)": "20000",
            }
        ]
    )

    rows = manager._normalize_rows(kosdaq, "kosdaq")

    assert rows[0]["name"] == "카카오게임즈"
    assert rows[0]["symbol"] == "293490"
    assert rows[0]["market"] == "kosdaq"
    assert rows[0]["market_cap_100m"] == 20000.0


def test_normalize_rows_tolerates_missing_and_bad_values(manager):
    import pandas as pd

    df = pd.DataFrame(
        [
            {"단축코드": "005930", "한글명": "삼성전자", "시가총액": "not-a-number"},
            {"단축코드": "", "한글명": "빈코드", "시가총액": "100"},
        ]
    )

    rows = manager._normalize_rows(df, "kospi")

    # Rows without a symbol are dropped; unparseable numbers become None.
    assert len(rows) == 1
    assert rows[0]["market_cap_100m"] is None
    assert rows[0]["listing_date"] is None


def test_service_rejects_unknown_market():
    from src.services.korean_market import korean_market_service

    with pytest.raises(ValueError, match="market must be one of"):
        asyncio.run(korean_market_service.get_stock_master(market="nasdaq"))


def test_service_paginates(monkeypatch):
    from src.integrations import stock_master as stock_master_module
    from src.services.korean_market import korean_market_service

    rows = [_row(f"00593{i}", f"종목{i}") for i in range(10)]

    monkeypatch.setattr(
        stock_master_module.master_file_manager,
        "get_market_rows",
        lambda *args, **kwargs: rows,
    )
    monkeypatch.setattr(
        stock_master_module.master_file_manager,
        "search_stocks",
        lambda *args, **kwargs: rows,
    )

    result = asyncio.run(
        korean_market_service.get_stock_master(
            query="종목", market="kospi", offset=2, limit=3
        )
    )

    assert result["total_matched"] == 10
    assert result["total_returned"] == 3
    assert result["offset"] == 2
    assert [item["symbol"] for item in result["items"]] == [
        "005932",
        "005933",
        "005934",
    ]
    assert result["markets"] == ["kospi"]
