"""Helpers for running blocking broker calls from async handlers."""

import asyncio
import functools
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Hashable, Optional, Tuple

# A single worker on purpose: the broker client throttles per call, so two
# multi-call fan-outs running side by side would exceed the rate limit.
_broker_executor = ThreadPoolExecutor(
    max_workers=1, thread_name_prefix="broker-fanout"
)


async def run_blocking(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Run a blocking function off the event loop, one at a time."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        _broker_executor, functools.partial(func, *args, **kwargs)
    )


class TTLCache:
    """Small in-memory cache whose entries expire after ``ttl_seconds``."""

    def __init__(self, ttl_seconds: float, max_items: int = 256) -> None:
        self._ttl = ttl_seconds
        self._max_items = max_items
        self._items: Dict[Hashable, Tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: Hashable) -> Optional[Any]:
        with self._lock:
            entry = self._items.get(key)
            if entry is None:
                return None
            stored_at, value = entry
            if time.monotonic() - stored_at > self._ttl:
                del self._items[key]
                return None
            return value

    def set(self, key: Hashable, value: Any) -> None:
        with self._lock:
            if len(self._items) >= self._max_items:
                oldest = min(self._items, key=lambda k: self._items[k][0])
                del self._items[oldest]
            self._items[key] = (time.monotonic(), value)
