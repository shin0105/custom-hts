"""OPENDART API client for Korean financial statements."""

import json
import re
import zipfile
import io
import xml.etree.ElementTree as ET
import logging
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
import requests
from ..utils.config import settings
from ..models.korean import KoreanFinancialStatement

# Set up logging
logger = logging.getLogger(__name__)


class OpenDartClient:
    """
    Client for OPENDART API.

    API Documentation: https://opendart.fss.or.kr/

    Key endpoints:
    - fnlttSinglAcnt.json: Get single-company major accounts
    - fnlttMultiAcnt.json: Get multi-company major accounts
    - company.json: Get company information
    - corpCode.xml: Download corp code mapping (requires processing)
    """

    def __init__(self, corp_code_cache_path: Optional[Path] = None) -> None:
        """Initialize the OPENDART API client.

        Args:
            corp_code_cache_path: Where the stock-code → corp-code snapshot
                lives. Defaults to ``src/data/opendart/corp_codes.json``.
        """
        self.api_key = settings.DART_API_KEY
        self.base_url = settings.DART_BASE_URL
        self._corp_code_cache: Dict[str, str] = {}
        # Listed companies' DART names → corp code (raw names, as persisted)
        # and a normalised index for lookups by name.
        self._corp_names: Dict[str, str] = {}
        self._corp_name_index: Dict[str, str] = {}
        self._corp_code_cache_path = corp_code_cache_path or (
            Path(__file__).parent.parent
            / "data"
            / "opendart"
            / "corp_codes.json"
        )
        self._corp_code_cache_ttl = timedelta(hours=24)
        self._corp_code_cache_loaded_at: Optional[datetime] = None
        # Lookups run on several pool threads; only one downloads the list.
        self._corp_code_download_lock = threading.Lock()
        self._corp_code_cache_path.parent.mkdir(parents=True, exist_ok=True)
        # The full corp code list is downloaded lazily (on a cache miss) to
        # avoid startup network calls; the committed snapshot covers every
        # listed company in the meantime.
        self._load_cached_corp_codes()

    def _load_cached_corp_codes(self) -> None:
        """Load the corp code snapshot from disk, however old it is.

        Corp codes are permanent per company, so a stale snapshot is still
        correct for every company it lists. Its age only decides whether a
        lookup miss triggers a fresh download.
        """
        if not self._corp_code_cache_path.exists():
            return

        try:
            with self._corp_code_cache_path.open(
                "r", encoding="utf-8"
            ) as handle:
                payload = json.load(handle)
            timestamp = payload.get("timestamp")
            codes = payload.get("codes")
            if not timestamp or not isinstance(codes, dict):
                return

            loaded_at = datetime.fromisoformat(timestamp)
            if loaded_at.tzinfo is None:
                loaded_at = loaded_at.replace(tzinfo=timezone.utc)

            self._corp_code_cache.update(codes)
            names = payload.get("names")
            if isinstance(names, dict):
                self._set_corp_names(names)
            self._corp_code_cache_loaded_at = loaded_at

            if (
                datetime.now(timezone.utc) - loaded_at
                > self._corp_code_cache_ttl
            ):
                logger.info(
                    "Cached corp code list is more than 24 hours old; using "
                    "it and refreshing on the next lookup miss."
                )
        except Exception as e:
            logger.warning(f"Failed to load cached corp code list: {e}")

    def _should_refresh_corp_code_cache(self) -> bool:
        if self._corp_code_cache_loaded_at is None:
            return True
        return (
            datetime.now(timezone.utc) - self._corp_code_cache_loaded_at
            > self._corp_code_cache_ttl
        )

    @staticmethod
    def _normalize_corp_name(name: str) -> str:
        """Normalise a company name for lookups (spaces, case, (주))."""
        name = re.sub(r"\(주\)|㈜|주식회사", "", name)
        return re.sub(r"\s+", "", name).casefold()

    def _set_corp_names(self, names: Dict[str, str]) -> None:
        self._corp_names.update(names)
        self._corp_name_index = {
            self._normalize_corp_name(name): code
            for name, code in self._corp_names.items()
            if name and code
        }

    def _persist_corp_code_cache(self) -> None:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "codes": self._corp_code_cache,
            "names": self._corp_names,
        }
        with self._corp_code_cache_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False)

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

        if not corp_code and self._should_refresh_corp_code_cache():
            if self.download_corp_code_list():
                corp_code = self._corp_code_cache.get(stock_code)

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
        loaded_before = self._corp_code_cache_loaded_at
        with self._corp_code_download_lock:
            if self._corp_code_cache_loaded_at != loaded_before:
                # Another thread downloaded the list while this one waited.
                return True
            return self._download_corp_code_list_locked()

    def _download_corp_code_list_locked(self) -> bool:
        """Body of ``download_corp_code_list``; the caller holds the lock."""
        if not self.api_key:
            logger.warning("DART API key not configured")
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

            # Extract mappings (listed companies only)
            names: Dict[str, str] = {}
            for corp in root.findall("list"):
                corp_code = corp.findtext("corp_code", "").strip()
                stock_code = corp.findtext("stock_code", "").strip()
                corp_name = corp.findtext("corp_name", "").strip()

                if corp_code and stock_code:
                    self._corp_code_cache[stock_code] = corp_code
                    if corp_name:
                        names[corp_name] = corp_code
            self._set_corp_names(names)

            self._corp_code_cache_loaded_at = datetime.now(timezone.utc)
            self._persist_corp_code_cache()
            logger.info(
                f"Successfully loaded {len(self._corp_code_cache)} corp codes"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to download corp code list: {e}")
            return False

    def get_financial_statement(
        self,
        symbol: str,
        year: int,
        quarter: Optional[int] = None,
        fs_div: str = "CFS",
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

        corp_code = self.get_corp_code(symbol)
        if not corp_code:
            logger.warning(f"Corp code not found for symbol {symbol}")
            return None

        try:
            list_data = self.get_financial_statement_raw(
                symbol=symbol, year=year, quarter=quarter, fs_div=fs_div
            )
            if list_data is None:
                return None
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
                bps=financial_data.get("bps"),
                updated_at=datetime.now(),
            )
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Network error fetching financial statement for {symbol}: {e}"
            )
            return None
        except Exception as e:
            logger.error(
                f"Failed to get financial statement for {symbol}: {e}"
            )
            return None

    def get_financial_statement_raw(
        self,
        symbol: str,
        year: int,
        quarter: Optional[int] = None,
        fs_div: str = "CFS",
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get raw major-account financial statement data from DART API.

        This returns merged results from:
        - fnlttSinglAcnt (API 2019016)
        - fnlttMultiAcnt (API 2019017)

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
            reprt_code = self._get_reprt_code(quarter)
            merged = self._fetch_financial_statement_major_accounts(
                corp_code=corp_code,
                year=year,
                reprt_code=reprt_code,
                fs_div=fs_div,
            )
            return merged

        except Exception as e:
            logger.error(f"Failed to get raw financial data for {symbol}: {e}")
            return None

    def _get_reprt_code(self, quarter: Optional[int]) -> str:
        """Convert quarter to DART report code."""
        if quarter:
            quarter_codes = {
                1: "11013",
                2: "11012",
                3: "11014",
                4: "11011",
            }
            return quarter_codes.get(quarter, "11011")
        return "11011"

    def _fetch_financial_statement_major_accounts(
        self,
        corp_code: str,
        year: int,
        reprt_code: str,
        fs_div: str = "CFS",
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch and merge major-account financial statements from both DART endpoints.

        Replaces legacy fnlttSinglAcntAll usage with:
        - fnlttSinglAcnt (API 2019016)
        - fnlttMultiAcnt (API 2019017)
        """
        # According to OPENDART docs for 2019016/2019017, request params are:
        # crtfc_key, corp_code, bsns_year, reprt_code.
        base_params = {
            "crtfc_key": self.api_key,
            "corp_code": corp_code,
            "bsns_year": str(year),
            "reprt_code": reprt_code,
        }
        endpoint_names = ["fnlttSinglAcnt", "fnlttMultiAcnt"]
        merged: List[Dict[str, Any]] = []

        for endpoint in endpoint_names:
            url = f"{self.base_url}/{endpoint}.json"
            response = requests.get(url, params=base_params, timeout=30)
            response.raise_for_status()
            data = response.json()

            status = data.get("status", "")
            if status != "000":
                error_msg = data.get("message", "Unknown error")
                if status == "013" or "조회된 데이타가 없습니다" in error_msg:
                    logger.info(
                        f"DART API no data for {corp_code} ({year}/{reprt_code}) on {endpoint}"
                    )
                    continue
                logger.error(
                    f"DART API error on {endpoint} (status: {status}): {error_msg}"
                )
                return None

            endpoint_items = data.get("list", [])
            if not isinstance(endpoint_items, list):
                logger.warning(
                    f"Unexpected DART response format on {endpoint}: list is not an array"
                )
                continue

            if fs_div:
                endpoint_items = [
                    item
                    for item in endpoint_items
                    if item.get("fs_div") in (None, "", fs_div)
                ]

            merged.extend(endpoint_items)

        if not merged:
            return []

        # Deduplicate because some companies/periods return overlapping rows
        # between fnlttSinglAcnt and fnlttMultiAcnt.
        deduped: List[Dict[str, Any]] = []
        seen = set()
        key_fields = (
            "rcept_no",
            "bsns_year",
            "reprt_code",
            "sj_div",
            "account_id",
            "account_nm",
            "ord",
            "thstrm_amount",
            "frmtrm_amount",
            "bfefrmtrm_amount",
            "fs_div",
        )
        for item in merged:
            key = tuple(item.get(field) for field in key_fields)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(item)

        return deduped

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
            "기본주당이익": "eps",
            "희석주당이익": "eps",
            "주당순이익": "eps",
            "EPS": "eps",
            "주당순자산": "bps",
            "주당순자산가치": "bps",
            "BPS": "bps",
        }

        for item in dart_data:
            account_nm = item.get("account_nm", "")
            thstrm_amount = item.get("thstrm_amount", "0")

            # Some endpoints omit corp_name; only set when present.
            corp_name = item.get("corp_name")
            if corp_name and not result.get("company_name"):
                result["company_name"] = corp_name

            # Match and store financial values
            for dart_name, field_name in account_mapping.items():
                if dart_name in account_nm:
                    # Convert to float (remove commas and handle negatives)
                    try:
                        amount_str = str(thstrm_amount).replace(",", "")
                        if amount_str and amount_str != "-":
                            if field_name not in result:
                                result[field_name] = float(amount_str)
                        else:
                            if field_name not in result:
                                result[field_name] = None
                    except (ValueError, AttributeError):
                        if field_name not in result:
                            result[field_name] = None
                    break

        return result

    def get_balance_sheet(
        self, symbol: str, year: int, quarter: Optional[int] = None
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
        self, symbol: str, year: int, quarter: Optional[int] = None
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

    def find_corp_code(self, corp_name_or_stock_code: str) -> Optional[str]:
        """
        Find a corp code by stock code, DART company name or corp code.

        Names are matched exactly against listed companies' DART names,
        ignoring spaces, letter case and "(주)" (e.g. "삼성전자", "NAVER",
        "현대자동차"). An 8-digit number is taken as a corp code as is.
        On a miss, the corp code list is downloaded when the snapshot is
        stale or has no company names yet.

        Args:
            corp_name_or_stock_code: Company name, stock code or corp code

        Returns:
            Corp code if found, None otherwise
        """
        query = corp_name_or_stock_code.strip()
        if not query:
            return None
        if re.fullmatch(r"\d{8}", query):
            return query

        stock_code = query.zfill(6) if query.isdigit() else query.upper()
        name_key = self._normalize_corp_name(query)

        def lookup() -> Optional[str]:
            return self._corp_code_cache.get(
                stock_code
            ) or self._corp_name_index.get(name_key)

        corp_code = lookup()
        if not corp_code and (
            self._should_refresh_corp_code_cache()
            or not self._corp_name_index
        ):
            if self.download_corp_code_list():
                corp_code = lookup()

        if not corp_code:
            logger.warning(
                f"Corp code not found for '{corp_name_or_stock_code}'."
            )
        return corp_code

    def get_company_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed company information from OPENDART.

        Returns comprehensive company profile including CEO, address, industry, etc.
        This uses the OPENDART company.json endpoint.

        Args:
            symbol: Stock code (e.g., "005930")

        Returns:
            Dictionary with company information or None if not available
        """
        if not self.api_key:
            logger.warning("DART API key not configured")
            return None

        corp_code = self.get_corp_code(symbol)
        if not corp_code:
            logger.warning(f"Corp code not found for symbol {symbol}")
            return None

        try:
            url = f"{self.base_url}/company.json"
            params = {"crtfc_key": self.api_key, "corp_code": corp_code}

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Check API response status
            status = data.get("status", "")
            if status != "000":
                error_msg = data.get("message", "Unknown error")
                logger.error(f"DART API error (status: {status}): {error_msg}")
                return None

            return data

        except Exception as e:
            logger.error(f"Failed to get company info for {symbol}: {e}")
            return None

    def get_disclosure_list(
        self,
        corp: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        kind: Optional[str] = None,
        final: bool = True,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of corporate disclosures from OPENDART.

        This uses the OPENDART list.json endpoint to retrieve disclosure listings.

        Args:
            corp: Stock code, DART company name or corp code (optional;
                omit for every company)
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
            List of disclosure dictionaries or None if not available

        Raises:
            LookupError: ``corp`` was given but matches no company. (Sending
                the request without corp_code would return every company's
                filings.)
        """
        if not self.api_key:
            logger.warning("DART API key not configured")
            return None

        params: Dict[str, str] = {"crtfc_key": self.api_key}
        if corp:
            corp_code = self.find_corp_code(corp)
            if not corp_code:
                raise LookupError(f"Company not found: {corp}")
            params["corp_code"] = corp_code

        try:
            url = f"{self.base_url}/list.json"

            # Add date parameters (convert to YYYYMMDD format if needed)
            if start:
                params["bgn_de"] = start.replace("-", "")
            if end:
                params["end_de"] = end.replace("-", "")

            # Add disclosure type
            if kind:
                params["pblntf_ty"] = kind

            # Add final flag (Y/N)
            params["last_reprt_at"] = "Y" if final else "N"

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Check API response status
            status = data.get("status", "")
            if status != "000":
                error_msg = data.get("message", "Unknown error")
                logger.error(f"DART API error (status: {status}): {error_msg}")
                return None

            return data.get("list", [])

        except Exception as e:
            logger.error(f"Failed to get disclosure list: {e}")
            return None

    def get_finstate_all(
        self,
        symbol: str,
        year: int,
        reprt_code: str = "11011",
        fs_div: str = "CFS",
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get merged major-account financial statement line items.

        This is an alias for get_financial_statement_raw() using the new
        OPENDART major-account endpoints. They return balance sheet (BS) and
        income statement (IS) accounts only; there are no cash flow items.

        Args:
            symbol: Stock code
            year: Fiscal year
            reprt_code: Report code (11011=annual, 11013=Q1, 11012=Q2, 11014=Q3)
            fs_div: Financial statement division (CFS/OFS)

        Returns:
            List of all financial statement line items or None
        """
        # Map report code to quarter for compatibility
        quarter_map = {
            "11013": 1,
            "11012": 2,
            "11014": 3,
            "11011": None,  # Annual
        }
        quarter = quarter_map.get(reprt_code)

        return self.get_financial_statement_raw(symbol, year, quarter, fs_div)


# Global instance
opendart_client = OpenDartClient()
