from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

EXPECTED_TABLES = {
    "DATABASECHANGELOG",
    "DATABASECHANGELOGLOCK",
    "accounting_categories",
    "accounting_movements",
    "accounting_opening_balances",
    "activities",
    "activity_participants",
    "app_settings",
    "associated_contacts",
    "audit_events",
    "course_installment_templates",
    "courses",
    "enrollment_discounts",
    "enrollments",
    "instruments",
    "lesson_attendances",
    "lessons",
    "members",
    "musician_instruments",
    "musicians",
    "people",
    "person_roles",
    "refresh_sessions",
    "sections",
    "students",
    "teachers",
    "users",
}
CHANGELOG_DIR = Path(__file__).parents[1] / "changelog" / "changes"


def expected_changeset_count() -> int:
    return sum(
        path.read_text(encoding="utf-8").count("--changeset ")
        for path in CHANGELOG_DIR.glob("*.sql")
    )


def verify_schema(database_path: Path) -> None:
    if not database_path.is_file():
        raise SystemExit(f"Database non trovato: {database_path}")

    with sqlite3.connect(database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        foreign_key_errors = connection.execute("PRAGMA foreign_key_check").fetchall()
        changesets = connection.execute(
            "SELECT COUNT(*) FROM DATABASECHANGELOG"
        ).fetchone()[0]

    missing = EXPECTED_TABLES - tables
    unexpected = tables - EXPECTED_TABLES
    expected_changesets = expected_changeset_count()
    if missing or unexpected or foreign_key_errors or changesets != expected_changesets:
        raise SystemExit(
            "Schema non valido: "
            f"missing={sorted(missing)}, unexpected={sorted(unexpected)}, "
            f"foreign_key_errors={foreign_key_errors}, changesets={changesets}"
        )

    print(f"Schema valido: {len(tables)} tabelle, {changesets} changeset.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verifica lo schema SQLite Arsis.")
    parser.add_argument("database", type=Path)
    arguments = parser.parse_args()
    verify_schema(arguments.database.resolve())


if __name__ == "__main__":
    main()

