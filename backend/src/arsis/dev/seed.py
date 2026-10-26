"""Idempotent development data aligned with the Angular mock scenarios."""

import argparse
import json
import sqlite3
from collections.abc import Mapping, Sequence
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

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


def _id(entity: str, key: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"https://arsis.local/dev/{entity}/{key}"))


def _upsert(
    connection: sqlite3.Connection,
    table: str,
    values: Mapping[str, Any],
    *,
    conflict_column: str = "id",
) -> None:
    columns = tuple(values)
    placeholders = ", ".join("?" for _ in columns)
    updates = ", ".join(
        f"{column} = excluded.{column}" for column in columns if column != conflict_column
    )
    connection.execute(
        f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders}) "
        f"ON CONFLICT({conflict_column}) DO UPDATE SET {updates}",
        tuple(values[column] for column in columns),
    )


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


def _seed_user(connection: sqlite3.Connection) -> str:
    user_id = _id("user", "responsabile")
    _upsert(
        connection,
        "users",
        {
            "id": user_id,
            "email": "responsabile@arsis.it",
            "password_hash": hash_password("arsis-demo-password"),
            "display_name": "Stefano",
            "is_active": 1,
        },
    )
    return user_id


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


def _seed_people(connection: sqlite3.Connection, user_id: str) -> dict[str, str]:
    person_ids: dict[str, str] = {}
    for person in PEOPLE:
        key = str(person["key"])
        person_id = _id("person", key)
        person_ids[key] = person_id
        _upsert(
            connection,
            "people",
            {
                "id": person_id,
                "first_name": person["first_name"],
                "last_name": person["last_name"],
                "email": person["email"],
                "phone": person["phone"],
                "created_by": user_id,
                "updated_by": user_id,
            },
        )
        for role_type in person["roles"]:
            role_id = _id("person-role", f"{key}:{role_type}")
            _upsert(
                connection,
                "person_roles",
                {
                    "id": role_id,
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
                "id": _id(subtype_table, key),
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
            "id": _id("associated-contact", "marco-rossi:giulia-moretti"),
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


def _seed_catalogues(connection: sqlite3.Connection, user_id: str) -> dict[str, str]:
    instrument_ids: dict[str, str] = {}
    for order, name in enumerate(("Clarinetto", "Saxofono"), start=1):
        instrument_id = _id("instrument", name.lower())
        instrument_ids[name.lower()] = instrument_id
        _upsert(
            connection,
            "instruments",
            {
                "id": instrument_id,
                "name": name,
                "is_active": 1,
                "display_order": order,
                "created_by": user_id,
                "updated_by": user_id,
            },
        )
    for order, name in enumerate(("Legni", "Ottoni", "Percussioni"), start=1):
        _upsert(
            connection,
            "sections",
            {
                "id": _id("section", name.lower()),
                "name": name,
                "is_active": 1,
                "display_order": order,
                "created_by": user_id,
                "updated_by": user_id,
            },
        )
    return instrument_ids


COURSES: tuple[dict[str, Any], ...] = (
    {
        "key": "clarinetto",
        "name": "Clarinetto",
        "mode": "individual",
        "category": "instrument",
        "instrument": "clarinetto",
        "teacher": "elena-bianchi",
        "weekday": 1,
        "start_time": "15:30",
        "annual_fee": "420.00",
        "color": "#378ADD",
    },
    {
        "key": "saxofono",
        "name": "Saxofono",
        "mode": "individual",
        "category": "instrument",
        "instrument": "saxofono",
        "teacher": "luca-ferri",
        "weekday": 3,
        "start_time": "17:00",
        "annual_fee": "420.00",
        "color": "#1D9E75",
    },
    {
        "key": "propedeutica-musicale",
        "name": "Propedeutica musicale",
        "mode": "group",
        "category": "ensemble",
        "instrument": None,
        "teacher": "chiara-pellegrini",
        "weekday": 2,
        "start_time": "16:30",
        "annual_fee": "280.00",
        "color": "#D85A30",
    },
    {
        "key": "musica-insieme",
        "name": "Musica d'insieme",
        "mode": "group",
        "category": "ensemble",
        "instrument": None,
        "teacher": "andrea-neri",
        "weekday": 4,
        "start_time": "18:30",
        "annual_fee": "180.00",
        "color": "#7F77DD",
    },
)


def _seed_school(
    connection: sqlite3.Connection,
    user_id: str,
    person_ids: Mapping[str, str],
    instrument_ids: Mapping[str, str],
) -> tuple[dict[str, str], int]:
    course_ids: dict[str, str] = {}
    for course in COURSES:
        key = str(course["key"])
        course_id = _id("course", key)
        course_ids[key] = course_id
        instrument = course["instrument"]
        _upsert(
            connection,
            "courses",
            {
                "id": course_id,
                "name": course["name"],
                "mode": course["mode"],
                "category": course["category"],
                "instrument_id": instrument_ids[str(instrument)] if instrument else None,
                "teacher_person_id": person_ids[str(course["teacher"])],
                "weekday": course["weekday"],
                "start_time": course["start_time"],
                "annual_fee": course["annual_fee"],
                "color": course["color"],
                "valid_from": "2026-01-01",
                "status": "active",
                "created_by": user_id,
                "updated_by": user_id,
            },
        )

    enrollment_pairs = (
        ("clarinetto", "marco-rossi"),
        ("saxofono", "giulia-moretti"),
        ("propedeutica-musicale", "giulia-moretti"),
    )
    for course_key, student_key in enrollment_pairs:
        _upsert(
            connection,
            "enrollments",
            {
                "id": _id("enrollment", f"{course_key}:{student_key}"),
                "course_id": course_ids[course_key],
                "student_person_id": person_ids[student_key],
                "enrolled_on": "2026-01-10",
                "starts_on": "2026-01-15",
                "status": "active",
                "created_by": user_id,
                "updated_by": user_id,
            },
        )

    lessons = (
        ("clarinetto-1", "clarinetto", "elena-bianchi", "2026-08-20T15:30:00+02:00"),
        (
            "propedeutica-1",
            "propedeutica-musicale",
            "chiara-pellegrini",
            "2026-08-20T16:30:00+02:00",
        ),
        ("saxofono-1", "saxofono", "luca-ferri", "2026-08-20T18:00:00+02:00"),
    )
    for lesson_key, course_key, teacher_key, starts_at in lessons:
        lesson_id = _id("lesson", lesson_key)
        _upsert(
            connection,
            "lessons",
            {
                "id": lesson_id,
                "course_id": course_ids[course_key],
                "teacher_person_id": person_ids[teacher_key],
                "starts_at": starts_at,
                "status": "planned",
                "created_by": user_id,
                "updated_by": user_id,
            },
        )
        for enrolled_course, student_key in enrollment_pairs:
            if enrolled_course != course_key:
                continue
            _upsert(
                connection,
                "lesson_attendances",
                {
                    "id": _id("lesson-attendance", f"{lesson_key}:{student_key}"),
                    "lesson_id": lesson_id,
                    "student_person_id": person_ids[student_key],
                    "created_by": user_id,
                    "updated_by": user_id,
                },
            )
    return course_ids, len(lessons)


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
    user_id: str,
    person_ids: Mapping[str, str],
) -> None:
    musicians = ("elena-bianchi", "andrea-neri", "chiara-pellegrini")
    for index, (key, activity_type, title, starts_at, ends_at, location) in enumerate(
        ACTIVITIES
    ):
        activity_id = _id("activity", key)
        _upsert(
            connection,
            "activities",
            {
                "id": activity_id,
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
                    "id": _id("activity-participant", f"{key}:{musician_key}"),
                    "activity_id": activity_id,
                    "person_id": person_ids[musician_key],
                    "source": "automatic",
                    "created_by": user_id,
                    "updated_by": user_id,
                },
            )


def _seed_settings(connection: sqlite3.Connection, user_id: str) -> None:
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
        instrument_ids = _seed_catalogues(connection, user_id)
        course_ids, lesson_count = _seed_school(
            connection, user_id, person_ids, instrument_ids
        )
        _seed_activities(connection, user_id, person_ids)
        _seed_settings(connection, user_id)

    return SeedResult(
        database_path=path,
        people=len(person_ids),
        courses=len(course_ids),
        activities=len(ACTIVITIES),
        lessons=lesson_count,
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
