from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from arsis.core.errors import ConflictError, ResourceNotFoundError, StaleVersionError
from arsis.generated.models import AuditEvent, Base, User
from arsis.generated.schemas import (
    PersonCreateDTO,
    PersonRoleCreateDTO,
    PersonUpdateDTO,
)
from arsis.people.service import PeopleService


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as database_session:
        actor = User(
            email="responsabile@example.it",
            password_hash="hash",
            display_name="Responsabile",
        )
        database_session.add(actor)
        database_session.commit()
        yield database_session
    engine.dispose()


def test_people_lifecycle_search_and_audit(session: Session) -> None:
    service = PeopleService()
    person = service.create_person(
        session,
        data=PersonCreateDTO(
            first_name="Maria", last_name="Rossi", email="maria@example.it"
        ),
        actor_id=1,
    )

    assert person.id == 1
    person_id = person.id
    assert [item.id for item in service.list_people(session, search="ross")] == [person_id]
    session.rollback()

    updated = service.update_person(
        session,
        person_id=person_id,
        data=PersonUpdateDTO(phone="3331234567"),
        expected_version=1,
        actor_id=1,
    )
    assert (updated.phone, updated.version, updated.updated_by) == ("3331234567", 2, 1)
    with pytest.raises(StaleVersionError):
        service.update_person(
            session,
            person_id=person_id,
            data=PersonUpdateDTO(phone="3337654321"),
            expected_version=1,
            actor_id=1,
        )

    archived = service.archive_person(
        session, person_id=person_id, expected_version=2, actor_id=1
    )
    assert archived.archived_by == 1
    assert service.list_people(session) == []
    assert service.list_people(session, include_archived=True) == [archived]
    assert session.scalars(select(AuditEvent.action).order_by(AuditEvent.id)).all() == [
        "person.created",
        "person.updated",
        "person.archived",
    ]


def test_person_role_lifecycle_and_optimistic_locking(session: Session) -> None:
    service = PeopleService()
    person = service.create_person(
        session,
        data=PersonCreateDTO(first_name="Luca", last_name="Bianchi"),
        actor_id=1,
    )
    role = service.create_role(
        session,
        data=PersonRoleCreateDTO(
            person_id=person.id,
            role_type="teacher",
            start_date="2026-01-01",
        ),
        actor_id=1,
    )
    person_id = person.id
    role_id = role.id
    assert role.id == 1
    assert role.status == "active"

    with pytest.raises(ConflictError, match="già questo ruolo"):
        service.create_role(
            session,
            data=PersonRoleCreateDTO(
                person_id=person_id,
                role_type="teacher",
                start_date="2026-01-01",
            ),
            actor_id=1,
        )
    session.rollback()

    archived = service.archive_role(
        session, role_id=role_id, expected_version=1, actor_id=1
    )
    assert archived.archived_at is not None
    assert service.list_roles(session, person_id=person_id) == []
    session.rollback()

    with pytest.raises(ResourceNotFoundError):
        service.archive_role(session, role_id=role_id, expected_version=1, actor_id=1)
    with pytest.raises(ResourceNotFoundError):
        service.get_person(session, 999)
