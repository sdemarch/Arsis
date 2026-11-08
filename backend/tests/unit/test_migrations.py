import importlib.util
import shutil
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

import pytest

from arsis.core.config import PROJECT_ROOT
from arsis.core.migrations import MigrationError, migrate, pending_changesets, read_changelog
from arsis.generated.models import SCHEMA_FINGERPRINT

CHANGELOG = PROJECT_ROOT / "database" / "changelog"


def _schema_fingerprint(database: Path) -> str:
    spec = importlib.util.spec_from_file_location(
        "generate_backend_schema", PROJECT_ROOT / "scripts" / "generate_backend_schema.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses look their module up while it executes
    spec.loader.exec_module(module)
    return str(module.read_schema(database)[1])


def _changelog_copy(tmp_path: Path, files: list[str]) -> Path:
    """A changelog directory including only ``files``, in that order."""
    target = tmp_path / "changelog"
    shutil.copytree(CHANGELOG / "changes", target / "changes")
    includes = "".join(
        f"  - include:\n      file: changes/{name}\n      relativeToChangelogFile: true\n"
        for name in files
    )
    (target / "db.changelog-master.yaml").write_text(
        f"databaseChangeLog:\n{includes}", encoding="utf-8"
    )
    return target


def _rows(database: Path, sql: str) -> list[tuple[object, ...]]:
    with closing(sqlite3.connect(database)) as connection:
        return connection.execute(sql).fetchall()


def test_fresh_database_gets_the_schema_liquibase_produces(tmp_path: Path) -> None:
    database = tmp_path / "data" / "arsis.db"
    changesets = read_changelog(CHANGELOG)

    result = migrate(database, CHANGELOG, backups_dir=tmp_path / "backups")

    assert result.applied == [changeset.id for changeset in changesets]
    assert result.backup is None
    # Same fingerprint as the models generated from the Liquibase-built database.
    assert _schema_fingerprint(database) == SCHEMA_FINGERPRINT
    rows = _rows(
        database, "SELECT ID, AUTHOR, FILENAME, ORDEREXECUTED, MD5SUM FROM DATABASECHANGELOG"
    )
    assert rows[0] == (
        "0001-initial-schema",
        "arsis",
        "changelog/changes/0001-initial-schema.sql",
        1,
        None,
    )
    assert len(rows) == len(changesets)
    assert _rows(database, "SELECT LOCKED FROM DATABASECHANGELOGLOCK") == [(0,)]
    assert _rows(database, "PRAGMA foreign_key_check") == []

    again = migrate(database, CHANGELOG, backups_dir=tmp_path / "backups")
    assert again.applied == []
    assert pending_changesets(database, CHANGELOG) == []


def test_existing_database_is_backed_up_before_new_changesets(tmp_path: Path) -> None:
    names = sorted(path.name for path in (CHANGELOG / "changes").glob("*.sql"))
    database = tmp_path / "arsis.db"
    migrate(database, _changelog_copy(tmp_path / "old", names[:-1]), backups_dir=tmp_path / "b")
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.execute("INSERT INTO app_settings (key, value) VALUES ('test.marker', '1')")

    result = migrate(database, CHANGELOG, backups_dir=tmp_path / "backups")

    assert result.applied == [names[-1].removesuffix(".sql")]
    assert result.backup is not None and result.backup.parent == tmp_path / "backups"
    assert _rows(result.backup, "SELECT value FROM app_settings WHERE key = 'test.marker'") == [
        ("1",)
    ]
    assert _rows(result.backup, "SELECT COUNT(*) FROM DATABASECHANGELOG") == [(len(names) - 1,)]
    assert _rows(database, "SELECT COUNT(*) FROM DATABASECHANGELOG") == [(len(names),)]


def test_failing_changeset_is_rolled_back_and_not_recorded(tmp_path: Path) -> None:
    changelog = _changelog_copy(tmp_path, ["0001-initial-schema.sql", "9999-broken.sql"])
    (changelog / "changes" / "9999-broken.sql").write_text(
        "--liquibase formatted sql\n\n--changeset arsis:9999-broken\n"
        "CREATE TABLE half_done (id INTEGER PRIMARY KEY);\n"
        "INSERT INTO missing_table VALUES (1);\n",
        encoding="utf-8",
    )
    database = tmp_path / "arsis.db"

    with pytest.raises(MigrationError, match="9999-broken"):
        migrate(database, changelog, backups_dir=tmp_path / "backups")

    assert _rows(database, "SELECT ID FROM DATABASECHANGELOG") == [("0001-initial-schema",)]
    assert _rows(database, "SELECT name FROM sqlite_master WHERE name = 'half_done'") == []
    assert _rows(database, "SELECT LOCKED FROM DATABASECHANGELOGLOCK") == [(0,)]


def test_database_from_a_newer_version_is_refused(tmp_path: Path) -> None:
    database = tmp_path / "arsis.db"
    migrate(database, CHANGELOG, backups_dir=tmp_path / "backups")
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.execute(
            "INSERT INTO DATABASECHANGELOG (ID, AUTHOR, FILENAME, DATEEXECUTED, ORDEREXECUTED, "
            "EXECTYPE) VALUES ('9000-future', 'arsis', 'changelog/changes/9000.sql', 'x', 99, "
            "'EXECUTED')"
        )

    with pytest.raises(MigrationError, match="più recente"):
        migrate(database, CHANGELOG, backups_dir=tmp_path / "backups")


def test_held_lock_stops_the_migration(tmp_path: Path) -> None:
    database = tmp_path / "arsis.db"
    migrate(database, _changelog_copy(tmp_path, ["0001-initial-schema.sql"]), backups_dir=tmp_path)
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.execute("UPDATE DATABASECHANGELOGLOCK SET LOCKED = 1")

    with pytest.raises(MigrationError, match="in corso"):
        migrate(database, CHANGELOG, backups_dir=tmp_path / "backups")
