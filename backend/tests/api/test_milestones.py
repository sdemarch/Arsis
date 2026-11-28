"""RB-19: milestones on attendance and reimbursements, reset per person keeping the excess."""

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
    "concert": "10.00",
    "event": "5.00",
    "mileage": {
        "enabled_types": ["event"],
        "rate_per_km": "0.00",
        "passenger_bonus_pct": 0,
        "max_bonus_passengers": 4,
    },
}


@pytest.fixture
def app(tmp_path) -> Iterator[FastAPI]:
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'milestones.db').as_posix()}",
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


def _person(client: TestClient, first_name: str) -> int:
    response = client.post("/api/v1/people", json={"first_name": first_name, "last_name": "Banda"})
    assert response.status_code == 201
    return int(response.json()["id"])


def _attend(client: TestClient, kind: str, present: list[int], times: int = 1) -> None:
    for index in range(times):
        activity = client.post(
            "/api/v1/activities",
            json={
                "type": kind,
                "title": f"{kind} {index}",
                "starts_at": f"2026-03-{index + 1:02d}T20:45",
            },
        ).json()
        response = client.put(
            f"/api/v1/activities/{activity['id']}/attendances",
            json={"rows": [{"person_id": pid, "attendance": "present"} for pid in present]},
        )
        assert response.status_code == 200


def _milestone(client: TestClient, name: str, metric: str, threshold: str) -> dict:
    response = client.post(
        "/api/v1/milestones", json={"name": name, "metric": metric, "threshold": threshold}
    )
    assert response.status_code == 201, response.text
    return response.json()


def _entry(client: TestClient, milestone_id: int) -> dict:
    board = client.get("/api/v1/milestones/board")
    assert board.status_code == 200
    return next(e for e in board.json() if e["milestone"]["id"] == milestone_id)


def test_new_milestone_counts_history_and_reset_keeps_excess(client: TestClient) -> None:
    anna, bruno = _person(client, "Anna"), _person(client, "Bruno")
    _attend(client, "rehearsal", [anna, bruno], times=3)
    _attend(client, "rehearsal", [anna], times=2)
    milestone = _milestone(client, "Due prove", "rehearsal_count", "2")

    entry = _entry(client, milestone["id"])
    reached = {row["person_id"]: row for row in entry["reached"]}
    assert reached[anna]["progress"] == "5.00"
    assert reached[anna]["times_reached"] == 2
    assert reached[bruno]["times_reached"] == 1
    assert entry["in_progress"] == []

    reset = client.post(
        f"/api/v1/milestones/{milestone['id']}/resets", json={"person_ids": [anna, bruno]}
    )
    assert reset.status_code == 200
    reached = {row["person_id"]: row for row in reset.json()["reached"]}
    in_progress = {row["person_id"]: row for row in reset.json()["in_progress"]}
    assert reached[anna]["progress"] == "3.00"  # 5 − 2: still reached once
    assert in_progress[bruno]["progress"] == "1.00"  # 3 − 2: excess kept
    assert in_progress[bruno]["remaining"] == "1.00"

    refused = client.post(
        f"/api/v1/milestones/{milestone['id']}/resets", json={"person_ids": [bruno]}
    )
    assert refused.status_code == 409
    assert refused.json()["error"]["code"] == "MILESTONE_NOT_REACHED"

    undone = client.delete(
        f"/api/v1/milestones/{milestone['id']}/resets/{in_progress[bruno]['last_reset_id']}"
    )
    assert undone.status_code == 200
    assert {row["person_id"] for row in undone.json()["reached"]} == {anna, bruno}


def test_reimbursement_and_type_metrics(client: TestClient) -> None:
    anna = _person(client, "Anna")
    _attend(client, "concert", [anna], times=2)  # 2 × 10 €
    _attend(client, "rehearsal", [anna], times=3)  # 3 × 2 €
    money = _milestone(client, "Cassa", "reimbursement_total", "25.50")
    concerts = _milestone(client, "Concerti", "concert_count", "3")
    total = _milestone(client, "Presenze", "attendance_count", "5")

    assert _entry(client, money["id"])["reached"][0]["progress"] == "26.00"
    assert _entry(client, concerts["id"])["in_progress"][0]["remaining"] == "1.00"
    assert _entry(client, total["id"])["reached"][0]["times_reached"] == 1


def test_milestone_configuration_rules(client: TestClient) -> None:
    fractional = client.post(
        "/api/v1/milestones",
        json={"name": "Prove", "metric": "rehearsal_count", "threshold": "2.5"},
    )
    assert fractional.status_code == 422

    created = _milestone(client, "Prove", "rehearsal_count", "10")
    duplicate = client.post(
        "/api/v1/milestones",
        json={"name": " prove ", "metric": "concert_count", "threshold": "1"},
    )
    assert duplicate.status_code == 409

    updated = client.patch(
        f"/api/v1/milestones/{created['id']}",
        json={
            "version": created["version"],
            "metric": "reimbursement_total",
            "threshold": "150.00",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["threshold"] == "150.00"

    archived = client.delete(
        f"/api/v1/milestones/{created['id']}", params={"version": updated.json()["version"]}
    )
    assert archived.status_code == 200
    assert client.get("/api/v1/milestones/board").json() == []
    listed = client.get("/api/v1/milestones", params={"include_archived": True}).json()
    assert listed["items"][0]["archived_at"] is not None
