"""Korean Investment Securities (KDevelopers) API client."""

import requests
import json
from typing import Optional, Dict, Any
from datetime import datetime
import hashlib
import hmac
import base64
from ..utils.config import settings
from ..models.korean import KoreanStockQuote
from ..utils.helpers import safe_float, safe_int, calculate_change_percent


class KDevelopersClient:
    """
    Client for Korean Investment Securities OpenAPI.
    
    API Documentation: https://apiportal.koreainvestment.com/
    """

    def __init__(self) -> None:
        """Initialize the Korean Investment API client."""
        self.api_key = settings.HANTU_API_KEY
        self.api_secret = settings.HANTU_API_SECRET
        self.base_url = settings.HANTU_BASE_URL
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None

    def _get_access_token(self) -> Optional[str]:
        """
        Get or refresh access token for API authentication.

        Returns:
            Access token or None if authentication fails
        """
        if not self.api_key or not self.api_secret:
            print("API credentials not configured")
            return None

        # Check if token is still valid
        if (
            self.access_token
            and self.token_expiry
            and datetime.now() < self.token_expiry
        ):
            return self.access_token

        # Request new token
        try:
            url = f"{self.base_url}/oauth2/tokenP"
            headers = {"content-type": "application/json"}
            body = {
                "grant_type": "client_credentials",
                "appkey": self.api_key,
                "appsecret": self.api_secret,
            }

            response = requests.post(url, headers=headers, json=body, timeout=10)
            response.raise_for_status()

            data = response.json()
            self.access_token = data.get("access_token")
            # Token typically expires in 24 hours
            self.token_expiry = datetime.now()

            return self.access_token
        except Exception as e:
            print(f"Failed to get access token: {e}")
            return None

    def get_quote(self, symbol: str) -> Optional[KoreanStockQuote]:
        """
        Get real-time quote for a Korean stock.

        Args:
            symbol: Stock code (e.g., "005930" for Samsung Electronics)

        Returns:
            KoreanStockQuote object or None if fetch fails
        """
        token = self._get_access_token()
        if not token:
            return None

        try:
            # This is a placeholder implementation
            # Actual endpoint and parameters need to match Korean Investment API
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = {
                "content-type": "application/json",
                "authorization": f"Bearer {token}",
                "appkey": self.api_key,
                "appsecret": self.api_secret,
                "tr_id": "FHKST01010100",  # Transaction ID for real-time quote
            }

            params = {
                "FID_COND_MRKT_DIV_CODE": "J",  # Market division
                "FID_INPUT_ISCD": symbol,  # Stock code
            }

            response = requests.get(
                url, headers=headers, params=params, timeout=10
            )
            response.raise_for_status()

            data = response.json()
            output = data.get("output", {})

            # Parse the response
            current_price = safe_float(output.get("stck_prpr"))
            previous_close = safe_float(output.get("stck_sdpr"))
            change = safe_float(output.get("prdy_vrss"))
            change_percent = safe_float(output.get("prdy_ctrt"))

            return KoreanStockQuote(
                symbol=symbol,
                name=output.get("hts_kor_isnm", symbol),
                current_price=current_price,
                change=change,
                change_percent=change_percent,
                volume=safe_int(output.get("acml_vol")),
                timestamp=datetime.now(),
                high=safe_float(output.get("stck_hgpr")),
                low=safe_float(output.get("stck_lwpr")),
                open=safe_float(output.get("stck_oprc")),
                previous_close=previous_close,
            )
        except Exception as e:
            print(f"Failed to get quote for {symbol}: {e}")
            return None


# Global instance
kdevelopers_client = KDevelopersClient()
