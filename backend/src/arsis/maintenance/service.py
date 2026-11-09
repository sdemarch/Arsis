"""Export and import of portable `.arsis-save` files from the running application."""

import json
import logging
import sqlite3
import tempfile
from contextlib import closing
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from arsis.core.config import Settings
from arsis.core.database import dispose_database_engine
from arsis.core.errors import DomainError
from arsis.core.maintenance import MaintenanceGate
from arsis.core.migrations import MigrationError, changelog_status, migrate
from arsis.core.saves import (
    SaveError,
    create_save,
    extract_save_database,
    inspect_save,
    restore_save,
)
from arsis.maintenance.schemas import SaveContents, SaveImportResult, SaveSummary

logger = logging.getLogger(__name__)


class InvalidSaveError(DomainError):
    def __init__(self, message: str, *, code: str = "INVALID_SAVE") -> None:
        super().__init__(code=code, message=message, status_code=422)


def save_file_name(now: datetime) -> str:
    return f"arsis-{now:%Y%m%d-%H%M}.arsis-save"


def staging_dir(settings: Settings) -> Path:
    """Scratch space on the data volume, so large files are never copied across disks."""
    path = settings.data_dir / "tmp"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _count(connection: sqlite3.Connection, table: str) -> int:
    try:
        row = connection.execute(
            f"SELECT COUNT(*) FROM {table} WHERE archived_at IS NULL"
        ).fetchone()
    except sqlite3.OperationalError:  # table not yet present in an older save
        return 0
    return int(row[0])


def _organization_name(connection: sqlite3.Connection) -> str | None:
    try:
        row = connection.execute(
            "SELECT value FROM app_settings WHERE key = 'organization.name'"
        ).fetchone()
        value = json.loads(row[0]) if row else None
    except sqlite3.OperationalError, ValueError:
        return None
    return value.strip() or None if isinstance(value, str) else None


class SaveService:
    def __init__(self, gate: MaintenanceGate) -> None:
        self._gate = gate

    def export(self, settings: Settings) -> Path:
        """A consistent save of the live data; the caller deletes the file once sent."""
        try:
            return create_save(
                staging_dir(settings) / f"export-{uuid4().hex}.arsis-save",
                database_path=settings.database_path,
                attachments_dir=settings.attachments_dir,
            )
        except SaveError as exception:
            raise DomainError(
                code="SAVE_EXPORT_FAILED", message=str(exception), status_code=500
            ) from exception

    def describe(self, source: Path, settings: Settings) -> SaveSummary:
        """Validate a save and tell what it holds, without touching the live data."""
        try:
            manifest = inspect_save(source)
        except SaveError as exception:
            raise InvalidSaveError(str(exception)) from exception
        with tempfile.TemporaryDirectory(dir=staging_dir(settings)) as directory:
            database = extract_save_database(source, Path(directory) / "database.sqlite")
            with closing(sqlite3.connect(f"{database.as_uri()}?mode=ro", uri=True)) as connection:
                is_arsis = connection.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' "
                    "AND name IN ('DATABASECHANGELOG', 'users', 'people')"
                ).fetchone()[0]
                if is_arsis != 3:
                    raise InvalidSaveError("Il file non contiene un database Arsis")
                contents = SaveContents(
                    people=_count(connection, "people"),
                    activities=_count(connection, "activities"),
                    courses=_count(connection, "courses"),
                    accounting_movements=_count(connection, "accounting_movements"),
                    responsible_users=_count(connection, "users"),
                    attachments=int(manifest.get("attachments", {}).get("count", 0)),
                )
                organization_name = _organization_name(connection)
            status = changelog_status(database, settings.changelog_dir)
        if status.unknown:
            raise InvalidSaveError(
                "Il salvataggio proviene da una versione più recente di Arsis: "
                "aggiornare l'applicazione prima di importarlo",
                code="SAVE_FROM_NEWER_VERSION",
            )
        return SaveSummary(
            created_at=manifest["created_at"],
            organization_name=organization_name,
            contents=contents,
            pending_migrations=len(status.pending),
        )

    def import_save(self, source: Path, settings: Settings) -> SaveImportResult:
        """Replace all local data with ``source``, keeping a save of what it replaces.

        The caller must hold no database session: the engine is disposed while
        the file is swapped and recreated on the next request.
        """
        summary = self.describe(source, settings)
        with self._gate.exclusive():
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            try:
                backup = create_save(
                    settings.backups_dir / f"pre-import-{stamp}.arsis-save",
                    database_path=settings.database_path,
                    attachments_dir=settings.attachments_dir,
                )
            except SaveError as exception:
                raise DomainError(
                    code="SAVE_BACKUP_FAILED",
                    message=f"Copia di sicurezza non riuscita, nessun dato modificato: {exception}",
                    status_code=500,
                ) from exception
            dispose_database_engine()
            _fold_write_ahead_log(settings.database_path)
            try:
                restore_save(
                    source,
                    database_path=settings.database_path,
                    attachments_dir=settings.attachments_dir,
                )
                applied = migrate(
                    settings.database_path, settings.changelog_dir, backups_dir=settings.backups_dir
                ).applied
            except (SaveError, MigrationError) as exception:
                logger.exception("Import del salvataggio fallito, ripristino dei dati precedenti")
                restore_save(
                    backup,
                    database_path=settings.database_path,
                    attachments_dir=settings.attachments_dir,
                )
                raise InvalidSaveError(
                    f"Importazione non riuscita, dati precedenti ripristinati: {exception}",
                    code="SAVE_IMPORT_FAILED",
                ) from exception
            # Sessions and tokens of the replaced data must not carry over.
            self._gate.revoke_tokens()
        logger.info("Salvataggio importato; dati precedenti in %s", backup)
        return SaveImportResult(
            summary=summary, backup_file=backup.name, applied_migrations=list(applied)
        )


def _fold_write_ahead_log(database_path: Path) -> None:
    """Checkpoint and drop the WAL, so no stale log is replayed over the new file."""
    if not database_path.is_file():
        return
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute("PRAGMA journal_mode=DELETE")
