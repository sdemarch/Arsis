from collections.abc import Sequence
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from arsis.accounting.repository import AccountingRepository
from arsis.audit.service import record_audit_event
from arsis.core.database import transaction
from arsis.core.errors import ConflictError, ResourceNotFoundError
from arsis.core.time import utc_now_iso
from arsis.core.versioning import update_versioned
from arsis.generated.models import AccountingCategory, AccountingMovement, AccountingOpeningBalance

ZERO = Decimal("0")


class AccountingService:
    def __init__(self, repository: AccountingRepository | None = None) -> None:
        self._repository = repository or AccountingRepository()

    def list_categories(
        self, session: Session, *, include_archived: bool = False
    ) -> Sequence[AccountingCategory]:
        return self._repository.list_categories(session, include_archived=include_archived)

    def create_category(
        self, session: Session, *, values: dict[str, Any], actor_id: int
    ) -> AccountingCategory:
        with transaction(session):
            self._ensure_unique_category_name(session, values["name"])
            category = AccountingCategory(**values, created_by=actor_id, updated_by=actor_id)
            session.add(category)
            session.flush()
            record_audit_event(
                session,
                action="accounting_category.created",
                entity_type="accounting_category",
                entity_id=category.id,
                user_id=actor_id,
            )
        return category

    def update_category(
        self,
        session: Session,
        *,
        category_id: int,
        values: dict[str, Any],
        expected_version: int,
        actor_id: int,
    ) -> AccountingCategory:
        with transaction(session):
            self._get_category(session, category_id)
            if "name" in values:
                self._ensure_unique_category_name(session, values["name"], exclude_id=category_id)
            if values:
                values["updated_by"] = actor_id
                update_versioned(
                    session,
                    AccountingCategory.__table__,
                    resource_name="Categoria contabile",
                    resource_id=category_id,
                    expected_version=expected_version,
                    values=values,
                )
                record_audit_event(
                    session,
                    action="accounting_category.updated",
                    entity_type="accounting_category",
                    entity_id=category_id,
                    user_id=actor_id,
                    details={"fields": sorted(values)},
                )
            session.flush()
            session.expire_all()
            return self._get_category(session, category_id)

    def archive_category(
        self, session: Session, *, category_id: int, expected_version: int, actor_id: int
    ) -> AccountingCategory:
        with transaction(session):
            self._get_category(session, category_id)
            update_versioned(
                session,
                AccountingCategory.__table__,
                resource_name="Categoria contabile",
                resource_id=category_id,
                expected_version=expected_version,
                values={
                    "is_active": False,
                    "archived_at": utc_now_iso(),
                    "archived_by": actor_id,
                    "updated_by": actor_id,
                },
            )
            record_audit_event(
                session,
                action="accounting_category.archived",
                entity_type="accounting_category",
                entity_id=category_id,
                user_id=actor_id,
            )
            session.flush()
            session.expire_all()
            return self._get_category(session, category_id, include_archived=True)

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
        highlighted: bool | None = None,
    ) -> Sequence[AccountingMovement]:
        return self._repository.list_movements(
            session,
            fiscal_year=fiscal_year,
            month=month,
            account=account,
            direction=direction,
            category_id=category_id,
            person_id=person_id,
            course_id=course_id,
            search=search,
            highlighted=highlighted,
        )

    def create_movement(
        self, session: Session, *, values: dict[str, Any], actor_id: int
    ) -> AccountingMovement:
        with transaction(session):
            self._validate_movement(session, values)
            movement = AccountingMovement(**values, created_by=actor_id, updated_by=actor_id)
            session.add(movement)
            session.flush()
            record_audit_event(
                session,
                action="accounting_movement.created",
                entity_type="accounting_movement",
                entity_id=movement.id,
                user_id=actor_id,
            )
        return movement

    def update_movement(
        self,
        session: Session,
        *,
        movement_id: int,
        values: dict[str, Any],
        expected_version: int,
        actor_id: int,
    ) -> AccountingMovement:
        with transaction(session):
            movement = self._get_movement(session, movement_id)
            merged = {
                column: getattr(movement, column)
                for column in (
                    "occurred_on",
                    "direction",
                    "account",
                    "category_id",
                    "amount",
                    "subject",
                    "person_id",
                    "course_id",
                    "description",
                    "document_reference",
                )
            }
            merged.update(values)
            # Flagging alone must work even if the category was archived in the meantime.
            if set(values) - {"is_highlighted"}:
                self._validate_movement(session, merged)
            if values:
                values["updated_by"] = actor_id
                update_versioned(
                    session,
                    AccountingMovement.__table__,
                    resource_name="Movimento contabile",
                    resource_id=movement_id,
                    expected_version=expected_version,
                    values=values,
                )
                record_audit_event(
                    session,
                    action="accounting_movement.updated",
                    entity_type="accounting_movement",
                    entity_id=movement_id,
                    user_id=actor_id,
                    details={"fields": sorted(values)},
                )
            session.flush()
            session.expire_all()
            return self._get_movement(session, movement_id)

    def delete_movement(self, session: Session, *, movement_id: int, actor_id: int) -> None:
        with transaction(session):
            self._get_movement(session, movement_id)
            session.delete(self._get_movement(session, movement_id))
            record_audit_event(
                session,
                action="accounting_movement.deleted",
                entity_type="accounting_movement",
                entity_id=movement_id,
                user_id=actor_id,
            )

    def get_opening_balances(self, session: Session, fiscal_year: int) -> dict[str, Decimal]:
        rows = self._repository.get_opening_balances(session, fiscal_year)
        return {
            "bank": next((row.amount for row in rows if row.account == "bank"), Decimal("0")),
            "cash": next((row.amount for row in rows if row.account == "cash"), Decimal("0")),
        }

    def save_opening_balances(
        self, session: Session, *, fiscal_year: int, bank: Decimal, cash: Decimal, actor_id: int
    ) -> dict[str, Decimal]:
        with transaction(session):
            rows = {
                row.account: row
                for row in self._repository.get_opening_balances(session, fiscal_year)
            }
            for account, amount in (("bank", bank), ("cash", cash)):
                if account in rows:
                    update_versioned(
                        session,
                        AccountingOpeningBalance.__table__,
                        resource_name="Saldo iniziale",
                        resource_id=rows[account].id,
                        expected_version=rows[account].version,
                        values={"amount": amount, "updated_by": actor_id},
                    )
                else:
                    session.add(
                        AccountingOpeningBalance(
                            fiscal_year=fiscal_year,
                            account=account,
                            amount=amount,
                            created_by=actor_id,
                            updated_by=actor_id,
                        )
                    )
            record_audit_event(
                session,
                action="accounting_opening_balances.saved",
                entity_type="accounting_opening_balances",
                entity_id=fiscal_year,
                user_id=actor_id,
            )
        session.expire_all()
        return self.get_opening_balances(session, fiscal_year)

    def summarize(self, session: Session, fiscal_year: int) -> dict[str, Any]:
        """Year totals per account and per category, starting from the opening balances."""
        opening = self.get_opening_balances(session, fiscal_year)
        accounts: dict[str, dict[str, Any]] = {
            account: {"account": account, "opening": amount, "income": ZERO, "expense": ZERO}
            for account, amount in opening.items()
        }
        categories: dict[tuple[int, str], Decimal] = {}
        for movement in self._repository.list_movements(
            session,
            fiscal_year=fiscal_year,
            account=None,
            direction=None,
            category_id=None,
            person_id=None,
            course_id=None,
            search=None,
        ):
            amount = Decimal(movement.amount)
            accounts[movement.account][movement.direction] += amount
            key = (movement.category_id, movement.direction)
            categories[key] = categories.get(key, ZERO) + amount
        for totals in accounts.values():
            totals["closing"] = totals["opening"] + totals["income"] - totals["expense"]
        return {
            "fiscal_year": fiscal_year,
            "accounts": list(accounts.values()),
            "categories": [
                {"category_id": category_id, "direction": direction, "amount": amount}
                for (category_id, direction), amount in sorted(categories.items())
            ],
        }

    def _get_category(
        self, session: Session, category_id: int, *, include_archived: bool = False
    ) -> AccountingCategory:
        category = self._repository.get_category(
            session, category_id, include_archived=include_archived
        )
        if category is None:
            raise ResourceNotFoundError("Categoria contabile", category_id)
        return category

    def _ensure_unique_category_name(
        self, session: Session, name: str, *, exclude_id: int | None = None
    ) -> None:
        existing = self._repository.find_category_by_name(session, name)
        if existing is not None and existing.id != exclude_id:
            raise ConflictError(
                "Esiste già una categoria con questo nome", code="ACCOUNTING_CATEGORY_EXISTS"
            )

    def _get_movement(self, session: Session, movement_id: int) -> AccountingMovement:
        movement = self._repository.get_movement(session, movement_id)
        if movement is None:
            raise ResourceNotFoundError("Movimento contabile", movement_id)
        return movement

    def _validate_movement(self, session: Session, values: dict[str, Any]) -> None:
        category = self._get_category(session, int(values["category_id"]))
        if not category.is_active:
            raise ConflictError(
                "La categoria selezionata non è attiva", code="INACTIVE_ACCOUNTING_CATEGORY"
            )
        if category.direction != "both" and category.direction != values["direction"]:
            raise ConflictError(
                "Il verso non è ammesso dalla categoria", code="INVALID_ACCOUNTING_DIRECTION"
            )
        person_id, course_id, occurred_on = (
            values.get("person_id"),
            values.get("course_id"),
            str(values["occurred_on"]),
        )
        if category.required_person_role:
            if (
                person_id is None
                or self._repository.get_active_person(session, int(person_id)) is None
                or not self._repository.has_role_on(
                    session,
                    person_id=int(person_id),
                    role_type=category.required_person_role,
                    on_date=occurred_on,
                )
            ):
                raise ConflictError(
                    "Il soggetto non possiede il ruolo richiesto alla data del movimento",
                    code="INVALID_ACCOUNTING_PERSON",
                )
        elif (
            person_id is not None
            and self._repository.get_active_person(session, int(person_id)) is None
        ):
            raise ConflictError(
                "Il soggetto selezionato non è attivo", code="INVALID_ACCOUNTING_PERSON"
            )
        if category.course_required and course_id is None:
            raise ConflictError("La categoria richiede un corso", code="ACCOUNTING_COURSE_REQUIRED")
        course = (
            self._repository.get_course(session, int(course_id)) if course_id is not None else None
        )
        if course_id is not None and course is None:
            raise ConflictError(
                "Il corso selezionato non è disponibile", code="INVALID_ACCOUNTING_COURSE"
            )
        if (
            category.required_person_role == "student"
            and course is not None
            and (
                person_id is None
                or not self._repository.has_enrollment_on(
                    session, person_id=int(person_id), course_id=course.id, on_date=occurred_on
                )
            )
        ):
            raise ConflictError(
                "L'allievo non risulta iscritto al corso alla data del movimento",
                code="INVALID_ACCOUNTING_ENROLLMENT",
            )
        if (
            category.required_person_role == "teacher"
            and course is not None
            and course.teacher_person_id != person_id
        ):
            raise ConflictError(
                "L'insegnante non è assegnato al corso", code="INVALID_ACCOUNTING_TEACHER_COURSE"
            )
