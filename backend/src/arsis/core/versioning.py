"""Atomic optimistic-lock updates for generated SQLAlchemy tables."""

from collections.abc import Mapping
from typing import Any, cast

from sqlalchemy import Table, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session
from sqlalchemy.sql import FromClause

from arsis.core.errors import ResourceNotFoundError, StaleVersionError
from arsis.core.time import utc_now_iso


def update_versioned(
    session: Session,
    table: FromClause,
    *,
    resource_name: str,
    resource_id: int,
    expected_version: int,
    values: Mapping[str, Any],
) -> int:
    """Update a record only when ``expected_version`` still matches."""

    if expected_version < 1:
        raise ValueError("expected_version deve essere almeno 1")
    if "id" not in table.c or "version" not in table.c:
        raise ValueError("La tabella deve avere colonne id e version")
    if "id" in values or "version" in values:
        raise ValueError("id e version non possono essere aggiornati direttamente")

    update_values = dict(values)
    update_values["version"] = expected_version + 1
    if "updated_at" in table.c:
        update_values["updated_at"] = utc_now_iso()

    result = cast(
        CursorResult[Any],
        session.execute(
            update(cast(Table, table))
            .where(table.c.id == resource_id, table.c.version == expected_version)
            .values(**update_values)
        ),
    )
    if result.rowcount == 1:
        return expected_version + 1

    current_version = session.execute(
        select(table.c.version).where(table.c.id == resource_id)
    ).scalar_one_or_none()
    if current_version is None:
        raise ResourceNotFoundError(resource_name, resource_id)
    raise StaleVersionError(
        expected_version=expected_version,
        current_version=int(current_version),
    )
