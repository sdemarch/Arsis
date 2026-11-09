import sqlite3
from collections.abc import Iterator
from contextlib import closing
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from arsis.core.config import get_settings
from arsis.core.database import dispose_database_engine
from arsis.core.maintenance import maintenance_gate
from arsis.core.saves import create_save
from arsis.main import create_app
from arsis.migrate import run_migrations

EMAIL = "responsabile@example.it"
PASSWORD = "correct horse battery staple"


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """A real installation in ``tmp_path``: import swaps the database file itself."""
    monkeypatch.setenv("ARSIS_DATA_DIR", str(tmp_path / "data"))
    get_settings.cache_clear()
    dispose_database_engine()
    run_migrations()
    with TestClient(create_app()) as test_client:
        test_client.post(
            "/api/v1/auth/setup",
            json={"email": EMAIL, "display_name": "Responsabile", "password": PASSWORD},
        )
        _sign_in(test_client)
        yield test_client
    dispose_database_engine()
    get_settings.cache_clear()
    maintenance_gate.tokens_not_before = None


def _sign_in(client: TestClient) -> None:
    response = client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
    client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"


def _organization(client: TestClient, name: str | None = None) -> str:
    settings = client.get("/api/v1/settings/general").json()
    if name is not None:
        settings = client.put(
            "/api/v1/settings/general", json={**settings, "organization_name": name}
        )
        settings = settings.json()
    return str(settings["organization_name"])


def _upload(content: bytes) -> dict[str, tuple[str, bytes, str]]:
    return {"file": ("dati.arsis-save", content, "application/octet-stream")}


def test_export_inspect_and_import_restore_the_saved_data(client: TestClient) -> None:
    _organization(client, "Banda prima")
    exported = client.get("/api/v1/maintenance/saves/export")
    assert exported.status_code == 200
    assert ".arsis-save" in exported.headers["content-disposition"]
    assert not list((get_settings().data_dir / "tmp").glob("export-*"))

    summary = client.post("/api/v1/maintenance/saves/inspect", files=_upload(exported.content))
    assert summary.status_code == 200, summary.text
    assert summary.json()["organization_name"] == "Banda prima"
    assert summary.json()["contents"]["responsible_users"] == 1
    assert summary.json()["pending_migrations"] == 0

    _organization(client, "Banda dopo")
    wrong = client.post(
        "/api/v1/maintenance/saves/import",
        files=_upload(exported.content),
        data={"password": "sbagliata"},
    )
    assert wrong.status_code == 422
    assert wrong.json()["error"]["code"] == "PASSWORD_MISMATCH"

    imported = client.post(
        "/api/v1/maintenance/saves/import",
        files=_upload(exported.content),
        data={"password": PASSWORD},
    )
    assert imported.status_code == 200, imported.text
    backup = get_settings().backups_dir / imported.json()["backup_file"]
    assert backup.is_file()

    # Tokens issued before the import are no longer accepted.
    assert client.get("/api/v1/settings/general").status_code == 401
    _sign_in(client)
    assert _organization(client) == "Banda prima"


def test_inspect_rejects_files_that_are_not_arsis_saves(client: TestClient, tmp_path: Path) -> None:
    garbage = client.post("/api/v1/maintenance/saves/inspect", files=_upload(b"non un archivio"))
    assert garbage.status_code == 422
    assert garbage.json()["error"]["code"] == "INVALID_SAVE"

    foreign = tmp_path / "altro.db"
    with closing(sqlite3.connect(foreign)) as connection, connection:
        connection.execute("CREATE TABLE example (value TEXT)")
    save = create_save(tmp_path / "altro.arsis-save", database_path=foreign)
    response = client.post("/api/v1/maintenance/saves/inspect", files=_upload(save.read_bytes()))
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_SAVE"


def test_saves_from_a_newer_version_are_refused(client: TestClient, tmp_path: Path) -> None:
    newer = tmp_path / "newer.db"
    with (
        closing(sqlite3.connect(get_settings().database_path)) as source,
        closing(sqlite3.connect(newer)) as target,
    ):
        source.backup(target)
        target.execute(
            "INSERT INTO DATABASECHANGELOG (ID, AUTHOR, FILENAME, DATEEXECUTED, ORDEREXECUTED, "
            "EXECTYPE) VALUES ('9999-futuro', 'arsis', 'changelog/9999.sql', '2030-01-01', 99, "
            "'EXECUTED')"
        )
        target.commit()
    save = create_save(tmp_path / "newer.arsis-save", database_path=newer)
    response = client.post(
        "/api/v1/maintenance/saves/import",
        files=_upload(save.read_bytes()),
        data={"password": PASSWORD},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "SAVE_FROM_NEWER_VERSION"
    assert _organization(client) is not None


def test_api_requests_wait_outside_while_maintenance_runs(client: TestClient) -> None:
    with maintenance_gate.exclusive(own_requests=0, timeout=1):
        response = client.get("/api/v1/settings/general")
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "MAINTENANCE_IN_PROGRESS"
        assert client.get("/health/live").status_code == 200
    assert client.get("/api/v1/settings/general").status_code == 200
