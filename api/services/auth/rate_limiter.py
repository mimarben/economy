"""Simple in-memory rate limiter for authentication endpoints.

Tracks failed login attempts per key (client IP or email). A key is blocked
after `max_attempts` failures within `window_seconds`; the block lifts when
the oldest failure leaves the window. Intentionally dependency-free and
per-process (a single-worker deployment is the current setup).
"""
import threading
import time
from collections import deque


class SlidingWindowRateLimiter:
    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def _prune(self, key: str, now: float) -> deque[float]:
        attempts = self._attempts.get(key)
        if attempts is None:
            attempts = deque()
            self._attempts[key] = attempts
        while attempts and now - attempts[0] > self.window_seconds:
            attempts.popleft()
        return attempts

    def is_blocked(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            return len(self._prune(key, now)) >= self.max_attempts

    def register_failure(self, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            self._prune(key, now).append(now)

    def reset(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)


# Shared limiter for the login endpoint: 5 failed attempts / 5 minutes.
login_rate_limiter = SlidingWindowRateLimiter(max_attempts=5, window_seconds=300)
