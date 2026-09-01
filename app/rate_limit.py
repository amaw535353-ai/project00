import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException

from app.logging_config import security_event


class InMemoryRateLimiter:
    """Per-process fixed resource limiter; production should use a shared atomic store."""

    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str, limit: int, window_seconds: int) -> None:
        now = time.monotonic()
        with self._lock:
            events = self._events[key]
            while events and events[0] <= now - window_seconds:
                events.popleft()
            if len(events) >= limit:
                security_event("rate_limit_exceeded", reason="request_limit")
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests",
                    headers={"Retry-After": str(window_seconds)},
                )
            events.append(now)

    def reset(self) -> None:
        with self._lock:
            self._events.clear()


limiter = InMemoryRateLimiter()
