#!/usr/bin/env python3
"""Check that each 한국투자증권 (KIS) app key / secret pair in .env works.

For every key pair found in the repo-root .env file this script:
  1. Requests an access token from /oauth2/tokenP (validates key + secret).
     If the real-trading server rejects the key, it retries against the
     paper-trading (모의투자) server to tell you which kind of key it is.
  2. Calls the stock price API for 삼성전자 (005930) with that token.
  3. Saves the token to the local token cache so the app reuses it
     instead of issuing another one (KIS allows 1 issuance per minute).

Secrets and tokens are never printed.

Usage (from backend/):
    uv run python scripts/check_hantu_keys.py
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import requests
from dotenv import dotenv_values, load_dotenv

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

# Put .env values (such as HANTU_TOKEN_CACHE_PATH) into the environment
# before token_store is imported, so the script writes the same token cache
# file as the app. Variables already set in the shell take precedence.
load_dotenv(ROOT / ".env")

from src.integrations.token_store import hash_api_key, token_store  # noqa: E402

SERVERS = {
    "real": "https://openapi.koreainvestment.com:9443",
    "paper": "https://openapivts.koreainvestment.com:29443",
}
KST = timezone(timedelta(hours=9))

# (label, env names for the key, env names for the secret)
KEY_PAIRS = [
    ("key 1", ["HANTU_API_KEY"], ["HANTU_API_SECRET"]),
    (
        "key 2",
        ["HANTU_API_KEY_2", "HANTU_API_KEY2"],
        ["HANTU_API_SECRET_2", "HANTU_API_SECRET2"],
    ),
]


def mask(value: str) -> str:
    return f"{value[:4]}…{value[-4:]}" if len(value) > 8 else "****"


def first_set(env: dict[str, Optional[str]], names: list[str]) -> tuple[str, str]:
    for name in names:
        value = (env.get(name) or "").strip()
        if value:
            return name, value
    return names[0], ""


def describe_error(resp: requests.Response) -> str:
    try:
        body = resp.json()
    except ValueError:
        return f"HTTP {resp.status_code}: {resp.text[:200]}"
    code = body.get("error_code") or body.get("msg_cd") or ""
    msg = body.get("error_description") or body.get("msg1") or ""
    return f"HTTP {resp.status_code} {code} {msg}".strip()


def issue_token(base_url: str, key: str, secret: str) -> tuple[Optional[dict[str, Any]], str]:
    resp = requests.post(
        f"{base_url}/oauth2/tokenP",
        json={"grant_type": "client_credentials", "appkey": key, "appsecret": secret},
        headers={"content-type": "application/json"},
        timeout=10,
    )
    if resp.status_code == 200 and resp.json().get("access_token"):
        return resp.json(), ""
    return None, describe_error(resp)


def check_quote(base_url: str, key: str, secret: str, token: str) -> tuple[bool, str]:
    resp = requests.get(
        f"{base_url}/uapi/domestic-stock/v1/quotations/inquire-price",
        headers={
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {token}",
            "appkey": key,
            "appsecret": secret,
            "tr_id": "FHKST01010100",
            "custtype": "P",
        },
        params={"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": "005930"},
        timeout=10,
    )
    try:
        body = resp.json()
    except ValueError:
        body = {}
    if resp.status_code == 200 and body.get("rt_cd") == "0":
        price = body.get("output", {}).get("stck_prpr", "?")
        return True, f"삼성전자 현재가 {int(price):,}원" if price.isdigit() else "ok"
    return False, describe_error(resp)


def check_pair(label: str, key_name: str, key: str, secret_name: str, secret: str) -> bool:
    print(f"\n[{label}] {key_name}={mask(key)}  {secret_name}=<{len(secret)} chars>")
    if not key or not secret:
        print(f"  SKIP  {key_name} or {secret_name} is empty in .env")
        return False

    token_data, real_error = issue_token(SERVERS["real"], key, secret)
    server = "real"
    if not token_data:
        print(f"  real server token:  FAIL  {real_error}")
        token_data, paper_error = issue_token(SERVERS["paper"], key, secret)
        server = "paper"
        if not token_data:
            print(f"  paper server token: FAIL  {paper_error}")
            return False

    expires = token_data.get("access_token_token_expired", "?")
    print(f"  token ({server} server): OK  expires {expires} KST")

    if server == "real":
        try:
            expiry = (
                datetime.strptime(expires, "%Y-%m-%d %H:%M:%S")
                .replace(tzinfo=KST)
                .astimezone(timezone.utc)
            )
            token_store.save(hash_api_key(key), token_data["access_token"], expiry)
            print(f"  cached token -> {token_store.path}")
        except ValueError:
            pass
    else:
        print("  note: this is a paper-trading (모의투자) key; the app is set "
              "up for the real server")

    ok, detail = check_quote(SERVERS[server], key, secret, token_data["access_token"])
    print(f"  price API:          {'OK  ' if ok else 'FAIL'}  {detail}")
    return ok


def main() -> int:
    env_path = ROOT / ".env"
    if not env_path.exists():
        print(f"No .env found at {env_path}")
        return 1
    env = dotenv_values(env_path)

    results = []
    for label, key_names, secret_names in KEY_PAIRS:
        key_name, key = first_set(env, key_names)
        secret_name, secret = first_set(env, secret_names)
        if label != "key 1" and not key and not secret:
            continue
        results.append((label, check_pair(label, key_name, key, secret_name, secret)))

    print("\nSummary: " + ", ".join(f"{l} {'OK' if ok else 'FAIL'}" for l, ok in results))
    return 0 if all(ok for _, ok in results) else 1


if __name__ == "__main__":
    sys.exit(main())
