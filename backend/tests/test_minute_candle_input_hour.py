"""
Test raw API results for different FID_INPUT_HOUR_1 values.

Usage:
  cd backend
  uv run python tests/test_minute_candle_input_hour.py
"""

import sys
import os
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.integrations.kdevelopers import kdevelopers_client

OUTPUT_DIR = Path(__file__).parent / "test-results" / "kdevelopers_responses"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def kst_today() -> str:
    kst_now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=9)))
    return kst_now.strftime("%Y%m%d")


def main():
    symbol = os.getenv("HANTU_TEST_SYMBOL", "005930")
    date = os.getenv("HANTU_MINUTE_CANDLE_DATE", kst_today())

    api_url = "/uapi/domestic-stock/v1/quotations/inquire-time-dailychartprice"
    tr_id = "FHKST03010230"

    time_values = [
        "",        # API default
        "090000",  # market open
        "100000",
        "113000",
        "130000",
        "150000",
        "153000",  # near close
    ]

    results = {
        "timestamp": datetime.now().isoformat(),
        "description": "Raw responses for different FID_INPUT_HOUR_1 values",
        "symbol": symbol,
        "date": date,
        "requests": [],
    }

    for time_str in time_values:
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": symbol,
            "FID_INPUT_HOUR_1": time_str,
            "FID_INPUT_DATE_1": date,
            "FID_PW_DATA_INCU_YN": "N",
            "FID_FAKE_TICK_INCU_YN": "",
        }

        res = kdevelopers_client._url_fetch(api_url, tr_id, "", params)
        raw_json = None
        try:
            raw_json = res.get_response().json()
        except Exception as e:
            raw_json = {"error": f"Failed to parse JSON: {e}"}

        results["requests"].append(
            {
                "params": params,
                "http_status": res.get_res_code(),
                "headers": dict(res.get_response().headers),
                "body": raw_json,
            }
        )

    output_path = OUTPUT_DIR / "06_minutecandleinputtest.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
