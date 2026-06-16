"""A tiny thread-safe TTL + LRU cache for hot redirect lookups.

Redirects are read far more often than links are created, so caching the
``code -> target_url`` mapping removes a database hit from the hot path. Entries
expire after ``cache_ttl_seconds`` and the cache is bounded to
``cache_max_size`` (least-recently-used eviction).
"""

import threading
import time
from collections import OrderedDict

from .config import get_settings

settings = get_settings()


class TTLCache:
    def __init__(self, max_size: int, ttl: float):
        self._max_size = max_size
        self._ttl = ttl
        self._data: OrderedDict[str, tuple[float, str]] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str) -> str | None:
        with self._lock:
            item = self._data.get(key)
            if item is None:
                return None
            expires_at, value = item
            if time.monotonic() > expires_at:
                del self._data[key]
                return None
            self._data.move_to_end(key)  # mark as recently used
            return value

    def set(self, key: str, value: str) -> None:
        with self._lock:
            self._data[key] = (time.monotonic() + self._ttl, value)
            self._data.move_to_end(key)
            while len(self._data) > self._max_size:
                self._data.popitem(last=False)  # evict least-recently-used

    def invalidate(self, key: str) -> None:
        with self._lock:
            self._data.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()


redirect_cache = TTLCache(
    max_size=settings.cache_max_size, ttl=settings.cache_ttl_seconds
)
