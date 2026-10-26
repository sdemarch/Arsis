import sqlite3
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace

import pytest

from arsis.dev import seed
from arsis.dev.seed import DevelopmentSeedError, seed_database


def _apply_schema(database_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[3]
    changes = project_root / "database" / "changelog" / "changes"
    with closing(sqlite3.connect(database_path)) as connection:
        for change in sorted(changes.glob("*.sql")):
            connection.executescript(change.read_text(encoding="utf-8"))


def test_development_seed_is_idempotent(tmp_path: Path) -> None:
    database_path = tmp_path / "arsis.db"
    _apply_schema(database_path)

    first = seed_database(database_path)
    second = seed_database(database_path)

    assert first == second
    assert first.people == 6
    assert first.courses == 4
    assert first.activities == 4
    assert first.lessons == 3

    with closing(sqlite3.connect(database_path)) as connection:
        assert connection.execute("SELECT count(*) FROM people").fetchone() == (6,)
        assert connection.execute("SELECT count(*) FROM courses").fetchone() == (4,)
        assert connection.execute("SELECT count(*) FROM activities").fetchone() == (4,)
        assert connection.execute("SELECT count(*) FROM lessons").fetchone() == (3,)
        assert connection.execute(
            "SELECT count(*) FROM associated_contacts"
        ).fetchone() == (1,)
        assert connection.execute("SELECT id FROM users").fetchone() == (1,)
        assert connection.execute("SELECT id FROM people ORDER BY id").fetchall() == [
            (1,),
            (2,),
            (3,),
            (4,),
            (5,),
            (6,),
        ]


def test_development_seed_rejects_production(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = SimpleNamespace(app_env="production", database_path=tmp_path / "arsis.db")
    monkeypatch.setattr(seed, "get_settings", lambda: settings)

    with pytest.raises(DevelopmentSeedError, match="local, development e test"):
        seed_database()
