import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from arsis.core.saves import SaveError, create_save, inspect_save, restore_save


def test_save_round_trip_includes_attachments(tmp_path: Path) -> None:
    database_path = tmp_path / "arsis.db"
    attachments_dir = tmp_path / "attachments"
    attachments_dir.mkdir()
    (attachments_dir / "note.txt").write_text("allegato", encoding="utf-8")
    with closing(sqlite3.connect(database_path)) as connection, connection:
        connection.execute("CREATE TABLE example (value TEXT NOT NULL)")
        connection.execute("INSERT INTO example VALUES ('prima')")

    save_path = create_save(
        tmp_path / "arsis.arsis-save", database_path=database_path, attachments_dir=attachments_dir
    )
    assert inspect_save(save_path)["attachments"]["count"] == 1

    with closing(sqlite3.connect(database_path)) as connection, connection:
        connection.execute("UPDATE example SET value = 'dopo'")
    (attachments_dir / "note.txt").write_text("modificato", encoding="utf-8")

    restore_save(save_path, database_path=database_path, attachments_dir=attachments_dir)
    with closing(sqlite3.connect(database_path)) as connection:
        assert connection.execute("SELECT value FROM example").fetchone() == ("prima",)
    assert (attachments_dir / "note.txt").read_text(encoding="utf-8") == "allegato"


def test_save_rejects_an_invalid_extension_or_checksum(tmp_path: Path) -> None:
    database_path = tmp_path / "arsis.db"
    with closing(sqlite3.connect(database_path)) as connection, connection:
        connection.execute("CREATE TABLE example (value TEXT NOT NULL)")
    with pytest.raises(SaveError, match="estensione"):
        create_save(tmp_path / "arsis.zip", database_path=database_path)
