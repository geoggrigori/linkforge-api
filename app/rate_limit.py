"""In-memory token-bucket rate limiting middleware.

Each client IP gets a bucket of ``rate_limit_requests`` tokens that refills
continuously over ``rate_limit_window_seconds``. A request costs one token; when
the bucket is empty the middleware returns ``429 Too Many Requests`` with a
``Retry-After`` header. No external store (Redis) required for a single instance.
"""

import threading
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .config import get_settings

settings = get_settings()


class _Bucket:
    __slots__ = ("tokens", "updated")

    def __init__(self, tokens: float, updated: float):
        self.tokens = tokens
        self.updated = updated


class RateLimiter:
    def __init__(self, capacity: int, window: float):
        self._capacity = capacity
        self._refill_rate = capacity / window  # tokens per second
        self._buckets: dict[str, _Bucket] = {}
        self._lock = threading.Lock()

    def allow(self, key: str) -> tuple[bool, float]:
        """Return (allowed, retry_after_seconds)."""
        now = time.monotonic()
        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None:
                bucket = _Bucket(self._capacity, now)
                self._buckets[key] = bucket

            # Refill based on elapsed time, capped at capacity.
            elapsed = now - bucket.updated
            bucket.tokens = min(
                self._capacity, bucket.tokens + elapsed * self._refill_rate
            )
            bucket.updated = now

            if bucket.tokens >= 1:
                bucket.tokens -= 1
                return True, 0.0
            retry_after = (1 - bucket.tokens) / self._refill_rate
            return False, retry_after


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._limiter = RateLimiter(
            settings.rate_limit_requests, settings.rate_limit_window_seconds
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        # Docs and health checks shouldn't be rate limited.
        if request.url.path in ("/health", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "anonymous"
        allowed, retry_after = self._limiter.allow(client_ip)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Slow down."},
                headers={"Retry-After": str(int(retry_after) + 1)},
            )
        return await call_next(request)
