import json
from contextlib import closing
from datetime import UTC, datetime

import pytest
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, insert, select
from sqlalchemy.orm import Session

from arsis.audit.service import record_audit_event
from arsis.core.api_models import (
    PaginationParams,
    SortDirection,
    build_page,
    parse_sort,
)
from arsis.core.database import transaction
from arsis.core.errors import InvalidSortError, ResourceNotFoundError, StaleVersionError
from arsis.core.time import to_iso8601
from arsis.core.versioning import update_versioned
from arsis.generated.models import AuditEvent


def test_page_metadata_and_offset() -> None:
    params = PaginationParams(page=2, page_size=25)

    page = build_page(["item"], total_items=51, params=params)

    assert params.offset == 25
    assert page.model_dump() == {
        "items": ["item"],
        "meta": {"page": 2, "page_size": 25, "total_items": 51, "total_pages": 3},
    }


def test_sort_parser_accepts_direction_and_rejects_unknown_fields() -> None:
    allowed = {"name", "updated_at"}

    assert parse_sort(
        "-updated_at", allowed_fields=allowed, default_field="name"
    ).model_dump() == {"field": "updated_at", "direction": SortDirection.DESC}

    with pytest.raises(InvalidSortError) as error:
        parse_sort("email", allowed_fields=allowed, default_field="name")
    assert error.value.code == "INVALID_SORT"


def test_timestamps_are_normalized_to_utc() -> None:
    value = datetime.fromisoformat("2026-10-16T12:30:00+02:00")

    assert to_iso8601(value) == "2026-10-16T10:30:00Z"
    assert to_iso8601(datetime(2026, 10, 16, 10, 30, tzinfo=UTC)).endswith("Z")
    with pytest.raises(ValueError, match="fuso orario"):
        to_iso8601(datetime(2026, 10, 16, 10, 30))


def _versioned_table() -> tuple[Session, Table]:
    engine = create_engine("sqlite:///:memory:")
    metadata = MetaData()
    table = Table(
        "records",
        metadata,
        Column("id", String, primary_key=True),
        Column("name", String, nullable=False),
        Column("version", Integer, nullable=False),
        Column("updated_at", String, nullable=False),
    )
    metadata.create_all(engine)
    session = Session(engine)
    session.execute(
        insert(table).values(id="record-1", name="Prima", version=1, updated_at="initial")
    )
    session.commit()
    return session, table


def test_versioned_update_is_atomic() -> None:
    session, table = _versioned_table()
    with closing(session):
        new_version = update_versioned(
            session,
            table,
            resource_name="Record",
            resource_id="record-1",
            expected_version=1,
            values={"name": "Dopo"},
        )
        row = session.execute(select(table).where(table.c.id == "record-1")).one()

    assert new_version == 2
    assert row.name == "Dopo"
    assert row.version == 2
    assert row.updated_at.endswith("Z")


def test_versioned_update_distinguishes_stale_and_missing_records() -> None:
    session, table = _versioned_table()
    with closing(session):
        with pytest.raises(StaleVersionError) as stale:
            update_versioned(
                session,
                table,
                resource_name="Record",
                resource_id="record-1",
                expected_version=2,
                values={"name": "Conflitto"},
            )
        assert stale.value.details == {"expected_version": 2, "current_version": 1}

        with pytest.raises(ResourceNotFoundError):
            update_versioned(
                session,
                table,
                resource_name="Record",
                resource_id="missing",
                expected_version=1,
                values={"name": "Assente"},
            )


def test_service_transaction_commits_or_rolls_back_as_a_unit() -> None:
    engine = create_engine("sqlite:///:memory:")
    metadata = MetaData()
    table = Table(
        "entries",
        metadata,
        Column("id", String, primary_key=True),
    )
    metadata.create_all(engine)

    with Session(engine) as session:
        with transaction(session):
            session.execute(insert(table).values(id="committed"))

        with pytest.raises(RuntimeError, match="rollback"):
            with transaction(session):
                session.execute(insert(table).values(id="rolled-back"))
                raise RuntimeError("rollback")

        assert session.execute(select(table.c.id)).scalars().all() == ["committed"]


def test_audit_event_is_added_to_the_callers_transaction() -> None:
    engine = create_engine("sqlite:///:memory:")
    AuditEvent.__table__.create(engine)
    with Session(engine) as session, session.begin():
        event = record_audit_event(
            session,
            action="person.updated",
            entity_type="person",
            entity_id="person-1",
            details={"fields": ["email"]},
            request_id="request-audit",
        )
        session.flush()

        stored = session.get(AuditEvent, event.id)
        assert stored is not None
        assert stored.request_id == "request-audit"
        assert json.loads(stored.details) == {"fields": ["email"]}
