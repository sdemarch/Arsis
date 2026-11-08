from collections.abc import Iterator
from io import BytesIO

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from openpyxl import Workbook
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from arsis.auth.service import bootstrap_first_responsible
from arsis.core.database import get_database_session
from arsis.generated.models import AppSetting, Base
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
        session.add_all(
            [
                AppSetting(key="organization.name", value='"Filarmonica di test"'),
                AppSetting(key="archive.google_drive_url", value='""'),
                AppSetting(key="ui.default_theme", value='"light"'),
            ]
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
        json={
            "email": "responsabile@example.it",
            "password": "correct horse battery staple",
        },
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_general_settings_are_persisted(people_app: FastAPI) -> None:
    with TestClient(people_app) as client:
        headers = _headers(client)
        initial = client.get("/api/v1/settings/general", headers=headers)
        assert initial.status_code == 200
        assert initial.json()["organization_name"] == "Filarmonica di test"

        saved = client.put(
            "/api/v1/settings/general",
            headers=headers,
            json={
                **initial.json(),
                "organization_name": "Nuova filarmonica",
                "archive_google_drive_url": "https://drive.google.com/drive/folders/test",
                "default_theme": "dark",
            },
        )
        assert saved.status_code == 200
        assert saved.json()["organization_name"] == "Nuova filarmonica"
        assert saved.json()["organization_name_version"] == 2
        assert saved.json()["default_theme"] == "dark"

        persisted = client.get("/api/v1/settings/general", headers=headers)
        assert persisted.json() == saved.json()

        stale = client.put(
            "/api/v1/settings/general",
            headers=headers,
            json={**initial.json(), "organization_name": "Versione obsoleta"},
        )
        assert stale.status_code == 409
        assert stale.json()["error"]["code"] == "STALE_VERSION"


def test_responsible_users_are_managed_from_settings(people_app: FastAPI) -> None:
    with TestClient(people_app) as client:
        headers = _headers(client)
        created = client.post(
            "/api/v1/settings/responsible-users",
            headers=headers,
            json={
                "email": "secondo@example.it",
                "display_name": "Secondo responsabile",
                "password": "another secure password",
            },
        )
        assert created.status_code == 201
        second_user = created.json()
        assert second_user["is_active"] is True

        listing = client.get("/api/v1/settings/responsible-users", headers=headers)
        assert listing.status_code == 200
        assert [user["email"] for user in listing.json()] == [
            "responsabile@example.it",
            "secondo@example.it",
        ]
        current_user = listing.json()[0]

        deactivated = client.patch(
            f"/api/v1/settings/responsible-users/{second_user['id']}",
            headers=headers,
            json={"is_active": False, "version": second_user["version"]},
        )
        assert deactivated.status_code == 200
        assert deactivated.json()["is_active"] is False

        self_deactivation = client.patch(
            "/api/v1/settings/responsible-users/1",
            headers=headers,
            json={"is_active": False, "version": current_user["version"]},
        )
        assert self_deactivation.status_code == 409
        assert self_deactivation.json()["error"]["code"] == "CANNOT_DEACTIVATE_SELF"


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


def test_courses_crud_search_and_archiving(people_app: FastAPI) -> None:
    with TestClient(people_app) as client:
        headers = _headers(client)
        teacher = client.post(
            "/api/v1/people",
            headers=headers,
            json={"first_name": "Luca", "last_name": "Bianchi"},
        ).json()
        client.post(
            f"/api/v1/people/{teacher['id']}/roles",
            headers=headers,
            json={"role_type": "teacher", "start_date": "2026-01-01"},
        )

        created = client.post(
            "/api/v1/courses",
            headers=headers,
            json={
                "name": "Clarinetto base",
                "mode": "individual",
                "category": "instrument",
                "instrument_id": 1,
                "teacher_person_id": teacher["id"],
                "annual_fee": "450",
                "color": "#0055AA",
            },
        )
        assert created.status_code == 201
        course = created.json()
        assert course["status"] == "active"
        assert course["annual_fee"] == "450.00"

        listing = client.get("/api/v1/courses?q=clarinetto", headers=headers)
        assert listing.status_code == 200
        assert listing.json()["meta"]["total_items"] == 1
        assert listing.json()["items"][0]["annual_fee"] == "450.00"

        updated = client.patch(
            f"/api/v1/courses/{course['id']}",
            headers=headers,
            json={"version": 1, "annual_fee": "475.00"},
        )
        assert updated.status_code == 200
        assert updated.json()["annual_fee"] == "475.00"
        assert updated.json()["version"] == 2

        archived = client.delete(f"/api/v1/courses/{course['id']}?version=2", headers=headers)
        assert archived.status_code == 200
        assert archived.json()["archived_at"] is not None
        assert client.get("/api/v1/courses", headers=headers).json()["items"] == []


def test_enrollments_crud_and_active_student_rule(people_app: FastAPI) -> None:
    with TestClient(people_app) as client:
        headers = _headers(client)
        teacher = client.post(
            "/api/v1/people",
            headers=headers,
            json={"first_name": "Elena", "last_name": "Verdi"},
        ).json()
        client.post(
            f"/api/v1/people/{teacher['id']}/roles",
            headers=headers,
            json={"role_type": "teacher", "start_date": "2026-01-01"},
        )
        course = client.post(
            "/api/v1/courses",
            headers=headers,
            json={
                "name": "Musica d'insieme",
                "mode": "group",
                "category": "ensemble",
                "teacher_person_id": teacher["id"],
                "annual_fee": "180.00",
                "color": "#0055AA",
            },
        ).json()
        student = client.post(
            "/api/v1/people",
            headers=headers,
            json={"first_name": "Anna", "last_name": "Neri"},
        ).json()
        client.post(
            f"/api/v1/people/{student['id']}/roles",
            headers=headers,
            json={"role_type": "student", "start_date": "2026-01-01"},
        )

        created = client.post(
            "/api/v1/enrollments",
            headers=headers,
            json={
                "course_id": course["id"],
                "student_person_id": student["id"],
                "enrolled_on": "2026-09-01",
                "starts_on": "2026-09-15",
            },
        )
        assert created.status_code == 201
        enrollment = created.json()
        assert enrollment["status"] == "active"

        duplicate = client.post(
            "/api/v1/enrollments",
            headers=headers,
            json={
                "course_id": course["id"],
                "student_person_id": student["id"],
                "enrolled_on": "2026-09-01",
                "starts_on": "2026-09-15",
            },
        )
        assert duplicate.status_code == 409
        assert duplicate.json()["error"]["code"] == "ACTIVE_ENROLLMENT_EXISTS"

        listing = client.get("/api/v1/enrollments?q=neri", headers=headers)
        assert listing.status_code == 200
        assert listing.json()["meta"]["total_items"] == 1

        updated = client.patch(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=headers,
            json={"version": 1, "notes": "Quota ricevuta"},
        )
        assert updated.status_code == 200
        assert updated.json()["version"] == 2

        archived = client.delete(
            f"/api/v1/enrollments/{enrollment['id']}?version=2", headers=headers
        )
        assert archived.status_code == 200
        assert archived.json()["archived_at"] is not None


def test_lessons_crud_search_and_active_relations(people_app: FastAPI) -> None:
    with TestClient(people_app) as client:
        headers = _headers(client)
        teacher = client.post(
            "/api/v1/people",
            headers=headers,
            json={"first_name": "Marta", "last_name": "Blu"},
        ).json()
        client.post(
            f"/api/v1/people/{teacher['id']}/roles",
            headers=headers,
            json={"role_type": "teacher", "start_date": "2026-01-01"},
        )
        course = client.post(
            "/api/v1/courses",
            headers=headers,
            json={
                "name": "Percussioni base",
                "mode": "group",
                "category": "ensemble",
                "teacher_person_id": teacher["id"],
                "annual_fee": "200.00",
                "color": "#0055AA",
            },
        ).json()

        created = client.post(
            "/api/v1/lessons",
            headers=headers,
            json={
                "course_id": course["id"],
                "teacher_person_id": teacher["id"],
                "starts_at": "2026-10-20T15:30:00Z",
                "ends_at": "2026-10-20T16:30:00Z",
                "topic": "Ritmo e coordinazione",
            },
        )
        assert created.status_code == 201
        lesson = created.json()
        assert lesson["status"] == "planned"

        listing = client.get("/api/v1/lessons?q=ritmo", headers=headers)
        assert listing.status_code == 200
        assert listing.json()["meta"]["total_items"] == 1

        invalid_schedule = client.post(
            "/api/v1/lessons",
            headers=headers,
            json={
                "course_id": course["id"],
                "teacher_person_id": teacher["id"],
                "starts_at": "2026-10-20T16:30:00Z",
                "ends_at": "2026-10-20T15:30:00Z",
            },
        )
        assert invalid_schedule.status_code == 409
        assert invalid_schedule.json()["error"]["code"] == "INVALID_LESSON_SCHEDULE"

        updated = client.patch(
            f"/api/v1/lessons/{lesson['id']}",
            headers=headers,
            json={"version": 1, "status": "completed"},
        )
        assert updated.status_code == 200
        assert updated.json()["version"] == 2

        archived = client.delete(f"/api/v1/lessons/{lesson['id']}?version=2", headers=headers)
        assert archived.status_code == 200
        assert archived.json()["archived_at"] is not None


def test_lesson_attendance_register_and_excel_import(people_app: FastAPI) -> None:
    with TestClient(people_app) as client:
        headers = _headers(client)
        teacher = client.post(
            "/api/v1/people",
            headers=headers,
            json={"first_name": "Paolo", "last_name": "Viola"},
        ).json()
        client.post(
            f"/api/v1/people/{teacher['id']}/roles",
            headers=headers,
            json={"role_type": "teacher", "start_date": "2026-01-01"},
        )
        student = client.post(
            "/api/v1/people",
            headers=headers,
            json={"first_name": "Sara", "last_name": "Gialli"},
        ).json()
        client.post(
            f"/api/v1/people/{student['id']}/roles",
            headers=headers,
            json={"role_type": "student", "start_date": "2026-01-01"},
        )
        course = client.post(
            "/api/v1/courses",
            headers=headers,
            json={
                "name": "Teoria musicale",
                "mode": "group",
                "category": "ensemble",
                "teacher_person_id": teacher["id"],
                "annual_fee": "150.00",
                "color": "#0055AA",
            },
        ).json()
        client.post(
            "/api/v1/enrollments",
            headers=headers,
            json={
                "course_id": course["id"],
                "student_person_id": student["id"],
                "enrolled_on": "2026-09-01",
                "starts_on": "2026-09-01",
            },
        )
        lesson = client.post(
            "/api/v1/lessons",
            headers=headers,
            json={
                "course_id": course["id"],
                "teacher_person_id": teacher["id"],
                "starts_at": "2026-10-20T15:30:00Z",
            },
        ).json()

        roster = client.get(f"/api/v1/lessons/{lesson['id']}/attendances", headers=headers)
        assert roster.status_code == 200
        assert roster.json()[0]["attendance"] is None
        assert roster.json()[0]["student_person_id"] == student["id"]

        saved = client.put(
            f"/api/v1/lessons/{lesson['id']}/attendances",
            headers=headers,
            json={"rows": [{"student_person_id": student["id"], "attendance": "present"}]},
        )
        assert saved.status_code == 200
        assert saved.json()["processed_rows"] == 1

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.append(["student_person_id", "student_name", "attendance"])
        worksheet.append([student["id"], "Sara Gialli", "assente"])
        content = BytesIO()
        workbook.save(content)
        imported = client.post(
            f"/api/v1/lessons/{lesson['id']}/attendances/import",
            headers=headers,
            files={
                "file": (
                    "presenze.xlsx",
                    content.getvalue(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )
        assert imported.status_code == 200
        assert imported.json()["processed_rows"] == 1
        assert (
            client.get(f"/api/v1/lessons/{lesson['id']}/attendances", headers=headers).json()[0][
                "attendance"
            ]
            == "absent"
        )

        invalid_workbook = Workbook()
        invalid_worksheet = invalid_workbook.active
        invalid_worksheet.append(["student_person_id", "attendance"])
        invalid_worksheet.append([999, "present"])
        invalid_content = BytesIO()
        invalid_workbook.save(invalid_content)
        invalid_import = client.post(
            f"/api/v1/lessons/{lesson['id']}/attendances/import",
            headers=headers,
            files={
                "file": (
                    "presenze-non-valide.xlsx",
                    invalid_content.getvalue(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )
        assert invalid_import.status_code == 422
        assert invalid_import.json()["error"]["code"] == "IMPORT_VALIDATION_ERROR"
        assert (
            client.get(f"/api/v1/lessons/{lesson['id']}/attendances", headers=headers).json()[0][
                "attendance"
            ]
            == "absent"
        )

        template = client.get(
            f"/api/v1/lessons/{lesson['id']}/attendances/template", headers=headers
        )
        assert template.status_code == 200
        assert template.headers["content-type"].startswith(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


def test_catalogues_manage_sections_and_instruments(people_app: FastAPI) -> None:
    with TestClient(people_app) as client:
        headers = _headers(client)
        section = client.post(
            "/api/v1/sections", headers=headers, json={"name": "Archi", "display_order": 10}
        )
        assert section.status_code == 201
        section_data = section.json()
        instrument = client.post(
            "/api/v1/instruments",
            headers=headers,
            json={"name": "Violino", "section_id": section_data["id"], "display_order": 10},
        )
        assert instrument.status_code == 201
        instrument_data = instrument.json()
        assert client.get("/api/v1/instruments", headers=headers).json()["meta"]["total_items"] == 1

        blocked = client.delete(
            f"/api/v1/sections/{section_data['id']}?version={section_data['version']}",
            headers=headers,
        )
        assert blocked.status_code == 409
        assert blocked.json()["error"]["code"] == "SECTION_HAS_ACTIVE_INSTRUMENTS"

        archived = client.delete(
            f"/api/v1/instruments/{instrument_data['id']}?version={instrument_data['version']}",
            headers=headers,
        )
        assert archived.status_code == 200
        section_archived = client.delete(
            f"/api/v1/sections/{section_data['id']}?version={section_data['version']}",
            headers=headers,
        )
        assert section_archived.status_code == 200
