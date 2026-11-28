from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from arsis.auth.service import bootstrap_first_responsible
from arsis.core.database import get_database_session
from arsis.generated.models import AppSetting, Base
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
        session.add(
            AppSetting(
                key="activities.refund_rules",
                value='{"rehearsal":"2.00","concert":"8.00","event":"5.00"}',
            )
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


def test_register_lists_every_active_person_without_convocation(
    activities_app: FastAPI,
) -> None:
    with TestClient(activities_app) as client:
        headers = _headers(client)
        _person(client, headers, "Anna Bianchi", "musician")
        _person(client, headers, "Bruno Conti", "musician", end="2026-03-01")
        _person(client, headers, "Dario Esposito", "member")
        _person(client, headers, "Gino Lodi")
        archived_id = _person(client, headers, "Elio Fabbri", "musician")
        version = client.get(f"/api/v1/people/{archived_id}", headers=headers).json()["version"]
        client.delete(f"/api/v1/people/{archived_id}?version={version}", headers=headers)

        activity = _activity(client, headers, "2026-05-10T20:45")
        assert activity["participant_count"] == 0

        register = client.get(f"/api/v1/activities/{activity['id']}/participants", headers=headers)
        assert register.status_code == 200
        assert _names(register) == ["Anna Bianchi", "Bruno Conti", "Dario Esposito", "Gino Lodi"]
        assert all(row["attendance"] is None for row in register.json())
        assert "source" not in register.json()[0]

        archived = client.put(
            f"/api/v1/activities/{activity['id']}/attendances",
            headers=headers,
            json={"rows": [{"person_id": archived_id, "attendance": "present"}]},
        )
        assert archived.status_code == 422
        # Convocation endpoints are gone.
        base = f"/api/v1/activities/{activity['id']}/participants"
        assert client.post(base, headers=headers, json={"person_id": 1}).status_code == 405
        assert client.post(f"{base}/musicians", headers=headers).status_code in {404, 405}


def test_archived_people_with_recorded_attendance_stay_in_the_register(
    activities_app: FastAPI,
) -> None:
    with TestClient(activities_app) as client:
        headers = _headers(client)
        anna = _person(client, headers, "Anna Bianchi")
        activity = _activity(client, headers, "2026-05-10T20:45")
        client.put(
            f"/api/v1/activities/{activity['id']}/attendances",
            headers=headers,
            json={"rows": [{"person_id": anna, "attendance": "present"}]},
        )
        version = client.get(f"/api/v1/people/{anna}", headers=headers).json()["version"]
        client.delete(f"/api/v1/people/{anna}?version={version}", headers=headers)

        register = client.get(f"/api/v1/activities/{activity['id']}/participants", headers=headers)
        assert [(row["person_name"], row["attendance"]) for row in register.json()] == [
            ("Anna Bianchi", "present")
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
            "Dario Esposito": None,
        }
        recorded = [row for row in saved.json() if row["attendance"]]
        assert all(row["attendance_recorded_at"] for row in recorded)

        counted = client.get(f"/api/v1/activities/{activity['id']}", headers=headers).json()
        assert (counted["participant_count"], counted["present_count"]) == (2, 1)
        assert counted["absent_count"] == 1
        listed = client.get("/api/v1/activities", headers=headers).json()["items"][0]
        assert listed["present_count"] == 1

        # No convocation: anyone active can be marked present.
        outsider_saved = client.put(
            url, headers=headers, json={"rows": [{"person_id": outsider, "attendance": "present"}]}
        )
        assert outsider_saved.status_code == 200
        unknown = client.put(
            url, headers=headers, json={"rows": [{"person_id": 999, "attendance": "present"}]}
        )
        assert unknown.status_code == 422
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
                "attendance": "absent",
                "is_driver": False,
                "passenger_count": None,
                "distance_km": None,
                "reimbursement_flat": "0.00",
                "reimbursement_mileage": "0.00",
                "reimbursement_highway": "0.00",
                "reimbursement_amount": "0.00",
            }
        ]


def test_refunds_are_calculated_from_present_attendance(activities_app: FastAPI) -> None:
    with TestClient(activities_app) as client:
        headers = _headers(client)
        anna = _person(client, headers, "Anna Bianchi", "musician")
        bruno = _person(client, headers, "Bruno Conti", "musician")
        rehearsal = _activity(client, headers, "2026-05-10T20:45")
        concert = client.post(
            "/api/v1/activities",
            headers=headers,
            json={"type": "concert", "title": "Concerto", "starts_at": "2026-05-11T20:45"},
        ).json()
        for activity, rows in (
            (rehearsal, [{"person_id": anna, "attendance": "present"}]),
            (
                concert,
                [
                    {"person_id": anna, "attendance": "present"},
                    {"person_id": bruno, "attendance": "present"},
                ],
            ),
        ):
            response = client.put(
                f"/api/v1/activities/{activity['id']}/attendances",
                headers=headers,
                json={"rows": rows},
            )
            assert response.status_code == 200

        detail = client.get(f"/api/v1/activities/{concert['id']}", headers=headers)
        assert detail.json()["reimbursement_total"] == "16.00"
        anna_history = client.get(
            f"/api/v1/activities/participations?person_id={anna}", headers=headers
        )
        assert [row["reimbursement_amount"] for row in anna_history.json()] == ["8.00", "2.00"]
        summary = client.get("/api/v1/activities/refund-summary", headers=headers)
        assert summary.json() == [
            {
                "person_id": anna,
                "person_name": "Anna Bianchi",
                "rehearsal": "2.00",
                "concert": "8.00",
                "event": "0.00",
                "mileage": "0.00",
                "highway": "0.00",
                "distance_km": 0,
                "total": "10.00",
            },
            {
                "person_id": bruno,
                "person_name": "Bruno Conti",
                "rehearsal": "0.00",
                "concert": "8.00",
                "event": "0.00",
                "mileage": "0.00",
                "highway": "0.00",
                "distance_km": 0,
                "total": "8.00",
            },
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
