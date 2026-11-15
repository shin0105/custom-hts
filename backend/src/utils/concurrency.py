"""Helpers for running blocking calls from async handlers."""

import asyncio
import functools
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    Hashable,
    Optional,
    ParamSpec,
    Tuple,
    TypeVar,
)

P = ParamSpec("P")
R = TypeVar("R")

# The broker clients (KIS via requests, OpenDART, master-file downloads) are
# synchronous. Calling them directly inside ``async def`` would block the
# event loop, so every request would wait for the slowest one. They run on
# this pool instead.
#
# More workers do not mean more KIS traffic: the KIS client spaces requests
# with its own thread-safe rate limiter. Several workers let a quick quote go
# through while a long fan-out (bond master, option chain) is still running.
BLOCKING_POOL_WORKERS = 4

_blocking_executor = ThreadPoolExecutor(
    max_workers=BLOCKING_POOL_WORKERS, thread_name_prefix="blocking-io"
)


async def run_blocking(func: Callable[..., R], *args: Any, **kwargs: Any) -> R:
    """Run a blocking function on the blocking-call pool and await it.

    Never call this (or wait on its result) from code that is itself
    running on the pool: with every worker busy that would deadlock.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        _blocking_executor, functools.partial(func, *args, **kwargs)
    )


def to_thread(
    func: Callable[P, R],
) -> Callable[P, Coroutine[Any, Any, R]]:
    """Decorate a blocking function so that awaiting it runs it on the pool.

    The decorated method is written as plain synchronous code but is
    called as ``await service.method(...)``. Inside other blocking code,
    call a plain helper instead: the decorated method returns a coroutine.
    """

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return await run_blocking(func, *args, **kwargs)

    return wrapper


def holding_lock(
    lock_attr: str,
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """Run a method while holding the lock stored at ``self.<lock_attr>``.

    For methods that download or parse files at fixed paths, which two pool
    threads must not do at once. Use an ``RLock`` if decorated methods call
    one another.
    """

    def decorate(method: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(method)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> R:
            with getattr(self, lock_attr):
                return method(self, *args, **kwargs)

        return wrapper

    return decorate


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
