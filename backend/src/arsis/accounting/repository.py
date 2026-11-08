from collections.abc import Sequence

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from arsis.generated.models import (
    AccountingCategory,
    AccountingMovement,
    AccountingOpeningBalance,
    Course,
    Enrollment,
    Person,
    PersonRole,
)


class AccountingRepository:
    def get_category(
        self, session: Session, category_id: int, *, include_archived: bool = False
    ) -> AccountingCategory | None:
        statement = select(AccountingCategory).where(AccountingCategory.id == category_id)
        if not include_archived:
            statement = statement.where(AccountingCategory.archived_at.is_(None))
        return session.scalar(statement)

    def list_categories(
        self, session: Session, *, include_archived: bool = False
    ) -> Sequence[AccountingCategory]:
        statement: Select[tuple[AccountingCategory]] = select(AccountingCategory)
        if not include_archived:
            statement = statement.where(AccountingCategory.archived_at.is_(None))
        return session.scalars(
            statement.order_by(
                AccountingCategory.display_order,
                func.lower(AccountingCategory.name),
                AccountingCategory.id,
            )
        ).all()

    def find_category_by_name(self, session: Session, name: str) -> AccountingCategory | None:
        return session.scalar(
            select(AccountingCategory).where(
                func.lower(AccountingCategory.name) == name.strip().casefold()
            )
        )

    def get_movement(self, session: Session, movement_id: int) -> AccountingMovement | None:
        return session.scalar(
            select(AccountingMovement).where(AccountingMovement.id == movement_id)
        )

    def list_movements(
        self,
        session: Session,
        *,
        fiscal_year: int | None,
        month: int | None = None,
        account: str | None,
        direction: str | None,
        category_id: int | None,
        person_id: int | None,
        course_id: int | None,
        search: str | None,
    ) -> Sequence[AccountingMovement]:
        statement: Select[tuple[AccountingMovement]] = select(AccountingMovement)
        if fiscal_year is not None:
            first_month, last_month = (month, month) if month is not None else (1, 12)
            statement = statement.where(
                AccountingMovement.occurred_on.between(
                    f"{fiscal_year:04d}-{first_month:02d}-01",
                    f"{fiscal_year:04d}-{last_month:02d}-31",
                )
            )
        for column, value in (
            (AccountingMovement.account, account),
            (AccountingMovement.direction, direction),
            (AccountingMovement.category_id, category_id),
            (AccountingMovement.person_id, person_id),
            (AccountingMovement.course_id, course_id),
        ):
            if value is not None:
                statement = statement.where(column == value)
        if search and (query := search.strip()):
            pattern = f"%{query.casefold()}%"
            statement = statement.where(
                or_(
                    func.lower(AccountingMovement.subject).like(pattern),
                    func.lower(AccountingMovement.description).like(pattern),
                    func.lower(AccountingMovement.document_reference).like(pattern),
                )
            )
        return session.scalars(
            statement.order_by(AccountingMovement.occurred_on.desc(), AccountingMovement.id.desc())
        ).all()

    def get_opening_balances(
        self, session: Session, fiscal_year: int
    ) -> Sequence[AccountingOpeningBalance]:
        return session.scalars(
            select(AccountingOpeningBalance).where(
                AccountingOpeningBalance.fiscal_year == fiscal_year
            )
        ).all()

    def get_active_person(self, session: Session, person_id: int) -> Person | None:
        return session.scalar(
            select(Person).where(Person.id == person_id, Person.archived_at.is_(None))
        )

    def has_role_on(
        self, session: Session, *, person_id: int, role_type: str, on_date: str
    ) -> bool:
        return (
            session.scalar(
                select(PersonRole.id).where(
                    PersonRole.person_id == person_id,
                    PersonRole.role_type == role_type,
                    PersonRole.status == "active",
                    PersonRole.archived_at.is_(None),
                    PersonRole.start_date <= on_date,
                    or_(PersonRole.end_date.is_(None), PersonRole.end_date >= on_date),
                )
            )
            is not None
        )

    def get_course(self, session: Session, course_id: int) -> Course | None:
        return session.scalar(
            select(Course).where(Course.id == course_id, Course.archived_at.is_(None))
        )

    def has_enrollment_on(
        self, session: Session, *, person_id: int, course_id: int, on_date: str
    ) -> bool:
        return (
            session.scalar(
                select(Enrollment.id).where(
                    Enrollment.student_person_id == person_id,
                    Enrollment.course_id == course_id,
                    Enrollment.archived_at.is_(None),
                    Enrollment.status.in_(("active", "completed")),
                    Enrollment.starts_on <= on_date,
                    or_(Enrollment.ends_on.is_(None), Enrollment.ends_on >= on_date),
                )
            )
            is not None
        )
