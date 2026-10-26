from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from arsis.auth.service import bootstrap_first_responsible
from arsis.core.database import get_database_session
from arsis.core.errors import ConflictError
from arsis.generated.models import Base, RefreshSession
from arsis.main import create_app

EMAIL = "responsabile@example.it"
PASSWORD = "correct horse battery staple"


@pytest.fixture
def auth_app(tmp_path) -> tuple[FastAPI, sessionmaker[Session]]:
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'auth.db').as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as session:
        bootstrap_first_responsible(
            session,
            email=EMAIL,
            display_name="Responsabile Test",
            password=PASSWORD,
        )

    def override_session() -> Iterator[Session]:
        with factory() as session:
            try:
                yield session
            finally:
                if session.in_transaction():
                    session.rollback()

    application = create_app()
    application.dependency_overrides[get_database_session] = override_session
    yield application, factory
    engine.dispose()


def _login(client: TestClient):
    return client.post(
        "/api/v1/auth/login",
        json={"email": EMAIL, "password": PASSWORD},
    )


def test_login_me_and_protected_api(auth_app) -> None:
    application, _factory = auth_app
    with TestClient(application) as client:
        assert client.get("/api/v1").status_code == 401

        response = _login(client)
        assert response.status_code == 200
        body = response.json()
        assert body["token_type"] == "bearer"
        assert body["expires_in"] == 900
        assert isinstance(body["user"]["id"], int)
        assert body["user"]["email"] == EMAIL
        assert "refresh_token" not in body
        assert "HttpOnly" in response.headers["set-cookie"]
        assert "SameSite=lax" in response.headers["set-cookie"]

        headers = {"Authorization": f"Bearer {body['access_token']}"}
        assert client.get("/api/v1/auth/me", headers=headers).json()["email"] == EMAIL
        assert client.get("/api/v1", headers=headers).status_code == 200


def test_invalid_login_is_generic_and_does_not_create_cookie(auth_app) -> None:
    application, _factory = auth_app
    with TestClient(application) as client:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "unknown@example.it", "password": "wrong-password"},
        )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"
    assert "set-cookie" not in response.headers


def test_refresh_is_rotated_and_old_token_cannot_be_replayed(auth_app) -> None:
    application, factory = auth_app
    with TestClient(application) as client:
        assert _login(client).status_code == 200
        old_token = client.cookies["arsis_refresh_token"]

        refreshed = client.post("/api/v1/auth/refresh")
        assert refreshed.status_code == 200
        assert client.cookies["arsis_refresh_token"] != old_token

        with TestClient(application) as replay_client:
            replay_client.cookies.set(
                "arsis_refresh_token", old_token, path="/api/v1/auth"
            )
            replay = replay_client.post("/api/v1/auth/refresh")
        assert replay.status_code == 401
        assert replay.json()["error"]["code"] == "INVALID_REFRESH_SESSION"

    with factory() as session:
        sessions = session.scalars(select(RefreshSession)).all()
    assert len(sessions) == 2
    assert sessions[0].revoked_at is not None
    assert sessions[1].revoked_at is None


def test_logout_revokes_session_and_clears_cookie(auth_app) -> None:
    application, _factory = auth_app
    with TestClient(application) as client:
        assert _login(client).status_code == 200
        refresh_token = client.cookies["arsis_refresh_token"]

        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 204
        assert "arsis_refresh_token=" in response.headers["set-cookie"]

        client.cookies.set(
            "arsis_refresh_token", refresh_token, path="/api/v1/auth"
        )
        assert client.post("/api/v1/auth/refresh").status_code == 401


def test_bootstrap_can_only_create_the_first_user(auth_app) -> None:
    _application, factory = auth_app
    with factory() as session, pytest.raises(
        ConflictError, match="già stato configurato"
    ):
        bootstrap_first_responsible(
            session,
            email="secondo@example.it",
            display_name="Secondo",
            password="another secure password",
        )
