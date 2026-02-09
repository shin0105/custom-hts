"""Service layer for Korean market operations."""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date, timedelta
import re
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

ESTIMATE_AMOUNT_UNIT = "억원"
ESTIMATE_AMOUNT_MULTIPLIER = 100_000_000


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
        data["units"] = {
            "output2": {
                "default": ESTIMATE_AMOUNT_UNIT,
                "scale_to_krw": ESTIMATE_AMOUNT_MULTIPLIER,
                "metrics": {
                    "revenue": ESTIMATE_AMOUNT_UNIT,
                    "operating_income": ESTIMATE_AMOUNT_UNIT,
                    "net_income": ESTIMATE_AMOUNT_UNIT,
                },
            },
            "output3": {
                "ebitda": ESTIMATE_AMOUNT_UNIT,
                "eps": "원",
                "per": "배",
                "ev_ebitda": "배",
                "roe": "%",
                "debt_ratio": "%",
                "interest_coverage_ratio": "배",
            },
        }
        data["unit_notes"] = (
            "KDevelopers estimate-perform monetary values are reported in 억원. "
            "Convert to KRW by multiplying by 100,000,000 when using them in calculations."
        )
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

        def parse_estimate_year_label(label: str) -> Optional[Tuple[int, bool]]:
            if not label:
                return None
            match = re.search(r"(20\d{2})", label)
            if not match:
                return None
            year_value = int(match.group(1))
            is_estimate = "E" in label.upper()
            return year_value, is_estimate

        def previous_quarter_safe(
            base_year: int, base_quarter: Optional[int]
        ) -> Tuple[int, int]:
            if base_quarter is None:
                return base_year, 4
            if base_quarter == 1:
                return base_year - 1, 4
            return base_year, base_quarter - 1

        def add_year_safe(input_date: date) -> date:
            try:
                return input_date.replace(year=input_date.year + 1)
            except ValueError:
                # Handle Feb 29 -> Feb 28 for non-leap years
                return input_date.replace(month=2, day=28, year=input_date.year + 1)

        def overlap_days(
            period_start: date, period_end: date, year_value: int
        ) -> int:
            year_start = date(year_value, 1, 1)
            year_end_exclusive = date(year_value, 12, 31) + timedelta(days=1)
            start = max(period_start, year_start)
            end = min(period_end, year_end_exclusive)
            delta = (end - start).days
            return max(delta, 0)

        def estimate_amount_to_krw(value: Optional[float]) -> Optional[float]:
            if value is None:
                return None
            return value * ESTIMATE_AMOUNT_MULTIPLIER

        quote = kdevelopers_client.get_quote(symbol)
        if not quote:
            return None

        notes: List[str] = []
        requested_year = year
        requested_quarter = quarter
        actual_year = year
        actual_quarter = quarter

        financials = opendart_client.get_financial_statement(
            symbol, requested_year, requested_quarter, fs_div=fs_div
        )
        if financials is None:
            logger.info(
                "No financials available for %s (requested %s Q%s, fs_div=%s)",
                symbol,
                requested_year,
                requested_quarter if requested_quarter is not None else "annual",
                fs_div,
            )
            notes.append(
                f"No financials available for requested period (year: {requested_year}, quarter: {requested_quarter})."
            )
            fallback_year, fallback_quarter = previous_quarter_safe(
                requested_year, requested_quarter
            )
            if (fallback_year, fallback_quarter) != (
                requested_year,
                requested_quarter,
            ):
                fallback_financials = opendart_client.get_financial_statement(
                    symbol, fallback_year, fallback_quarter, fs_div=fs_div
                )
                if fallback_financials is not None:
                    financials = fallback_financials
                    actual_year, actual_quarter = fallback_year, fallback_quarter
                    notes.append(
                        "Safe fallback used: "
                        f"{actual_year} Q{actual_quarter} (one quarter back)."
                    )
                else:
                    notes.append(
                        "Safe fallback failed; no financials for "
                        f"{fallback_year} Q{fallback_quarter}."
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

        eps_12mf = None
        per_12mf = None
        estimate_12mf_labels: Optional[List[str]] = None
        estimate_perform = await self.get_estimate_perform(symbol)
        if estimate_perform:
            output4 = estimate_perform.output4 or []
            estimate_labels = [
                label for label in output4 if label and "E" in str(label).upper()
            ]
            if len(estimate_labels) >= 2:
                label_1, label_2 = estimate_labels[0], estimate_labels[1]
                estimate_12mf_labels = [str(label_1), str(label_2)]
                year_info_1 = parse_estimate_year_label(str(label_1))
                year_info_2 = parse_estimate_year_label(str(label_2))
                if year_info_1 and year_info_2:
                    year_1, _ = year_info_1
                    year_2, _ = year_info_2
                    eps_map: Dict[str, Optional[float]] = {}
                    net_income_row = next(
                        (
                            row
                            for row in estimate_perform.output2
                            if row.get("metric") == "net_income"
                        ),
                        None,
                    )
                    if net_income_row and shares_outstanding:
                        year_values = net_income_row.get("year_values") or {}
                        if not year_values and net_income_row.get("values"):
                            for idx, label in enumerate(output4):
                                if idx < len(net_income_row["values"]):
                                    year_values[label] = net_income_row["values"][idx]
                        for label in output4:
                            net_income_value = parse_number(
                                year_values.get(label)
                            )
                            net_income_krw = estimate_amount_to_krw(
                                net_income_value
                            )
                            if (
                                net_income_krw is not None
                                and shares_outstanding
                                and shares_outstanding != 0
                            ):
                                eps_map[label] = (
                                    net_income_krw / shares_outstanding
                                )
                    if not eps_map:
                        eps_row = next(
                            (
                                row
                                for row in estimate_perform.output3
                                if row.get("metric") == "eps"
                            ),
                            None,
                        )
                        if eps_row:
                            year_values = eps_row.get("year_values") or {}
                            if not year_values and eps_row.get("values"):
                                for idx, label in enumerate(output4):
                                    if idx < len(eps_row["values"]):
                                        year_values[label] = eps_row["values"][idx]
                            for label in output4:
                                eps_map[label] = parse_number(
                                    year_values.get(label)
                                )

                    eps_1 = eps_map.get(label_1)
                    eps_2 = eps_map.get(label_2)
                    if eps_1 is not None and eps_2 is not None:
                        today = date.today()
                        period_start = today
                        period_end = add_year_safe(today)
                        total_days = (period_end - period_start).days
                        if total_days > 0:
                            days_year_1 = overlap_days(
                                period_start, period_end, year_1
                            )
                            days_year_2 = overlap_days(
                                period_start, period_end, year_2
                            )
                            overlap_total = days_year_1 + days_year_2
                            if overlap_total > 0:
                                weight_1 = days_year_1 / overlap_total
                                weight_2 = days_year_2 / overlap_total
                                eps_12mf = (eps_1 * weight_1) + (eps_2 * weight_2)
                                if eps_12mf != 0:
                                    per_12mf = quote.current_price / eps_12mf

        eps_ttm = None
        bps_ttm = None
        per_ttm = None
        pbr_ttm = None

        ttm_quarters: List[Tuple[int, int]] = []
        if actual_quarter is None:
            start_year, start_quarter = requested_year, 4
            notes.append(
                f"TTM window uses {requested_year} Q4 as the latest quarter because no quarter was specified."
            )
        else:
            start_year, start_quarter = actual_year, actual_quarter

        current_year, current_quarter = start_year, start_quarter
        for _ in range(4):
            ttm_quarters.append((current_year, current_quarter))
            if current_quarter == 1:
                current_year -= 1
                current_quarter = 4
            else:
                current_quarter -= 1

        ttm_financials: List[Tuple[Tuple[int, int], Optional[KoreanFinancialStatement]]] = []
        missing_ttm = []
        for ttm_year, ttm_quarter in ttm_quarters:
            fs = opendart_client.get_financial_statement(
                symbol, ttm_year, ttm_quarter, fs_div=fs_div
            )
            if fs is None:
                missing_ttm.append((ttm_year, ttm_quarter))
            ttm_financials.append(((ttm_year, ttm_quarter), fs))

        if missing_ttm:
            missing_label = ", ".join(
                [f"{year_value} Q{quarter_value}" for year_value, quarter_value in missing_ttm]
            )
            notes.append(
                f"TTM metrics unavailable; missing quarterly data for {missing_label}."
            )
        else:
            net_income_values = [
                fs.net_income for _, fs in ttm_financials if fs and fs.net_income is not None
            ]
            equity_values = [
                fs.total_equity for _, fs in ttm_financials if fs and fs.total_equity is not None
            ]

            if len(net_income_values) == 4 and shares_outstanding:
                net_income_ttm = sum(net_income_values)
                if shares_outstanding != 0:
                    eps_ttm = net_income_ttm / shares_outstanding
                    if eps_ttm != 0:
                        per_ttm = quote.current_price / eps_ttm
            elif net_income_values:
                notes.append("TTM EPS/PER partial data; require 4 quarterly net income values.")

            if equity_values and shares_outstanding:
                equity_avg = sum(equity_values) / len(equity_values)
                if shares_outstanding != 0:
                    bps_ttm = equity_avg / shares_outstanding
                    if bps_ttm != 0:
                        pbr_ttm = quote.current_price / bps_ttm
            elif missing_ttm:
                notes.append("TTM BPS/PBR partial data; missing quarterly total equity values.")

        return KoreanValuationMetrics(
            symbol=symbol,
            price=quote.current_price,
            fiscal_year=actual_year,
            fiscal_quarter=actual_quarter,
            eps=eps,
            eps_12mf=eps_12mf,
            bps=bps,
            per=per,
            per_12mf=per_12mf,
            pbr=pbr,
            eps_ttm=eps_ttm,
            bps_ttm=bps_ttm,
            per_ttm=per_ttm,
            pbr_ttm=pbr_ttm,
            ttm_quarters=[
                {"year": year_value, "quarter": quarter_value}
                for year_value, quarter_value in ttm_quarters
            ],
            estimate_12mf_labels=estimate_12mf_labels,
            shares_outstanding=shares_outstanding,
            market_cap=market_cap,
            notes=notes or None,
            as_of=datetime.now(),
        )

korean_market_service = KoreanMarketService()
