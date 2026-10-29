import sqlite3
from contextlib import closing
from pathlib import Path

import pytest
from sqlalchemy import text

from arsis.core import database
from arsis.core.config import Settings
from arsis.core.database_backup import DatabaseBackupError, backup_database, restore_database


def test_sqlite_engine_enables_safety_pragmas(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = Settings(arsis_data_dir=tmp_path)
    monkeypatch.setattr(database, "get_settings", lambda: settings)

    engine = database.create_database_engine()
    try:
        with engine.connect() as connection:
            foreign_keys = connection.execute(text("PRAGMA foreign_keys")).scalar_one()
            journal_mode = connection.execute(text("PRAGMA journal_mode")).scalar_one()
            busy_timeout = connection.execute(text("PRAGMA busy_timeout")).scalar_one()

        assert settings.database_path.exists()
        assert foreign_keys == 1
        assert journal_mode == "wal"
        assert busy_timeout == 5000
    finally:
        engine.dispose()


def test_backup_and_restore_round_trip(tmp_path: Path) -> None:
    database_path = tmp_path / "arsis.db"
    backup_path = tmp_path / "exports" / "arsis-backup.db"
    with closing(sqlite3.connect(database_path)) as connection, connection:
        connection.execute("CREATE TABLE example (value TEXT NOT NULL)")
        connection.execute("INSERT INTO example VALUES ('prima')")

    assert backup_database(backup_path, database_path=database_path) == backup_path

    with closing(sqlite3.connect(database_path)) as connection, connection:
        connection.execute("UPDATE example SET value = 'dopo'")

    assert restore_database(backup_path, database_path=database_path) == database_path
    with closing(sqlite3.connect(database_path)) as connection:
        value = connection.execute("SELECT value FROM example").fetchone()
    assert value == ("prima",)


def test_backup_includes_committed_wal_data(tmp_path: Path) -> None:
    database_path = tmp_path / "arsis.db"
    backup_path = tmp_path / "arsis-backup.db"
    with closing(sqlite3.connect(database_path)) as connection, connection:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("CREATE TABLE example (value TEXT NOT NULL)")
        connection.execute("INSERT INTO example VALUES ('nel-wal')")

    backup_database(backup_path, database_path=database_path)

    with closing(sqlite3.connect(backup_path)) as connection:
        value = connection.execute("SELECT value FROM example").fetchone()
    assert value == ("nel-wal",)


def test_restore_rejects_invalid_file_without_touching_database(tmp_path: Path) -> None:
    database_path = tmp_path / "arsis.db"
    invalid_backup = tmp_path / "invalid.db"
    with closing(sqlite3.connect(database_path)) as connection, connection:
        connection.execute("CREATE TABLE example (value TEXT NOT NULL)")
        connection.execute("INSERT INTO example VALUES ('intatto')")
    invalid_backup.write_text("non e un database", encoding="utf-8")

    with pytest.raises(DatabaseBackupError, match="Impossibile ripristinare"):
        restore_database(invalid_backup, database_path=database_path)

    with closing(sqlite3.connect(database_path)) as connection:
        value = connection.execute("SELECT value FROM example").fetchone()
    assert value == ("intatto",)

