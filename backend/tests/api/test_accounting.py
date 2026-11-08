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
def accounting_app(tmp_path) -> Iterator[FastAPI]:
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'accounting.db').as_posix()}",
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


def _person_with_role(client: TestClient, headers: dict[str, str], name: str, role: str) -> int:
    first_name, last_name = name.split()
    person = client.post(
        "/api/v1/people",
        headers=headers,
        json={"first_name": first_name, "last_name": last_name},
    ).json()
    client.post(
        f"/api/v1/people/{person['id']}/roles",
        headers=headers,
        json={"role_type": role, "start_date": "2026-01-01"},
    )
    return int(person["id"])


def _category(client: TestClient, headers: dict[str, str], **values: object) -> dict:
    response = client.post("/api/v1/accounting/categories", headers=headers, json=values)
    assert response.status_code == 201
    return response.json()


def _movement(client: TestClient, headers: dict[str, str], **values: object):
    return client.post(
        "/api/v1/accounting/movements",
        headers=headers,
        json={
            "occurred_on": "2026-03-10",
            "account": "bank",
            "subject": "Soggetto",
            "description": "Movimento",
            **values,
        },
    )


def test_accounting_requires_authentication(accounting_app: FastAPI) -> None:
    with TestClient(accounting_app) as client:
        assert client.get("/api/v1/accounting/categories").status_code == 401
        assert client.get("/api/v1/accounting/summary/2026").status_code == 401


def test_categories_crud_and_archiving(accounting_app: FastAPI) -> None:
    with TestClient(accounting_app) as client:
        headers = _headers(client)
        category = _category(client, headers, name="Donazioni", direction="income", color="#1D9E75")
        assert category["is_active"] is True
        assert category["version"] == 1

        duplicate = client.post(
            "/api/v1/accounting/categories",
            headers=headers,
            json={"name": "Donazioni", "direction": "income"},
        )
        assert duplicate.status_code == 409
        assert duplicate.json()["error"]["code"] == "ACCOUNTING_CATEGORY_EXISTS"

        updated = client.patch(
            f"/api/v1/accounting/categories/{category['id']}",
            headers=headers,
            json={"version": 1, "name": "Contributi", "direction": "both"},
        )
        assert updated.status_code == 200
        assert updated.json()["name"] == "Contributi"
        assert updated.json()["version"] == 2

        stale = client.patch(
            f"/api/v1/accounting/categories/{category['id']}",
            headers=headers,
            json={"version": 1, "name": "Obsoleta"},
        )
        assert stale.status_code == 409

        archived = client.delete(
            f"/api/v1/accounting/categories/{category['id']}?version=2", headers=headers
        )
        assert archived.status_code == 200
        assert archived.json()["archived_at"] is not None
        assert client.get("/api/v1/accounting/categories", headers=headers).json() == []
        assert (
            len(
                client.get(
                    "/api/v1/accounting/categories?include_archived=true", headers=headers
                ).json()
            )
            == 1
        )


def test_movements_crud_filters_and_validation(accounting_app: FastAPI) -> None:
    with TestClient(accounting_app) as client:
        headers = _headers(client)
        income = _category(client, headers, name="Donazioni", direction="income")
        expense = _category(client, headers, name="Materiali", direction="expense")
        member_fee = _category(
            client, headers, name="Quota", direction="income", required_person_role="member"
        )

        created = _movement(
            client,
            headers,
            direction="income",
            category_id=income["id"],
            amount="150.00",
            subject="Comune",
        )
        assert created.status_code == 201
        movement = created.json()
        assert movement["amount"] == "150.00"
        assert (
            _movement(
                client,
                headers,
                occurred_on="2026-05-02",
                direction="expense",
                account="cash",
                category_id=expense["id"],
                amount="20.50",
                description="Ance",
            ).status_code
            == 201
        )

        wrong_direction = _movement(
            client, headers, direction="expense", category_id=income["id"], amount="1.00"
        )
        assert wrong_direction.status_code == 409
        assert wrong_direction.json()["error"]["code"] == "INVALID_ACCOUNTING_DIRECTION"

        missing_person = _movement(
            client, headers, direction="income", category_id=member_fee["id"], amount="30.00"
        )
        assert missing_person.json()["error"]["code"] == "INVALID_ACCOUNTING_PERSON"
        member_id = _person_with_role(client, headers, "Anna Neri", "member")
        with_person = _movement(
            client,
            headers,
            direction="income",
            category_id=member_fee["id"],
            amount="30.00",
            person_id=member_id,
        )
        assert with_person.status_code == 201

        listing = client.get("/api/v1/accounting/movements?fiscal_year=2026", headers=headers)
        assert listing.json()["meta"]["total_items"] == 3
        assert {item["amount"] for item in listing.json()["items"]} == {"150.00", "20.50", "30.00"}
        march = client.get(
            "/api/v1/accounting/movements?fiscal_year=2026&month=3", headers=headers
        ).json()
        assert {item["direction"] for item in march["items"]} == {"income"}
        cash = client.get("/api/v1/accounting/movements?account=cash", headers=headers).json()
        assert [item["description"] for item in cash["items"]] == ["Ance"]
        search = client.get("/api/v1/accounting/movements?q=comune", headers=headers).json()
        assert [item["id"] for item in search["items"]] == [movement["id"]]
        assert (
            client.get("/api/v1/accounting/movements?month=13", headers=headers).status_code == 422
        )

        updated = client.patch(
            f"/api/v1/accounting/movements/{movement['id']}",
            headers=headers,
            json={"version": 1, "amount": "175.00", "account": "cash"},
        )
        assert updated.status_code == 200
        assert updated.json()["amount"] == "175.00"
        assert updated.json()["version"] == 2

        deleted = client.delete(f"/api/v1/accounting/movements/{movement['id']}", headers=headers)
        assert deleted.status_code == 204
        missing = client.delete(f"/api/v1/accounting/movements/{movement['id']}", headers=headers)
        assert missing.status_code == 404


def test_course_categories_check_enrollment_and_teacher(accounting_app: FastAPI) -> None:
    with TestClient(accounting_app) as client:
        headers = _headers(client)
        teacher_id = _person_with_role(client, headers, "Elena Verdi", "teacher")
        student_id = _person_with_role(client, headers, "Luca Bianchi", "student")
        course = client.post(
            "/api/v1/courses",
            headers=headers,
            json={
                "name": "Clarinetto",
                "mode": "individual",
                "category": "instrument",
                "teacher_person_id": teacher_id,
                "annual_fee": "300.00",
                "color": "#0055AA",
            },
        ).json()
        fee = _category(
            client,
            headers,
            name="Retta",
            direction="income",
            required_person_role="student",
            course_required=True,
        )
        refund = _category(
            client,
            headers,
            name="Rimborso",
            direction="expense",
            required_person_role="teacher",
            course_required=True,
        )

        without_course = _movement(
            client,
            headers,
            direction="income",
            category_id=fee["id"],
            amount="100.00",
            person_id=student_id,
        )
        assert without_course.json()["error"]["code"] == "ACCOUNTING_COURSE_REQUIRED"
        not_enrolled = _movement(
            client,
            headers,
            direction="income",
            category_id=fee["id"],
            amount="100.00",
            person_id=student_id,
            course_id=course["id"],
        )
        assert not_enrolled.json()["error"]["code"] == "INVALID_ACCOUNTING_ENROLLMENT"

        client.post(
            "/api/v1/enrollments",
            headers=headers,
            json={
                "course_id": course["id"],
                "student_person_id": student_id,
                "enrolled_on": "2026-01-10",
                "starts_on": "2026-01-15",
            },
        )
        enrolled = _movement(
            client,
            headers,
            direction="income",
            category_id=fee["id"],
            amount="100.00",
            person_id=student_id,
            course_id=course["id"],
        )
        assert enrolled.status_code == 201

        teacher_refund = _movement(
            client,
            headers,
            direction="expense",
            category_id=refund["id"],
            amount="40.00",
            person_id=teacher_id,
            course_id=course["id"],
        )
        assert teacher_refund.status_code == 201


def test_opening_balances_and_summary(accounting_app: FastAPI) -> None:
    with TestClient(accounting_app) as client:
        headers = _headers(client)
        empty = client.get("/api/v1/accounting/opening-balances/2026", headers=headers)
        assert empty.json() == {"fiscal_year": 2026, "bank": "0.00", "cash": "0.00"}

        saved = client.put(
            "/api/v1/accounting/opening-balances/2026",
            headers=headers,
            json={"bank": "1000.00", "cash": "50.00"},
        )
        assert saved.status_code == 200
        resaved = client.put(
            "/api/v1/accounting/opening-balances/2026",
            headers=headers,
            json={"bank": "1200.00", "cash": "50.00"},
        )
        assert resaved.json()["bank"] == "1200.00"

        income = _category(client, headers, name="Donazioni", direction="income")
        other = _category(client, headers, name="Altro", direction="both")
        _movement(client, headers, direction="income", category_id=income["id"], amount="300.00")
        _movement(
            client,
            headers,
            direction="expense",
            account="cash",
            category_id=other["id"],
            amount="20.00",
        )
        _movement(
            client,
            headers,
            occurred_on="2025-12-31",
            direction="income",
            category_id=income["id"],
            amount="999.00",
        )

        summary = client.get("/api/v1/accounting/summary/2026", headers=headers)
        assert summary.status_code == 200
        body = summary.json()
        assert body["fiscal_year"] == 2026
        assert body["accounts"] == [
            {
                "account": "bank",
                "opening": "1200.00",
                "income": "300.00",
                "expense": "0.00",
                "closing": "1500.00",
            },
            {
                "account": "cash",
                "opening": "50.00",
                "income": "0.00",
                "expense": "20.00",
                "closing": "30.00",
            },
        ]
        assert body["categories"] == [
            {"category_id": income["id"], "direction": "income", "amount": "300.00"},
            {"category_id": other["id"], "direction": "expense", "amount": "20.00"},
        ]
