"""Service layer for Korean market operations."""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date, timedelta
import re
import logging
import csv
from pathlib import Path
from ..models.korean import (
    KoreanStockQuote,
    KoreanFinancialStatement,
    KoreanCandleData,
    KoreanValuationMetrics,
    KoreanEstimatePerform,
    KoreanBondQuote,
    KoreanBondValuation,
    KoreanBondMasterItem,
    KoreanFuturesOptionsMasterItem,
    KoreanFuturesOptionQuote,
    KoreanFuturesOptionReferenceIndex,
    KoreanFuturesOptionOrderbook,
    KoreanFuturesOptionOrderbookLevel,
    KoreanFuturesOptionMinuteCandle,
    KoreanFuturesOptionMinuteCandleResponse,
    KoreanFuturesOptionChainRow,
    KoreanFuturesOptionChainResponse,
)
from ..integrations.kdevelopers import kdevelopers_client
from ..integrations.bond_master import bond_master_file_manager
from ..integrations.futures_options_master import (
    futures_options_master_file_manager,
)
from ..integrations.opendart import opendart_client
from ..integrations.supabase_client import supabase_client
from .bond_analytics import bond_analytics_service

logger = logging.getLogger(__name__)

ESTIMATE_AMOUNT_UNIT = "억원"
ESTIMATE_AMOUNT_MULTIPLIER = 100_000_000


class KoreanMarketService:
    """Service for Korean market data operations."""

    _bond_master_candidates = [
        Path(__file__).parent.parent.parent
        / "data"
        / "kr_bond_master"
        / "bond_codes.csv",
        Path(__file__).parent.parent.parent
        / "data"
        / "kr_bond_master"
        / "bond_codes.tsv",
        Path(__file__).parent.parent.parent
        / "data"
        / "kr_bond_master"
        / "bond_codes.txt",
    ]
    _option_chain_min_interval_sec = 1.0
    _option_chain_cache: Dict[str, Tuple[datetime, KoreanFuturesOptionChainResponse]] = {}

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

    def _find_bond_master_file(self) -> Optional[Path]:
        for candidate in self._bond_master_candidates:
            if candidate.exists():
                return candidate
        return None

    def _normalize_master_row(self, row: Dict[str, str]) -> Optional[Dict[str, str]]:
        key_candidates = [
            "pdno",
            "code",
            "bond_code",
            "stnd_iscd",
            "표준종목코드",
            "종목코드",
        ]
        name_candidates = [
            "name",
            "bond_name",
            "ksd_bond_item_name",
            "bond_isnm",
            "종목명",
            "채권종목명",
        ]
        code = ""
        for key in key_candidates:
            value = row.get(key)
            if value:
                code = value.strip()
                break
        if not code:
            return None
        if not re.fullmatch(r"KR[0-9A-Z]{10}", code):
            return None

        name = ""
        for key in name_candidates:
            value = row.get(key)
            if value:
                name = value.strip()
                break
        return {"pdno": code, "name": name}

    def _load_bond_master_rows(
        self,
    ) -> Tuple[Optional[str], List[Dict[str, str]]]:
        # Preferred path: integration-based bond master parser (same style as stock master)
        df = bond_master_file_manager.parse_bond_master(auto_download=False)
        if df is not None and not df.empty:
            return (
                str(bond_master_file_manager.get_local_master_file()),
                df.to_dict(orient="records"),
            )

        master_file = self._find_bond_master_file()
        if not master_file:
            return None, []

        rows: List[Dict[str, str]] = []
        seen = set()

        suffix = master_file.suffix.lower()
        if suffix in {".csv", ".tsv"}:
            delimiter = "," if suffix == ".csv" else "\t"
            with open(master_file, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                for row in reader:
                    normalized = self._normalize_master_row(
                        {k.strip(): (v or "").strip() for k, v in row.items() if k}
                    )
                    if not normalized:
                        continue
                    code = normalized["pdno"]
                    if code in seen:
                        continue
                    seen.add(code)
                    rows.append(normalized)
        else:
            with open(master_file, "r", encoding="utf-8", errors="ignore") as f:
                for raw_line in f:
                    line = raw_line.strip()
                    if not line:
                        continue
                    match = re.search(r"(KR[0-9A-Z]{10})", line)
                    if not match:
                        continue
                    code = match.group(1)
                    if code in seen:
                        continue
                    name = line.replace(code, "").strip(" ,|\t-")
                    seen.add(code)
                    rows.append({"pdno": code, "name": name})

        return str(master_file), rows

    async def get_bond_price(self, pdno: str) -> Optional[KoreanBondQuote]:
        output = kdevelopers_client.get_bond_price(pdno)
        if not output:
            return None
        asking = kdevelopers_client.get_bond_asking_price(pdno) or {}
        best_ask = self._to_float(asking.get("bond_askp1"))
        best_bid = self._to_float(asking.get("bond_bidp1"))
        middle_price = None
        if best_ask is not None and best_bid is not None:
            middle_price = (best_ask + best_bid) / 2
        return KoreanBondQuote(
            pdno=output.get("stnd_iscd", pdno),
            name=output.get("hts_kor_isnm") or pdno,
            current_price=self._to_float(output.get("bond_prpr")),
            change=self._to_float(output.get("bond_prdy_vrss")),
            change_percent=self._to_float(output.get("prdy_ctrt")),
            volume=self._to_int(output.get("acml_vol")),
            high=self._to_float(output.get("bond_hgpr")),
            low=self._to_float(output.get("bond_lwpr")),
            open=self._to_float(output.get("bond_oprc")),
            previous_close=self._to_float(output.get("bond_prdy_clpr")),
            earning_rate=self._to_float(output.get("ernn_rate")),
            best_ask=best_ask,
            best_bid=best_bid,
            middle_price=middle_price,
        )

    async def get_bond_basic_info(self, pdno: str) -> Optional[Dict[str, Any]]:
        return kdevelopers_client.get_bond_basic_info(pdno)

    async def get_bond_issue_info(self, pdno: str) -> Optional[Dict[str, Any]]:
        return kdevelopers_client.get_bond_issue_info(pdno)

    async def get_bond_valuation(self, pdno: str) -> Optional[KoreanBondValuation]:
        """Compare the market price with the pricing agencies' valuation.

        The theoretical price discounts the bond's cash flows at the
        agencies' average yield, so the gap to the market price is a real
        rich/cheap signal. Prices are dirty (KRX quotes include accrued
        interest) and rescaled from the 10,000-face quote to face 100.
        """
        try:
            analytics = await bond_analytics_service.get_analytics(pdno)
        except LookupError:
            return None

        def per_100(value: Optional[float]) -> Optional[float]:
            return round(value / 100.0, 6) if value is not None else None

        notes = list(analytics.notes)
        market = per_100(analytics.reference_price)
        theoretical = per_100(analytics.agency_implied_price)
        accrued = per_100(analytics.accrued_interest)
        if analytics.supported and theoretical is None:
            notes.append("민평 수익률이 없어 이론가격을 계산하지 못했습니다.")

        mispricing = None
        mispricing_percent = None
        if market is not None and theoretical:
            mispricing = round(market - theoretical, 6)
            mispricing_percent = round(mispricing / theoretical * 100.0, 6)

        return KoreanBondValuation(
            pdno=pdno,
            name=analytics.name,
            as_of=analytics.as_of,
            raw_market_price=analytics.reference_price,
            market_price=market,
            market_price_source=analytics.reference_source,
            theoretical_dirty_price=theoretical,
            accrued_interest=accrued,
            theoretical_clean_price=round(theoretical - accrued, 6)
            if theoretical is not None and accrued is not None
            else None,
            mispricing=mispricing,
            mispricing_percent=mispricing_percent,
            annual_coupon_rate=analytics.coupon_rate,
            annual_yield_rate=analytics.agency_yield,
            payment_interval_months=analytics.interval_months,
            face_value=100.0,
            next_coupon_date=analytics.next_coupon_date,
            maturity_date=analytics.maturity_date,
            notes=notes,
        )

    async def get_bond_daily_price(
        self, pdno: str, limit: Optional[int] = None
    ) -> Optional[List[KoreanCandleData]]:
        return kdevelopers_client.get_bond_daily_price(pdno, limit=limit)

    async def get_bond_master(
        self,
        query: Optional[str] = None,
        bond_type: Optional[str] = None,
        bond_class_code: Optional[str] = None,
        bond_interest_class_code: Optional[str] = None,
        listed_date_from: Optional[str] = None,
        listed_date_to: Optional[str] = None,
        issue_date_from: Optional[str] = None,
        issue_date_to: Optional[str] = None,
        maturity_date_from: Optional[str] = None,
        maturity_date_to: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
        enrich: bool = True,
        include_quotes: bool = False,
    ) -> Dict[str, Any]:
        bond_type = (bond_type or "").strip().upper() or None
        bond_class_code = (bond_class_code or "").strip().upper() or None
        bond_interest_class_code = (
            (bond_interest_class_code or "").strip().upper() or None
        )
        listed_date_from = self._normalize_yyyymmdd(listed_date_from)
        listed_date_to = self._normalize_yyyymmdd(listed_date_to)
        issue_date_from = self._normalize_yyyymmdd(issue_date_from)
        issue_date_to = self._normalize_yyyymmdd(issue_date_to)
        maturity_date_from = self._normalize_yyyymmdd(maturity_date_from)
        maturity_date_to = self._normalize_yyyymmdd(maturity_date_to)

        source_file, rows = self._load_bond_master_rows()
        available_bond_types: Dict[str, int] = {}
        available_bond_class_codes_by_type: Dict[str, Dict[str, int]] = {}
        available_bond_interest_class_codes_by_type: Dict[str, Dict[str, int]] = {}

        for row in rows:
            row_type = str(row.get("bond_type") or "").strip().upper()
            row_class = str(row.get("bond_class_code") or "").strip().upper()
            row_interest = (
                str(row.get("bond_interest_class_code") or "").strip().upper()
            )
            if row_type:
                available_bond_types[row_type] = (
                    available_bond_types.get(row_type, 0) + 1
                )
                if row_class:
                    class_counts = available_bond_class_codes_by_type.setdefault(
                        row_type, {}
                    )
                    class_counts[row_class] = class_counts.get(row_class, 0) + 1
                if row_interest:
                    interest_counts = (
                        available_bond_interest_class_codes_by_type.setdefault(
                            row_type, {}
                        )
                    )
                    interest_counts[row_interest] = (
                        interest_counts.get(row_interest, 0) + 1
                    )

        if not rows:
            return {
                "source_file": source_file,
                "total_loaded": 0,
                "total_returned": 0,
                "offset": offset,
                "limit": limit,
                "query": query,
                "bond_type": bond_type,
                "bond_class_code": bond_class_code,
                "bond_interest_class_code": bond_interest_class_code,
                "listed_date_from": listed_date_from,
                "listed_date_to": listed_date_to,
                "issue_date_from": issue_date_from,
                "issue_date_to": issue_date_to,
                "maturity_date_from": maturity_date_from,
                "maturity_date_to": maturity_date_to,
                "available_bond_types": available_bond_types,
                "available_bond_class_codes_by_type": (
                    available_bond_class_codes_by_type
                ),
                "available_bond_interest_class_codes_by_type": (
                    available_bond_interest_class_codes_by_type
                ),
                "items": [],
            }

        if bond_type:
            rows = [
                row
                for row in rows
                if (str(row.get("bond_type") or "").strip().upper() == bond_type)
            ]

        if bond_class_code:
            rows = [
                row
                for row in rows
                if (
                    str(row.get("bond_class_code") or "").strip().upper()
                    == bond_class_code
                )
            ]

        if bond_interest_class_code:
            rows = [
                row
                for row in rows
                if (
                    str(row.get("bond_interest_class_code") or "")
                    .strip()
                    .upper()
                    == bond_interest_class_code
                )
            ]

        rows = [
            row
            for row in rows
            if self._is_in_yyyymmdd_range(
                row.get("listed_date"), listed_date_from, listed_date_to
            )
        ]
        rows = [
            row
            for row in rows
            if self._is_in_yyyymmdd_range(
                row.get("issue_date"), issue_date_from, issue_date_to
            )
        ]
        rows = [
            row
            for row in rows
            if self._is_in_yyyymmdd_range(
                row.get("maturity_date"), maturity_date_from, maturity_date_to
            )
        ]

        if query:
            q = query.strip().lower()
            rows = [
                row
                for row in rows
                if q in row["pdno"].lower() or q in (row.get("name") or "").lower()
            ]

        total_loaded = len(rows)
        sliced = rows[offset : offset + limit]

        items: List[KoreanBondMasterItem] = []
        for row in sliced:
            pdno = row["pdno"]
            name = row.get("name") or None
            info = kdevelopers_client.get_bond_basic_info(pdno) if enrich else None
            quote = kdevelopers_client.get_bond_price(pdno) if include_quotes else None
            item = KoreanBondMasterItem(
                pdno=pdno,
                bond_type=row.get("bond_type"),
                bond_class_code=row.get("bond_class_code"),
                bond_interest_class_code=row.get("bond_interest_class_code"),
                name=(info or {}).get("ksd_bond_item_name") or name,
                english_name=(info or {}).get("ksd_bond_item_eng_name"),
                bond_class_name=(info or {}).get("bond_clsf_kor_name")
                or row.get("bond_class_code"),
                issue_date=(info or {}).get("issu_dt")
                or row.get("issue_date"),
                maturity_date=(info or {}).get("rdpt_dt")
                or row.get("maturity_date"),
                listed_date=(info or {}).get("lstg_dt")
                or row.get("listed_date"),
                delisted_date=(info or {}).get("lstg_abol_dt"),
                currency=(info or {}).get("iso_crcy_cd"),
                surface_interest_rate=self._to_float(
                    (info or {}).get("ksd_rcvg_bond_srfc_inrt")
                ),
                total_issue_amount=self._to_float(
                    (info or {}).get("ksd_tot_issu_amt")
                ),
                current_price=self._to_float((quote or {}).get("bond_prpr")),
                change_percent=self._to_float((quote or {}).get("prdy_ctrt")),
                volume=self._to_int((quote or {}).get("acml_vol")),
            )
            items.append(item)

        return {
            "source_file": source_file,
            "total_loaded": total_loaded,
            "total_returned": len(items),
            "offset": offset,
            "limit": limit,
            "query": query,
            "bond_type": bond_type,
            "bond_class_code": bond_class_code,
            "bond_interest_class_code": bond_interest_class_code,
            "listed_date_from": listed_date_from,
            "listed_date_to": listed_date_to,
            "issue_date_from": issue_date_from,
            "issue_date_to": issue_date_to,
            "maturity_date_from": maturity_date_from,
            "maturity_date_to": maturity_date_to,
            "available_bond_types": available_bond_types,
            "available_bond_class_codes_by_type": (
                available_bond_class_codes_by_type
            ),
            "available_bond_interest_class_codes_by_type": (
                available_bond_interest_class_codes_by_type
            ),
            "items": items,
        }

    async def refresh_bond_master(
        self,
        output_format: str = "csv",
        force: bool = False,
        source_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Download latest bond master and export as csv/json."""
        return bond_master_file_manager.refresh_and_export(
            output_format=output_format,
            force=force,
            source_url=source_url,
        )

    async def get_futures_options_master(
        self,
        market: str = "all",
        query: Optional[str] = None,
        info_type: Optional[str] = None,
        underlying_short_code: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
        auto_download: bool = False,
        force_download: bool = False,
    ) -> Dict[str, Any]:
        market_key = (market or "all").strip().lower()
        if market_key not in {"all", "index", "stock", "commodity"}:
            raise ValueError("market must be one of: all/index/stock/commodity")

        target_markets = (
            ["index", "stock", "commodity"]
            if market_key == "all"
            else [market_key]
        )
        source_files: Dict[str, Optional[str]] = {}
        available_markets: Dict[str, int] = {}
        available_info_types_by_market: Dict[str, Dict[str, int]] = {}
        rows: List[Dict[str, Any]] = []

        for one_market in target_markets:
            # Contracts are relisted daily; a stale file names expired months.
            futures_options_master_file_manager.ensure_fresh(one_market)
            local_file = futures_options_master_file_manager.get_local_master_file(
                one_market
            )
            source_files[one_market] = str(local_file) if local_file else None

            market_rows = futures_options_master_file_manager.get_market_rows(
                one_market,
                auto_download=auto_download,
                force_download=force_download,
            )
            available_markets[one_market] = len(market_rows)
            info_counts: Dict[str, int] = {}
            for row in market_rows:
                row_info_type = str(row.get("info_type") or "").strip().upper()
                if row_info_type:
                    info_counts[row_info_type] = info_counts.get(row_info_type, 0) + 1
                row["market"] = one_market
                rows.append(row)
            available_info_types_by_market[one_market] = info_counts

        normalized_info_type = (info_type or "").strip().upper() or None
        normalized_underlying_code = (
            (underlying_short_code or "").strip().upper() or None
        )

        if normalized_info_type:
            rows = [
                row
                for row in rows
                if str(row.get("info_type") or "").strip().upper()
                == normalized_info_type
            ]

        if normalized_underlying_code:
            rows = [
                row
                for row in rows
                if str(row.get("underlying_short_code") or "").strip().upper()
                == normalized_underlying_code
            ]

        if query:
            needle = query.strip().lower()
            rows = [
                row
                for row in rows
                if needle in str(row.get("short_code") or "").lower()
                or needle in str(row.get("standard_code") or "").lower()
                or needle in str(row.get("name_kr") or "").lower()
                or needle in str(row.get("underlying_name_kr") or "").lower()
            ]

        total_loaded = len(rows)
        sliced = rows[offset : offset + limit]
        items = [KoreanFuturesOptionsMasterItem(**row) for row in sliced]

        return {
            "market": market_key,
            "source_files": source_files,
            "total_loaded": total_loaded,
            "total_returned": len(items),
            "offset": offset,
            "limit": limit,
            "query": query,
            "info_type": normalized_info_type,
            "underlying_short_code": normalized_underlying_code,
            "available_markets": available_markets,
            "available_info_types_by_market": available_info_types_by_market,
            "items": items,
        }

    async def refresh_futures_options_master(
        self,
        market: str = "all",
        output_format: str = "csv",
        force: bool = False,
    ) -> Dict[str, Any]:
        return futures_options_master_file_manager.refresh_and_export(
            market=market,
            output_format=output_format,
            force=force,
        )

    async def get_futures_option_quote(
        self,
        symbol: str,
        market_div_code: str = "F",
    ) -> Optional[KoreanFuturesOptionQuote]:
        """Get normalized domestic futures/options quote."""
        raw = kdevelopers_client.get_future_option_quote(
            symbol=symbol, market_div_code=market_div_code
        )
        if not raw:
            return None

        output1 = raw.get("output1") or {}
        reference_indices: List[KoreanFuturesOptionReferenceIndex] = []
        for output_key in ("output2", "output3"):
            index_raw = raw.get(output_key) or {}
            if not index_raw:
                continue
            reference_indices.append(
                KoreanFuturesOptionReferenceIndex(
                    code=index_raw.get("bstp_cls_code"),
                    name=index_raw.get("hts_kor_isnm"),
                    current_price=self._to_float(index_raw.get("bstp_nmix_prpr")),
                    change_sign=index_raw.get("prdy_vrss_sign"),
                    change=self._to_float(index_raw.get("bstp_nmix_prdy_vrss")),
                    change_percent=self._to_float(
                        index_raw.get("bstp_nmix_prdy_ctrt")
                    ),
                )
            )

        return KoreanFuturesOptionQuote(
            symbol=symbol,
            market_div_code=market_div_code,
            name=output1.get("hts_kor_isnm"),
            current_price=self._to_float(output1.get("futs_prpr")),
            change_sign=output1.get("prdy_vrss_sign"),
            change=self._to_float(output1.get("futs_prdy_vrss")),
            change_percent=self._to_float(output1.get("futs_prdy_ctrt")),
            previous_close=self._to_float(output1.get("futs_prdy_clpr")),
            volume=self._to_int(output1.get("acml_vol")),
            trading_value=self._to_float(output1.get("acml_tr_pbmn")),
            open_interest=self._to_int(output1.get("hts_otst_stpl_qty")),
            open_interest_change=self._to_int(output1.get("otst_stpl_qty_icdc")),
            open=self._to_float(output1.get("futs_oprc")),
            high=self._to_float(output1.get("futs_hgpr")),
            low=self._to_float(output1.get("futs_lwpr")),
            upper_limit=self._to_float(output1.get("futs_mxpr")),
            lower_limit=self._to_float(output1.get("futs_llam")),
            theoretical_price=self._to_float(output1.get("hts_thpr")),
            basis=self._to_float(output1.get("basis")),
            market_basis=self._to_float(output1.get("mrkt_basis")),
            discrepancy_rate=self._to_float(output1.get("dprt")),
            strike_price=self._to_float(output1.get("acpr")),
            delta=self._to_float(output1.get("delta_val")),
            gamma=self._to_float(output1.get("gama")),
            theta=self._to_float(output1.get("theta")),
            vega=self._to_float(output1.get("vega")),
            rho=self._to_float(output1.get("rho")),
            historical_volatility=self._to_float(output1.get("hist_vltl")),
            implied_volatility=self._to_float(output1.get("hts_ints_vltl")),
            last_trade_date=output1.get("futs_last_tr_date"),
            remaining_days=self._to_int(output1.get("hts_rmnn_dynu")),
            reference_indices=reference_indices,
        )

    async def get_futures_option_orderbook(
        self,
        symbol: str,
        market_div_code: str = "F",
    ) -> Optional[KoreanFuturesOptionOrderbook]:
        """Get normalized domestic futures/options orderbook (5 levels)."""
        raw = kdevelopers_client.get_future_option_orderbook(
            symbol=symbol, market_div_code=market_div_code
        )
        if not raw:
            return None

        output1 = raw.get("output1") or {}
        output2 = raw.get("output2") or {}
        levels: List[KoreanFuturesOptionOrderbookLevel] = []
        for level in range(1, 6):
            levels.append(
                KoreanFuturesOptionOrderbookLevel(
                    level=level,
                    ask_price=self._to_float(output2.get(f"futs_askp{level}")),
                    ask_quantity=self._to_int(output2.get(f"askp_rsqn{level}")),
                    ask_orders=self._to_int(output2.get(f"askp_csnu{level}")),
                    bid_price=self._to_float(output2.get(f"futs_bidp{level}")),
                    bid_quantity=self._to_int(output2.get(f"bidp_rsqn{level}")),
                    bid_orders=self._to_int(output2.get(f"bidp_csnu{level}")),
                )
            )

        return KoreanFuturesOptionOrderbook(
            symbol=symbol,
            market_div_code=market_div_code,
            name=output1.get("hts_kor_isnm"),
            current_price=self._to_float(output1.get("futs_prpr")),
            change_sign=output1.get("prdy_vrss_sign"),
            change=self._to_float(output1.get("futs_prdy_vrss")),
            change_percent=self._to_float(output1.get("futs_prdy_ctrt")),
            previous_close=self._to_float(output1.get("futs_prdy_clpr")),
            volume=self._to_int(output1.get("acml_vol")),
            as_of_time=output2.get("aspr_acpt_hour"),
            total_ask_quantity=self._to_int(output2.get("total_askp_rsqn")),
            total_bid_quantity=self._to_int(output2.get("total_bidp_rsqn")),
            total_ask_orders=self._to_int(output2.get("total_askp_csnu")),
            total_bid_orders=self._to_int(output2.get("total_bidp_csnu")),
            levels=levels,
        )

    async def get_futures_option_minute_candles(
        self,
        symbol: str,
        market_div_code: str = "F",
        timeframe_sec: int = 60,
        date_value: Optional[str] = None,
        time_value: Optional[str] = None,
        include_previous: bool = True,
        include_fake_tick: bool = False,
        limit: Optional[int] = None,
    ) -> Optional[KoreanFuturesOptionMinuteCandleResponse]:
        """Get normalized domestic futures/options intraday candle data."""
        raw = kdevelopers_client.get_future_option_minute_candles(
            symbol=symbol,
            market_div_code=market_div_code,
            timeframe_sec=timeframe_sec,
            include_previous=include_previous,
            include_fake_tick=include_fake_tick,
            date=date_value,
            time_str=time_value,
        )
        if not raw:
            return None

        output1 = raw.get("output1") or {}
        rows = raw.get("output2") or []
        if limit is not None:
            rows = rows[:limit]

        candles: List[KoreanFuturesOptionMinuteCandle] = []
        for row in rows:
            row_date = str(row.get("stck_bsop_date") or "").strip() or None
            row_time = str(row.get("stck_cntg_hour") or "").strip() or None
            timestamp = f"{row_date}{row_time}" if row_date and row_time else None
            candles.append(
                KoreanFuturesOptionMinuteCandle(
                    symbol=symbol,
                    market_div_code=market_div_code,
                    date=row_date,
                    time=row_time,
                    timestamp=timestamp,
                    open=self._to_float(row.get("futs_oprc")),
                    high=self._to_float(row.get("futs_hgpr")),
                    low=self._to_float(row.get("futs_lwpr")),
                    close=self._to_float(row.get("futs_prpr")),
                    volume=self._to_int(row.get("cntg_vol")),
                    cumulative_trading_value=self._to_float(
                        row.get("acml_tr_pbmn")
                    ),
                )
            )

        return KoreanFuturesOptionMinuteCandleResponse(
            symbol=symbol,
            market_div_code=market_div_code,
            timeframe_sec=timeframe_sec,
            date=date_value,
            time=time_value,
            name=output1.get("hts_kor_isnm"),
            current_price=self._to_float(output1.get("futs_prpr")),
            change=self._to_float(output1.get("futs_prdy_vrss")),
            change_sign=output1.get("prdy_vrss_sign"),
            change_percent=self._to_float(output1.get("futs_prdy_ctrt")),
            volume=self._to_int(output1.get("acml_vol")),
            open_interest=self._to_int(output1.get("hts_otst_stpl_qty")),
            open_interest_change=self._to_int(output1.get("otst_stpl_qty_icdc")),
            candles=candles,
        )

    async def get_futures_option_daily_candles(
        self,
        symbol: str,
        market_div_code: str = "F",
        period_code: str = "D",
        limit: Optional[int] = None,
        input_date: Optional[str] = None,
        input_date_to: Optional[str] = None,
    ) -> Optional[List[KoreanCandleData]]:
        """Get normalized domestic futures/options daily/period candle data."""
        raw = kdevelopers_client.get_future_option_daily_candles(
            symbol=symbol,
            market_div_code=market_div_code,
            period_code=period_code,
            input_date=input_date,
            input_date_to=input_date_to,
        )
        if not raw:
            return None

        rows = raw.get("output2") or raw.get("output") or []
        if not rows:
            output1 = raw.get("output1") or {}
            one_row = self._output_to_daily_candle_row(output1)
            rows = [one_row] if one_row else []

        candles: List[KoreanCandleData] = []
        for row in rows:
            row_date = self._extract_daily_candle_date(row)
            if not row_date:
                continue

            candles.append(
                KoreanCandleData(
                    symbol=symbol,
                    date=row_date,
                    open=self._to_float(
                        row.get("futs_oprc")
                        or row.get("optn_oprc")
                        or row.get("stck_oprc")
                        or row.get("open")
                    )
                    or 0.0,
                    high=self._to_float(
                        row.get("futs_hgpr")
                        or row.get("optn_hgpr")
                        or row.get("stck_hgpr")
                        or row.get("high")
                    )
                    or 0.0,
                    low=self._to_float(
                        row.get("futs_lwpr")
                        or row.get("optn_lwpr")
                        or row.get("stck_lwpr")
                        or row.get("low")
                    )
                    or 0.0,
                    close=self._to_float(
                        row.get("futs_prpr")
                        or row.get("optn_prpr")
                        or row.get("stck_clpr")
                        or row.get("stck_prpr")
                        or row.get("close")
                    )
                    or 0.0,
                    volume=self._to_int(
                        row.get("acml_vol")
                        or row.get("cntg_vol")
                        or row.get("volume")
                    )
                    or 0,
                    change=self._to_float(
                        row.get("futs_prdy_vrss")
                        or row.get("optn_prdy_vrss")
                        or row.get("prdy_vrss")
                        or row.get("change")
                    ),
                    change_percent=self._to_float(
                        row.get("futs_prdy_ctrt")
                        or row.get("optn_prdy_ctrt")
                        or row.get("prdy_ctrt")
                        or row.get("change_percent")
                    ),
                )
            )

        candles.sort(key=lambda candle: candle.date, reverse=True)
        if limit is not None:
            candles = candles[:limit]
        return candles or None

    async def get_futures_option_chain(
        self,
        expiry: str,
        market_class: str = "",
    ) -> Optional[KoreanFuturesOptionChainResponse]:
        """Get normalized domestic option chain (call/put), with light throttling."""
        normalized_market_class = (market_class or "").strip().upper()
        cache_key = f"{expiry}|{normalized_market_class}"
        now = datetime.now()
        cached = self._option_chain_cache.get(cache_key)
        if cached:
            cached_at, cached_resp = cached
            if (now - cached_at).total_seconds() < self._option_chain_min_interval_sec:
                return cached_resp

        raw = kdevelopers_client.get_future_option_callput(
            expiry=expiry,
            market_class=normalized_market_class,
        )
        if not raw:
            return None

        def to_chain_rows(rows: List[Dict[str, Any]]) -> List[KoreanFuturesOptionChainRow]:
            return [
                KoreanFuturesOptionChainRow(
                    option_code=row.get("optn_shrn_iscd"),
                    strike_price=self._to_float(row.get("acpr")),
                    current_price=self._to_float(row.get("optn_prpr")),
                    change_sign=row.get("prdy_vrss_sign"),
                    change=self._to_float(row.get("optn_prdy_vrss")),
                    change_percent=self._to_float(row.get("optn_prdy_ctrt")),
                    bid_price=self._to_float(row.get("optn_bidp")),
                    ask_price=self._to_float(row.get("optn_askp")),
                    volume=self._to_int(row.get("acml_vol")),
                    trading_value=self._to_float(row.get("acml_tr_pbmn")),
                    open_interest=self._to_int(row.get("hts_otst_stpl_qty")),
                    open_interest_change=self._to_int(row.get("otst_stpl_qty_icdc")),
                    delta=self._to_float(row.get("delta_val")),
                    gamma=self._to_float(row.get("gama")),
                    theta=self._to_float(row.get("theta")),
                    vega=self._to_float(row.get("vega")),
                    rho=self._to_float(row.get("rho")),
                    implied_volatility=self._to_float(row.get("hts_ints_vltl")),
                    historical_volatility=self._to_float(row.get("hist_vltl")),
                    theoretical_price=self._to_float(row.get("hts_thpr")),
                    intrinsic_value=self._to_float(row.get("invl_val")),
                    time_value=self._to_float(row.get("tmvl_val")),
                    moneyness=row.get("atm_cls_name"),
                )
                for row in rows
            ]

        calls = to_chain_rows(raw.get("output1") or [])
        puts = to_chain_rows(raw.get("output2") or [])
        resp = KoreanFuturesOptionChainResponse(
            expiry=expiry,
            market_class=normalized_market_class,
            fetched_at=now,
            total_calls=len(calls),
            total_puts=len(puts),
            calls=calls,
            puts=puts,
        )
        self._option_chain_cache[cache_key] = (now, resp)
        return resp

    def _to_float(self, value: Any) -> Optional[float]:
        try:
            if value is None:
                return None
            text = str(value).replace(",", "").strip()
            if not text:
                return None
            return float(text)
        except (TypeError, ValueError):
            return None

    def _to_int(self, value: Any) -> Optional[int]:
        try:
            if value is None:
                return None
            text = str(value).replace(",", "").strip()
            if not text:
                return None
            return int(float(text))
        except (TypeError, ValueError):
            return None

    def _extract_daily_candle_date(self, row: Dict[str, Any]) -> Optional[str]:
        for key in (
            "stck_bsop_date",
            "futs_bsop_date",
            "optn_bsop_date",
            "bass_dt",
            "date",
        ):
            value = str(row.get(key) or "").strip()
            if re.fullmatch(r"\d{8}", value):
                return value
        return None

    def _output_to_daily_candle_row(
        self, row: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        if not row:
            return None
        if not self._extract_daily_candle_date(row):
            return None
        return row

    def _normalize_yyyymmdd(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        if re.fullmatch(r"\d{8}", text):
            return text
        return None

    def _is_in_yyyymmdd_range(
        self,
        value: Any,
        start: Optional[str],
        end: Optional[str],
    ) -> bool:
        if not start and not end:
            return True
        raw = str(value or "").strip()
        if not re.fullmatch(r"\d{8}", raw):
            return False
        if start and raw < start:
            return False
        if end and raw > end:
            return False
        return True


korean_market_service = KoreanMarketService()
