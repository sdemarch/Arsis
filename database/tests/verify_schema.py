from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

EXPECTED_TABLES = {
    "DATABASECHANGELOG",
    "DATABASECHANGELOGLOCK",
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
    "musician_sections",
    "musicians",
    "people",
    "person_roles",
    "refresh_sessions",
    "sections",
    "students",
    "teachers",
    "users",
}


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
    if missing or unexpected or foreign_key_errors or changesets != 4:
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

