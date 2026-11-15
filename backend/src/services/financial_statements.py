"""Service for managing financial statement data insertion to Supabase."""

import logging
from typing import Callable, Optional, Dict, Any, List
from ..integrations.supabase_client import supabase_client
from ..integrations.opendart import opendart_client
from ..integrations.yfinance_client import yfinance_client

logger = logging.getLogger(__name__)


class FinancialStatementService:
    """Service for handling financial statement data operations."""

    def __init__(self):
        """Initialize the financial statement service."""
        self.supabase = supabase_client
        self.opendart = opendart_client
        self.yfinance = yfinance_client

    # Unique key of every statement table (database/financial_statements.sql).
    # Annual rows have quarter NULL; the constraint is NULLS NOT DISTINCT, so
    # they are updated in place like quarterly rows instead of piling up.
    CONFLICT_COLUMNS = "symbol,year,quarter"

    @property
    def is_configured(self) -> bool:
        """Whether a Supabase client is available to store statements."""
        return self.supabase.client is not None

    def _upsert(self, table: str, row: Dict[str, Any]) -> None:
        """Insert or update one statement row keyed by symbol/year/quarter."""
        self.supabase.client.table(table).upsert(
            row, on_conflict=self.CONFLICT_COLUMNS
        ).execute()

    # =========================================================================
    # Korean Financial Statements (OPENDART)
    # =========================================================================

    def insert_korean_balance_sheet(
        self, symbol: str, year: int, quarter: Optional[int] = None
    ) -> bool:
        """
        Fetch and insert Korean balance sheet data.

        Args:
            symbol: Korean stock code (e.g., "005930")
            year: Fiscal year
            quarter: Optional quarter (1-4)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured:
            logger.error("Supabase client not initialized")
            return False

        try:
            # Get raw balance sheet data from OPENDART
            raw_data = self.opendart.get_balance_sheet(symbol, year, quarter)

            if not raw_data:
                logger.warning(
                    f"No balance sheet data for {symbol} ({year}Q{quarter or 'Annual'})"
                )
                return False

            # Parse and map data
            balance_sheet_data = self._parse_korean_balance_sheet(
                symbol, year, quarter, raw_data
            )

            self._upsert("korean_balance_sheet", balance_sheet_data)

            logger.info(
                f"✅ Inserted Korean balance sheet: {symbol} ({year}Q{quarter or 'Annual'})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to insert Korean balance sheet: {e}")
            return False

    def insert_korean_income_statement(
        self, symbol: str, year: int, quarter: Optional[int] = None
    ) -> bool:
        """
        Fetch and insert Korean income statement data.

        Args:
            symbol: Korean stock code
            year: Fiscal year
            quarter: Optional quarter (1-4)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured:
            logger.error("Supabase client not initialized")
            return False

        try:
            # Get raw income statement data from OPENDART
            raw_data = self.opendart.get_income_statement(
                symbol, year, quarter
            )

            if not raw_data:
                logger.warning(
                    f"No income statement data for {symbol} ({year}Q{quarter or 'Annual'})"
                )
                return False

            # Parse and map data
            income_statement_data = self._parse_korean_income_statement(
                symbol, year, quarter, raw_data
            )

            self._upsert("korean_income_statement", income_statement_data)

            logger.info(
                f"✅ Inserted Korean income statement: {symbol} ({year}Q{quarter or 'Annual'})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to insert Korean income statement: {e}")
            return False

    def insert_korean_cashflow_statement(
        self, symbol: str, year: int, quarter: Optional[int] = None
    ) -> bool:
        """
        Fetch and insert Korean cash flow statement data.

        Args:
            symbol: Korean stock code
            year: Fiscal year
            quarter: Optional quarter (1-4)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured:
            logger.error("Supabase client not initialized")
            return False

        try:
            # Get raw cash flow data from OPENDART
            raw_data = self.opendart.get_cash_flow(symbol, year, quarter)

            if not raw_data:
                logger.warning(
                    f"No cash flow data for {symbol} ({year}Q{quarter or 'Annual'})"
                )
                return False

            # Parse and map data
            cashflow_data = self._parse_korean_cashflow_statement(
                symbol, year, quarter, raw_data
            )

            self._upsert("korean_cashflow_statement", cashflow_data)

            logger.info(
                f"✅ Inserted Korean cash flow: {symbol} ({year}Q{quarter or 'Annual'})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to insert Korean cash flow: {e}")
            return False

    def insert_all_korean_statements(
        self, symbol: str, year: int, quarter: Optional[int] = None
    ) -> Dict[str, bool]:
        """
        Insert all financial statements for a Korean company.

        Args:
            symbol: Korean stock code
            year: Fiscal year
            quarter: Optional quarter (1-4)

        Returns:
            Dictionary with results for each statement type
        """
        results = {
            "balance_sheet": self.insert_korean_balance_sheet(
                symbol, year, quarter
            ),
            "income_statement": self.insert_korean_income_statement(
                symbol, year, quarter
            ),
            "cashflow_statement": self.insert_korean_cashflow_statement(
                symbol, year, quarter
            ),
        }

        success_count = sum(1 for v in results.values() if v)
        logger.info(
            f"Inserted {success_count}/3 statements for {symbol} ({year}Q{quarter or 'Annual'})"
        )

        return results

    # =========================================================================
    # US Financial Statements (yfinance)
    # =========================================================================

    def insert_us_balance_sheet(
        self, symbol: str, year: int, quarter: Optional[int] = None
    ) -> bool:
        """
        Fetch and insert US balance sheet data.

        Args:
            symbol: US stock ticker (e.g., "AAPL")
            year: Fiscal year
            quarter: Optional quarter (1-4)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured:
            logger.error("Supabase client not initialized")
            return False

        try:
            import yfinance as yf

            ticker = yf.Ticker(symbol)

            # Get balance sheet data
            if quarter:
                balance_sheet_df = ticker.quarterly_balance_sheet
            else:
                balance_sheet_df = ticker.balance_sheet

            if balance_sheet_df is None or balance_sheet_df.empty:
                logger.warning(f"No balance sheet data for {symbol}")
                return False

            # Find the column matching the year
            target_col = self._find_matching_date_column(
                balance_sheet_df, year, quarter
            )
            if target_col is None:
                logger.warning(
                    f"No data found for {symbol} year {year} quarter {quarter}"
                )
                return False

            # Parse and map data
            balance_sheet_data = self._parse_us_balance_sheet(
                symbol, year, quarter, balance_sheet_df, target_col
            )

            self._upsert("us_balance_sheet", balance_sheet_data)

            logger.info(
                f"✅ Inserted US balance sheet: {symbol} ({year}Q{quarter or 'Annual'})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to insert US balance sheet: {e}")
            return False

    def insert_us_income_statement(
        self, symbol: str, year: int, quarter: Optional[int] = None
    ) -> bool:
        """
        Fetch and insert US income statement data.

        Args:
            symbol: US stock ticker
            year: Fiscal year
            quarter: Optional quarter (1-4)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured:
            logger.error("Supabase client not initialized")
            return False

        try:
            import yfinance as yf

            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Get income statement data
            if quarter:
                financials_df = ticker.quarterly_financials
            else:
                financials_df = ticker.financials

            if financials_df is None or financials_df.empty:
                logger.warning(f"No income statement data for {symbol}")
                return False

            # Find the column matching the year
            target_col = self._find_matching_date_column(
                financials_df, year, quarter
            )
            if target_col is None:
                logger.warning(
                    f"No data found for {symbol} year {year} quarter {quarter}"
                )
                return False

            # Parse and map data
            income_statement_data = self._parse_us_income_statement(
                symbol, year, quarter, financials_df, target_col, info
            )

            self._upsert("us_income_statement", income_statement_data)

            logger.info(
                f"✅ Inserted US income statement: {symbol} ({year}Q{quarter or 'Annual'})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to insert US income statement: {e}")
            return False

    def insert_us_cashflow_statement(
        self, symbol: str, year: int, quarter: Optional[int] = None
    ) -> bool:
        """
        Fetch and insert US cash flow statement data.

        Args:
            symbol: US stock ticker
            year: Fiscal year
            quarter: Optional quarter (1-4)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured:
            logger.error("Supabase client not initialized")
            return False

        try:
            import yfinance as yf

            ticker = yf.Ticker(symbol)

            # Get cash flow data
            if quarter:
                cashflow_df = ticker.quarterly_cashflow
            else:
                cashflow_df = ticker.cashflow

            if cashflow_df is None or cashflow_df.empty:
                logger.warning(f"No cash flow data for {symbol}")
                return False

            # Find the column matching the year
            target_col = self._find_matching_date_column(
                cashflow_df, year, quarter
            )
            if target_col is None:
                logger.warning(
                    f"No data found for {symbol} year {year} quarter {quarter}"
                )
                return False

            # Parse and map data
            cashflow_data = self._parse_us_cashflow_statement(
                symbol, year, quarter, cashflow_df, target_col
            )

            self._upsert("us_cashflow_statement", cashflow_data)

            logger.info(
                f"✅ Inserted US cash flow: {symbol} ({year}Q{quarter or 'Annual'})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to insert US cash flow: {e}")
            return False

    def insert_all_us_statements(
        self, symbol: str, year: int, quarter: Optional[int] = None
    ) -> Dict[str, bool]:
        """
        Insert all financial statements for a US company.

        Args:
            symbol: US stock ticker
            year: Fiscal year
            quarter: Optional quarter (1-4)

        Returns:
            Dictionary with results for each statement type
        """
        results = {
            "balance_sheet": self.insert_us_balance_sheet(
                symbol, year, quarter
            ),
            "income_statement": self.insert_us_income_statement(
                symbol, year, quarter
            ),
            "cashflow_statement": self.insert_us_cashflow_statement(
                symbol, year, quarter
            ),
        }

        success_count = sum(1 for v in results.values() if v)
        logger.info(
            f"Inserted {success_count}/3 statements for {symbol} ({year}Q{quarter or 'Annual'})"
        )

        return results

    # =========================================================================
    # Batch insertion
    # =========================================================================

    def batch_insert_korean_statements(
        self, symbols: List[str], year: int, quarters: Optional[List[int]]
    ) -> Dict[str, Any]:
        """Insert Korean statements for several symbols and periods."""
        return self._batch_insert(
            self.insert_all_korean_statements, symbols, year, quarters
        )

    def batch_insert_us_statements(
        self, symbols: List[str], year: int, quarters: Optional[List[int]]
    ) -> Dict[str, Any]:
        """Insert US statements for several symbols and periods."""
        return self._batch_insert(
            self.insert_all_us_statements, symbols, year, quarters
        )

    @staticmethod
    def _batch_insert(
        insert_all: Callable[[str, int, Optional[int]], Dict[str, bool]],
        symbols: List[str],
        year: int,
        quarters: Optional[List[int]],
    ) -> Dict[str, Any]:
        """Run insert_all per symbol/period and summarise honestly.

        ``success`` is true only when every requested symbol/period stored at
        least one statement (the same rule as the single-insert endpoint).
        """
        periods: List[Optional[int]] = (
            [None] if quarters is None else list(quarters)
        )
        results: Dict[str, Dict[str, Dict[str, bool]]] = {}
        stored = 0
        attempted = 0
        failed_periods: List[str] = []

        for symbol in symbols:
            symbol_results: Dict[str, Dict[str, bool]] = {}
            for quarter in periods:
                period_key = f"{year}Q{quarter}" if quarter else str(year)
                outcome = insert_all(symbol, year, quarter)
                symbol_results[period_key] = outcome
                stored += sum(1 for ok in outcome.values() if ok)
                attempted += len(outcome)
                if not any(outcome.values()):
                    failed_periods.append(f"{symbol} {period_key}")
            results[symbol] = symbol_results

        return {
            "success": bool(results) and not failed_periods,
            "stored": stored,
            "attempted": attempted,
            "failed": failed_periods,
            "results": results,
        }

    # =========================================================================
    # Helper Methods - Korean Data Parsing
    # =========================================================================

    def _parse_korean_balance_sheet(
        self,
        symbol: str,
        year: int,
        quarter: Optional[int],
        raw_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Parse OPENDART balance sheet data into database format."""
        # Korean account name mapping
        mapping = {
            "자산총계": "total_assets",
            "유동자산": "current_assets",
            "현금및현금성자산": "cash_and_cash_equivalents",
            "단기금융상품": "short_term_financial_instruments",
            "매출채권": "accounts_receivable",
            "재고자산": "inventory",
            "비유동자산": "non_current_assets",
            "장기금융상품": "long_term_financial_instruments",
            "유형자산": "property_plant_equipment",
            "무형자산": "intangible_assets",
            "부채총계": "total_liabilities",
            "유동부채": "current_liabilities",
            "매입채무": "accounts_payable",
            "단기차입금": "short_term_debt",
            "비유동부채": "non_current_liabilities",
            "장기차입금": "long_term_debt",
            "자본총계": "total_equity",
            "자본금": "paid_in_capital",
            "이익잉여금": "retained_earnings",
        }

        # Get company name from OPENDART
        corp_code = self.opendart.get_corp_code(symbol)
        company_info = (
            self.opendart.get_company_info(symbol) if corp_code else None
        )
        company_name = (
            company_info.get("corp_name", symbol) if company_info else symbol
        )

        # Map fields
        data = {
            "symbol": symbol,
            "company_name": company_name,
            "year": year,
            "quarter": quarter,
            "raw_data": raw_data,
        }

        # Map account values
        for kr_name, field_name in mapping.items():
            for account_name, value in raw_data.items():
                if kr_name in account_name and value is not None:
                    data[field_name] = value
                    break

        return data

    def _parse_korean_income_statement(
        self,
        symbol: str,
        year: int,
        quarter: Optional[int],
        raw_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Parse OPENDART income statement data into database format."""
        mapping = {
            "매출액": "revenue",
            "매출원가": "cost_of_revenue",
            "매출총이익": "gross_profit",
            "판매비와관리비": "selling_general_admin",
            "연구개발비": "research_development",
            "영업이익": "operating_income",
            "법인세비용차감전순이익": "income_before_tax",
            "법인세비용": "income_tax_expense",
            "당기순이익": "net_income",
        }

        corp_code = self.opendart.get_corp_code(symbol)
        company_info = (
            self.opendart.get_company_info(symbol) if corp_code else None
        )
        company_name = (
            company_info.get("corp_name", symbol) if company_info else symbol
        )

        data = {
            "symbol": symbol,
            "company_name": company_name,
            "year": year,
            "quarter": quarter,
            "raw_data": raw_data,
        }

        for kr_name, field_name in mapping.items():
            for account_name, value in raw_data.items():
                if kr_name in account_name and value is not None:
                    data[field_name] = value
                    break

        return data

    def _parse_korean_cashflow_statement(
        self,
        symbol: str,
        year: int,
        quarter: Optional[int],
        raw_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Parse OPENDART cash flow data into database format."""
        mapping = {
            "영업활동현금흐름": "operating_cash_flow",
            "당기순이익": "net_income_for_cf",
            "감가상각비": "depreciation_amortization",
            "투자활동현금흐름": "investing_cash_flow",
            "유형자산의취득": "capital_expenditure",
            "재무활동현금흐름": "financing_cash_flow",
            "배당금지급": "dividends_paid",
        }

        corp_code = self.opendart.get_corp_code(symbol)
        company_info = (
            self.opendart.get_company_info(symbol) if corp_code else None
        )
        company_name = (
            company_info.get("corp_name", symbol) if company_info else symbol
        )

        data = {
            "symbol": symbol,
            "company_name": company_name,
            "year": year,
            "quarter": quarter,
            "raw_data": raw_data,
        }

        for kr_name, field_name in mapping.items():
            for account_name, value in raw_data.items():
                if kr_name in account_name and value is not None:
                    data[field_name] = value
                    break

        return data

    # =========================================================================
    # Helper Methods - US Data Parsing
    # =========================================================================

    def _find_matching_date_column(
        self, df, year: int, quarter: Optional[int]
    ):
        """Find the column in DataFrame matching the specified year/quarter."""
        for col in df.columns:
            if col.year == year:
                if quarter is None:
                    return col
                elif quarter and col.month in [3, 6, 9, 12]:
                    # Match quarter based on month
                    q = (col.month - 1) // 3 + 1
                    if q == quarter:
                        return col
        return None

    def _safe_get_value(self, df, index_name: str, column) -> Optional[float]:
        """Safely get value from DataFrame."""
        try:
            if index_name in df.index:
                value = df.loc[index_name, column]
                if value is not None and not (
                    isinstance(value, float) and value != value
                ):  # Check for NaN
                    return float(value)
        except Exception:
            pass
        return None

    def _parse_us_balance_sheet(
        self, symbol: str, year: int, quarter: Optional[int], df, target_col
    ) -> Dict[str, Any]:
        """Parse yfinance balance sheet data into database format."""
        # Get company info
        import yfinance as yf

        ticker = yf.Ticker(symbol)
        company_name = ticker.info.get("longName", symbol)

        # Map yfinance fields to database fields
        data = {
            "symbol": symbol,
            "company_name": company_name,
            "year": year,
            "quarter": quarter,
            "total_assets": self._safe_get_value(
                df, "Total Assets", target_col
            ),
            "current_assets": self._safe_get_value(
                df, "Current Assets", target_col
            ),
            "cash_and_cash_equivalents": self._safe_get_value(
                df, "Cash And Cash Equivalents", target_col
            ),
            "receivables": self._safe_get_value(df, "Receivables", target_col),
            "inventory": self._safe_get_value(df, "Inventory", target_col),
            "property_plant_equipment": self._safe_get_value(
                df, "Gross PPE", target_col
            ),
            "goodwill": self._safe_get_value(df, "Goodwill", target_col),
            "intangible_assets": self._safe_get_value(
                df, "Other Intangible Assets", target_col
            ),
            "total_liabilities": self._safe_get_value(
                df, "Total Liabilities Net Minority Interest", target_col
            ),
            "current_liabilities": self._safe_get_value(
                df, "Current Liabilities", target_col
            ),
            "accounts_payable": self._safe_get_value(
                df, "Accounts Payable", target_col
            ),
            "long_term_debt": self._safe_get_value(
                df, "Long Term Debt", target_col
            ),
            "stockholders_equity": self._safe_get_value(
                df, "Stockholders Equity", target_col
            ),
            "common_stock": self._safe_get_value(
                df, "Common Stock", target_col
            ),
            "retained_earnings": self._safe_get_value(
                df, "Retained Earnings", target_col
            ),
            "raw_data": self._convert_series_to_json(df[target_col]),
        }

        return data

    def _parse_us_income_statement(
        self,
        symbol: str,
        year: int,
        quarter: Optional[int],
        df,
        target_col,
        info: Dict,
    ) -> Dict[str, Any]:
        """Parse yfinance income statement data into database format."""
        company_name = info.get("longName", symbol)

        data = {
            "symbol": symbol,
            "company_name": company_name,
            "year": year,
            "quarter": quarter,
            "total_revenue": self._safe_get_value(
                df, "Total Revenue", target_col
            ),
            "cost_of_revenue": self._safe_get_value(
                df, "Cost Of Revenue", target_col
            ),
            "gross_profit": self._safe_get_value(
                df, "Gross Profit", target_col
            ),
            "operating_expense": self._safe_get_value(
                df, "Operating Expense", target_col
            ),
            "selling_general_admin": self._safe_get_value(
                df, "Selling General And Administration", target_col
            ),
            "research_development": self._safe_get_value(
                df, "Research And Development", target_col
            ),
            "operating_income": self._safe_get_value(
                df, "Operating Income", target_col
            ),
            "interest_income": self._safe_get_value(
                df, "Interest Income", target_col
            ),
            "interest_expense": self._safe_get_value(
                df, "Interest Expense", target_col
            ),
            "pretax_income": self._safe_get_value(
                df, "Pretax Income", target_col
            ),
            "tax_provision": self._safe_get_value(
                df, "Tax Provision", target_col
            ),
            "net_income": self._safe_get_value(df, "Net Income", target_col),
            "raw_data": self._convert_series_to_json(df[target_col]),
        }

        return data

    def _parse_us_cashflow_statement(
        self, symbol: str, year: int, quarter: Optional[int], df, target_col
    ) -> Dict[str, Any]:
        """Parse yfinance cash flow data into database format."""
        import yfinance as yf

        ticker = yf.Ticker(symbol)
        company_name = ticker.info.get("longName", symbol)

        data = {
            "symbol": symbol,
            "company_name": company_name,
            "year": year,
            "quarter": quarter,
            "operating_cash_flow": self._safe_get_value(
                df, "Operating Cash Flow", target_col
            ),
            "depreciation_amortization": self._safe_get_value(
                df, "Depreciation And Amortization", target_col
            ),
            "stock_based_compensation": self._safe_get_value(
                df, "Stock Based Compensation", target_col
            ),
            "change_working_capital": self._safe_get_value(
                df, "Change In Working Capital", target_col
            ),
            "investing_cash_flow": self._safe_get_value(
                df, "Investing Cash Flow", target_col
            ),
            "capital_expenditure": self._safe_get_value(
                df, "Capital Expenditure", target_col
            ),
            "financing_cash_flow": self._safe_get_value(
                df, "Financing Cash Flow", target_col
            ),
            "cash_dividends_paid": self._safe_get_value(
                df, "Cash Dividends Paid", target_col
            ),
            "repurchase_capital_stock": self._safe_get_value(
                df, "Repurchase Of Capital Stock", target_col
            ),
            "free_cash_flow": self._safe_get_value(
                df, "Free Cash Flow", target_col
            ),
            "raw_data": self._convert_series_to_json(df[target_col]),
        }

        return data

    def _convert_series_to_json(self, series) -> Dict[str, Any]:
        """Convert pandas Series to JSON-serializable dict, handling Timestamp indexes."""
        result = {}
        for key, value in series.items():
            # Convert key to string if it's a Timestamp or other non-serializable type
            str_key = str(key)
            # Handle NaN values
            if value is not None and not (
                isinstance(value, float) and value != value
            ):
                result[str_key] = (
                    float(value) if isinstance(value, (int, float)) else value
                )
            else:
                result[str_key] = None
        return result


# Global service instance
financial_statement_service = FinancialStatementService()
