"""RB-22: recurring activities, created as a series of ordinary activities."""

import json
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from arsis.auth.service import bootstrap_first_responsible
from arsis.core.database import get_database_session
from arsis.generated.models import AppSetting, Base
from arsis.main import create_app

RULE = {"frequency": "weekly", "interval": 1, "weekdays": [2, 5], "ends_on": "2026-12-18"}


@pytest.fixture
def client(tmp_path) -> Iterator[TestClient]:
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'series.db').as_posix()}",
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
        # Recording attendance reads the refund rules (seeded by migrations in production).
        session.add(
            AppSetting(
                key="activities.refund_rules",
                value=json.dumps(
                    {
                        "rehearsal": "2.00",
                        "concert": "0.00",
                        "event": "0.00",
                        "mileage": {
                            "enabled_types": [],
                            "rate_per_km": "0.00",
                            "passenger_bonus_pct": 0,
                            "max_bonus_passengers": 4,
                        },
                    }
                ),
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
    with TestClient(application) as test_client:
        login = test_client.post(
            "/api/v1/auth/login",
            json={"email": "responsabile@example.it", "password": "correct horse battery staple"},
        )
        test_client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
        yield test_client
    engine.dispose()


def _preview(client: TestClient, starts_on: str = "2026-12-01", rule: dict | None = None):
    return client.post(
        "/api/v1/activities/series/preview",
        json={"starts_on": starts_on, "recurrence": rule or RULE},
    )


def _create(client: TestClient, dates: list[str], **extra: object):
    # The browser sends local midnight with its own offset, as the create form does.
    return client.post(
        "/api/v1/activities/series",
        json={
            "type": "rehearsal",
            "title": "Prova settimanale",
            "starts_on": "2026-12-01",
            "recurrence": RULE,
            "occurrences": [f"{day}T00:00:00+01:00" for day in dates],
            **extra,
        },
    )


def test_preview_and_create_series(client: TestClient) -> None:
    preview = _preview(client)
    assert preview.status_code == 200
    dates = preview.json()["dates"]
    assert dates == [
        "2026-12-01",
        "2026-12-04",
        "2026-12-08",
        "2026-12-11",
        "2026-12-15",
        "2026-12-18",
    ]
    assert preview.json()["description"] == "Ogni settimana: martedì, venerdì"

    created = _create(client, dates)
    assert created.status_code == 201, created.text
    activities = created.json()
    assert [a["starts_at"][:10] for a in activities] == dates
    assert {a["series_id"] for a in activities} == {activities[0]["series_id"]}
    third = client.get(f"/api/v1/activities/{activities[2]['id']}").json()
    assert third["series"]["position"] == 3
    assert third["series"]["occurrence_count"] == 6
    assert third["series"]["description"] == "Ogni settimana: martedì, venerdì"

    series = client.get(f"/api/v1/activities/series/{third['series_id']}").json()
    assert [o["id"] for o in series["occurrences"]] == [a["id"] for a in activities]

    plain = client.post(
        "/api/v1/activities",
        json={"type": "concert", "title": "Concerto", "starts_at": "2026-12-20T00:00:00+01:00"},
    ).json()
    assert plain["series_id"] is None and plain["series"] is None


def test_dates_must_match_the_rule(client: TestClient) -> None:
    dates = _preview(client).json()["dates"]
    tampered = _create(client, [*dates[:-1], "2026-12-19"])
    assert tampered.status_code == 422
    assert "anteprima" in tampered.json()["error"]["message"]
    no_offset = client.post(
        "/api/v1/activities/series",
        json={
            "type": "rehearsal",
            "title": "Prova",
            "starts_on": "2026-12-01",
            "recurrence": RULE,
            "occurrences": [f"{day}T00:00:00" for day in dates],
        },
    )
    assert no_offset.status_code == 422
    too_long = _preview(client, rule={**RULE, "ends_on": "2028-01-01"})
    assert too_long.status_code == 422
    assert "un anno" in too_long.json()["error"]["message"]


def test_update_following_and_end_series(client: TestClient) -> None:
    activities = _create(client, _preview(client).json()["dates"]).json()
    ids = [a["id"] for a in activities]

    changed = client.patch(
        f"/api/v1/activities/{ids[2]}/following",
        json={"title": "Prova d'insieme", "location": "Sala nuova"},
    )
    assert changed.status_code == 200
    assert changed.json()["updated"] == 4
    titles = [client.get(f"/api/v1/activities/{i}").json()["title"] for i in ids]
    assert titles == ["Prova settimanale"] * 2 + ["Prova d'insieme"] * 4

    person = client.post("/api/v1/people", json={"first_name": "Anna", "last_name": "Banda"}).json()
    recorded = client.put(
        f"/api/v1/activities/{ids[4]}/attendances",
        json={"rows": [{"person_id": person["id"], "attendance": "present"}]},
    )
    assert recorded.status_code == 200, recorded.text

    ended = client.post(f"/api/v1/activities/{ids[1]}/end-series")
    assert ended.status_code == 200
    assert ended.json() == {"updated": 0, "archived": 3, "kept": 1}
    series = client.get(f"/api/v1/activities/series/{activities[0]['series_id']}").json()
    assert [o["id"] for o in series["occurrences"]] == [ids[0], ids[1], ids[4]]
    assert series["series"]["ends_on"] == "2026-12-15"  # the last occurrence kept

    alone = client.post(
        "/api/v1/activities",
        json={"type": "concert", "title": "Concerto", "starts_at": "2026-12-20T00:00:00+01:00"},
    ).json()
    not_series = client.post(f"/api/v1/activities/{alone['id']}/end-series")
    assert not_series.status_code == 409
    assert not_series.json()["error"]["code"] == "ACTIVITY_NOT_IN_SERIES"
