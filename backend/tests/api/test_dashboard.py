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
def dashboard_app(tmp_path) -> Iterator[FastAPI]:
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'dashboard.db').as_posix()}",
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
                value='{"rehearsal":"0.00","concert":"0.00","event":"0.00"}',
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


def _person(client: TestClient, headers: dict[str, str], name: str, role: str | None) -> int:
    first_name, last_name = name.split()
    person = client.post(
        "/api/v1/people", headers=headers, json={"first_name": first_name, "last_name": last_name}
    ).json()
    if role:
        client.post(
            f"/api/v1/people/{person['id']}/roles",
            headers=headers,
            json={"role_type": role, "start_date": "2026-01-01"},
        )
    return int(person["id"])


def _post(client: TestClient, headers: dict[str, str], url: str, **values: object) -> dict:
    response = client.post(url, headers=headers, json=values)
    assert response.status_code == 201, response.json()
    return response.json()


def test_dashboard_requires_authentication(dashboard_app: FastAPI) -> None:
    with TestClient(dashboard_app) as client:
        assert client.get("/api/v1/dashboard/summary").status_code == 401


def test_dashboard_summary_reflects_people_school_and_agenda(dashboard_app: FastAPI) -> None:
    with TestClient(dashboard_app) as client:
        headers = _headers(client)
        teacher = _person(client, headers, "Elena Verdi", "teacher")
        student = _person(client, headers, "Luca Bianchi", "student")
        future_student = _person(client, headers, "Sara Neri", "student")
        _person(client, headers, "Marco Rossi", "musician")
        _person(client, headers, "Paola Galli", "member")
        _person(client, headers, "Ugo Senza", None)

        course = _post(
            client,
            headers,
            "/api/v1/courses",
            name="Clarinetto",
            mode="individual",
            category="ensemble",
            teacher_person_id=teacher,
            annual_fee="300.00",
            color="#378ADD",
        )
        for person, starts_on in ((student, "2026-09-15"), (future_student, "2026-12-01")):
            _post(
                client,
                headers,
                "/api/v1/enrollments",
                course_id=course["id"],
                student_person_id=person,
                enrolled_on="2026-09-01",
                starts_on=starts_on,
            )
        lessons = [
            _post(
                client,
                headers,
                "/api/v1/lessons",
                course_id=course["id"],
                teacher_person_id=teacher,
                starts_at=starts_at,
            )
            for starts_at in ("2026-11-09T15:30", "2026-11-02T15:30", "2026-10-20T15:30")
        ]
        for lesson, attendance in ((lessons[0], "absent"), (lessons[1], "present")):
            saved = client.put(
                f"/api/v1/lessons/{lesson['id']}/attendances",
                headers=headers,
                json={"rows": [{"student_person_id": student, "attendance": attendance}]},
            )
            assert saved.status_code == 200

        upcoming = _post(
            client,
            headers,
            "/api/v1/activities",
            type="concert",
            title="Concerto d'autunno",
            starts_at="2026-11-10T21:00:00+01:00",
            location="Teatro",
        )
        _post(
            client,
            headers,
            "/api/v1/activities",
            type="rehearsal",
            title="Prova",
            starts_at="2026-11-01T20:45:00+01:00",
        )
        _post(
            client,
            headers,
            "/api/v1/activities",
            type="event",
            title="Festa",
            starts_at="2026-11-12T18:00:00+01:00",
            status="cancelled",
        )

        response = client.get("/api/v1/dashboard/summary?on=2026-11-09", headers=headers)
        assert response.status_code == 200
        body = response.json()

        assert body["date"] == "2026-11-09"
        assert body["people"] == {
            "active": 6,
            "members": 1,
            "musicians": 1,
            "students": 2,
            "teachers": 1,
            "sections": 0,
        }
        assert body["school"] == {
            "active_courses": 1,
            "active_enrollments": 1,
            "enrolled_students": 1,
            "lessons_this_month": 2,
            "attendance_rate": 0.5,
        }
        assert body["upcoming_activities"] == [
            {
                "id": upcoming["id"],
                "title": "Concerto d'autunno",
                "type": "concert",
                "status": "planned",
                "starts_at": "2026-11-10T21:00:00+01:00",
                "location": "Teatro",
                "participant_count": 1,
            }
        ]
        assert body["today_lessons"] == [
            {
                "id": lessons[0]["id"],
                "course_id": course["id"],
                "course_name": "Clarinetto",
                "course_color": "#378ADD",
                "teacher_name": "Elena Verdi",
                "starts_at": "2026-11-09T15:30",
                "ends_at": None,
                "status": "planned",
                "students": 1,
                "recorded": 1,
            }
        ]
        assert body["course_students"] == [{"course_id": course["id"], "students": 1}]


def test_dashboard_without_data_has_no_attendance_rate(dashboard_app: FastAPI) -> None:
    with TestClient(dashboard_app) as client:
        body = client.get("/api/v1/dashboard/summary", headers=_headers(client)).json()
        assert body["school"]["attendance_rate"] is None
        assert body["upcoming_activities"] == []
        assert body["today_lessons"] == []
