from pathlib import Path

import pytest
from sqlalchemy import text

from arsis.core import database
from arsis.core.config import Settings


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

