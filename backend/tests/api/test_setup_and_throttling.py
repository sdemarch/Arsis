from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from arsis.auth.rate_limit import (
    MAX_FAILURES_PER_ACCOUNT,
    MAX_FAILURES_PER_ADDRESS,
    WINDOW_SECONDS,
    LoginRateLimiter,
    TooManyLoginAttemptsError,
)
from arsis.core.database import get_database_session
from arsis.generated.models import Base
from arsis.main import create_app

EMAIL = "responsabile@example.it"
PASSWORD = "correct horse battery staple"


@pytest.fixture
def empty_app(tmp_path) -> Iterator[FastAPI]:
    """An installation that has never been configured: no users at all."""
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'setup.db').as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    def override_session() -> Iterator[Session]:
        with factory() as session:
            try:
                yield session
            finally:
                if session.in_transaction():
                    session.rollback()

    application = create_app()
    application.dependency_overrides[get_database_session] = override_session
    yield application
    engine.dispose()


def _setup(client: TestClient, **overrides: str):
    return client.post(
        "/api/v1/auth/setup",
        json={"email": EMAIL, "display_name": "Responsabile", "password": PASSWORD, **overrides},
    )


def _login(client: TestClient, password: str = PASSWORD, email: str = EMAIL):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


def test_first_run_setup_creates_the_first_responsible_once(empty_app: FastAPI) -> None:
    with TestClient(empty_app) as client:
        assert client.get("/api/v1/auth/setup").json() == {"required": True}
        assert _setup(client, password="corta123").status_code == 422
        assert _setup(client, email="non-una-email").status_code == 422

        created = _setup(client, email=" Responsabile@Example.it ")
        assert created.status_code == 201
        assert created.json()["email"] == EMAIL
        assert client.get("/api/v1/auth/setup").json() == {"required": False}
        assert _login(client).status_code == 200

        again = _setup(client, email="altro@example.it")
        assert again.status_code == 409
        assert again.json()["error"]["code"] == "BOOTSTRAP_ALREADY_COMPLETED"


def test_repeated_failed_logins_are_throttled(empty_app: FastAPI) -> None:
    with TestClient(empty_app) as client:
        _setup(client)
        for _ in range(MAX_FAILURES_PER_ACCOUNT):
            assert _login(client, password="password sbagliata").status_code == 401

        blocked = _login(client)
        assert blocked.status_code == 429
        assert blocked.json()["error"]["code"] == "TOO_MANY_LOGIN_ATTEMPTS"
        assert 0 < int(blocked.headers["Retry-After"]) <= WINDOW_SECONDS
        # Another account from the same address is not blocked by this counter.
        assert _login(client, email="altro@example.it").status_code == 401


def test_successful_login_clears_the_account_counter(empty_app: FastAPI) -> None:
    with TestClient(empty_app) as client:
        _setup(client)
        for _ in range(MAX_FAILURES_PER_ACCOUNT - 1):
            _login(client, password="password sbagliata")
        assert _login(client).status_code == 200
        for _ in range(MAX_FAILURES_PER_ACCOUNT - 1):
            assert _login(client, password="password sbagliata").status_code == 401
        assert _login(client).status_code == 200


def test_limiter_counts_per_address_and_forgets_after_the_window() -> None:
    now = [1000.0]
    limiter = LoginRateLimiter(clock=lambda: now[0])
    for index in range(MAX_FAILURES_PER_ADDRESS):
        limiter.check(address="10.0.0.1", email=f"utente{index}@example.it")
        limiter.record_failure(address="10.0.0.1", email=f"utente{index}@example.it")

    with pytest.raises(TooManyLoginAttemptsError):
        limiter.check(address="10.0.0.1", email="nuovo@example.it")
    limiter.check(address="10.0.0.2", email="nuovo@example.it")

    now[0] += WINDOW_SECONDS
    limiter.check(address="10.0.0.1", email="nuovo@example.it")
