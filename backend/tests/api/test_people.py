from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from arsis.auth.service import bootstrap_first_responsible
from arsis.core.database import get_database_session
from arsis.generated.models import Base
from arsis.main import create_app


@pytest.fixture
def people_app(tmp_path) -> Iterator[FastAPI]:
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'people.db').as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as session:
        bootstrap_first_responsible(
            session,
            email="responsabile@example.it",
            display_name="Responsabile",
            password="correct horse battery staple",
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
    yield application
    engine.dispose()


def _headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "responsabile@example.it",
            "password": "correct horse battery staple",
        },
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_people_crud_roles_and_pagination(people_app: FastAPI) -> None:
    with TestClient(people_app) as client:
        headers = _headers(client)
        created = client.post(
            "/api/v1/people",
            headers=headers,
            json={"first_name": "Maria", "last_name": "Rossi", "email": "maria@example.it"},
        )
        assert created.status_code == 201
        person = created.json()
        assert person["id"] == 1
        assert person["version"] == 1

        listing = client.get("/api/v1/people?q=ross", headers=headers)
        assert listing.status_code == 200
        assert listing.json()["meta"]["total_items"] == 1
        assert listing.json()["items"][0]["id"] == person["id"]

        updated = client.patch(
            f"/api/v1/people/{person['id']}",
            headers=headers,
            json={"version": 1, "phone": "3331234567"},
        )
        assert updated.status_code == 200
        assert updated.json()["version"] == 2
        assert updated.json()["phone"] == "3331234567"

        role = client.post(
            f"/api/v1/people/{person['id']}/roles",
            headers=headers,
            json={"role_type": "teacher", "start_date": "2026-01-01"},
        )
        assert role.status_code == 201
        assert role.json()["status"] == "active"

        duplicate_role = client.post(
            f"/api/v1/people/{person['id']}/roles",
            headers=headers,
            json={"role_type": "teacher", "start_date": "2026-01-01"},
        )
        assert duplicate_role.status_code == 409
        assert duplicate_role.json()["error"]["code"] == "ACTIVE_ROLE_EXISTS"

        archived = client.delete(f"/api/v1/people/{person['id']}?version=2", headers=headers)
        assert archived.status_code == 200
        assert archived.json()["archived_at"] is not None
        assert client.get("/api/v1/people", headers=headers).json()["items"] == []


def test_activities_crud_and_archiving(people_app: FastAPI) -> None:
    with TestClient(people_app) as client:
        headers = _headers(client)
        created = client.post(
            "/api/v1/activities",
            headers=headers,
            json={
                "type": "rehearsal",
                "title": "Prova generale",
                "starts_at": "2026-10-30T20:30:00Z",
                "location": "Sala prove",
            },
        )
        assert created.status_code == 201
        activity = created.json()
        assert activity["status"] == "planned"

        listing = client.get("/api/v1/activities?q=generale", headers=headers)
        assert listing.status_code == 200
        assert listing.json()["meta"]["total_items"] == 1

        updated = client.patch(
            f"/api/v1/activities/{activity['id']}",
            headers=headers,
            json={"version": 1, "status": "confirmed"},
        )
        assert updated.status_code == 200
        assert updated.json()["version"] == 2

        archived = client.delete(f"/api/v1/activities/{activity['id']}?version=2", headers=headers)
        assert archived.status_code == 200
        assert archived.json()["archived_at"] is not None
