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

import json
import hashlib
import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
from collections import namedtuple
import requests
from ..utils.config import settings
from ..integrations.supabase_client import supabase_client
from ..models.korean import (
    KoreanStockQuote,
    KoreanCandleData,
    KoreanAccountBalance,
    KoreanStockPosition,
)
from ..utils.helpers import safe_float, safe_int, calculate_change_percent

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
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
            self._err_code = (
                self._body.msg_cd if hasattr(self._body, "msg_cd") else None
            )
            self._err_message = (
                self._body.msg1 if hasattr(self._body, "msg1") else None
            )
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
                field_name = x.replace("-", "_")
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
        self._kst_tz = timezone(timedelta(hours=9))

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

        api_key_hash = (
            hashlib.sha256(self.api_key.encode("utf-8")).hexdigest()
            if self.api_key
            else ""
        )

        # Check in-memory token first
        if (
            self.access_token
            and self.token_expiry
            and datetime.now(timezone.utc) < self.token_expiry
        ):
            return self.access_token

        # Check cached token in Supabase
        if api_key_hash and supabase_client.client:
            cached = (
                supabase_client.get_kdevelopers_token(api_key_hash)
                if hasattr(supabase_client, "get_kdevelopers_token")
                else None
            )

            if cached:
                cached_token = cached.get("access_token")
                expires_at = cached.get("expires_at")
                cached_expiry = None
                if expires_at:
                    try:
                        cached_expiry = datetime.fromisoformat(expires_at)
                        if cached_expiry.tzinfo is None:
                            cached_expiry = cached_expiry.replace(
                                tzinfo=timezone.utc
                            )
                    except Exception:
                        cached_expiry = None

                if (
                    cached_token
                    and cached_expiry
                    and datetime.now(timezone.utc) < cached_expiry
                ):
                    self.access_token = cached_token
                    self.token_expiry = cached_expiry
                    return self.access_token

                if (
                    cached_expiry
                    and datetime.now(timezone.utc) >= cached_expiry
                ):
                    if hasattr(supabase_client, "delete_kdevelopers_token"):
                        supabase_client.delete_kdevelopers_token(api_key_hash)

        # Request new token
        try:
            url = f"{self.base_url}/oauth2/tokenP"
            headers = self._get_base_headers()
            body = {
                "grant_type": "client_credentials",
                "appkey": self.api_key,
                "appsecret": self.api_secret,
            }

            response = requests.post(
                url, headers=headers, json=body, timeout=10
            )
            response.raise_for_status()

            data = response.json()
            self.access_token = data.get("access_token")
            # Token typically expires in 24 hours
            token_expired = data.get("access_token_token_expired")
            if token_expired:
                self.token_expiry = (
                    datetime.strptime(token_expired, "%Y-%m-%d %H:%M:%S")
                    .replace(tzinfo=self._kst_tz)
                    .astimezone(timezone.utc)
                )
            else:
                self.token_expiry = datetime.now(timezone.utc)

            self._last_auth_time = datetime.now()
            logger.info(
                f"[{self._last_auth_time}] => Token acquired successfully"
            )

            if api_key_hash and supabase_client.client and self.access_token:
                supabase_client.save_kdevelopers_token(
                    api_key_hash, self.access_token, self.token_expiry
                )

            return self.access_token
        except Exception as e:
            if api_key_hash and supabase_client.client:
                supabase_client.delete_kdevelopers_token(api_key_hash)
            logger.error(f"Failed to get access token: {e}")
            return None

    def revoke_access_token(self, token: Optional[str] = None) -> bool:
        """
        Revoke an access token via /oauth2/revokeP and clear cached token.

        Args:
            token: Access token to revoke. If None, uses in-memory or cached token.

        Returns:
            True if revoke succeeded, False otherwise.
        """
        if not self.api_key or not self.api_secret:
            logger.error("API credentials not configured")
            return False

        api_key_hash = (
            hashlib.sha256(self.api_key.encode("utf-8")).hexdigest()
            if self.api_key
            else ""
        )

        access_token = token or self.access_token

        if not access_token and api_key_hash and supabase_client.client:
            cached = supabase_client.get_kdevelopers_token(api_key_hash)
            if cached:
                access_token = cached.get("access_token")

        if not access_token:
            logger.error("No access token available to revoke")
            return False

        try:
            url = f"{self.base_url}/oauth2/revokeP"
            headers = self._get_base_headers()
            body = {
                "appkey": self.api_key,
                "appsecret": self.api_secret,
                "token": access_token,
            }
            response = requests.post(
                url, headers=headers, json=body, timeout=10
            )
            if response.status_code == 200:
                logger.info("Access token revoked successfully")
                self.access_token = None
                self.token_expiry = None
                if api_key_hash and supabase_client.client:
                    supabase_client.delete_kdevelopers_token(api_key_hash)
                return True

            logger.error(
                "Failed to revoke token: %s - %s",
                response.status_code,
                response.text,
            )
            return False
        except Exception as e:
            logger.error(f"Exception in revoke_access_token: {e}")
            return False

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

        def _do_request(auth_token: str) -> APIResponse:
            url = f"{self.base_url}{api_url}"
            headers = self._get_base_headers()

            # Add authorization headers
            headers["authorization"] = f"Bearer {auth_token}"
            headers["appkey"] = self.api_key
            headers["appsecret"] = self.api_secret
            headers["tr_id"] = tr_id
            headers["custtype"] = "P"  # Personal customer
            headers["tr_cont"] = tr_cont

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
            return APIResponse(response)

        token = self._get_access_token()
        if not token:
            raise Exception("Failed to get access token")

        try:
            res = _do_request(token)
            if not res.is_ok() and self._is_token_expired_response(res):
                self._purge_cached_token()
                refreshed = self._get_access_token()
                if not refreshed:
                    return res
                res = _do_request(refreshed)
            if res.get_res_code() != 200:
                logger.error(
                    f"API Error: {res.get_res_code()} - {res.get_response().text}"
                )
            return res
        except Exception as e:
            logger.error(f"Request failed for {api_url}: {e}")
            raise

    def _is_token_expired_response(self, res: APIResponse) -> bool:
        err_code = res.get_error_code()
        err_message = res.get_error_message()
        if err_code == "EGW00123":
            return True
        if (
            err_message
            and "token" in err_message.lower()
            and "만료" in err_message
        ):
            return True
        return False

    def _purge_cached_token(self) -> None:
        self.access_token = None
        self.token_expiry = None
        api_key_hash = (
            hashlib.sha256(self.api_key.encode("utf-8")).hexdigest()
            if self.api_key
            else ""
        )
        if api_key_hash and supabase_client.client:
            supabase_client.delete_kdevelopers_token(api_key_hash)

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
                output = getattr(body, "output", None)
                if output is None:
                    logger.error(f"No output in response for {symbol}")
                    return None

                # Convert namedtuple to dict for easier access
                if hasattr(output, "_asdict"):
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

    def get_bond_price(self, pdno: str) -> Optional[Dict[str, Any]]:
        """
        Get domestic listed bond current price.

        API: [장내채권] 기본시세 > 장내채권현재가(시세) [국내주식-200]
        """
        try:
            api_url = "/uapi/domestic-bond/v1/quotations/inquire-price"
            tr_id = "FHKBJ773400C0"
            params = {
                "FID_COND_MRKT_DIV_CODE": "B",
                "FID_INPUT_ISCD": pdno,
            }
            res = self._url_fetch(api_url, tr_id, "", params)
            if not res.is_ok():
                res.print_error(api_url)
                return None

            body = res.get_body()
            output = getattr(body, "output", None)
            if output is None:
                return None
            if hasattr(output, "_asdict"):
                return output._asdict()
            if isinstance(output, dict):
                return output
            return None
        except Exception as e:
            logger.error(f"Exception in get_bond_price for {pdno}: {e}")
            return None

    def get_bond_basic_info(self, pdno: str) -> Optional[Dict[str, Any]]:
        """
        Get domestic listed bond basic information.

        API: [장내채권] 기본시세 > 장내채권 기본조회 [국내주식-129]
        """
        try:
            api_url = "/uapi/domestic-bond/v1/quotations/search-bond-info"
            tr_id = "CTPF1114R"
            params = {
                "PDNO": pdno,
                "PRDT_TYPE_CD": "302",
            }
            res = self._url_fetch(api_url, tr_id, "", params)
            if not res.is_ok():
                res.print_error(api_url)
                return None

            body = res.get_body()
            output = getattr(body, "output", None)
            if output is None:
                return None
            if hasattr(output, "_asdict"):
                return output._asdict()
            if isinstance(output, dict):
                return output
            return None
        except Exception as e:
            logger.error(f"Exception in get_bond_basic_info for {pdno}: {e}")
            return None

    def get_bond_issue_info(self, pdno: str) -> Optional[Dict[str, Any]]:
        """
        Get domestic listed bond issuance information.

        API: [장내채권] 기본시세 > 장내채권 발행정보 [국내주식-119]
        """
        try:
            api_url = "/uapi/domestic-bond/v1/quotations/issue-info"
            tr_id = "CTPF1101R"
            params = {
                "PDNO": pdno,
            }
            res = self._url_fetch(api_url, tr_id, "", params)
            if not res.is_ok():
                res.print_error(api_url)
                return None

            body = res.get_body()
            output = getattr(body, "output", None)
            if output is None:
                return None
            if hasattr(output, "_asdict"):
                return output._asdict()
            if isinstance(output, dict):
                return output
            return None
        except Exception as e:
            logger.error(f"Exception in get_bond_issue_info for {pdno}: {e}")
            return None

    def get_daily_candle(
        self,
        symbol: str,
        period: str = "D",
        adjust_price: bool = True,
        limit: int = 100,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
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
                    if limit is not None and i >= limit:
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

                if start_date or end_date:
                    if start_date and (
                        len(start_date) != 8 or not start_date.isdigit()
                    ):
                        raise ValueError(
                            "start_date must be in YYYYMMDD format"
                        )
                    if end_date and (
                        len(end_date) != 8 or not end_date.isdigit()
                    ):
                        raise ValueError("end_date must be in YYYYMMDD format")
                    if start_date and end_date and start_date > end_date:
                        start_date, end_date = end_date, start_date

                    def in_range(date_str: str) -> bool:
                        if start_date and date_str < start_date:
                            return False
                        if end_date and date_str > end_date:
                            return False
                        return True

                    candles = [
                        c for c in candles if c.date and in_range(c.date)
                    ]

                return candles
            else:
                res.print_error(api_url)
                logger.error(f"Failed to get candle data for {symbol}")
                return None

        except Exception as e:
            logger.error(f"Exception in get_daily_candle for {symbol}: {e}")
            return None

    def get_minute_candle(
        self,
        symbol: str,
        interval: int = 1,
        limit: Optional[int] = None,
        date: Optional[str] = None,
        time_str: str = "",
        include_previous: bool = False,
    ) -> Optional[List[KoreanCandleData]]:
        """
        Get minute candle chart data for a Korean stock on a specific date.

        API: [국내주식] 기본시세 > 주식일별분봉조회[국내주식-213]

        Args:
            symbol: Stock code (e.g., "005930" for Samsung Electronics)
            interval: Minute interval (1, 5, 10, 30, 60)
            limit: Number of candles to retrieve (default: 100)
            date: Trading date (YYYYMMDD). Defaults to today in KST if not provided.
            time_str: Time filter (HHMMSS). Empty string returns all.
            include_previous: Whether to include previous data (FID_PW_DATA_INCU_YN)

        Returns:
            List of KoreanCandleData objects or None if fetch fails
        """
        try:
            if interval not in {1, 5, 10, 30, 60}:
                raise ValueError("interval must be one of 1, 5, 10, 30, 60")

            date_provided = date is not None
            if date is None:
                kst_now = datetime.now(timezone.utc).astimezone(
                    timezone(timedelta(hours=9))
                )
                date = kst_now.strftime("%Y%m%d")

            if len(date) != 8 or not date.isdigit():
                raise ValueError("date must be in YYYYMMDD format")

            if time_str and (len(time_str) != 6 or not time_str.isdigit()):
                raise ValueError("time_str must be in HHMMSS format or empty")

            if not time_str:
                time_str = "153000"

            api_url = "/uapi/domestic-stock/v1/quotations/inquire-time-dailychartprice"
            tr_id = "FHKST03010230"

            params = {
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": symbol,
                "FID_INPUT_HOUR_1": "",
                "FID_INPUT_DATE_1": date,
                "FID_PW_DATA_INCU_YN": "Y" if include_previous else "N",
                "FID_FAKE_TICK_INCU_YN": "",
            }

            def fetch_day(
                day_date: str, start_time: str
            ) -> list[dict[str, Any]]:
                day_rows: list[dict[str, Any]] = []
                cursor_time = start_time
                max_pages = 20

                for _ in range(max_pages):
                    params["FID_INPUT_DATE_1"] = day_date
                    params["FID_INPUT_HOUR_1"] = cursor_time
                    res = self._url_fetch(api_url, tr_id, "", params)

                    if not res.is_ok():
                        res.print_error(api_url)
                        logger.error(
                            f"Failed to get minute candle data for {symbol}"
                        )
                        return []

                    batch = res.get_body().output2 or []
                    if not batch:
                        break

                    day_rows.extend(batch)

                    # Stop if we received fewer than 120 rows (no more pages).
                    if len(batch) < 120:
                        break

                    # Move cursor to one second before the oldest candle in batch.
                    oldest = min(
                        batch,
                        key=lambda x: x.get("stck_cntg_hour", "000000"),
                    )
                    oldest_time = oldest.get("stck_cntg_hour", "")
                    if not oldest_time or len(oldest_time) != 6:
                        break

                    try:
                        cursor_dt = datetime.strptime(
                            f"{day_date}{oldest_time}", "%Y%m%d%H%M%S"
                        ) - timedelta(seconds=1)
                        cursor_time = cursor_dt.strftime("%H%M%S")
                    except ValueError:
                        break

                    if cursor_time < "090000":
                        break

                return day_rows

            output_list: list[dict[str, Any]] = []
            output_list.extend(fetch_day(date, time_str))

            # Optionally include previous days if explicitly requested.
            if include_previous:
                try:
                    date_dt = datetime.strptime(date, "%Y%m%d")
                    prev_date = (date_dt - timedelta(days=1)).strftime(
                        "%Y%m%d"
                    )
                except ValueError:
                    prev_date = None

                if prev_date:
                    output_list.extend(fetch_day(prev_date, "153000"))

            if not output_list:
                return None

            # Normalize and sort ascending for aggregation.
            minute_rows = []
            for item in output_list:
                bsop_date = item.get("stck_bsop_date", "")
                cntg_hour = item.get("stck_cntg_hour", "")
                if not bsop_date or not cntg_hour:
                    continue

                dt_key = f"{bsop_date}{cntg_hour}"
                minute_rows.append(
                    {
                        "dt_key": dt_key,
                        "open": safe_float(item.get("stck_oprc")),
                        "high": safe_float(item.get("stck_hgpr")),
                        "low": safe_float(item.get("stck_lwpr")),
                        "close": safe_float(item.get("stck_prpr")),
                        "volume": safe_int(item.get("cntg_vol")),
                    }
                )

            if not minute_rows:
                return None

            # Constrain to selected date and time window (09:00 -> selected time).
            selected_time = time_str or "153000"
            minute_rows = [
                row
                for row in minute_rows
                if row["dt_key"][:8] == date
                and "090000" <= row["dt_key"][8:] <= selected_time
            ]

            minute_rows.sort(key=lambda x: x["dt_key"])

            def to_datetime(dt_key: str) -> datetime:
                return datetime.strptime(dt_key, "%Y%m%d%H%M%S")

            # Aggregate to interval if needed.
            aggregated = []
            if interval == 1:
                aggregated = minute_rows
            else:
                bucket = None
                bucket_start = None
                for row in minute_rows:
                    dt = to_datetime(row["dt_key"])
                    bucket_minute = (dt.minute // interval) * interval
                    bucket_dt = dt.replace(minute=bucket_minute, second=0)

                    if bucket is None or bucket_start != bucket_dt:
                        if bucket:
                            aggregated.append(bucket)
                        bucket_start = bucket_dt
                        bucket = {
                            "dt_key": bucket_dt.strftime("%Y%m%d%H%M%S"),
                            "open": row["open"],
                            "high": row["high"],
                            "low": row["low"],
                            "close": row["close"],
                            "volume": row["volume"],
                        }
                    else:
                        bucket["high"] = max(bucket["high"], row["high"])
                        bucket["low"] = min(bucket["low"], row["low"])
                        bucket["close"] = row["close"]
                        bucket["volume"] += row["volume"]

                if bucket:
                    aggregated.append(bucket)

            # Compute change vs previous close across aggregated list
            prev_close = None
            candles = []
            for row in aggregated:
                change = None
                change_percent = None
                if prev_close is not None:
                    change = row["close"] - prev_close
                    change_percent = calculate_change_percent(
                        row["close"], prev_close
                    )
                    change_percent = (
                        round(change_percent, 2)
                        if change_percent is not None
                        else None
                    )
                prev_close = row["close"]

                candles.append(
                    KoreanCandleData(
                        symbol=symbol,
                        date=row["dt_key"],
                        open=row["open"],
                        high=row["high"],
                        low=row["low"],
                        close=row["close"],
                        volume=row["volume"],
                        change=change,
                        change_percent=change_percent,
                    )
                )

            if limit is not None and len(candles) > limit:
                candles = candles[-limit:]
            return candles

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
                    output2 = (
                        {}
                    )  # Fallback when account summary is missing or empty

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
                logger.error(
                    f"Failed to get account balance for {account_number}"
                )
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

        scty_grp_id_cd_map = {
            "BC": "수익증권",
            "DR": "주식예탁증서",
            "EF": "ETF",
            "EN": "ETN",
            "EW": "ELW",
            "FE": "해외ETF",
            "FO": "선물옵션",
            "FS": "외국주권",
            "FU": "선물",
            "FX": "플렉스 선물",
            "GD": "금현물",
            "IC": "투자계약증권",
            "IF": "사회간접자본투융자회사",
            "KN": "코넥스주권",
            "MF": "투자회사",
            "OP": "옵션",
            "RT": "부동산투자회사",
            "SC": "선박투자회사",
            "SR": "신주인수권증서",
            "ST": "주권",
            "SW": "신주인수권증권",
            "TC": "신탁수익증권",
        }
        stck_kind_cd_map = {
            "000": "해당사항없음",
            "101": "보통주",
            "201": "우선주",
            "202": "2우선주",
            "203": "3우선주",
            "204": "4우선주",
            "205": "5우선주",
            "206": "6우선주",
            "207": "7우선주",
            "208": "8우선주",
            "209": "9우선주",
            "210": "10우선주",
            "211": "11우선주",
            "212": "12우선주",
            "213": "13우선주",
            "214": "14우선주",
            "215": "15우선주",
            "216": "16우선주",
            "217": "17우선주",
            "218": "18우선주",
            "219": "19우선주",
            "220": "20우선주",
            "301": "후배주",
            "401": "혼합주",
        }
        field_map = {
            "scty_grp_id_cd": "security_group_code",
            "setl_mmdd": "settlement_month_day",
            "lstg_stqt": "listed_shares",
            "cpta": "capital_amount",
            "papr": "par_value",
            "kospi200_item_yn": "is_kospi200",
            "scts_mket_lstg_dt": "securities_market_listed_date",
            "scts_mket_lstg_abol_dt": "securities_market_delisted_date",
            "kosdaq_mket_lstg_dt": "kosdaq_listed_date",
            "kosdaq_mket_lstg_abol_dt": "kosdaq_delisted_date",
            "lstg_abol_dt": "delisted_date",
            "stck_kind_cd": "stock_kind_code",
            "prdt_name": "product_full_name",
            "prdt_abrv_name": "product_short_name",
        }

        filtered_results: List[Dict[str, Any]] = []
        for item in results:
            filtered = {
                out_key: item.get(in_key, "")
                for in_key, out_key in field_map.items()
            }
            scty_cd = item.get("scty_grp_id_cd", "")
            if scty_cd:
                filtered["security_group_name_kr"] = scty_grp_id_cd_map.get(
                    scty_cd, ""
                )
            stck_cd = item.get("stck_kind_cd", "")
            if stck_cd:
                filtered["stock_kind_name_kr"] = stck_kind_cd_map.get(
                    stck_cd, ""
                )
            filtered_results.append(filtered)

        return filtered_results

    def get_estimate_perform(
        self,
        sht_cd: str,
        tr_cont: str = "",
        max_depth: int = 10,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        [국내주식] 종목정보 > 국내주식 종목추정실적[국내주식-187]
        국내주식 종목추정실적 API를 호출하여 raw output list로 반환합니다.
        Note: Monetary values in estimate performance (e.g., revenue, operating income,
        net income) are reported in 억원. Convert to KRW by multiplying by 100,000,000
        when using them in calculations.

        Args:
            sht_cd: 종목코드 (예: 265520)
            tr_cont: 연속 거래 여부
            max_depth: 최대 재귀 깊이 (기본값: 10)

        Returns:
            Dict[str, List[Dict[str, Any]]]: output1~output4 raw output lists
        """
        if not sht_cd:
            logger.error("sht_cd is required. (e.g. '265520')")
            raise ValueError("sht_cd is required. (e.g. '265520')")

        api_url = "/uapi/domestic-stock/v1/quotations/estimate-perform"
        tr_id = "HHKST668300C0"

        params = {
            "SHT_CD": sht_cd,
        }

        def normalize_output(output: Any) -> List[Dict[str, Any]]:
            if output is None:
                return []
            if isinstance(output, list):
                normalized = []
                for item in output:
                    if hasattr(item, "_asdict"):
                        normalized.append(item._asdict())
                    elif isinstance(item, dict):
                        normalized.append(item)
                return normalized
            if hasattr(output, "_asdict"):
                return [output._asdict()]
            if isinstance(output, dict):
                return [output]
            return []

        results = {
            "output1": [],
            "output2": [],
            "output3": [],
            "output4": [],
        }

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
                return results

            body = res.get_body()
            results["output1"].extend(
                normalize_output(getattr(body, "output1", None))
            )
            results["output2"].extend(
                normalize_output(getattr(body, "output2", None))
            )
            results["output3"].extend(
                normalize_output(getattr(body, "output3", None))
            )
            results["output4"].extend(
                normalize_output(getattr(body, "output4", None))
            )

            next_tr_cont = res.get_header().tr_cont
            if next_tr_cont in ["M", "F"]:
                logger.info("Calling next page for estimate_perform...")
                self._smart_sleep()
                current_tr_cont = "N"
                depth += 1
                continue

            logger.info("estimate_perform fetch complete.")
            break

        if depth >= max_depth:
            logger.warning(
                "Maximum recursion depth (%d) reached. Stopping further requests.",
                max_depth,
            )

        return results


# Global instance
kdevelopers_client = KDevelopersClient()
