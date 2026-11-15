"""Offline tests for running KIS calls off the event loop (no network)."""

import asyncio
import threading
import time
from datetime import datetime, timedelta, timezone

import httpx
import pytest

from src.integrations import kdevelopers
from src.integrations.kdevelopers import KDevelopersClient, RateLimiter
from src.main import app
from src.services import korean_market
from src.utils.concurrency import holding_lock, run_blocking, to_thread


class MemoryTokenStore:
    """Stand-in for the on-disk token cache."""

    def __init__(self):
        self.entries = {}
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            return self.entries.get(key)

    def save(self, key, token, expires_at):
        with self._lock:
            self.entries[key] = {
                "access_token": token,
                "expires_at": expires_at.isoformat() if expires_at else None,
            }
        return True

    def delete(self, key):
        with self._lock:
            self.entries.pop(key, None)
        return True


class FakeHTTPResponse:
    """Just enough of requests.Response for APIResponse."""

    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.headers = {"tr_cont": ""}
        self.text = str(payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        pass


class FakeKISSession:
    """Issues tokens slowly and rejects the stale token "old"."""

    def __init__(self, issue_delay=0.2):
        self.issue_delay = issue_delay
        self.tokens_issued = 0
        self._lock = threading.Lock()

    def post(self, url, headers=None, json=None, timeout=None):
        time.sleep(self.issue_delay)
        with self._lock:
            self.tokens_issued += 1
            token = f"new-{self.tokens_issued}"
        return FakeHTTPResponse({"access_token": token, "expires_in": 86400})

    def get(self, url, headers=None, params=None, timeout=None):
        if headers["authorization"] == "Bearer old":
            return FakeHTTPResponse(
                {
                    "rt_cd": "1",
                    "msg_cd": "EGW00123",
                    "msg1": "기간이 만료된 token 입니다.",
                },
                status_code=500,
            )
        return FakeHTTPResponse({"rt_cd": "0", "output": {}})


@pytest.fixture()
def kis(monkeypatch):
    """A client with stub keys whose HTTP calls go to FakeKISSession."""
    store = MemoryTokenStore()
    session = FakeKISSession()
    monkeypatch.setattr(kdevelopers, "token_store", store)
    monkeypatch.setattr(
        KDevelopersClient, "_session", property(lambda self: session)
    )
    client = KDevelopersClient()
    client.api_key = "your_api_key"
    client.api_secret = "your_api_secret"
    client._rate_limiter = RateLimiter(0)
    return client, session, store


def _run_in_threads(func, count):
    results = [None] * count
    barrier = threading.Barrier(count)

    def worker(index):
        barrier.wait()
        results[index] = func()

    threads = [
        threading.Thread(target=worker, args=(i,)) for i in range(count)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)
    return results


def test_concurrent_callers_share_one_token_issuance(kis):
    client, session, _ = kis

    tokens = _run_in_threads(client._get_access_token, 8)

    assert session.tokens_issued == 1
    assert tokens == ["new-1"] * 8


def test_expired_token_is_reissued_once_for_concurrent_requests(kis):
    client, session, store = kis
    client.access_token = "old"
    client.token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)

    responses = _run_in_threads(
        lambda: client._url_fetch("/uapi/test", "TR0000", "", {}), 4
    )

    assert session.tokens_issued == 1
    assert all(res.is_ok() for res in responses)
    assert client.access_token == "new-1"
    cached = store.get(kdevelopers.hash_api_key("your_api_key"))
    assert cached["access_token"] == "new-1"


def test_invalidating_a_replaced_token_keeps_the_new_one(kis):
    client, _, store = kis
    key = kdevelopers.hash_api_key("your_api_key")
    client.access_token = "new-1"
    store.save(key, "new-1", None)

    client._invalidate_token("old")

    assert client.access_token == "new-1"
    assert store.get(key)["access_token"] == "new-1"


def test_rate_limiter_spaces_calls_across_threads():
    interval = 0.02
    limiter = RateLimiter(interval)

    def wait_and_stamp():
        limiter.wait()
        return time.monotonic()

    stamps = sorted(_run_in_threads(wait_and_stamp, 6))
    gaps = [later - earlier for earlier, later in zip(stamps, stamps[1:])]

    # Allow a little scheduler jitter below the nominal interval.
    assert min(gaps) >= interval * 0.8
    assert stamps[-1] - stamps[0] >= interval * 5 * 0.9


def test_to_thread_runs_on_the_blocking_pool():
    @to_thread
    def thread_name():
        return threading.current_thread().name

    assert asyncio.run(thread_name()).startswith("blocking-io")


def test_holding_lock_serializes_a_method():
    class Loader:
        def __init__(self):
            self._file_lock = threading.Lock()
            self.active = 0
            self.max_active = 0

        @holding_lock("_file_lock")
        def load(self):
            self.active += 1
            self.max_active = max(self.max_active, self.active)
            time.sleep(0.02)
            self.active -= 1

    loader = Loader()
    _run_in_threads(loader.load, 4)

    assert loader.max_active == 1


def test_slow_kis_call_does_not_block_other_requests(monkeypatch):
    """/health answers while a quote is stuck waiting on KIS."""
    delay = 0.5

    def slow_quote(symbol):
        time.sleep(delay)
        return None

    monkeypatch.setattr(
        korean_market.kdevelopers_client, "get_quote", slow_quote
    )

    async def scenario():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            # Time from the start of the quote: a blocked loop would stall
            # inside the sleep below, before /health is even sent.
            started = time.monotonic()
            quote_task = asyncio.create_task(
                client.get("/api/korean/quote/005930")
            )
            await asyncio.sleep(0.05)
            health = await client.get("/health")
            health_seconds = time.monotonic() - started
            quote = await quote_task
        return health, health_seconds, quote

    health, health_seconds, quote = asyncio.run(scenario())

    assert health.status_code == 200
    assert health_seconds < delay / 2
    assert quote.status_code == 404


def test_concurrent_service_calls_overlap(monkeypatch):
    delay = 0.3

    def slow_quote(symbol):
        time.sleep(delay)
        return None

    monkeypatch.setattr(
        korean_market.kdevelopers_client, "get_quote", slow_quote
    )
    service = korean_market.korean_market_service

    async def scenario():
        started = time.monotonic()
        await asyncio.gather(
            service.get_quote("005930"), service.get_quote("000660")
        )
        return time.monotonic() - started

    assert asyncio.run(scenario()) < delay * 1.8


def test_run_blocking_returns_the_result():
    assert asyncio.run(run_blocking(sum, [1, 2, 3])) == 6
