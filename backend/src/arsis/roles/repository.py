"""Persistence for the catalogue of person roles (RB-21)."""

from collections.abc import Sequence

from sqlalchemy import event, func, or_, select, text
from sqlalchemy.orm import Session

from arsis.generated.models import AccountingCategory, PersonRole, RoleType

# The built-in roles, seeded by changeset 0013. Their codes drive behaviour elsewhere
# (courses, enrollments, instruments, member data) and never change.
SYSTEM_ROLES: tuple[tuple[str, str, str, str, int], ...] = (
    ("member", "Socio", "Soci", "Iscritto all'associazione, con tessera e quota.", 10),
    ("musician", "Musicante", "Musicanti", "Suona nella banda, con strumenti e sezione.", 20),
    ("student", "Allievo", "Allievi", "Iscritto ai corsi della scuola.", 30),
    ("teacher", "Insegnante", "Insegnanti", "Tiene corsi e lezioni della scuola.", 40),
)


@event.listens_for(RoleType.__table__, "after_create")
def _seed_system_roles(target: object, connection: object, **_: object) -> None:
    """Seed built-in roles when the table comes from ``create_all`` (tests only).

    Real databases get them from the Liquibase changeset; this keeps test schemas,
    built from the generated models, equivalent.
    """
    for code, name, plural, description, order in SYSTEM_ROLES:
        connection.execute(  # type: ignore[attr-defined]
            text(
                "INSERT INTO role_types (code, name, plural_name, description, is_system, "
                "display_order) VALUES (:code, :name, :plural, :description, 1, :order)"
            ),
            {
                "code": code,
                "name": name,
                "plural": plural,
                "description": description,
                "order": order,
            },
        )


class RoleTypesRepository:
    def list_role_types(
        self, session: Session, *, include_archived: bool = False
    ) -> Sequence[RoleType]:
        statement = select(RoleType)
        if not include_archived:
            statement = statement.where(RoleType.archived_at.is_(None))
        return session.scalars(
            statement.order_by(RoleType.display_order, func.lower(RoleType.name), RoleType.id)
        ).all()

    def get_role_type(
        self, session: Session, role_type_id: int, *, active_only: bool = True
    ) -> RoleType | None:
        statement = select(RoleType).where(RoleType.id == role_type_id)
        if active_only:
            statement = statement.where(RoleType.archived_at.is_(None))
        return session.scalar(statement)

    def code_taken(self, session: Session, code: str) -> bool:
        # Codes are unique across archived rows too: assignments keep pointing at them.
        return session.scalar(select(RoleType.id).where(RoleType.code == code)) is not None

    def name_taken(self, session: Session, name: str, *, exclude_id: int | None = None) -> bool:
        statement = select(RoleType.id).where(
            func.lower(RoleType.name) == name.strip().lower(), RoleType.archived_at.is_(None)
        )
        if exclude_id is not None:
            statement = statement.where(RoleType.id != exclude_id)
        return session.scalar(statement) is not None

    def next_display_order(self, session: Session) -> int:
        current = session.scalar(select(func.max(RoleType.display_order)))
        return int(current or 0) + 10

    def active_assignment_counts(self, session: Session, *, on_date: str) -> dict[str, int]:
        """People currently holding each role (active, not ended before ``on_date``)."""
        rows = session.execute(
            select(PersonRole.role_type, func.count(func.distinct(PersonRole.person_id)))
            .where(
                PersonRole.archived_at.is_(None),
                PersonRole.status == "active",
                PersonRole.start_date <= on_date,
                or_(PersonRole.end_date.is_(None), PersonRole.end_date >= on_date),
            )
            .group_by(PersonRole.role_type)
        ).all()
        return {code: int(count) for code, count in rows}

    def categories_requiring(self, session: Session, code: str) -> Sequence[str]:
        return session.scalars(
            select(AccountingCategory.name).where(
                AccountingCategory.required_person_role == code,
                AccountingCategory.archived_at.is_(None),
                AccountingCategory.is_active.is_(True),
            )
        ).all()
