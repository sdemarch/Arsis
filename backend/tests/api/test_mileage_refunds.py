"""RB-18: fuel reimbursement for drivers, recorded as a snapshot with the attendance."""

import json
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

RULES = {
    "rehearsal": "2.00",
    "concert": "8.00",
    "event": "5.00",
    "mileage": {
        "enabled_types": ["event"],
        "rate_per_km": "0.25",
        "passenger_bonus_pct": 10,
        "max_bonus_passengers": 4,
    },
}


@pytest.fixture
def app(tmp_path) -> Iterator[FastAPI]:
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'mileage.db').as_posix()}",
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
        session.add(AppSetting(key="activities.refund_rules", value=json.dumps(RULES)))
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


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        response = test_client.post(
            "/api/v1/auth/login",
            json={"email": "responsabile@example.it", "password": "correct horse battery staple"},
        )
        test_client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"
        yield test_client


def _musicians(client: TestClient, count: int) -> list[int]:
    ids = []
    for index in range(count):
        person = client.post(
            "/api/v1/people", json={"first_name": f"Musicista{index}", "last_name": "Banda"}
        ).json()
        role = client.post(
            f"/api/v1/people/{person['id']}/roles",
            json={"role_type": "musician", "start_date": "2026-01-01"},
        )
        assert role.status_code == 201
        ids.append(int(person["id"]))
    return ids


def _place(client: TestClient, name: str = "Teatro", km: int = 84, toll: str = "12.40") -> dict:
    response = client.post(
        "/api/v1/places", json={"name": name, "distance_km": km, "highway_cost": toll}
    )
    assert response.status_code == 201
    return response.json()


def _activity(client: TestClient, kind: str = "event", place_id: int | None = None) -> dict:
    response = client.post(
        "/api/v1/activities",
        json={
            "type": kind,
            "title": "Festa patronale",
            "starts_at": "2026-06-10T20:45",
            "place_id": place_id,
        },
    )
    assert response.status_code == 201
    return response.json()


def _record(client: TestClient, activity_id: int, rows: list[dict]):
    return client.put(f"/api/v1/activities/{activity_id}/attendances", json={"rows": rows})


def _by_person(rows: list[dict]) -> dict[int, dict]:
    return {row["person_id"]: row for row in rows}


def test_drivers_get_km_with_passenger_bonus_plus_toll(client: TestClient) -> None:
    driver_a, driver_b, *riders = _musicians(client, 5)
    place = _place(client)
    event = _activity(client, place_id=place["id"])
    assert event["place"] == {
        "id": place["id"],
        "name": "Teatro",
        "distance_km": 84,
        "highway_cost": "12.40",
        "archived": False,
    }

    response = _record(
        client,
        event["id"],
        [
            {
                "person_id": driver_a,
                "attendance": "present",
                "is_driver": True,
                "passenger_count": 2,
            },
            {"person_id": driver_b, "attendance": "present", "is_driver": True},
            *({"person_id": rider, "attendance": "present"} for rider in riders),
        ],
    )
    assert response.status_code == 200
    rows = _by_person(response.json())
    # 84 km × 0.25 = 21.00; +20% for 2 passengers = 25.20; + toll 12.40; + flat 5.00
    assert rows[driver_a]["refund_mileage_amount"] == "25.20"
    assert rows[driver_a]["refund_highway_amount"] == "12.40"
    assert rows[driver_a]["refund_bonus_pct"] == 20
    assert rows[driver_a]["refund_total"] == "42.60"
    assert rows[driver_b]["passenger_count"] == 0
    assert rows[driver_b]["refund_total"] == "38.40"
    assert rows[riders[0]]["refund_total"] == "5.00"

    detail = client.get(f"/api/v1/activities/{event['id']}").json()
    assert detail["reimbursement_flat"] == "25.00"
    assert detail["reimbursement_mileage"] == "46.20"
    assert detail["reimbursement_highway"] == "24.80"
    assert detail["reimbursement_total"] == "96.00"
    assert (detail["driver_count"], detail["passenger_count"]) == (2, 2)

    summary = _by_person(client.get("/api/v1/activities/refund-summary").json())
    assert summary[driver_a]["event"] == "5.00"
    assert summary[driver_a]["mileage"] == "25.20"
    assert summary[driver_a]["highway"] == "12.40"
    assert summary[driver_a]["distance_km"] == 84
    assert summary[driver_a]["total"] == "42.60"

    history = client.get(f"/api/v1/activities/participations?person_id={driver_a}").json()
    assert history[0]["is_driver"] is True
    assert history[0]["reimbursement_amount"] == "42.60"


def test_rule_and_place_changes_apply_only_to_later_recordings(client: TestClient) -> None:
    first, second = _musicians(client, 2)
    place = _place(client)
    event = _activity(client, place_id=place["id"])
    _record(client, event["id"], [{"person_id": first, "attendance": "present", "is_driver": True}])

    rules = client.get("/api/v1/settings/activity-refund-rules").json()
    updated = client.put(
        "/api/v1/settings/activity-refund-rules",
        json={**rules, "event": "6.00", "mileage": {**rules["mileage"], "rate_per_km": "0.50"}},
    )
    assert updated.status_code == 200
    client.patch(f"/api/v1/places/{place['id']}", json={"version": 1, "highway_cost": "20.00"})

    rows = _by_person(
        _record(
            client,
            event["id"],
            [
                {"person_id": first, "attendance": "present", "is_driver": True},
                {"person_id": second, "attendance": "present"},
            ],
        ).json()
    )
    assert rows[first]["refund_total"] == "38.40"
    assert rows[second]["refund_total"] == "6.00"


def test_marking_a_driver_absent_clears_driving_data(client: TestClient) -> None:
    (driver,) = _musicians(client, 1)
    event = _activity(client, place_id=_place(client)["id"])
    _record(
        client, event["id"], [{"person_id": driver, "attendance": "present", "is_driver": True}]
    )

    row = _record(client, event["id"], [{"person_id": driver, "attendance": "absent"}]).json()[0]
    assert row["is_driver"] is False
    assert row["passenger_count"] is None
    assert row["refund_total"] == "0.00"


@pytest.mark.parametrize(
    "row",
    [
        {"attendance": "absent", "is_driver": True},
        {"attendance": None, "is_driver": True},
        {"attendance": "present", "is_driver": False, "passenger_count": 1},
        {"attendance": "present", "is_driver": True, "passenger_count": -1},
    ],
)
def test_driver_data_is_validated(client: TestClient, row: dict) -> None:
    (person,) = _musicians(client, 1)
    event = _activity(client, place_id=_place(client)["id"])
    assert _record(client, event["id"], [{"person_id": person, **row}]).status_code == 422


def test_passengers_cannot_exceed_present_non_drivers(client: TestClient) -> None:
    driver, rider, _absent = _musicians(client, 3)
    event = _activity(client, place_id=_place(client)["id"])
    response = _record(
        client,
        event["id"],
        [
            {"person_id": driver, "attendance": "present", "is_driver": True, "passenger_count": 2},
            {"person_id": rider, "attendance": "present"},
        ],
    )
    assert response.status_code == 422
    assert response.json()["error"]["details"] == {"passengers": 2, "available": 1}


@pytest.mark.parametrize("kind, with_place", [("rehearsal", True), ("event", False)])
def test_no_mileage_for_disabled_types_or_without_place(
    client: TestClient, kind: str, with_place: bool
) -> None:
    (driver,) = _musicians(client, 1)
    place_id = _place(client)["id"] if with_place else None
    activity = _activity(client, kind=kind, place_id=place_id)
    row = _record(
        client, activity["id"], [{"person_id": driver, "attendance": "present", "is_driver": True}]
    ).json()[0]
    assert row["is_driver"] is True
    assert row["refund_mileage_amount"] == "0.00"
    assert row["refund_highway_amount"] == "0.00"
    assert row["refund_total"] == RULES[kind]


def test_changing_place_with_recorded_attendance_needs_confirmation(client: TestClient) -> None:
    (driver,) = _musicians(client, 1)
    near = _place(client, "Vicino", km=10, toll="0.00")
    far = _place(client, "Lontano", km=200, toll="30.00")
    event = _activity(client, place_id=near["id"])
    _record(
        client, event["id"], [{"person_id": driver, "attendance": "present", "is_driver": True}]
    )

    refused = client.patch(
        f"/api/v1/activities/{event['id']}", json={"version": 1, "place_id": far["id"]}
    )
    assert refused.status_code == 409
    assert refused.json()["error"]["code"] == "ACTIVITY_REFUNDS_RECALCULATION_REQUIRED"

    # Title changes do not touch reimbursements and need no confirmation.
    renamed = client.patch(f"/api/v1/activities/{event['id']}", json={"version": 1, "title": "X"})
    assert renamed.status_code == 200

    moved = client.patch(
        f"/api/v1/activities/{event['id']}",
        json={"version": 2, "place_id": far["id"], "recalculate_refunds": True},
    )
    assert moved.status_code == 200
    # 200 km × 0.25 = 50.00 + toll 30.00 + flat 5.00
    assert moved.json()["reimbursement_total"] == "85.00"


def test_activities_only_accept_active_places(client: TestClient) -> None:
    place = _place(client)
    client.delete(f"/api/v1/places/{place['id']}", params={"version": 1})
    response = client.post(
        "/api/v1/activities",
        json={
            "type": "event",
            "title": "Sfilata",
            "starts_at": "2026-06-10T20:45",
            "place_id": place["id"],
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_ACTIVITY_PLACE"


def test_refund_rules_update_keeps_mileage_when_omitted(client: TestClient) -> None:
    rules = client.get("/api/v1/settings/activity-refund-rules").json()
    assert rules["mileage"] == RULES["mileage"]
    flat_only = {key: rules[key] for key in ("rehearsal", "concert", "event", "version")}
    saved = client.put("/api/v1/settings/activity-refund-rules", json=flat_only)
    assert saved.status_code == 200
    assert saved.json()["mileage"] == RULES["mileage"]

    invalid = client.put(
        "/api/v1/settings/activity-refund-rules",
        json={**saved.json(), "mileage": {**RULES["mileage"], "passenger_bonus_pct": 7.5}},
    )
    assert invalid.status_code == 422
