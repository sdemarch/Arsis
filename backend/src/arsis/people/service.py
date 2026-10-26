"""Business operations for people and their roles."""

from collections.abc import Sequence

from sqlalchemy.orm import Session

from arsis.audit.service import record_audit_event
from arsis.core.database import transaction
from arsis.core.errors import ConflictError, ResourceNotFoundError
from arsis.core.time import utc_now_iso
from arsis.core.versioning import update_versioned
from arsis.generated.models import Person, PersonRole
from arsis.generated.schemas import (
    PersonCreateDTO,
    PersonRoleCreateDTO,
    PersonRoleUpdateDTO,
    PersonUpdateDTO,
)
from arsis.people.repository import PeopleRepository

_ROLE_TYPES = {"member", "musician", "student", "teacher"}
_ROLE_STATUSES = {"active", "inactive"}


class PeopleService:
    def __init__(self, repository: PeopleRepository | None = None) -> None:
        self._repository = repository or PeopleRepository()

    def list_people(
        self,
        session: Session,
        *,
        search: str | None = None,
        include_archived: bool = False,
    ) -> Sequence[Person]:
        return self._repository.list_people(
            session, search=search, include_archived=include_archived
        )

    def get_person(self, session: Session, person_id: int) -> Person:
        person = self._repository.get_person(session, person_id)
        if person is None:
            raise ResourceNotFoundError("Persona", person_id)
        return person

    def create_person(
        self, session: Session, *, data: PersonCreateDTO, actor_id: int
    ) -> Person:
        with transaction(session):
            person = self._repository.add_person(
                session,
                Person(
                    **data.model_dump(),
                    created_by=actor_id,
                    updated_by=actor_id,
                ),
            )
            session.flush()
            record_audit_event(
                session,
                action="person.created",
                entity_type="person",
                entity_id=person.id,
                user_id=actor_id,
            )
        return person

    def update_person(
        self,
        session: Session,
        *,
        person_id: int,
        data: PersonUpdateDTO,
        expected_version: int,
        actor_id: int,
    ) -> Person:
        values = data.model_dump(exclude_unset=True)
        with transaction(session):
            self.get_person(session, person_id)
            if values:
                values["updated_by"] = actor_id
                update_versioned(
                    session,
                    Person.__table__,
                    resource_name="Persona",
                    resource_id=person_id,
                    expected_version=expected_version,
                    values=values,
                )
                record_audit_event(
                    session,
                    action="person.updated",
                    entity_type="person",
                    entity_id=person_id,
                    user_id=actor_id,
                    details={"fields": sorted(values)},
                )
            session.flush()
            session.expire_all()
            person = self._repository.get_person(session, person_id)
            assert person is not None
        return person

    def archive_person(
        self, session: Session, *, person_id: int, expected_version: int, actor_id: int
    ) -> Person:
        with transaction(session):
            self.get_person(session, person_id)
            update_versioned(
                session,
                Person.__table__,
                resource_name="Persona",
                resource_id=person_id,
                expected_version=expected_version,
                values={
                    "archived_at": utc_now_iso(),
                    "archived_by": actor_id,
                    "updated_by": actor_id,
                },
            )
            record_audit_event(
                session,
                action="person.archived",
                entity_type="person",
                entity_id=person_id,
                user_id=actor_id,
            )
            session.flush()
            session.expire_all()
            person = self._repository.get_person(
                session, person_id, include_archived=True
            )
            assert person is not None
        return person

    def list_roles(
        self, session: Session, *, person_id: int, include_archived: bool = False
    ) -> Sequence[PersonRole]:
        self.get_person(session, person_id)
        return self._repository.list_roles(
            session, person_id=person_id, include_archived=include_archived
        )

    def create_role(
        self, session: Session, *, data: PersonRoleCreateDTO, actor_id: int
    ) -> PersonRole:
        status = data.status or "active"
        self._validate_role_values(data.role_type, status, data.start_date, data.end_date)
        with transaction(session):
            self.get_person(session, data.person_id)
            if status == "active" and data.end_date is None and self._repository.has_active_role(
                session, person_id=data.person_id, role_type=data.role_type
            ):
                raise ConflictError(
                    "La persona ha già questo ruolo attivo", code="ACTIVE_ROLE_EXISTS"
                )
            role = self._repository.add_role(
                session,
                PersonRole(
                    **data.model_dump(exclude={"status"}),
                    status=status,
                    created_by=actor_id,
                    updated_by=actor_id,
                ),
            )
            session.flush()
            record_audit_event(
                session,
                action="person_role.created",
                entity_type="person_role",
                entity_id=role.id,
                user_id=actor_id,
            )
        return role

    def update_role(
        self,
        session: Session,
        *,
        role_id: int,
        data: PersonRoleUpdateDTO,
        expected_version: int,
        actor_id: int,
    ) -> PersonRole:
        values = data.model_dump(exclude_unset=True)
        with transaction(session):
            role = self._repository.get_role(session, role_id)
            if role is None:
                raise ResourceNotFoundError("Ruolo persona", role_id)
            self._validate_role_values(
                str(values.get("role_type", role.role_type)),
                str(values.get("status", role.status)),
                str(values.get("start_date", role.start_date)),
                values.get("end_date", role.end_date),
            )
            if values:
                values["updated_by"] = actor_id
                update_versioned(
                    session,
                    PersonRole.__table__,
                    resource_name="Ruolo persona",
                    resource_id=role_id,
                    expected_version=expected_version,
                    values=values,
                )
                record_audit_event(
                    session,
                    action="person_role.updated",
                    entity_type="person_role",
                    entity_id=role_id,
                    user_id=actor_id,
                    details={"fields": sorted(values)},
                )
            session.flush()
            session.expire_all()
            updated = self._repository.get_role(session, role_id)
            assert updated is not None
        return updated

    def archive_role(
        self, session: Session, *, role_id: int, expected_version: int, actor_id: int
    ) -> PersonRole:
        with transaction(session):
            role = self._repository.get_role(session, role_id)
            if role is None:
                raise ResourceNotFoundError("Ruolo persona", role_id)
            update_versioned(
                session,
                PersonRole.__table__,
                resource_name="Ruolo persona",
                resource_id=role_id,
                expected_version=expected_version,
                values={
                    "archived_at": utc_now_iso(),
                    "archived_by": actor_id,
                    "updated_by": actor_id,
                },
            )
            record_audit_event(
                session,
                action="person_role.archived",
                entity_type="person_role",
                entity_id=role_id,
                user_id=actor_id,
            )
            session.flush()
            session.expire_all()
            archived = self._repository.get_role(session, role_id, include_archived=True)
            assert archived is not None
        return archived

    @staticmethod
    def _validate_role_values(
        role_type: str, status: str | None, start_date: str, end_date: str | None
    ) -> None:
        if role_type not in _ROLE_TYPES:
            raise ValueError("Tipo ruolo non valido")
        if status is not None and status not in _ROLE_STATUSES:
            raise ValueError("Stato ruolo non valido")
        if end_date is not None and end_date < start_date:
            raise ValueError("La data di fine non può precedere la data di inizio")
