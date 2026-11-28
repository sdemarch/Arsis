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
def places_app(tmp_path) -> Iterator[FastAPI]:
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'places.db').as_posix()}",
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
        session.commit()

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
        json={"email": "responsabile@example.it", "password": "correct horse battery staple"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_place_lifecycle(places_app: FastAPI) -> None:
    with TestClient(places_app) as client:
        headers = _headers(client)
        created = client.post(
            "/api/v1/places",
            headers=headers,
            json={"name": " Teatro Comunale ", "distance_km": 84, "highway_cost": "12.40"},
        )
        assert created.status_code == 201
        place = created.json()
        assert place["name"] == "Teatro Comunale"
        assert place["distance_km"] == 84
        assert place["highway_cost"] == "12.40"

        updated = client.patch(
            f"/api/v1/places/{place['id']}",
            headers=headers,
            json={"version": place["version"], "distance_km": 90, "address": "Via Roma 1"},
        )
        assert updated.status_code == 200
        assert updated.json()["distance_km"] == 90
        assert updated.json()["address"] == "Via Roma 1"

        stale = client.patch(
            f"/api/v1/places/{place['id']}",
            headers=headers,
            json={"version": place["version"], "distance_km": 10},
        )
        assert stale.status_code == 409

        listed = client.get("/api/v1/places", headers=headers).json()
        assert [item["name"] for item in listed["items"]] == ["Teatro Comunale"]

        archived = client.delete(
            f"/api/v1/places/{place['id']}",
            headers=headers,
            params={"version": updated.json()["version"]},
        )
        assert archived.status_code == 200
        assert archived.json()["archived_at"] is not None
        assert client.get("/api/v1/places", headers=headers).json()["items"] == []
        with_archived = client.get(
            "/api/v1/places", headers=headers, params={"include_archived": True}
        ).json()
        assert len(with_archived["items"]) == 1


def test_place_names_are_unique_among_active_places(places_app: FastAPI) -> None:
    with TestClient(places_app) as client:
        headers = _headers(client)
        first = client.post("/api/v1/places", headers=headers, json={"name": "Piazza"}).json()
        duplicate = client.post("/api/v1/places", headers=headers, json={"name": "piazza"})
        assert duplicate.status_code == 409
        assert duplicate.json()["error"]["code"] == "PLACE_NAME_TAKEN"

        client.delete(
            f"/api/v1/places/{first['id']}", headers=headers, params={"version": first["version"]}
        )
        assert (
            client.post("/api/v1/places", headers=headers, json={"name": "Piazza"}).status_code
            == 201
        )


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "Fuori", "distance_km": -1},
        {"name": "Fuori", "distance_km": 12.5},
        {"name": "Fuori", "highway_cost": "-0.01"},
        {"name": "Fuori", "highway_cost": "1.234"},
        {"name": ""},
    ],
)
def test_place_values_are_validated(places_app: FastAPI, payload: dict) -> None:
    with TestClient(places_app) as client:
        response = client.post("/api/v1/places", headers=_headers(client), json=payload)
        assert response.status_code == 422
