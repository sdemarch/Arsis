"""RB-21: the catalogue of person roles is configurable."""

from collections.abc import Iterator
from io import BytesIO

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from openpyxl import Workbook, load_workbook
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from arsis.auth.service import bootstrap_first_responsible
from arsis.core.database import get_database_session
from arsis.generated.models import Base
from arsis.main import create_app
from arsis.roles.service import slugify


@pytest.fixture
def client(tmp_path) -> Iterator[TestClient]:
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'roles.db').as_posix()}",
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

    application: FastAPI = create_app()
    application.dependency_overrides[get_database_session] = override_session
    with TestClient(application) as test_client:
        login = test_client.post(
            "/api/v1/auth/login",
            json={"email": "responsabile@example.it", "password": "correct horse battery staple"},
        )
        test_client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
        yield test_client
    engine.dispose()


def _role(client: TestClient, name: str, plural: str) -> dict:
    response = client.post("/api/v1/role-types", json={"name": name, "plural_name": plural})
    assert response.status_code == 201, response.text
    return response.json()


def _person(client: TestClient, first_name: str) -> int:
    response = client.post("/api/v1/people", json={"first_name": first_name, "last_name": "Banda"})
    assert response.status_code == 201
    return int(response.json()["id"])


def _codes(client: TestClient, person_id: int) -> set[str]:
    return {role["role_type"] for role in client.get(f"/api/v1/people/{person_id}/roles").json()}


def _assign(client: TestClient, person_id: int, code: str):
    return client.post(
        f"/api/v1/people/{person_id}/roles",
        json={"role_type": code, "start_date": "2026-01-01"},
    )


def test_slugify_builds_ascii_codes() -> None:
    assert slugify("Maestro di Banda") == "maestro-di-banda"
    assert slugify("Più Àccenti!") == "piu-accenti"
    assert slugify("2° tromba") == "ruolo-2-tromba"


def test_system_roles_are_listed_renamable_but_not_archivable(client: TestClient) -> None:
    roles = client.get("/api/v1/role-types").json()
    assert [role["code"] for role in roles] == ["member", "musician", "student", "teacher"]
    assert all(role["is_system"] for role in roles)
    member = roles[0]

    renamed = client.patch(
        f"/api/v1/role-types/{member['id']}",
        json={"version": member["version"], "name": "Associato", "plural_name": "Associati"},
    )
    assert renamed.status_code == 200
    assert renamed.json()["code"] == "member"  # the code never changes
    assert renamed.json()["name"] == "Associato"

    refused = client.delete(
        f"/api/v1/role-types/{member['id']}", params={"version": renamed.json()["version"]}
    )
    assert refused.status_code == 409
    assert refused.json()["error"]["code"] == "ROLE_TYPE_SYSTEM"


def test_custom_role_lifecycle(client: TestClient) -> None:
    volunteer = _role(client, "Volontario", "Volontari")
    assert volunteer["code"] == "volontario"
    assert volunteer["is_system"] is False
    assert volunteer["display_order"] > 40  # after the built-in roles

    duplicate = client.post("/api/v1/role-types", json={"name": " volontario ", "plural_name": "x"})
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "ROLE_TYPE_NAME_TAKEN"

    anna = _person(client, "Anna")
    assigned = _assign(client, anna, "volontario")
    assert assigned.status_code == 201
    assert "volontario" in _codes(client, anna)
    listed = next(r for r in client.get("/api/v1/role-types").json() if r["code"] == "volontario")
    assert listed["active_people"] == 1

    in_use = client.delete(
        f"/api/v1/role-types/{volunteer['id']}", params={"version": volunteer["version"]}
    )
    assert in_use.status_code == 409
    assert in_use.json()["error"]["code"] == "ROLE_TYPE_IN_USE"

    role = assigned.json()
    client.delete(f"/api/v1/people/roles/{role['id']}", params={"version": role["version"]})
    archived = client.delete(
        f"/api/v1/role-types/{volunteer['id']}", params={"version": volunteer["version"]}
    )
    assert archived.status_code == 200
    assert archived.json()["archived_at"] is not None
    assert "volontario" not in [r["code"] for r in client.get("/api/v1/role-types").json()]
    assert _assign(client, anna, "volontario").status_code == 422  # no longer assignable

    # The name is free again; the code stays unique because history points at it.
    again = _role(client, "Volontario", "Volontari")
    assert again["code"] == "volontario-2"


def test_unknown_role_is_rejected(client: TestClient) -> None:
    assert _assign(client, _person(client, "Bruno"), "astronauta").status_code == 422


def test_import_accepts_custom_role_names(client: TestClient) -> None:
    _role(client, "Maestro di Banda", "Maestri di Banda")
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["first_name", "last_name", "roles"])
    worksheet.append(["Carla", "Verdi", "maestro di banda; Musicante"])
    content = BytesIO()
    workbook.save(content)
    imported = client.post(
        "/api/v1/people/import",
        files={
            "file": (
                "anagrafiche.xlsx",
                content.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    assert imported.status_code == 200, imported.text
    person = client.get("/api/v1/people?q=carla").json()["items"][0]
    assert _codes(client, person["id"]) == {"maestro-di-banda", "musician"}

    template = client.get("/api/v1/people/import/template")
    legend = load_workbook(BytesIO(template.content), read_only=True)["Legenda"]
    values = [(row[0].value, row[1].value) for row in legend.iter_rows(min_row=8)]
    assert ("Maestro di Banda", "maestro-di-banda") in values


def test_accounting_category_can_require_a_custom_role(client: TestClient) -> None:
    volunteer = _role(client, "Volontario", "Volontari")
    category = client.post(
        "/api/v1/accounting/categories",
        json={
            "name": "Rimborso volontari",
            "direction": "expense",
            "required_person_role": "volontario",
        },
    )
    assert category.status_code == 201, category.text

    bad = client.post(
        "/api/v1/accounting/categories",
        json={"name": "Altro", "direction": "expense", "required_person_role": "astronauta"},
    )
    assert bad.status_code == 409
    assert bad.json()["error"]["code"] == "INVALID_ROLE_TYPE"

    movement = {
        "occurred_on": "2026-03-10",
        "account": "cash",
        "subject": "Soggetto",
        "description": "Benzina",
        "direction": "expense",
        "amount": "12.00",
        "category_id": category.json()["id"],
    }
    dario = _person(client, "Dario")
    without_role = client.post(
        "/api/v1/accounting/movements", json={**movement, "person_id": dario}
    )
    assert without_role.status_code == 409
    assert without_role.json()["error"]["code"] == "INVALID_ACCOUNTING_PERSON"
    assert _assign(client, dario, "volontario").status_code == 201
    with_role = client.post("/api/v1/accounting/movements", json={**movement, "person_id": dario})
    assert with_role.status_code == 201, with_role.text

    # Close Dario's role: the category still requires it, so it cannot be archived.
    role = client.get(f"/api/v1/people/{dario}/roles").json()[0]
    client.delete(f"/api/v1/people/roles/{role['id']}", params={"version": role["version"]})
    blocked = client.delete(
        f"/api/v1/role-types/{volunteer['id']}", params={"version": volunteer["version"]}
    )
    assert blocked.status_code == 409
    assert "Rimborso volontari" in blocked.json()["error"]["message"]
