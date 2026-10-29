"""Portable, versioned application saves for a local Arsis installation."""

import hashlib
import json
import os
import sqlite3
import tempfile
import zipfile
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any
from uuid import uuid4

from arsis.core.database_backup import DatabaseBackupError, backup_database, restore_database

SAVE_FORMAT = "arsis-save"
SAVE_FORMAT_VERSION = 1
_DATABASE_MEMBER = "database.sqlite"
_MANIFEST_MEMBER = "manifest.json"


class SaveError(RuntimeError):
    """Raised when a portable save cannot be exported, validated, or restored."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_member(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise SaveError("Il salvataggio contiene un percorso non sicuro")
    return path


def _manifest(database_snapshot: Path, attachment_count: int) -> dict[str, Any]:
    return {
        "format": SAVE_FORMAT,
        "format_version": SAVE_FORMAT_VERSION,
        "created_at": datetime.now(UTC).isoformat(),
        "database": {"member": _DATABASE_MEMBER, "sha256": _sha256(database_snapshot)},
        "attachments": {"directory": "attachments", "count": attachment_count},
    }


def create_save(
    destination: Path,
    *,
    database_path: Path,
    attachments_dir: Path | None = None,
) -> Path:
    """Create an atomic `.arsis-save` archive from a consistent SQLite snapshot."""

    target = destination.expanduser().resolve()
    if target.suffix != ".arsis-save":
        raise SaveError("Il salvataggio deve usare l'estensione .arsis-save")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_archive = target.with_name(f".{target.name}.{uuid4().hex}.tmp")
    with tempfile.TemporaryDirectory(prefix="arsis-save-") as temporary_directory:
        snapshot = Path(temporary_directory) / _DATABASE_MEMBER
        try:
            backup_database(snapshot, database_path=database_path)
        except DatabaseBackupError as exc:
            raise SaveError(str(exc)) from exc

        attachment_root = attachments_dir.expanduser().resolve() if attachments_dir else None
        attachment_files = (
            [path for path in attachment_root.rglob("*") if path.is_file()]
            if attachment_root and attachment_root.is_dir()
            else []
        )
        try:
            with zipfile.ZipFile(
                temporary_archive, "w", compression=zipfile.ZIP_DEFLATED
            ) as archive:
                archive.writestr(
                    _MANIFEST_MEMBER, json.dumps(_manifest(snapshot, len(attachment_files)))
                )
                archive.write(snapshot, _DATABASE_MEMBER)
                if attachment_root is not None:
                    for file_path in attachment_files:
                        archive.write(
                            file_path,
                            PurePosixPath("attachments")
                            / file_path.relative_to(attachment_root),
                        )
            os.replace(temporary_archive, target)
        except OSError as exc:
            raise SaveError(f"Impossibile creare il salvataggio: {exc}") from exc
        finally:
            temporary_archive.unlink(missing_ok=True)
    return target


def inspect_save(source: Path) -> dict[str, Any]:
    """Validate an archive and return its manifest without changing local state."""

    archive_path = source.expanduser().resolve()
    if not archive_path.is_file():
        raise SaveError(f"File di salvataggio non trovato: {archive_path}")
    try:
        with zipfile.ZipFile(archive_path) as archive:
            members = {member.filename: member for member in archive.infolist()}
            for name in members:
                _safe_member(name)
            if _MANIFEST_MEMBER not in members or _DATABASE_MEMBER not in members:
                raise SaveError("Il salvataggio non contiene manifest e database richiesti")
            manifest = json.loads(archive.read(_MANIFEST_MEMBER))
            if not isinstance(manifest, dict) or manifest.get("format") != SAVE_FORMAT:
                raise SaveError("Formato del salvataggio non riconosciuto")
            if manifest.get("format_version") != SAVE_FORMAT_VERSION:
                raise SaveError("Versione del formato di salvataggio non supportata")
            with tempfile.TemporaryDirectory(prefix="arsis-inspect-") as temporary_directory:
                database_snapshot = Path(temporary_directory) / _DATABASE_MEMBER
                database_snapshot.write_bytes(archive.read(_DATABASE_MEMBER))
                expected_hash = manifest.get("database", {}).get("sha256")
                if expected_hash != _sha256(database_snapshot):
                    raise SaveError("Il checksum del database nel salvataggio non corrisponde")
                with closing(sqlite3.connect(database_snapshot)) as connection:
                    result = connection.execute("PRAGMA integrity_check").fetchone()
                    if result is None or result[0] != "ok":
                        raise SaveError(
                            "Il database nel salvataggio non supera il controllo di integrita"
                        )
            return manifest
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        raise SaveError(f"Salvataggio non valido: {exc}") from exc


def restore_save(
    source: Path,
    *,
    database_path: Path,
    attachments_dir: Path | None = None,
) -> Path:
    """Restore a validated save after the caller has stopped all application writes."""

    inspect_save(source)
    with tempfile.TemporaryDirectory(prefix="arsis-restore-") as temporary_directory:
        temporary_root = Path(temporary_directory)
        with zipfile.ZipFile(source) as archive:
            snapshot = temporary_root / _DATABASE_MEMBER
            snapshot.write_bytes(archive.read(_DATABASE_MEMBER))
            staged_attachments = temporary_root / "attachments"
            for member in archive.infolist():
                relative = _safe_member(member.filename)
                if relative.parts[0] == "attachments" and not member.is_dir():
                    target = staged_attachments.joinpath(*relative.parts[1:])
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.read(member))
        try:
            restored = restore_database(snapshot, database_path=database_path)
        except DatabaseBackupError as exc:
            raise SaveError(str(exc)) from exc
        if attachments_dir is not None:
            attachment_root = attachments_dir.expanduser().resolve()
            replacement = attachment_root.with_name(f".{attachment_root.name}.{uuid4().hex}.tmp")
            if staged_attachments.exists():
                os.replace(staged_attachments, replacement)
            else:
                replacement.mkdir(parents=True, exist_ok=True)
            previous = attachment_root.with_name(f".{attachment_root.name}.{uuid4().hex}.previous")
            try:
                if attachment_root.exists():
                    os.replace(attachment_root, previous)
                os.replace(replacement, attachment_root)
            finally:
                if replacement.exists():
                    os.replace(replacement, attachment_root)
        return restored
