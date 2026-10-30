"""Idempotent development data aligned with the Angular mock scenarios."""

import argparse
import json
import sqlite3
from collections.abc import Mapping, Sequence
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arsis.core.config import get_settings
from arsis.core.security import hash_password

ALLOWED_ENVIRONMENTS = {"local", "development", "test"}
REQUIRED_TABLES = {
    "activities",
    "activity_participants",
    "app_settings",
    "associated_contacts",
    "courses",
    "enrollments",
    "instruments",
    "lesson_attendances",
    "lessons",
    "members",
    "musicians",
    "people",
    "person_roles",
    "sections",
    "students",
    "teachers",
    "users",
}


class DevelopmentSeedError(RuntimeError):
    """Raised when the development seed cannot be applied safely."""


@dataclass(frozen=True)
class SeedResult:
    database_path: Path
    people: int
    courses: int
    activities: int
    lessons: int


SEED_IDENTITIES: dict[str, tuple[str, ...]] = {
    "users": ("email",),
    "people": ("email",),
    "person_roles": ("person_id", "role_type"),
    "members": ("person_role_id",),
    "musicians": ("person_role_id",),
    "students": ("person_role_id",),
    "teachers": ("person_role_id",),
    "associated_contacts": ("person_id", "contact_person_id", "relationship_type"),
    "instruments": ("name",),
    "sections": ("name",),
    "courses": ("name",),
    "enrollments": ("course_id", "student_person_id"),
    "lessons": ("course_id", "starts_at"),
    "lesson_attendances": ("lesson_id", "student_person_id"),
    "activities": ("title", "starts_at"),
    "activity_participants": ("activity_id", "person_id"),
    "app_settings": ("key",),
}


def _upsert(
    connection: sqlite3.Connection,
    table: str,
    values: Mapping[str, Any],
    *,
    conflict_column: str | None = None,
) -> int:
    identity_columns = (conflict_column,) if conflict_column is not None else SEED_IDENTITIES[table]
    where_clause = " AND ".join(f"{column} = ?" for column in identity_columns)
    identity_values = tuple(values[column] for column in identity_columns)
    existing = connection.execute(
        f"SELECT rowid FROM {table} WHERE {where_clause}", identity_values
    ).fetchone()
    if existing:
        updates = ", ".join(f"{column} = ?" for column in values)
        connection.execute(
            f"UPDATE {table} SET {updates} WHERE rowid = ?",
            (*values.values(), existing[0]),
        )
        return int(existing[0])

    columns = tuple(values)
    placeholders = ", ".join("?" for _ in columns)
    cursor = connection.execute(
        f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
        tuple(values[column] for column in columns),
    )
    if cursor.lastrowid is None:
        raise DevelopmentSeedError(f"Inserimento senza rowid per la tabella {table}")
    return cursor.lastrowid


def _require_schema(connection: sqlite3.Connection) -> None:
    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }
    missing = sorted(REQUIRED_TABLES - tables)
    if missing:
        raise DevelopmentSeedError(
            "Schema SQLite non inizializzato; eseguire scripts/init-db.ps1. "
            f"Tabelle mancanti: {', '.join(missing)}"
        )


def _seed_user(connection: sqlite3.Connection) -> int:
    return _upsert(
        connection,
        "users",
        {
            "email": "responsabile@arsis.it",
            "password_hash": hash_password("arsis-demo-password"),
            "display_name": "Stefano",
            "is_active": 1,
        },
    )


PEOPLE: tuple[dict[str, Any], ...] = (
    {
        "key": "elena-bianchi",
        "first_name": "Elena",
        "last_name": "Bianchi",
        "email": "elena.bianchi@example.it",
        "phone": "+39 333 142 9081",
        "roles": ("teacher", "musician"),
    },
    {
        "key": "marco-rossi",
        "first_name": "Marco",
        "last_name": "Rossi",
        "email": "famiglia.rossi@example.it",
        "phone": "+39 347 550 1832",
        "roles": ("student",),
    },
    {
        "key": "luca-ferri",
        "first_name": "Luca",
        "last_name": "Ferri",
        "email": "luca.ferri@example.it",
        "phone": "+39 328 711 2045",
        "roles": ("member", "teacher"),
    },
    {
        "key": "giulia-moretti",
        "first_name": "Giulia",
        "last_name": "Moretti",
        "email": "giulia.moretti@example.it",
        "phone": "+39 340 901 4432",
        "roles": ("student", "member"),
    },
    {
        "key": "andrea-neri",
        "first_name": "Andrea",
        "last_name": "Neri",
        "email": "andrea.neri@example.it",
        "phone": "+39 349 224 8700",
        "roles": ("musician", "member", "teacher"),
    },
    {
        "key": "chiara-pellegrini",
        "first_name": "Chiara",
        "last_name": "Pellegrini",
        "email": "chiara.p@example.it",
        "phone": "+39 333 875 1022",
        "roles": ("musician", "teacher"),
    },
)


def _seed_people(connection: sqlite3.Connection, user_id: int) -> dict[str, int]:
    person_ids: dict[str, int] = {}
    for person in PEOPLE:
        key = str(person["key"])
        person_id = _upsert(
            connection,
            "people",
            {
                "first_name": person["first_name"],
                "last_name": person["last_name"],
                "email": person["email"],
                "phone": person["phone"],
                "created_by": user_id,
                "updated_by": user_id,
            },
        )
        person_ids[key] = person_id
        for role_type in person["roles"]:
            role_id = _upsert(
                connection,
                "person_roles",
                {
                    "person_id": person_id,
                    "role_type": role_type,
                    "start_date": "2020-01-01",
                    "status": "active",
                    "created_by": user_id,
                    "updated_by": user_id,
                },
            )
            subtype_table = {
                "member": "members",
                "musician": "musicians",
                "student": "students",
                "teacher": "teachers",
            }[role_type]
            subtype_values: dict[str, Any] = {
                "person_role_id": role_id,
                "created_by": user_id,
                "updated_by": user_id,
            }
            if role_type == "member":
                subtype_values["membership_start_date"] = "2020-01-01"
            elif role_type == "musician":
                subtype_values["joined_on"] = "2020-01-01"
            _upsert(connection, subtype_table, subtype_values)

    _upsert(
        connection,
        "associated_contacts",
        {
            "person_id": person_ids["marco-rossi"],
            "contact_person_id": person_ids["giulia-moretti"],
            "relationship_type": "reference",
            "is_primary": 1,
            "is_payment_contact": 1,
            "created_by": user_id,
            "updated_by": user_id,
        },
    )
    return person_ids


def _seed_catalogues(connection: sqlite3.Connection, user_id: int) -> None:
    section_ids: dict[str, int] = {}
    for order, name in enumerate(BAND_SECTIONS, start=1):
        section_ids[name] = _upsert(
            connection,
            "sections",
            {
                "name": name,
                "is_active": 1,
                "display_order": order,
                "created_by": user_id,
                "updated_by": user_id,
            },
        )
    for order, (name, section) in enumerate(BAND_INSTRUMENTS, start=1):
        _upsert(
            connection,
            "instruments",
            {
                "name": name,
                "section_id": section_ids[section],
                "is_active": 1,
                "display_order": order,
                "created_by": user_id,
                "updated_by": user_id,
            },
        )


BAND_SECTIONS = (
    "Clarinetti",
    "Trombe",
    "Corni",
    "Oboi",
    "Flauti",
    "Ottoni",
    "Percussioni",
    "Sax",
)

BAND_INSTRUMENTS: tuple[tuple[str, str], ...] = (
    ("Clarinetto", "Clarinetti"),
    ("Clarinetto Basso", "Clarinetti"),
    ("Clarinetto Piccolo", "Clarinetti"),
    ("Cornetta", "Trombe"),
    ("Corno", "Corni"),
    ("Corno Inglese", "Oboi"),
    ("Flauto Traverso", "Flauti"),
    ("Flicorno Baritono", "Ottoni"),
    ("Flicorno Contralto", "Corni"),
    ("Flicorno Soprano", "Ottoni"),
    ("Flicorno Tenore", "Ottoni"),
    ("Glockenspiel", "Percussioni"),
    ("Grancassa", "Percussioni"),
    ("Marimba", "Percussioni"),
    ("Oboe", "Oboi"),
    ("Ottavino", "Flauti"),
    ("Piatti", "Percussioni"),
    ("Rullante", "Percussioni"),
    ("Sax Baritono", "Sax"),
    ("Sax Contralto", "Sax"),
    ("Sax Soprano", "Sax"),
    ("Sax Tenore", "Sax"),
    ("Timpani", "Percussioni"),
    ("Tromba", "Ottoni"),
    ("Trombone", "Ottoni"),
    ("Tuba", "Ottoni"),
    ("Vibrafono", "Percussioni"),
    ("Xilofono", "Percussioni"),
)


ACTIVITIES: tuple[tuple[str, str, str, str, str, str], ...] = (
    (
        "prova-settimanale",
        "rehearsal",
        "Prova settimanale",
        "2026-08-24T20:45:00+02:00",
        "2026-08-24T22:30:00+02:00",
        "Sala prove",
    ),
    (
        "concerto-fine-estate",
        "concert",
        "Concerto di fine estate",
        "2026-08-30T21:00:00+02:00",
        "2026-08-30T23:00:00+02:00",
        "Piazza Municipale",
    ),
    (
        "festa-associazioni",
        "event",
        "Festa delle associazioni",
        "2026-09-05T16:30:00+02:00",
        "2026-09-05T19:00:00+02:00",
        "Parco comunale",
    ),
    (
        "prova-sezioni",
        "rehearsal",
        "Prova a sezioni",
        "2026-09-14T20:30:00+02:00",
        "2026-09-14T22:15:00+02:00",
        "Sala prove",
    ),
)


def _seed_activities(
    connection: sqlite3.Connection,
    user_id: int,
    person_ids: Mapping[str, int],
) -> None:
    musicians = ("elena-bianchi", "andrea-neri", "chiara-pellegrini")
    for index, (_key, activity_type, title, starts_at, ends_at, location) in enumerate(ACTIVITIES):
        activity_id = _upsert(
            connection,
            "activities",
            {
                "type": activity_type,
                "title": title,
                "starts_at": starts_at,
                "ends_at": ends_at,
                "location": location,
                "status": "confirmed" if index < 2 else "planned",
                "created_by": user_id,
                "updated_by": user_id,
            },
        )
        for musician_key in musicians:
            _upsert(
                connection,
                "activity_participants",
                {
                    "activity_id": activity_id,
                    "person_id": person_ids[musician_key],
                    "source": "automatic",
                    "created_by": user_id,
                    "updated_by": user_id,
                },
            )


def _seed_settings(connection: sqlite3.Connection, user_id: int) -> None:
    _upsert(
        connection,
        "app_settings",
        {
            "key": "archive.google_drive_url",
            "value": json.dumps(
                "https://drive.google.com/drive/folders/arsis-demo", ensure_ascii=False
            ),
            "description": "URL della cartella principale Google Drive",
            "created_by": user_id,
            "updated_by": user_id,
        },
        conflict_column="key",
    )


def seed_database(database_path: Path | None = None) -> SeedResult:
    settings = get_settings()
    if settings.app_env.lower() not in ALLOWED_ENVIRONMENTS:
        raise DevelopmentSeedError(
            "Il seed è consentito soltanto negli ambienti local, development e test"
        )

    path = (database_path or settings.database_path).expanduser().resolve()
    if not path.is_file():
        raise DevelopmentSeedError(
            f"Database SQLite non trovato: {path}. Eseguire scripts/init-db.ps1."
        )

    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=5000")
        _require_schema(connection)
        user_id = _seed_user(connection)
        person_ids = _seed_people(connection, user_id)
        _seed_catalogues(connection, user_id)
        _seed_activities(connection, user_id, person_ids)
        _seed_settings(connection, user_id)

    return SeedResult(
        database_path=path,
        people=len(person_ids),
        courses=0,
        activities=len(ACTIVITIES),
        lessons=0,
    )


def _parse_args(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, help="Percorso di un database già migrato")
    return parser.parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> None:
    options = _parse_args(arguments)
    result = seed_database(options.database)
    print(
        "Seed completato: "
        f"{result.people} persone, {result.courses} corsi, "
        f"{result.activities} attività, {result.lessons} lezioni. "
        f"Database: {result.database_path}"
    )


if __name__ == "__main__":
    main()
