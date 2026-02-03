"""Korean Investment Securities (KDevelopers) API client."""

import requests
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
import hashlib
import hmac
import base64
from ..utils.config import settings
from ..models.korean import (
    KoreanStockQuote,
    KoreanCandleData,
    KoreanAccountBalance,
    KoreanStockPosition,
)
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

    def get_daily_candle(
        self,
        symbol: str,
        period: str = "D",
        adjust_price: bool = True,
        limit: int = 100,
    ) -> Optional[List[KoreanCandleData]]:
        """
        Get daily/period candle chart data for a Korean stock.

        Args:
            symbol: Stock code (e.g., "005930" for Samsung Electronics)
            period: Period type - "D" (daily), "W" (weekly), "M" (monthly)
            adjust_price: Whether to adjust for stock splits
            limit: Number of candles to retrieve (default: 100)

        Returns:
            List of KoreanCandleData objects or None if fetch fails
        """
        token = self._get_access_token()
        if not token:
            return None

        try:
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-daily-price"
            headers = {
                "content-type": "application/json",
                "authorization": f"Bearer {token}",
                "appkey": self.api_key,
                "appsecret": self.api_secret,
                "tr_id": "FHKST01010400",  # Transaction ID for daily price
            }

            params = {
                "FID_COND_MRKT_DIV_CODE": "J",  # Market division
                "FID_INPUT_ISCD": symbol,  # Stock code
                "FID_PERIOD_DIV_CODE": period,  # Period (D/W/M)
                "FID_ORG_ADJ_PRC": "0" if adjust_price else "1",
            }

            response = requests.get(
                url, headers=headers, params=params, timeout=10
            )
            response.raise_for_status()

            data = response.json()
            output_list = data.get("output", [])

            # Parse the response
            candles = []
            for i, item in enumerate(output_list):
                if i >= limit:
                    break

                close_price = safe_float(item.get("stck_clpr"))
                open_price = safe_float(item.get("stck_oprc"))
                change = safe_float(item.get("prdy_vrss"))
                change_percent = safe_float(item.get("prdy_ctrt"))

                candle = KoreanCandleData(
                    symbol=symbol,
                    date=item.get("stck_bsop_date", ""),
                    open=open_price,
                    high=safe_float(item.get("stck_hgpr")),
                    low=safe_float(item.get("stck_lwpr")),
                    close=close_price,
                    volume=safe_int(item.get("acml_vol")),
                    change=change,
                    change_percent=change_percent,
                )
                candles.append(candle)

            return candles
        except Exception as e:
            print(f"Failed to get candle data for {symbol}: {e}")
            return None

    def get_minute_candle(
        self, symbol: str, interval: int = 1, limit: int = 100
    ) -> Optional[List[KoreanCandleData]]:
        """
        Get minute candle chart data for a Korean stock.

        Args:
            symbol: Stock code (e.g., "005930" for Samsung Electronics)
            interval: Minute interval (1, 5, 10, 30, 60)
            limit: Number of candles to retrieve (default: 100)

        Returns:
            List of KoreanCandleData objects or None if fetch fails
        """
        token = self._get_access_token()
        if not token:
            return None

        try:
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"
            headers = {
                "content-type": "application/json",
                "authorization": f"Bearer {token}",
                "appkey": self.api_key,
                "appsecret": self.api_secret,
                "tr_id": "FHKST03010200",  # Transaction ID for minute price
            }

            params = {
                "FID_COND_MRKT_DIV_CODE": "J",  # Market division
                "FID_INPUT_ISCD": symbol,  # Stock code
                "FID_INPUT_HOUR_1": "",  # Time filter (empty for all)
                "FID_PW_DATA_INCU_YN": "Y",  # Include previous data
                "FID_TICK_RANGE": str(interval),  # Minute interval
            }

            response = requests.get(
                url, headers=headers, params=params, timeout=10
            )
            response.raise_for_status()

            data = response.json()
            output_list = data.get("output2", [])

            # Parse the response
            candles = []
            for i, item in enumerate(output_list):
                if i >= limit:
                    break

                close_price = safe_float(item.get("stck_prpr"))
                open_price = safe_float(item.get("stck_oprc"))

                candle = KoreanCandleData(
                    symbol=symbol,
                    date=item.get("stck_cntg_hour", ""),  # Time in HHMMSS
                    open=open_price,
                    high=safe_float(item.get("stck_hgpr")),
                    low=safe_float(item.get("stck_lwpr")),
                    close=close_price,
                    volume=safe_int(item.get("cntg_vol")),
                    change=safe_float(item.get("prdy_vrss")),
                    change_percent=safe_float(item.get("prdy_ctrt")),
                )
                candles.append(candle)

            return candles
        except Exception as e:
            print(f"Failed to get minute candle data for {symbol}: {e}")
            return None

    def get_account_balance(
        self, account_number: str, account_product_code: str = "01"
    ) -> Optional[Dict[str, Any]]:
        """
        Get account balance and positions.

        Args:
            account_number: Account number (8 digits)
            account_product_code: Account product code (default: "01")

        Returns:
            Dictionary containing balance info and positions, or None if fails
        """
        token = self._get_access_token()
        if not token:
            return None

        try:
            url = f"{self.base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
            headers = {
                "content-type": "application/json",
                "authorization": f"Bearer {token}",
                "appkey": self.api_key,
                "appsecret": self.api_secret,
                "tr_id": "TTTC8434R",  # Real account (use VTTC8434R for mock)
            }

            params = {
                "CANO": account_number,  # Account number
                "ACNT_PRDT_CD": account_product_code,  # Account product code
                "AFHR_FLPR_YN": "N",  # After-hours flag
                "OFL_YN": "",  # Offline flag
                "INQR_DVSN": "02",  # Inquiry division (01: total, 02: detail)
                "UNPR_DVSN": "01",  # Unit price division
                "FUND_STTL_ICLD_YN": "N",  # Fund settlement included
                "FNCG_AMT_AUTO_RDPT_YN": "N",  # Financing auto redemption
                "PRCS_DVSN": "01",  # Process division
                "CTX_AREA_FK100": "",  # Continuation key
                "CTX_AREA_NK100": "",  # Continuation key
            }

            response = requests.get(
                url, headers=headers, params=params, timeout=10
            )
            response.raise_for_status()

            data = response.json()
            output1 = data.get("output1", [])  # Stock positions
            
            # Safely access output2 with proper handling for empty lists
            raw_output2 = data.get("output2")
            if isinstance(raw_output2, list) and raw_output2:
                output2 = raw_output2[0]  # Account summary
            else:
                output2 = {}  # Fallback when account summary is missing or empty

            # Parse account balance
            total_evaluation = safe_float(output2.get("tot_evlu_amt"))
            cash_balance = safe_float(output2.get("dnca_tot_amt"))
            total_purchase = safe_float(output2.get("pchs_amt_smtl_amt"))
            profit_loss = safe_float(output2.get("evlu_pfls_smtl_amt"))
            profit_loss_percent = safe_float(
                output2.get("tot_evlu_pfls_rt")
            )

            balance = KoreanAccountBalance(
                account_number=account_number,
                total_evaluation=total_evaluation,
                cash_balance=cash_balance,
                investment_amount=total_purchase,
                profit_loss=profit_loss,
                profit_loss_percent=profit_loss_percent,
                timestamp=datetime.now(),
            )

            # Parse stock positions
            positions = []
            for item in output1:
                symbol = item.get("pdno", "")
                if not symbol:
                    continue

                position = KoreanStockPosition(
                    symbol=symbol,
                    name=item.get("prdt_name", symbol),
                    quantity=safe_int(item.get("hldg_qty")),
                    average_price=safe_float(item.get("pchs_avg_pric")),
                    current_price=safe_float(item.get("prpr")),
                    evaluation_amount=safe_float(item.get("evlu_amt")),
                    profit_loss=safe_float(item.get("evlu_pfls_amt")),
                    profit_loss_percent=safe_float(
                        item.get("evlu_pfls_rt")
                    ),
                )
                positions.append(position)

            return {
                "balance": balance,
                "positions": positions,
            }
        except Exception as e:
            print(f"Failed to get account balance: {e}")
            return None


# Global instance
kdevelopers_client = KDevelopersClient()
