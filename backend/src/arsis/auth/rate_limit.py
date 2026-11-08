"""In-memory throttling of failed logins.

The local runtime is a single process, so counters live in memory and reset
on restart. A failed login counts against both the address+account pair and
the address alone, so one client cannot cycle through accounts.
"""

import math
import time
from collections import deque
from collections.abc import Callable
from threading import Lock

from arsis.core.errors import DomainError

WINDOW_SECONDS = 15 * 60
MAX_FAILURES_PER_ACCOUNT = 5
MAX_FAILURES_PER_ADDRESS = 20


class TooManyLoginAttemptsError(DomainError):
    def __init__(self, retry_after: int) -> None:
        minutes = max(1, math.ceil(retry_after / 60))
        super().__init__(
            code="TOO_MANY_LOGIN_ATTEMPTS",
            message=f"Troppi tentativi di accesso non riusciti. Riprova tra {minutes} minuti.",
            status_code=429,
            headers={"Retry-After": str(retry_after)},
        )


class LoginRateLimiter:
    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._failures: dict[str, deque[float]] = {}
        self._lock = Lock()

    def check(self, *, address: str | None, email: str) -> None:
        """Raise before authenticating when either counter is exhausted."""
        with self._lock:
            now = self._clock()
            for key, limit in self._keys(address, email):
                failures = self._recent(key, now)
                if len(failures) >= limit:
                    raise TooManyLoginAttemptsError(
                        retry_after=max(1, math.ceil(failures[0] + WINDOW_SECONDS - now))
                    )

    def record_failure(self, *, address: str | None, email: str) -> None:
        with self._lock:
            now = self._clock()
            for key, _ in self._keys(address, email):
                self._recent(key, now).append(now)

    def record_success(self, *, address: str | None, email: str) -> None:
        with self._lock:
            self._failures.pop(self._account_key(address, email), None)

    def reset(self) -> None:
        with self._lock:
            self._failures.clear()

    def _keys(self, address: str | None, email: str) -> tuple[tuple[str, int], ...]:
        return (
            (self._account_key(address, email), MAX_FAILURES_PER_ACCOUNT),
            (f"address:{address or '-'}", MAX_FAILURES_PER_ADDRESS),
        )

    @staticmethod
    def _account_key(address: str | None, email: str) -> str:
        return f"account:{address or '-'}:{email.strip().lower()}"

    def _recent(self, key: str, now: float) -> deque[float]:
        failures = self._failures.setdefault(key, deque())
        while failures and failures[0] <= now - WINDOW_SECONDS:
            failures.popleft()
        return failures


login_rate_limiter = LoginRateLimiter()
