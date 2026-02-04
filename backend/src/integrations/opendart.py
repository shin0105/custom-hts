"""OPENDART API client for Korean financial statements."""

import requests
import zipfile
import io
import xml.etree.ElementTree as ET
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import pandas as pd
from ..utils.config import settings
from ..models.korean import KoreanFinancialStatement
from ..utils.helpers import safe_float, safe_int

# Set up logging
logger = logging.getLogger(__name__)

# Import OpenDartReader if available
try:
    import OpenDartReader as DartReaderModule
    OPENDARTREADER_AVAILABLE = True
except ImportError:
    logger.warning("OpenDartReader library not available. Using fallback implementation.")
    OPENDARTREADER_AVAILABLE = False
    DartReaderModule = None


class OpenDartClient:
    """
    Client for OPENDART API.
    
    API Documentation: https://opendart.fss.or.kr/
    GitHub: https://github.com/FinanceData/OpenDartReader
    
    This client uses the OpenDartReader library for enhanced functionality
    including automatic corp code mapping, pandas DataFrame support, and
    simplified API access.
    
    Key endpoints:
    - fnlttSinglAcntAll.json: Get all financial statements
    - company.json: Get company information
    - corpCode.xml: Download corp code mapping (requires processing)
    """

    def __init__(self) -> None:
        """Initialize the OPENDART API client."""
        self.api_key = settings.DART_API_KEY
        self.base_url = settings.DART_BASE_URL
        self._corp_code_cache: Dict[str, str] = {}
        self._load_common_corp_codes()
        
        # Initialize OpenDartReader if available
        self.dart_reader = None
        if OPENDARTREADER_AVAILABLE and self.api_key:
            try:
                self.dart_reader = DartReaderModule(self.api_key)
                logger.info("OpenDartReader initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenDartReader: {e}")
                self.dart_reader = None

    def _load_common_corp_codes(self) -> None:
        """
        Load commonly used corp codes for major Korean companies.
        
        In production, you should download the full corp code list from DART.
        This is a hardcoded mapping for demonstration purposes.
        """
        # Mapping of stock codes to DART corp codes for major companies
        self._corp_code_cache = {
            "005930": "00126380",  # Samsung Electronics
            "000660": "00164742",  # SK Hynix
            "035420": "00234904",  # NAVER
            "035720": "00164779",  # Kakao
            "051910": "00164384",  # LG Chemicals
            "006400": "00126186",  # Samsung SDI
            "207940": "00401731",  # Samsung Biologics
            "068270": "00356370",  # Celltrion
            "028260": "00164308",  # Samsung C&T
            "012330": "00164485",  # Hyundai Mobis
        }

    def get_corp_code(self, stock_code: str) -> Optional[str]:
        """
        Get DART corporation code from stock code.
        
        DART uses 8-digit corporation codes which are different from
        6-digit stock codes. This method provides a cached mapping.

        Args:
            stock_code: Stock code (e.g., "005930")

        Returns:
            DART corporation code or None if not found
        """
        # Remove any spaces and pad with zeros if needed
        stock_code = stock_code.strip().zfill(6)
        
        # Check cache first
        corp_code = self._corp_code_cache.get(stock_code)
        
        # If not in cache and OpenDartReader is available, try to fetch
        if not corp_code and self.dart_reader:
            try:
                corp_code = self.dart_reader.find_corp_code(stock_code)
                if corp_code:
                    self._corp_code_cache[stock_code] = corp_code
                    logger.debug(f"Corp code for {stock_code} fetched from OpenDartReader: {corp_code}")
            except Exception as e:
                logger.debug(f"Failed to fetch corp code from OpenDartReader: {e}")
        
        if not corp_code:
            logger.warning(
                f"Corp code not found for {stock_code}. "
                "Add to mapping or download corp code list."
            )
        
        return corp_code
    
    def download_corp_code_list(self) -> bool:
        """
        Download and parse the complete corp code list from DART.
        
        This downloads a ZIP file containing XML with all corp codes.
        Updates the internal cache with the mapping.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.api_key:
            print("DART API key not configured")
            return False
            
        try:
            url = f"{self.base_url}/corpCode.xml"
            params = {"crtfc_key": self.api_key}
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Extract ZIP file
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                xml_content = zip_file.read("CORPCODE.xml")
            
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # Extract mappings
            for corp in root.findall("list"):
                corp_code = corp.findtext("corp_code", "")
                stock_code = corp.findtext("stock_code", "")
                
                if corp_code and stock_code and stock_code.strip():
                    # Only add entries with valid stock codes
                    self._corp_code_cache[stock_code.strip()] = corp_code.strip()
            
            logger.info(f"Successfully loaded {len(self._corp_code_cache)} corp codes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download corp code list: {e}")
            return False

    def get_financial_statement(
        self, 
        symbol: str, 
        year: int, 
        quarter: Optional[int] = None,
        fs_div: str = "CFS"
    ) -> Optional[KoreanFinancialStatement]:
        """
        Get financial statement for a Korean company.

        Args:
            symbol: Stock code (e.g., "005930")
            year: Fiscal year
            quarter: Optional quarter (1-4 for quarterly, None for annual)
            fs_div: Financial statement division - "CFS" for consolidated, "OFS" for separate

        Returns:
            KoreanFinancialStatement object or None if fetch fails
        """
        if not self.api_key:
            logger.warning("DART API key not configured")
            return None

        # Try to use OpenDartReader if available
        if self.dart_reader:
            try:
                return self._get_financial_statement_with_reader(
                    symbol, year, quarter, fs_div
                )
            except Exception as e:
                logger.warning(f"OpenDartReader failed, falling back to raw API: {e}")
        
        # Fallback to raw API implementation
        return self._get_financial_statement_raw_api(symbol, year, quarter, fs_div)
    
    def _get_financial_statement_with_reader(
        self,
        symbol: str,
        year: int,
        quarter: Optional[int] = None,
        fs_div: str = "CFS"
    ) -> Optional[KoreanFinancialStatement]:
        """
        Get financial statement using OpenDartReader library.
        
        Args:
            symbol: Stock code
            year: Fiscal year
            quarter: Optional quarter (1-4)
            fs_div: Financial statement division
            
        Returns:
            KoreanFinancialStatement or None
        """
        if not self.dart_reader:
            return None
        
        # Determine report code based on quarter
        reprt_code = None
        if quarter:
            # Quarterly reports: 11013 (Q1), 11012 (Q2), 11014 (Q3), 11011 (Annual/Q4)
            quarter_codes = {1: "11013", 2: "11012", 3: "11014", 4: "11011"}
            reprt_code = quarter_codes.get(quarter, "11011")
        else:
            reprt_code = "11011"  # Annual report
        
        # Use OpenDartReader's finstate method
        df = self.dart_reader.finstate(symbol, year, reprt_code=reprt_code)
        
        if df is None or df.empty:
            logger.warning(
                f"No financial data available for {symbol} "
                f"(year: {year}, quarter: {quarter})"
            )
            return None
        
        # Extract key financial data from DataFrame
        financial_data = self._parse_finstate_dataframe(df, symbol)
        
        return KoreanFinancialStatement(
            symbol=symbol,
            company_name=financial_data.get("company_name", symbol),
            year=year,
            quarter=quarter,
            revenue=financial_data.get("revenue"),
            operating_income=financial_data.get("operating_income"),
            net_income=financial_data.get("net_income"),
            total_assets=financial_data.get("total_assets"),
            total_liabilities=financial_data.get("total_liabilities"),
            total_equity=financial_data.get("total_equity"),
            eps=financial_data.get("eps"),
            updated_at=datetime.now(),
        )
    
    def _parse_finstate_dataframe(
        self, 
        df: pd.DataFrame, 
        symbol: str
    ) -> Dict[str, Any]:
        """
        Parse OpenDartReader's finstate DataFrame into structured format.
        
        Args:
            df: DataFrame from OpenDartReader.finstate()
            symbol: Stock code
            
        Returns:
            Dictionary with parsed financial data
        """
        result: Dict[str, Any] = {}
        
        # Extract company name if available
        if 'corp_name' in df.columns and not df.empty:
            result["company_name"] = df.iloc[0]['corp_name']
        else:
            result["company_name"] = symbol
        
        # Map of account names (Korean) to field names
        account_mapping = {
            "매출액": "revenue",
            "영업이익": "operating_income",
            "당기순이익": "net_income",
            "자산총계": "total_assets",
            "부채총계": "total_liabilities",
            "자본총계": "total_equity",
        }
        
        # Parse the DataFrame to extract key accounts
        if 'account_nm' in df.columns and 'thstrm_amount' in df.columns:
            for _, row in df.iterrows():
                account_nm = row.get('account_nm', '')
                thstrm_amount = row.get('thstrm_amount', 0)
                
                for dart_name, field_name in account_mapping.items():
                    if dart_name in account_nm:
                        try:
                            # Convert to float
                            if isinstance(thstrm_amount, str):
                                amount_str = thstrm_amount.replace(',', '')
                                if amount_str and amount_str != '-':
                                    result[field_name] = float(amount_str)
                            elif isinstance(thstrm_amount, (int, float)):
                                result[field_name] = float(thstrm_amount)
                        except (ValueError, AttributeError):
                            result[field_name] = None
                        break
        
        return result
    
    def _get_financial_statement_raw_api(
        self,
        symbol: str,
        year: int,
        quarter: Optional[int] = None,
        fs_div: str = "CFS"
    ) -> Optional[KoreanFinancialStatement]:
        """
        Fallback method using raw API calls (original implementation).
        
        Args:
            symbol: Stock code
            year: Fiscal year
            quarter: Optional quarter (1-4)
            fs_div: Financial statement division
            
        Returns:
            KoreanFinancialStatement or None
        """

        corp_code = self.get_corp_code(symbol)
        if not corp_code:
            logger.warning(f"Corp code not found for symbol {symbol}")
            return None

        try:
            # Determine report code based on quarter
            if quarter:
                # Quarterly reports: 11013 (Q1), 11012 (Q2), 11014 (Q3), 11011 (Annual/Q4)
                quarter_codes = {1: "11013", 2: "11012", 3: "11014", 4: "11011"}
                reprt_code = quarter_codes.get(quarter, "11011")
            else:
                reprt_code = "11011"  # Annual report

            # Get financial statement from DART API
            url = f"{self.base_url}/fnlttSinglAcntAll.json"
            params = {
                "crtfc_key": self.api_key,
                "corp_code": corp_code,
                "bsns_year": str(year),
                "reprt_code": reprt_code,
                "fs_div": fs_div,
            }

            logger.debug(
                f"Fetching financial data for {symbol} "
                f"(corp_code: {corp_code}), year: {year}, quarter: {quarter}"
            )
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Check API response status
            status = data.get("status", "")
            if status != "000":
                error_msg = data.get("message", "Unknown error")
                logger.error(f"DART API error (status: {status}): {error_msg}")
                return None

            list_data = data.get("list", [])
            if not list_data:
                logger.warning(
                    f"No financial data available for {symbol} "
                    f"(year: {year}, quarter: {quarter})"
                )
                return None

            # Extract key financial data
            financial_data = self._parse_financial_data(list_data)

            return KoreanFinancialStatement(
                symbol=symbol,
                company_name=financial_data.get("company_name", symbol),
                year=year,
                quarter=quarter,
                revenue=financial_data.get("revenue"),
                operating_income=financial_data.get("operating_income"),
                net_income=financial_data.get("net_income"),
                total_assets=financial_data.get("total_assets"),
                total_liabilities=financial_data.get("total_liabilities"),
                total_equity=financial_data.get("total_equity"),
                eps=financial_data.get("eps"),
                updated_at=datetime.now(),
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching financial statement for {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to get financial statement for {symbol}: {e}")
            return None
    
    def get_financial_statement_raw(
        self,
        symbol: str,
        year: int,
        quarter: Optional[int] = None,
        fs_div: str = "CFS"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get raw financial statement data from DART API.
        
        This returns the complete, unprocessed data which includes all
        line items from balance sheet, income statement, and cash flow.

        Args:
            symbol: Stock code
            year: Fiscal year
            quarter: Optional quarter (1-4)
            fs_div: Financial statement division - "CFS" or "OFS"

        Returns:
            List of financial line items or None if fetch fails
        """
        if not self.api_key:
            logger.warning("DART API key not configured")
            return None

        corp_code = self.get_corp_code(symbol)
        if not corp_code:
            return None

        try:
            # Determine report code
            if quarter:
                quarter_codes = {1: "11013", 2: "11012", 3: "11014", 4: "11011"}
                reprt_code = quarter_codes.get(quarter, "11011")
            else:
                reprt_code = "11011"

            url = f"{self.base_url}/fnlttSinglAcntAll.json"
            params = {
                "crtfc_key": self.api_key,
                "corp_code": corp_code,
                "bsns_year": str(year),
                "reprt_code": reprt_code,
                "fs_div": fs_div,
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get("status") != "000":
                logger.error(f"DART API error: {data.get('message')}")
                return None

            return data.get("list", [])
            
        except Exception as e:
            logger.error(f"Failed to get raw financial data for {symbol}: {e}")
            return None

    def _parse_financial_data(
        self, dart_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Parse DART financial data into a structured format.

        Args:
            dart_data: Raw data from DART API

        Returns:
            Dictionary with parsed financial data
        """
        result: Dict[str, Any] = {}

        # Map of DART account names to our fields
        # These are common Korean account names used in financial statements
        account_mapping = {
            "매출액": "revenue",
            "영업이익": "operating_income",
            "당기순이익": "net_income",
            "자산총계": "total_assets",
            "부채총계": "total_liabilities",
            "자본총계": "total_equity",
        }

        for item in dart_data:
            account_nm = item.get("account_nm", "")
            thstrm_amount = item.get("thstrm_amount", "0")

            # Store company name from first record
            if not result.get("company_name"):
                result["company_name"] = item.get("corp_name", "")

            # Match and store financial values
            for dart_name, field_name in account_mapping.items():
                if dart_name in account_nm:
                    # Convert to float (remove commas and handle negatives)
                    try:
                        amount_str = str(thstrm_amount).replace(",", "")
                        if amount_str and amount_str != "-":
                            result[field_name] = float(amount_str)
                        else:
                            result[field_name] = None
                    except (ValueError, AttributeError):
                        result[field_name] = None
                    break

        return result
    
    def get_balance_sheet(
        self,
        symbol: str,
        year: int,
        quarter: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get balance sheet data for a Korean company.
        
        Returns a dictionary with balance sheet line items including:
        - Assets (current, non-current, total)
        - Liabilities (current, non-current, total)
        - Equity
        
        Args:
            symbol: Stock code
            year: Fiscal year
            quarter: Optional quarter (1-4)
            
        Returns:
            Dictionary with balance sheet data
        """
        raw_data = self.get_financial_statement_raw(symbol, year, quarter)
        if not raw_data:
            return {}
        
        balance_sheet = {}
        
        # Filter for balance sheet items (sj_div == "BS")
        for item in raw_data:
            if item.get("sj_div") == "BS":
                account_nm = item.get("account_nm", "")
                amount = item.get("thstrm_amount", "0")
                
                # Convert amount to float
                try:
                    amount_str = str(amount).replace(",", "")
                    if amount_str and amount_str != "-":
                        balance_sheet[account_nm] = float(amount_str)
                except (ValueError, AttributeError):
                    balance_sheet[account_nm] = None
        
        return balance_sheet
    
    def get_income_statement(
        self,
        symbol: str,
        year: int,
        quarter: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get income statement data for a Korean company.
        
        Returns a dictionary with income statement line items including:
        - Revenue
        - Operating income
        - Net income
        - EPS
        
        Args:
            symbol: Stock code
            year: Fiscal year
            quarter: Optional quarter (1-4)
            
        Returns:
            Dictionary with income statement data
        """
        raw_data = self.get_financial_statement_raw(symbol, year, quarter)
        if not raw_data:
            return {}
        
        income_statement = {}
        
        # Filter for income statement items (sj_div == "IS")
        for item in raw_data:
            if item.get("sj_div") == "IS":
                account_nm = item.get("account_nm", "")
                amount = item.get("thstrm_amount", "0")
                
                # Convert amount to float
                try:
                    amount_str = str(amount).replace(",", "")
                    if amount_str and amount_str != "-":
                        income_statement[account_nm] = float(amount_str)
                except (ValueError, AttributeError):
                    income_statement[account_nm] = None
        
        return income_statement
    
    def get_cash_flow(
        self,
        symbol: str,
        year: int,
        quarter: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get cash flow statement data for a Korean company.
        
        Returns a dictionary with cash flow line items including:
        - Operating activities
        - Investing activities
        - Financing activities
        
        Args:
            symbol: Stock code
            year: Fiscal year
            quarter: Optional quarter (1-4)
            
        Returns:
            Dictionary with cash flow data
        """
        raw_data = self.get_financial_statement_raw(symbol, year, quarter)
        if not raw_data:
            return {}
        
        cash_flow = {}
        
        # Filter for cash flow items (sj_div == "CF")
        for item in raw_data:
            if item.get("sj_div") == "CF":
                account_nm = item.get("account_nm", "")
                amount = item.get("thstrm_amount", "0")
                
                # Convert amount to float
                try:
                    amount_str = str(amount).replace(",", "")
                    if amount_str and amount_str != "-":
                        cash_flow[account_nm] = float(amount_str)
                except (ValueError, AttributeError):
                    cash_flow[account_nm] = None
        
        return cash_flow
    
    def get_company_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed company information.
        
        Uses OpenDartReader's company() method to get comprehensive
        company profile information including CEO, address, industry, etc.
        
        Args:
            symbol: Stock code (e.g., "005930")
            
        Returns:
            Dictionary with company information or None if not available
        """
        if not self.dart_reader:
            logger.warning("OpenDartReader not available for company info")
            return None
        
        try:
            company_df = self.dart_reader.company(symbol)
            if company_df is None or company_df.empty:
                return None
            
            # Convert DataFrame to dictionary
            return company_df.iloc[0].to_dict() if len(company_df) > 0 else None
        except Exception as e:
            logger.error(f"Failed to get company info for {symbol}: {e}")
            return None
    
    def get_disclosure_list(
        self,
        symbol: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        kind: Optional[str] = None,
        final: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Get list of disclosures for a company or all companies.
        
        Uses OpenDartReader's list() method to retrieve disclosure listings.
        
        Args:
            symbol: Stock code (optional, if None returns all companies)
            start: Start date (YYYY-MM-DD or YYYYMMDD)
            end: End date (YYYY-MM-DD or YYYYMMDD)
            kind: Disclosure type:
                - 'A': Regular disclosure (정기공시)
                - 'B': Major matters (주요사항보고)
                - 'C': Issue disclosure (발행공시)
                - 'D': Equity disclosure (지분공시)
                - 'E': Other disclosure (기타공시)
                - 'F': External audit (외부감사관련)
                - 'G': Fund disclosure (펀드공시)
                - 'H': Asset securitization (자산유동화)
                - 'I': Exchange disclosure (거래소공시)
                - 'J': Fair Trade Commission (공정위공시)
            final: If True, only return final reports (exclude corrections)
            
        Returns:
            DataFrame with disclosure listings or None if not available
        """
        if not self.dart_reader:
            logger.warning("OpenDartReader not available for disclosure list")
            return None
        
        try:
            return self.dart_reader.list(
                corp=symbol,
                start=start,
                end=end,
                kind=kind,
                final=final
            )
        except Exception as e:
            logger.error(f"Failed to get disclosure list: {e}")
            return None
    
    def get_finstate_all(
        self,
        symbol: str,
        year: int,
        reprt_code: str = "11011"
    ) -> Optional[pd.DataFrame]:
        """
        Get all financial statements (comprehensive data).
        
        Uses OpenDartReader's finstate_all() method to get complete
        financial statement data including all line items.
        
        Args:
            symbol: Stock code
            year: Fiscal year
            reprt_code: Report code (11011=annual, 11013=Q1, 11012=Q2, 11014=Q3)
            
        Returns:
            DataFrame with all financial statement data or None
        """
        if not self.dart_reader:
            logger.warning("OpenDartReader not available for finstate_all")
            return None
        
        try:
            return self.dart_reader.finstate_all(symbol, year, reprt_code=reprt_code)
        except Exception as e:
            logger.error(f"Failed to get all financial statements for {symbol}: {e}")
            return None


# Global instance
opendart_client = OpenDartClient()
