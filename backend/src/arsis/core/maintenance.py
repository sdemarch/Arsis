"""Maintenance mode: exclusive access to the database while its file is replaced.

Every API request is counted on entry. An operation that replaces the database
(importing a save) first waits for the other requests to finish, then keeps new
ones out with ``503 MAINTENANCE_IN_PROGRESS`` until it is done.
"""

import json
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime

from starlette.types import ASGIApp, Receive, Scope, Send

from arsis.core.errors import DomainError
from arsis.core.time import utc_now

DRAIN_TIMEOUT_SECONDS = 30.0


class MaintenanceBusyError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code="MAINTENANCE_BUSY",
            message="Altre operazioni sono in corso: riprovare tra qualche istante",
            status_code=409,
        )


class MaintenanceGate:
    def __init__(self) -> None:
        self._condition = threading.Condition()
        self._active = False
        self._in_flight = 0
        # Access tokens issued before the last data replacement may name a different user.
        self.tokens_not_before: datetime | None = None

    @property
    def active(self) -> bool:
        return self._active

    def enter(self) -> bool:
        with self._condition:
            if self._active:
                return False
            self._in_flight += 1
            return True

    def leave(self) -> None:
        with self._condition:
            self._in_flight -= 1
            self._condition.notify_all()

    @contextmanager
    def exclusive(
        self, *, own_requests: int = 1, timeout: float = DRAIN_TIMEOUT_SECONDS
    ) -> Iterator[None]:
        """Run the block alone; ``own_requests`` is the caller's own share of in-flight requests."""
        with self._condition:
            if self._active:
                raise MaintenanceBusyError()
            self._active = True
            if not self._condition.wait_for(lambda: self._in_flight <= own_requests, timeout):
                self._active = False
                raise MaintenanceBusyError()
        try:
            yield
        finally:
            with self._condition:
                self._active = False

    def revoke_tokens(self) -> None:
        self.tokens_not_before = utc_now()


maintenance_gate = MaintenanceGate()

_UNAVAILABLE = json.dumps(
    {
        "error": {
            "code": "MAINTENANCE_IN_PROGRESS",
            "message": "Arsis sta sostituendo i dati: riprovare tra qualche istante",
            "details": None,
            "request_id": None,
        }
    }
).encode()


class MaintenanceMiddleware:
    """Count API requests and turn them away while maintenance is running."""

    def __init__(self, app: ASGIApp, gate: MaintenanceGate = maintenance_gate) -> None:
        self.app = app
        self.gate = gate

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not scope["path"].startswith("/api/"):
            await self.app(scope, receive, send)
            return
        if not self.gate.enter():
            await send(
                {
                    "type": "http.response.start",
                    "status": 503,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (b"retry-after", b"5"),
                    ],
                }
            )
            await send({"type": "http.response.body", "body": _UNAVAILABLE})
            return
        try:
            await self.app(scope, receive, send)
        finally:
            self.gate.leave()
