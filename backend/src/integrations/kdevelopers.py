"""Korean Investment Securities (KDevelopers) API client.

This module implements the KDEVELOPERS OpenAPI integration based on the
official reference implementation from:
https://github.com/koreainvestment/open-trading-api

Key features:
- Token management with file-based caching
- Structured API response handling
- Comprehensive error handling
- Rate limiting support
"""

import requests
import json
import os
import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from collections import namedtuple
from ..utils.config import settings
from ..models.korean import (
    KoreanStockQuote,
    KoreanCandleData,
    KoreanAccountBalance,
    KoreanStockPosition,
)
from ..utils.helpers import safe_float, safe_int, calculate_change_percent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class APIResponse:
    """
    Structured API response wrapper based on kis_auth.py APIResp class.
    
    Provides structured access to API response headers and body with
    convenient error checking methods.
    """

    def __init__(self, resp: requests.Response):
        """Initialize API response wrapper."""
        self._rescode = resp.status_code
        self._resp = resp
        self._header = self._set_header()
        self._body = self._set_body()
        try:
            self._err_code = self._body.msg_cd if hasattr(self._body, 'msg_cd') else None
            self._err_message = self._body.msg1 if hasattr(self._body, 'msg1') else None
        except:
            self._err_code = None
            self._err_message = None

    def get_res_code(self) -> int:
        """Get HTTP response status code."""
        return self._rescode

    def _set_header(self):
        """Parse response headers into named tuple."""
        fld = {}
        for x in self._resp.headers.keys():
            if x.islower():
                # Replace hyphens with underscores for valid Python identifiers
                field_name = x.replace('-', '_')
                fld[field_name] = self._resp.headers.get(x)
        if not fld:
            return namedtuple("header", ["tr_cont"])("")
        _th_ = namedtuple("header", fld.keys())
        return _th_(**fld)

    def _set_body(self):
        """Parse response body JSON into named tuple."""
        try:
            json_data = self._resp.json()
            _tb_ = namedtuple("body", json_data.keys())
            return _tb_(**json_data)
        except:
            return namedtuple("body", ["rt_cd"])("1")

    def get_header(self):
        """Get response header."""
        return self._header

    def get_body(self):
        """Get response body."""
        return self._body

    def get_response(self) -> requests.Response:
        """Get raw response object."""
        return self._resp

    def is_ok(self) -> bool:
        """Check if API call was successful (rt_cd == "0")."""
        try:
            return self.get_body().rt_cd == "0"
        except:
            return False

    def get_error_code(self) -> Optional[str]:
        """Get error code from response."""
        return self._err_code

    def get_error_message(self) -> Optional[str]:
        """Get error message from response."""
        return self._err_message

    def print_error(self, url: str):
        """Print formatted error message."""
        print(
            "-------------------------------\n"
            f"Error in response: {self.get_res_code()} url={url}\n"
            f"rt_cd: {getattr(self.get_body(), 'rt_cd', 'N/A')}\n"
            f"msg_cd: {self.get_error_code()}\n"
            f"msg1: {self.get_error_message()}\n"
            "-------------------------------"
        )


class KDevelopersClient:
    """
    Client for Korean Investment Securities OpenAPI.
    
    Based on reference implementation from:
    https://github.com/koreainvestment/open-trading-api
    
    API Documentation: https://apiportal.koreainvestment.com/
    """

    def __init__(self) -> None:
        """Initialize the Korean Investment API client."""
        self.api_key = settings.HANTU_API_KEY
        self.api_secret = settings.HANTU_API_SECRET
        self.base_url = settings.HANTU_BASE_URL
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self._last_auth_time = datetime.now()
        
        # Rate limiting (0.05s for real trading, 0.5s for paper trading)
        self._smart_sleep_time = 0.05

    def _smart_sleep(self):
        """Rate limiting sleep to avoid API throttling."""
        time.sleep(self._smart_sleep_time)

    def _get_base_headers(self) -> Dict[str, str]:
        """Get base headers for API requests."""
        return {
            "Content-Type": "application/json",
            "Accept": "text/plain",
            "charset": "UTF-8",
        }

    def _get_access_token(self) -> Optional[str]:
        """
        Get or refresh access token for API authentication.
        
        Token is valid for 24 hours. This method checks token validity
        and requests a new one if expired.

        Returns:
            Access token or None if authentication fails
        """
        if not self.api_key or not self.api_secret:
            logger.error("API credentials not configured")
            return None

        # Check if token is still valid (24 hour expiry)
        if (
            self.access_token
            and self.token_expiry
            and (datetime.now() - self._last_auth_time).total_seconds() < 86400
        ):
            return self.access_token

        # Request new token
        try:
            url = f"{self.base_url}/oauth2/tokenP"
            headers = self._get_base_headers()
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
            token_expired = data.get("access_token_token_expired")
            if token_expired:
                self.token_expiry = datetime.strptime(
                    token_expired, "%Y-%m-%d %H:%M:%S"
                )
            else:
                self.token_expiry = datetime.now()
            
            self._last_auth_time = datetime.now()
            logger.info(f"[{self._last_auth_time}] => Token acquired successfully")

            return self.access_token
        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            return None

    def _url_fetch(
        self,
        api_url: str,
        tr_id: str,
        tr_cont: str,
        params: Dict[str, Any],
        post_flag: bool = False,
    ) -> APIResponse:
        """
        Common API request wrapper based on kis_auth._url_fetch.
        
        Args:
            api_url: API endpoint path
            tr_id: Transaction ID
            tr_cont: Transaction continuation flag
            params: Request parameters
            post_flag: Whether to use POST instead of GET
            
        Returns:
            APIResponse object with structured response data
        """
        token = self._get_access_token()
        if not token:
            raise Exception("Failed to get access token")

        url = f"{self.base_url}{api_url}"
        headers = self._get_base_headers()
        
        # Add authorization headers
        headers["authorization"] = f"Bearer {token}"
        headers["appkey"] = self.api_key
        headers["appsecret"] = self.api_secret
        headers["tr_id"] = tr_id
        headers["custtype"] = "P"  # Personal customer
        headers["tr_cont"] = tr_cont

        try:
            if post_flag:
                response = requests.post(
                    url, headers=headers, data=json.dumps(params), timeout=10
                )
            else:
                response = requests.get(
                    url, headers=headers, params=params, timeout=10
                )
            
            # Apply rate limiting
            self._smart_sleep()
            
            if response.status_code == 200:
                return APIResponse(response)
            else:
                logger.error(f"API Error: {response.status_code} - {response.text}")
                return APIResponse(response)
                
        except Exception as e:
            logger.error(f"Request failed for {url}: {e}")
            raise

    def get_quote(self, symbol: str) -> Optional[KoreanStockQuote]:
        """
        Get real-time quote for a Korean stock.
        
        Based on examples_llm/domestic_stock/inquire_price/inquire_price.py
        API: [국내주식] 기본시세 > 주식현재가 시세[v1_국내주식-008]

        Args:
            symbol: Stock code (e.g., "005930" for Samsung Electronics)

        Returns:
            KoreanStockQuote object or None if fetch fails
        """
        try:
            api_url = "/uapi/domestic-stock/v1/quotations/inquire-price"
            tr_id = "FHKST01010100"  # Transaction ID for real-time quote

            params = {
                "FID_COND_MRKT_DIV_CODE": "J",  # Market division (J: KRX)
                "FID_INPUT_ISCD": symbol,  # Stock code
            }

            res = self._url_fetch(api_url, tr_id, "", params)

            if res.is_ok():
                # Access output as attribute or dict key
                body = res.get_body()
                output = getattr(body, 'output', None)
                if output is None:
                    logger.error(f"No output in response for {symbol}")
                    return None
                
                # Convert namedtuple to dict for easier access
                if hasattr(output, '_asdict'):
                    output_dict = output._asdict()
                elif isinstance(output, dict):
                    output_dict = output
                else:
                    logger.error(f"Unexpected output type: {type(output)}")
                    return None
                
                # Parse the response
                current_price = safe_float(output_dict.get("stck_prpr"))
                previous_close = safe_float(output_dict.get("stck_sdpr"))
                change = safe_float(output_dict.get("prdy_vrss"))
                change_percent = safe_float(output_dict.get("prdy_ctrt"))

                return KoreanStockQuote(
                    symbol=symbol,
                    name=output_dict.get("hts_kor_isnm", symbol),
                    current_price=current_price,
                    change=change,
                    change_percent=change_percent,
                    volume=safe_int(output_dict.get("acml_vol")),
                    timestamp=datetime.now(),
                    high=safe_float(output_dict.get("stck_hgpr")),
                    low=safe_float(output_dict.get("stck_lwpr")),
                    open=safe_float(output_dict.get("stck_oprc")),
                    previous_close=previous_close,
                )
            else:
                res.print_error(api_url)
                logger.error(f"Failed to get quote for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Exception in get_quote for {symbol}: {e}")
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
        
        API: [국내주식] 기본시세 > 국내주식기간별시세(일/주/월/년)[v1_국내주식-016]

        Args:
            symbol: Stock code (e.g., "005930" for Samsung Electronics)
            period: Period type - "D" (daily), "W" (weekly), "M" (monthly)
            adjust_price: Whether to adjust for stock splits
            limit: Number of candles to retrieve (default: 100)

        Returns:
            List of KoreanCandleData objects or None if fetch fails
        """
        try:
            api_url = "/uapi/domestic-stock/v1/quotations/inquire-daily-price"
            tr_id = "FHKST01010400"  # Transaction ID for daily price

            params = {
                "FID_COND_MRKT_DIV_CODE": "J",  # Market division
                "FID_INPUT_ISCD": symbol,  # Stock code
                "FID_PERIOD_DIV_CODE": period,  # Period (D/W/M)
                "FID_ORG_ADJ_PRC": "0" if adjust_price else "1",
            }

            res = self._url_fetch(api_url, tr_id, "", params)

            if res.is_ok():
                output_list = res.get_body().output
                
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
            else:
                res.print_error(api_url)
                logger.error(f"Failed to get candle data for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Exception in get_daily_candle for {symbol}: {e}")
            return None

    def get_minute_candle(
        self, symbol: str, interval: int = 1, limit: int = 100
    ) -> Optional[List[KoreanCandleData]]:
        """
        Get minute candle chart data for a Korean stock.
        
        API: [국내주식] 기본시세 > 국내주식분봉조회[v1_국내주식-024]

        Args:
            symbol: Stock code (e.g., "005930" for Samsung Electronics)
            interval: Minute interval (1, 5, 10, 30, 60)
            limit: Number of candles to retrieve (default: 100)

        Returns:
            List of KoreanCandleData objects or None if fetch fails
        """
        try:
            api_url = "/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"
            tr_id = "FHKST03010200"  # Transaction ID for minute price

            params = {
                "FID_COND_MRKT_DIV_CODE": "J",  # Market division
                "FID_INPUT_ISCD": symbol,  # Stock code
                "FID_INPUT_HOUR_1": "",  # Time filter (empty for all)
                "FID_PW_DATA_INCU_YN": "Y",  # Include previous data
                "FID_TICK_RANGE": str(interval),  # Minute interval
            }

            res = self._url_fetch(api_url, tr_id, "", params)

            if res.is_ok():
                output_list = res.get_body().output2
                
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
            else:
                res.print_error(api_url)
                logger.error(f"Failed to get minute candle data for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Exception in get_minute_candle for {symbol}: {e}")
            return None

    def get_account_balance(
        self, account_number: str, account_product_code: str = "01"
    ) -> Optional[Dict[str, Any]]:
        """
        Get account balance and positions.
        
        API: [국내주식] 계좌/잔고 > 주식잔고조회[v1_국내주식-006]

        Args:
            account_number: Account number (8 digits)
            account_product_code: Account product code (default: "01")

        Returns:
            Dictionary containing balance info and positions, or None if fails
        """
        try:
            api_url = "/uapi/domestic-stock/v1/trading/inquire-balance"
            tr_id = "TTTC8434R"  # Real account (use VTTC8434R for mock)

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

            res = self._url_fetch(api_url, tr_id, "", params)

            if res.is_ok():
                output1 = res.get_body().output1  # Stock positions
                
                # Safely access output2 with proper handling for empty lists
                raw_output2 = res.get_body().output2
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
            else:
                res.print_error(api_url)
                logger.error(f"Failed to get account balance for {account_number}")
                return None
                
        except Exception as e:
            logger.error(f"Exception in get_account_balance: {e}")
            return None

    def search_stock_info(
        self,
        prdt_type_cd: str,
        pdno: str,
        tr_cont: str = "",
        max_depth: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        [국내주식] 종목정보 > 주식기본조회[v1_국내주식-067]
        주식기본조회 API를 호출하여 raw output list로 반환합니다.

        Args:
            prdt_type_cd: 상품유형코드 (300: 주식/ETF/ETN/ELW, 301: 선물옵션, 302: 채권, 306: ELS)
            pdno: 종목번호 (6자리) ETN의 경우 Q로 시작 (EX. Q500001)
            tr_cont: 연속 거래 여부
            max_depth: 최대 재귀 깊이 (기본값: 10)

        Returns:
            List[Dict[str, Any]]: 주식기본조회 raw output list
        """
        if not prdt_type_cd:
            logger.error("prdt_type_cd is required. (e.g. '300')")
            raise ValueError("prdt_type_cd is required. (e.g. '300')")

        if not pdno:
            logger.error("pdno is required. (e.g. '000660')")
            raise ValueError("pdno is required. (e.g. '000660')")

        api_url = "/uapi/domestic-stock/v1/quotations/search-stock-info"
        tr_id = "CTPF1002R"

        params = {
            "PRDT_TYPE_CD": prdt_type_cd,
            "PDNO": pdno,
        }

        results: List[Dict[str, Any]] = []
        depth = 0
        current_tr_cont = tr_cont

        while depth < max_depth:
            res = self._url_fetch(api_url, tr_id, current_tr_cont, params)

            if not res.is_ok():
                res.print_error(api_url)
                logger.error(
                    "API call failed: %s - %s",
                    res.get_error_code(),
                    res.get_error_message(),
                )
                return []

            body = res.get_body()
            output = getattr(body, "output", None)

            if output is None:
                current_batch: List[Dict[str, Any]] = []
            elif isinstance(output, list):
                current_batch = output
            elif hasattr(output, "_asdict"):
                current_batch = [output._asdict()]
            elif isinstance(output, dict):
                current_batch = [output]
            else:
                current_batch = []

            results.extend(current_batch)

            next_tr_cont = res.get_header().tr_cont
            if next_tr_cont == "M":
                logger.info("Calling next page for search_stock_info...")
                self._smart_sleep()
                current_tr_cont = "N"
                depth += 1
                continue

            logger.info("search_stock_info fetch complete.")
            break

        if depth >= max_depth:
            logger.warning(
                "Maximum recursion depth (%d) reached. Stopping further requests.",
                max_depth,
            )

        return results


# Global instance
kdevelopers_client = KDevelopersClient()
