"""Consistent backup and restore helpers for the local SQLite database."""

import os
import sqlite3
from contextlib import closing
from pathlib import Path
from uuid import uuid4

from arsis.core.config import get_settings


class DatabaseBackupError(RuntimeError):
    """Raised when a database backup or restore cannot be completed safely."""


def _resolved_database_path(database_path: Path | None) -> Path:
    path = database_path or get_settings().database_path
    return path.expanduser().resolve()


def _temporary_path(target: Path) -> Path:
    return target.with_name(f".{target.name}.{uuid4().hex}.tmp")


def _sqlite_uri(path: Path, *, read_only: bool) -> str:
    mode = "ro" if read_only else "rwc"
    return f"{path.as_uri()}?mode={mode}"


def _check_integrity(connection: sqlite3.Connection) -> None:
    result = connection.execute("PRAGMA integrity_check").fetchone()
    if result is None or result[0] != "ok":
        detail = "nessun risultato" if result is None else str(result[0])
        raise DatabaseBackupError(f"Controllo integrita SQLite fallito: {detail}")


def backup_database(destination: Path, *, database_path: Path | None = None) -> Path:
    """Export a transactionally consistent SQLite snapshot to ``destination``.

    SQLite's online backup API is used instead of copying the database file, so
    committed data in the WAL is included while the application is running.
    The destination is replaced only after the snapshot passes an integrity
    check.
    """

    source = _resolved_database_path(database_path)
    target = destination.expanduser().resolve()
    if not source.is_file():
        raise DatabaseBackupError(f"Database SQLite non trovato: {source}")
    if source == target:
        raise DatabaseBackupError("Il backup non puo sovrascrivere il database attivo")

    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = _temporary_path(target)
    try:
        with closing(
            sqlite3.connect(_sqlite_uri(source, read_only=True), uri=True)
        ) as source_connection, closing(sqlite3.connect(temporary)) as backup_connection:
            source_connection.backup(backup_connection)
            _check_integrity(backup_connection)
        os.replace(temporary, target)
    except (OSError, sqlite3.Error) as exc:
        raise DatabaseBackupError(f"Impossibile creare il backup SQLite: {exc}") from exc
    finally:
        temporary.unlink(missing_ok=True)

    return target


def restore_database(backup: Path, *, database_path: Path | None = None) -> Path:
    """Validate and atomically restore an exported SQLite database.

    The caller must stop writes and dispose active SQLAlchemy connections before
    invoking this function. The current database is untouched if validation or
    import fails.
    """

    source = backup.expanduser().resolve()
    target = _resolved_database_path(database_path)
    if not source.is_file():
        raise DatabaseBackupError(f"File di backup non trovato: {source}")
    if source == target:
        raise DatabaseBackupError("Il file da importare coincide con il database attivo")

    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = _temporary_path(target)
    try:
        with closing(
            sqlite3.connect(_sqlite_uri(source, read_only=True), uri=True)
        ) as backup_connection, closing(sqlite3.connect(temporary)) as restored_connection:
            _check_integrity(backup_connection)
            backup_connection.backup(restored_connection)
            _check_integrity(restored_connection)
        os.replace(temporary, target)
    except (OSError, sqlite3.Error) as exc:
        raise DatabaseBackupError(f"Impossibile ripristinare il backup SQLite: {exc}") from exc
    finally:
        temporary.unlink(missing_ok=True)

    return target
