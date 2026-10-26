"""Persistence operations for the people registry."""

from collections.abc import Sequence

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from arsis.generated.models import Person, PersonRole


class PeopleRepository:
    """Thin SQLAlchemy repository; transaction ownership stays in the service."""

    def get_person(
        self, session: Session, person_id: int, *, include_archived: bool = False
    ) -> Person | None:
        statement = select(Person).where(Person.id == person_id)
        if not include_archived:
            statement = statement.where(Person.archived_at.is_(None))
        return session.scalar(statement)

    def list_people(
        self,
        session: Session,
        *,
        search: str | None = None,
        include_archived: bool = False,
    ) -> Sequence[Person]:
        statement: Select[tuple[Person]] = select(Person)
        if not include_archived:
            statement = statement.where(Person.archived_at.is_(None))
        if search and (query := search.strip()):
            pattern = f"%{query.casefold()}%"
            statement = statement.where(
                or_(
                    func.lower(Person.first_name).like(pattern),
                    func.lower(Person.last_name).like(pattern),
                    func.lower(Person.email).like(pattern),
                    func.lower(Person.tax_code).like(pattern),
                )
            )
        statement = statement.order_by(
            func.lower(Person.last_name), func.lower(Person.first_name), Person.id
        )
        return session.scalars(statement).all()

    def add_person(self, session: Session, person: Person) -> Person:
        session.add(person)
        return person

    def get_role(
        self, session: Session, role_id: int, *, include_archived: bool = False
    ) -> PersonRole | None:
        statement = select(PersonRole).where(PersonRole.id == role_id)
        if not include_archived:
            statement = statement.where(PersonRole.archived_at.is_(None))
        return session.scalar(statement)

    def list_roles(
        self,
        session: Session,
        *,
        person_id: int,
        include_archived: bool = False,
    ) -> Sequence[PersonRole]:
        statement = select(PersonRole).where(PersonRole.person_id == person_id)
        if not include_archived:
            statement = statement.where(PersonRole.archived_at.is_(None))
        return session.scalars(statement.order_by(PersonRole.start_date, PersonRole.id)).all()

    def has_active_role(
        self, session: Session, *, person_id: int, role_type: str
    ) -> bool:
        statement = select(PersonRole.id).where(
            PersonRole.person_id == person_id,
            PersonRole.role_type == role_type,
            PersonRole.status == "active",
            PersonRole.end_date.is_(None),
            PersonRole.archived_at.is_(None),
        )
        return session.scalar(statement) is not None

    def add_role(self, session: Session, role: PersonRole) -> PersonRole:
        session.add(role)
        return role
