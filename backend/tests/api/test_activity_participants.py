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
def activities_app(tmp_path) -> Iterator[FastAPI]:
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'activities.db').as_posix()}",
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
        json={"email": "responsabile@example.it", "password": "correct horse battery staple"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _person(
    client: TestClient,
    headers: dict[str, str],
    name: str,
    role: str | None = None,
    *,
    start: str = "2026-01-01",
    end: str | None = None,
) -> int:
    first_name, last_name = name.split()
    person = client.post(
        "/api/v1/people", headers=headers, json={"first_name": first_name, "last_name": last_name}
    ).json()
    if role:
        response = client.post(
            f"/api/v1/people/{person['id']}/roles",
            headers=headers,
            json={"role_type": role, "start_date": start, "end_date": end},
        )
        assert response.status_code == 201
    return int(person["id"])


def _activity(client: TestClient, headers: dict[str, str], starts_at: str) -> dict:
    response = client.post(
        "/api/v1/activities",
        headers=headers,
        json={"type": "rehearsal", "title": "Prova generale", "starts_at": starts_at},
    )
    assert response.status_code == 201
    return response.json()


def _names(response) -> list[str]:
    return [row["person_name"] for row in response.json()]


def test_new_activity_convokes_musicians_active_on_its_date(activities_app: FastAPI) -> None:
    with TestClient(activities_app) as client:
        headers = _headers(client)
        _person(client, headers, "Anna Bianchi", "musician")
        _person(client, headers, "Bruno Conti", "musician", end="2026-03-01")
        _person(client, headers, "Carla Dini", "musician", start="2026-06-01")
        _person(client, headers, "Dario Esposito", "member")
        archived_id = _person(client, headers, "Elio Fabbri", "musician")
        version = client.get(f"/api/v1/people/{archived_id}", headers=headers).json()["version"]
        client.delete(f"/api/v1/people/{archived_id}?version={version}", headers=headers)

        activity = _activity(client, headers, "2026-05-10T20:45")
        assert activity["participant_count"] == 1

        participants = client.get(
            f"/api/v1/activities/{activity['id']}/participants", headers=headers
        )
        assert participants.status_code == 200
        assert participants.json()[0]["source"] == "automatic"
        assert participants.json()[0]["attendance"] is None
        assert _names(participants) == ["Anna Bianchi"]


def test_participants_can_be_added_removed_and_refreshed(activities_app: FastAPI) -> None:
    with TestClient(activities_app) as client:
        headers = _headers(client)
        anna = _person(client, headers, "Anna Bianchi", "musician")
        guest = _person(client, headers, "Dario Esposito")
        activity = _activity(client, headers, "2026-05-10T20:45")
        base = f"/api/v1/activities/{activity['id']}/participants"

        added = client.post(base, headers=headers, json={"person_id": guest})
        assert added.status_code == 201
        assert added.json()["source"] == "manual"
        duplicate = client.post(base, headers=headers, json={"person_id": guest})
        assert duplicate.json()["error"]["code"] == "ACTIVITY_PARTICIPANT_EXISTS"
        missing = client.post(base, headers=headers, json={"person_id": 999})
        assert missing.json()["error"]["code"] == "INVALID_ACTIVITY_PARTICIPANT"

        assert client.delete(f"{base}/{anna}", headers=headers).status_code == 204
        assert client.delete(f"{base}/{anna}", headers=headers).status_code == 404
        assert _names(client.get(base, headers=headers)) == ["Dario Esposito"]

        # A musician added after the activity was created is convoked on refresh,
        # while the one removed by hand stays out.
        _person(client, headers, "Carla Dini", "musician")
        refreshed = client.post(f"{base}/musicians", headers=headers)
        assert refreshed.status_code == 200
        assert _names(refreshed) == ["Carla Dini", "Dario Esposito"]

        readded = client.post(base, headers=headers, json={"person_id": anna})
        assert readded.status_code == 201
        assert readded.json()["source"] == "manual"
        assert _names(client.get(base, headers=headers)) == [
            "Anna Bianchi",
            "Carla Dini",
            "Dario Esposito",
        ]


def test_attendance_is_recorded_counted_and_listed_per_person(activities_app: FastAPI) -> None:
    with TestClient(activities_app) as client:
        headers = _headers(client)
        anna = _person(client, headers, "Anna Bianchi", "musician")
        bruno = _person(client, headers, "Bruno Conti", "musician")
        outsider = _person(client, headers, "Dario Esposito")
        activity = _activity(client, headers, "2026-05-10T20:45")
        url = f"/api/v1/activities/{activity['id']}/attendances"

        saved = client.put(
            url,
            headers=headers,
            json={
                "rows": [
                    {"person_id": anna, "attendance": "present"},
                    {"person_id": bruno, "attendance": "absent"},
                ]
            },
        )
        assert saved.status_code == 200
        assert {row["person_name"]: row["attendance"] for row in saved.json()} == {
            "Anna Bianchi": "present",
            "Bruno Conti": "absent",
        }
        assert all(row["attendance_recorded_at"] for row in saved.json())

        counted = client.get(f"/api/v1/activities/{activity['id']}", headers=headers).json()
        assert (counted["participant_count"], counted["present_count"]) == (2, 1)
        assert counted["absent_count"] == 1
        listed = client.get("/api/v1/activities", headers=headers).json()["items"][0]
        assert listed["present_count"] == 1

        not_participant = client.put(
            url, headers=headers, json={"rows": [{"person_id": outsider, "attendance": "present"}]}
        )
        assert not_participant.status_code == 422
        duplicated = client.put(
            url,
            headers=headers,
            json={
                "rows": [
                    {"person_id": anna, "attendance": "present"},
                    {"person_id": anna, "attendance": "absent"},
                ]
            },
        )
        assert duplicated.status_code == 422
        invalid = client.put(
            url, headers=headers, json={"rows": [{"person_id": anna, "attendance": "late"}]}
        )
        assert invalid.status_code == 422

        cleared = client.put(
            url, headers=headers, json={"rows": [{"person_id": anna, "attendance": None}]}
        )
        anna_row = next(row for row in cleared.json() if row["person_id"] == anna)
        assert anna_row["attendance"] is None
        assert anna_row["attendance_recorded_at"] is None

        history = client.get(
            f"/api/v1/activities/participations?person_id={bruno}", headers=headers
        )
        assert history.status_code == 200
        assert history.json() == [
            {
                "activity_id": activity["id"],
                "title": "Prova generale",
                "type": "rehearsal",
                "starts_at": "2026-05-10T20:45",
                "status": "planned",
                "source": "automatic",
                "attendance": "absent",
            }
        ]


def test_activities_can_be_listed_by_local_date_range(activities_app: FastAPI) -> None:
    with TestClient(activities_app) as client:
        headers = _headers(client)
        _activity(client, headers, "2026-10-31T23:30:00+01:00")
        november = _activity(client, headers, "2026-11-01T00:30:00+01:00")
        _activity(client, headers, "2026-12-01T20:45:00+01:00")

        listed = client.get(
            "/api/v1/activities?starts_from=2026-11-01&starts_to=2026-11-30", headers=headers
        )
        assert [item["id"] for item in listed.json()["items"]] == [november["id"]]
        assert (
            client.get("/api/v1/activities?starts_from=01/11/2026", headers=headers).status_code
            == 422
        )
