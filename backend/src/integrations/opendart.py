"""OPENDART API client for Korean financial statements."""

import requests
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..utils.config import settings
from ..models.korean import KoreanFinancialStatement
from ..utils.helpers import safe_float, safe_int


class OpenDartClient:
    """
    Client for OPENDART API.
    
    API Documentation: https://opendart.fss.or.kr/
    """

    def __init__(self) -> None:
        """Initialize the OPENDART API client."""
        self.api_key = settings.DART_API_KEY
        self.base_url = settings.DART_BASE_URL

    def get_corp_code(self, stock_code: str) -> Optional[str]:
        """
        Get DART corporation code from stock code.
        
        Note: DART uses different corporation codes than stock codes.
        This requires maintaining a mapping or using their corp code list.

        Args:
            stock_code: Stock code (e.g., "005930")

        Returns:
            DART corporation code or None
        """
        # This is a placeholder - in production, you'd need to:
        # 1. Download the corp code list from DART
        # 2. Maintain a mapping between stock codes and corp codes
        # 3. Or use a database lookup
        
        # For now, return the stock code as-is
        return stock_code

    def get_financial_statement(
        self, symbol: str, year: int, quarter: Optional[int] = None
    ) -> Optional[KoreanFinancialStatement]:
        """
        Get financial statement for a Korean company.

        Args:
            symbol: Stock code
            year: Fiscal year
            quarter: Optional quarter (1-4)

        Returns:
            KoreanFinancialStatement object or None if fetch fails
        """
        if not self.api_key:
            print("DART API key not configured")
            return None

        corp_code = self.get_corp_code(symbol)
        if not corp_code:
            return None

        try:
            # Determine report code
            if quarter:
                reprt_code = f"{quarter:02d}"  # 01, 02, 03, 04
            else:
                reprt_code = "11"  # Annual report

            # Get financial statement
            url = f"{self.base_url}/fnlttSinglAcntAll.json"
            params = {
                "crtfc_key": self.api_key,
                "corp_code": corp_code,
                "bsns_year": str(year),
                "reprt_code": reprt_code,
                "fs_div": "CFS",  # Consolidated financial statements
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get("status") != "000":
                print(f"DART API error: {data.get('message')}")
                return None

            list_data = data.get("list", [])
            if not list_data:
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
        except Exception as e:
            print(f"Failed to get financial statement for {symbol}: {e}")
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
                        amount_str = thstrm_amount.replace(",", "")
                        result[field_name] = float(amount_str)
                    except (ValueError, AttributeError):
                        result[field_name] = None
                    break

        return result


# Global instance
opendart_client = OpenDartClient()
