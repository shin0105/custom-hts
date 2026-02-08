"""Service layer for Korean market operations."""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import logging
from ..models.korean import (
    KoreanStockQuote,
    KoreanFinancialStatement,
    KoreanCandleData,
    KoreanValuationMetrics,
    KoreanEstimatePerform,
)
from ..integrations.kdevelopers import kdevelopers_client
from ..integrations.opendart import opendart_client
from ..integrations.supabase_client import supabase_client

logger = logging.getLogger(__name__)


class KoreanMarketService:
    """Service for Korean market data operations."""

    async def get_quote(self, symbol: str) -> Optional[KoreanStockQuote]:
        """
        Get real-time quote for a Korean stock.

        Args:
            symbol: Stock code (e.g., "005930")

        Returns:
            KoreanStockQuote or None
        """
        return kdevelopers_client.get_quote(symbol)

    async def get_financials(
        self,
        symbol: str,
        year: int,
        quarter: Optional[int] = None,
        use_cache: bool = True,
    ) -> Optional[KoreanFinancialStatement]:
        """
        Get financial statement for a Korean company.

        Args:
            symbol: Stock code
            year: Fiscal year
            quarter: Optional quarter (1-4)
            use_cache: Whether to use cached data (parameter kept for API compatibility but not used)

        Returns:
            KoreanFinancialStatement or None
        """
        # Fetch directly from OPENDART without database caching
        statement = opendart_client.get_financial_statement(
            symbol, year, quarter
        )

        return statement

    async def get_daily_candle(
        self,
        symbol: str,
        period: str = "D",
        adjust_price: bool = True,
        limit: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[List[KoreanCandleData]]:
        """
        Get daily/period candle chart data for a Korean stock.

        Args:
            symbol: Stock code
            period: Period type - "D" (daily), "W" (weekly), "M" (monthly)
            adjust_price: Whether to adjust for stock splits
            limit: Number of candles to retrieve

        Returns:
            List of KoreanCandleData or None
        """
        return kdevelopers_client.get_daily_candle(
            symbol,
            period,
            adjust_price,
            limit,
            start_date=start_date,
            end_date=end_date,
        )

    async def get_minute_candle(
        self,
        symbol: str,
        interval: int = 1,
        limit: Optional[int] = None,
        date: Optional[str] = None,
        time_str: str = "",
    ) -> Optional[List[KoreanCandleData]]:
        """
        Get minute candle chart data for a Korean stock.

        Args:
            symbol: Stock code
            interval: Minute interval (1, 5, 10, 30, 60)
            limit: Number of candles to retrieve

        Returns:
            List of KoreanCandleData or None
        """
        max_per_day = 390 // interval if interval else 390
        include_previous = limit is not None and limit > max_per_day
        return kdevelopers_client.get_minute_candle(
            symbol,
            interval,
            limit,
            date=date,
            time_str=time_str,
            include_previous=include_previous,
        )

    async def get_account_balance(
        self, account_number: str, account_product_code: str = "01"
    ) -> Optional[Dict[str, Any]]:
        """
        Get account balance and positions.

        Args:
            account_number: Account number (8 digits)
            account_product_code: Account product code

        Returns:
            Dictionary containing balance and positions, or None
        """
        return kdevelopers_client.get_account_balance(
            account_number, account_product_code
        )

    async def get_stock_info(
        self, prdt_type_cd: str, pdno: str
    ) -> List[Dict[str, Any]]:
        """
        Get stock basic information from KDevelopers.

        Args:
            prdt_type_cd: Product type code
            pdno: Product number (stock code)

        Returns:
            Raw output list from search-stock-info API
        """
        return kdevelopers_client.search_stock_info(prdt_type_cd, pdno)

    async def get_estimate_perform(
        self, symbol: str
    ) -> Optional[KoreanEstimatePerform]:
        """
        Get estimated performance data for a Korean stock.

        Args:
            symbol: Stock code

        Returns:
            KoreanEstimatePerform or None
        """
        data = kdevelopers_client.get_estimate_perform(symbol)
        if data is None:
            return None
        if all(not data.get(key) for key in ["output1", "output2", "output3", "output4"]):
            return None
        output1 = data.get("output1") or []
        if output1:
            output1_field_map = {
                "sht_cd": "elw_short_code",
                "item_kor_nm": "hts_korean_name",
                "name1": "elw_current_price",
                "name2": "change_vs_prev_close",
                "estdate": "change_sign",
                "rcmd_name": "change_rate",
                "capital": "cumulative_volume",
                "forn_item_lmtrt": "strike_price",
            }
            mapped_output1 = []
            for row in output1:
                mapped_row = {}
                for key, value in row.items():
                    mapped_key = output1_field_map.get(key, key)
                    mapped_row[mapped_key] = value
                mapped_output1.append(mapped_row)
            data["output1"] = mapped_output1

        output4_rows = data.get("output4") or []
        years = [row.get("dt") for row in output4_rows if row.get("dt")]
        if years:
            data["output4"] = years

        output2_rows = data.get("output2") or []
        output2_labels = [
            "revenue",
            "revenue_growth_rate",
            "operating_income",
            "operating_income_growth_rate",
            "net_income",
            "net_income_growth_rate",
        ]
        if output2_rows:
            mapped_output2 = []
            for idx, row in enumerate(output2_rows):
                metric_key = (
                    output2_labels[idx]
                    if idx < len(output2_labels)
                    else f"metric_{idx + 1}"
                )
                values = []
                year_values = {}
                for col_idx, year in enumerate(years):
                    value = row.get(f"data{col_idx + 1}")
                    values.append(value)
                    year_values[year] = value
                mapped_output2.append(
                    {
                        "metric": metric_key,
                        "values": values,
                        "year_values": year_values,
                    }
                )
            data["output2"] = mapped_output2

        output3_rows = data.get("output3") or []
        output3_labels = [
            "ebitda",
            "eps",
            "eps_growth_rate",
            "per",
            "ev_ebitda",
            "roe",
            "debt_ratio",
            "interest_coverage_ratio",
        ]
        if output3_rows:
            mapped_output3 = []
            for idx, row in enumerate(output3_rows):
                metric_key = (
                    output3_labels[idx]
                    if idx < len(output3_labels)
                    else f"metric_{idx + 1}"
                )
                values = []
                year_values = {}
                for col_idx, year in enumerate(years):
                    value = row.get(f"data{col_idx + 1}")
                    values.append(value)
                    year_values[year] = value
                mapped_output3.append(
                    {
                        "metric": metric_key,
                        "values": values,
                        "year_values": year_values,
                    }
                )
            data["output3"] = mapped_output3
        return KoreanEstimatePerform(symbol=symbol, **data)

    async def get_valuation_metrics(
        self,
        symbol: str,
        year: int,
        quarter: Optional[int] = None,
        fs_div: str = "CFS",
    ) -> Optional[KoreanValuationMetrics]:
        """
        Get valuation metrics for a Korean stock using KDevelopers + OpenDART.

        Args:
            symbol: Stock code
            year: Fiscal year for financials
            quarter: Optional quarter (1-4)
            fs_div: Financial statement division (CFS/OFS)

        Returns:
            KoreanValuationMetrics or None
        """

        def parse_number(value: Any) -> Optional[float]:
            try:
                if value is None:
                    return None
                text = str(value).replace(",", "").strip()
                if not text or text == "-":
                    return None
                return float(text)
            except (ValueError, TypeError):
                return None

        quote = kdevelopers_client.get_quote(symbol)
        if not quote:
            return None

        financials, _, _ = self._get_latest_financials(
            symbol, year, quarter, fs_div
        )
        if financials is None:
            logger.info(
                "No financials available for %s (requested %s Q%s, fs_div=%s)",
                symbol,
                year,
                quarter if quarter is not None else "annual",
                fs_div,
            )

        stock_info = kdevelopers_client.search_stock_info("300", symbol)
        info_row = stock_info[0] if stock_info else {}

        shares_outstanding = None
        share_keys = [
            "listed_shares",
            "lstn_stcn",
            "lstn_stcn_cnt",
            "list_shrs",
            "lstn_shrs",
            "issu_shrs",
            "istt_shrs",
            "stck_lstn",
            "stck_list_shrs",
        ]
        for key in share_keys:
            shares_outstanding = parse_number(info_row.get(key))
            if shares_outstanding:
                break

        eps = financials.eps if financials else None
        if eps is None and financials and financials.net_income and shares_outstanding:
            if shares_outstanding != 0:
                eps = financials.net_income / shares_outstanding

        bps = financials.bps if financials else None
        if bps is None and financials and financials.total_equity and shares_outstanding:
            if shares_outstanding != 0:
                bps = financials.total_equity / shares_outstanding

        per = None
        if eps is not None and eps != 0:
            per = quote.current_price / eps

        pbr = None
        if bps is not None and bps != 0:
            pbr = quote.current_price / bps

        market_cap = None
        if shares_outstanding:
            market_cap = quote.current_price * shares_outstanding

        return KoreanValuationMetrics(
            symbol=symbol,
            price=quote.current_price,
            eps=eps,
            bps=bps,
            per=per,
            pbr=pbr,
            shares_outstanding=shares_outstanding,
            market_cap=market_cap,
            as_of=datetime.now(),
        )

    def _get_latest_financials(
        self,
        symbol: str,
        year: int,
        quarter: Optional[int],
        fs_div: str,
        lookback_years: int = 4,
    ) -> Tuple[Optional[KoreanFinancialStatement], Optional[int], Optional[int]]:
        """
        Fetch the most recent available financials, falling back to prior years.

        Returns:
            (financials, used_year, used_quarter)
        """
        candidates: List[Tuple[int, Optional[int]]] = []

        if quarter is not None:
            candidates.append((year, quarter))
            candidates.append((year, None))
            for offset in range(1, lookback_years + 1):
                candidates.append((year - offset, quarter))
                candidates.append((year - offset, None))
        else:
            candidates.append((year, None))
            for offset in range(1, lookback_years + 1):
                candidates.append((year - offset, None))

        seen = set()
        for candidate_year, candidate_quarter in candidates:
            key = (candidate_year, candidate_quarter)
            if key in seen:
                continue
            seen.add(key)
            financials = opendart_client.get_financial_statement(
                symbol, candidate_year, candidate_quarter, fs_div=fs_div
            )
            if financials:
                return financials, candidate_year, candidate_quarter

        return None, None, None


korean_market_service = KoreanMarketService()
