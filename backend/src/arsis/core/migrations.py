"""Apply the Liquibase changelog to SQLite without Java.

The installed application cannot depend on Liquibase, so this module reads the
same formatted-SQL changelog and records applied changesets in the same
``DATABASECHANGELOG`` table. Databases stay interchangeable between the two
tools: changesets applied here are skipped by Liquibase, which fills in the
checksum left empty here on its next run.
"""

import re
import sqlite3
import time
from collections.abc import Iterator, Sequence
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from arsis.core.database_backup import backup_database

_CHANGESET = re.compile(r"^--changeset\s+([^:\s]+):(\S+)")
_INCLUDE = re.compile(r"^\s*(?:-\s*)?file:\s*(\S+)\s*$")
TOOL_NAME = "arsis-migrate"

# Same DDL Liquibase uses, so either tool can open a database created by the other.
_CHANGELOG_DDL = (
    "CREATE TABLE IF NOT EXISTS DATABASECHANGELOG (ID VARCHAR(255) NOT NULL, "
    "AUTHOR VARCHAR(255) NOT NULL, FILENAME VARCHAR(255) NOT NULL, DATEEXECUTED TEXT NOT NULL, "
    "ORDEREXECUTED INTEGER NOT NULL, EXECTYPE VARCHAR(10) NOT NULL, MD5SUM VARCHAR(35), "
    "DESCRIPTION VARCHAR(255), COMMENTS VARCHAR(255), TAG VARCHAR(255), LIQUIBASE VARCHAR(20), "
    "CONTEXTS VARCHAR(255), LABELS VARCHAR(255), DEPLOYMENT_ID VARCHAR(10))"
)
_LOCK_DDL = (
    "CREATE TABLE IF NOT EXISTS DATABASECHANGELOGLOCK (ID INTEGER NOT NULL, LOCKED BOOLEAN NOT "
    "NULL, LOCKGRANTED TEXT, LOCKEDBY VARCHAR(255), "
    "CONSTRAINT PK_DATABASECHANGELOGLOCK PRIMARY KEY (ID))"
)


class MigrationError(RuntimeError):
    """The database could not be brought up to date; it is left as it was."""


@dataclass(frozen=True)
class Changeset:
    id: str
    author: str
    filename: str
    comment: str | None
    sql: str

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.id, self.author, self.filename)


@dataclass(frozen=True)
class MigrationResult:
    applied: Sequence[str]
    backup: Path | None


def read_changelog(changelog_dir: Path) -> list[Changeset]:
    """Changesets in the order of ``db.changelog-master.yaml``."""
    master = changelog_dir / "db.changelog-master.yaml"
    if not master.is_file():
        raise MigrationError(f"Changelog non trovato: {master}")
    changesets: list[Changeset] = []
    for line in master.read_text(encoding="utf-8").splitlines():
        if match := _INCLUDE.match(line):
            relative = match.group(1)
            # Liquibase records paths relative to the directory holding "changelog/".
            changesets.extend(
                _parse_sql_file(changelog_dir / relative, f"{changelog_dir.name}/{relative}")
            )
    return changesets


def _parse_sql_file(path: Path, filename: str) -> Iterator[Changeset]:
    header: tuple[str, str] | None = None
    comment: str | None = None
    body: list[str] = []

    def flush() -> Iterator[Changeset]:
        if header is not None:
            author, changeset_id = header
            yield Changeset(changeset_id, author, filename, comment, "\n".join(body).strip())

    for line in path.read_text(encoding="utf-8").splitlines():
        if match := _CHANGESET.match(line):
            yield from flush()
            header, comment, body = (match.group(1), match.group(2)), None, []
        elif line.startswith("--comment"):
            comment = line.removeprefix("--comment").strip(": ").strip() or None
        elif not line.startswith("--"):
            body.append(line)
    yield from flush()


def _statements(sql: str) -> Iterator[str]:
    """Split a script on complete statements, so ';' inside strings or triggers is safe."""
    buffer: list[str] = []
    for line in sql.splitlines():
        buffer.append(line)
        candidate = "\n".join(buffer).strip()
        if candidate and sqlite3.complete_statement(candidate):
            yield candidate
            buffer = []
    rest = "\n".join(buffer).strip()
    if rest:
        raise MigrationError(f"Istruzione SQL incompleta: {rest[:80]}")


def pending_changesets(database_path: Path, changelog_dir: Path) -> list[Changeset]:
    changesets = read_changelog(changelog_dir)
    if not database_path.is_file():
        return changesets
    with closing(sqlite3.connect(database_path)) as connection:
        applied = _applied_keys(connection)
    return [changeset for changeset in changesets if changeset.key not in applied]


@dataclass(frozen=True)
class ChangelogStatus:
    pending: Sequence[Changeset]
    unknown: Sequence[str]


def changelog_status(database_path: Path, changelog_dir: Path) -> ChangelogStatus:
    """Changesets still to apply, and those applied by a newer Arsis than this one."""
    changesets = read_changelog(changelog_dir)
    with closing(sqlite3.connect(f"{database_path.as_uri()}?mode=ro", uri=True)) as connection:
        applied = _applied_keys(connection)
    known = {changeset.key for changeset in changesets}
    return ChangelogStatus(
        pending=[changeset for changeset in changesets if changeset.key not in applied],
        unknown=sorted(key[0] for key in applied - known),
    )


def _applied_keys(connection: sqlite3.Connection) -> set[tuple[str, str, str]]:
    exists = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'DATABASECHANGELOG'"
    ).fetchone()
    if not exists:
        return set()
    return {
        (row[0], row[1], row[2])
        for row in connection.execute("SELECT ID, AUTHOR, FILENAME FROM DATABASECHANGELOG")
    }


def migrate(database_path: Path, changelog_dir: Path, *, backups_dir: Path) -> MigrationResult:
    """Apply pending changesets, each in its own transaction.

    An existing database is first copied to ``backups_dir``; a failing
    changeset is rolled back and stops the run, leaving earlier ones applied.
    """
    changesets = read_changelog(changelog_dir)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    existed = database_path.is_file()

    with closing(sqlite3.connect(database_path, isolation_level=None)) as connection:
        applied = _applied_keys(connection)
        known = {changeset.key for changeset in changesets}
        unknown = sorted(key[0] for key in applied - known)
        if unknown:
            raise MigrationError(
                "Il database è stato aggiornato da una versione più recente di Arsis "
                f"(changeset sconosciuti: {', '.join(unknown)})"
            )
        pending = [changeset for changeset in changesets if changeset.key not in applied]
        if not pending:
            return MigrationResult(applied=[], backup=None)

        backup = None
        if existed and applied:
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = backup_database(
                backups_dir / f"pre-migrazione-{stamp}.db", database_path=database_path
            )

        connection.execute(_CHANGELOG_DDL)
        connection.execute(_LOCK_DDL)
        connection.execute("INSERT OR IGNORE INTO DATABASECHANGELOGLOCK (ID, LOCKED) VALUES (1, 0)")
        locked = connection.execute(
            "UPDATE DATABASECHANGELOGLOCK SET LOCKED = 1, LOCKGRANTED = ?, LOCKEDBY = ? "
            "WHERE ID = 1 AND LOCKED = 0",
            (_now(), TOOL_NAME),
        ).rowcount
        if not locked:
            raise MigrationError("Un'altra migrazione è in corso (DATABASECHANGELOGLOCK bloccato)")
        try:
            done = [_apply(connection, changeset) for changeset in pending]
        finally:
            connection.execute(
                "UPDATE DATABASECHANGELOGLOCK SET LOCKED = 0, LOCKGRANTED = NULL, "
                "LOCKEDBY = NULL WHERE ID = 1"
            )
        return MigrationResult(applied=done, backup=backup)


def _apply(connection: sqlite3.Connection, changeset: Changeset) -> str:
    connection.execute("BEGIN")
    try:
        for statement in _statements(changeset.sql):
            connection.execute(statement)
        order = connection.execute(
            "SELECT COALESCE(MAX(ORDEREXECUTED), 0) + 1 FROM DATABASECHANGELOG"
        ).fetchone()[0]
        connection.execute(
            "INSERT INTO DATABASECHANGELOG (ID, AUTHOR, FILENAME, DATEEXECUTED, ORDEREXECUTED, "
            "EXECTYPE, MD5SUM, DESCRIPTION, COMMENTS, LIQUIBASE, DEPLOYMENT_ID) "
            "VALUES (?, ?, ?, ?, ?, 'EXECUTED', NULL, 'sql', ?, ?, ?)",
            (
                changeset.id,
                changeset.author,
                changeset.filename,
                _now(),
                order,
                changeset.comment,
                TOOL_NAME,
                str(int(time.time()))[-10:],
            ),
        )
        connection.execute("COMMIT")
    except sqlite3.Error as exc:
        connection.execute("ROLLBACK")
        raise MigrationError(f"Changeset {changeset.id} non applicato: {exc}") from exc
    except MigrationError:
        connection.execute("ROLLBACK")
        raise
    return changeset.id


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
