"""Bring the SQLite database up to date with the bundled changelog."""

import argparse
from collections.abc import Sequence
from pathlib import Path

from arsis.core.config import get_settings
from arsis.core.migrations import MigrationError, MigrationResult, migrate


def run_migrations(database_path: Path | None = None) -> MigrationResult:
    settings = get_settings()
    return migrate(
        database_path or settings.database_path,
        settings.changelog_dir,
        backups_dir=settings.backups_dir,
    )


def main(arguments: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, help="File SQLite, predefinito quello dei dati")
    options = parser.parse_args(arguments)
    try:
        result = run_migrations(options.database)
    except MigrationError as exception:
        raise SystemExit(f"Migrazione non riuscita: {exception}") from exception
    if result.backup:
        print(f"Backup precedente alla migrazione: {result.backup}")
    print(
        f"Changeset applicati: {', '.join(result.applied)}"
        if result.applied
        else "Database già aggiornato."
    )


if __name__ == "__main__":
    main()
