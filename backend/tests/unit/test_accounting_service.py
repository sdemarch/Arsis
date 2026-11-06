from collections.abc import Iterator
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from arsis.accounting.service import AccountingService
from arsis.core.errors import ConflictError
from arsis.generated.models import Base, User


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as database_session:
        database_session.add(
            User(
                email="responsabile@example.it",
                password_hash="hash",
                display_name="Responsabile",
            )
        )
        database_session.commit()
        yield database_session
    engine.dispose()


def test_movement_must_follow_the_category_direction_and_balances_are_saved(
    session: Session,
) -> None:
    service = AccountingService()
    category = service.create_category(
        session,
        values={
            "name": "Donazioni",
            "direction": "income",
            "course_required": False,
            "display_order": 0,
        },
        actor_id=1,
    )

    movement = service.create_movement(
        session,
        values={
            "occurred_on": "2026-01-15",
            "direction": "income",
            "account": "bank",
            "category_id": category.id,
            "amount": Decimal("50.00"),
            "subject": "Comune",
            "description": "Contributo",
        },
        actor_id=1,
    )
    category_id = category.id

    assert movement.amount == Decimal("50.00")
    assert [
        item.id
        for item in service.list_movements(
            session,
            fiscal_year=2026,
            account=None,
            direction=None,
            category_id=None,
            person_id=None,
            course_id=None,
            search=None,
        )
    ] == [movement.id]
    session.rollback()

    with pytest.raises(ConflictError, match="verso"):
        service.create_movement(
            session,
            values={
                "occurred_on": "2026-01-15",
                "direction": "expense",
                "account": "cash",
                "category_id": category_id,
                "amount": Decimal("5.00"),
                "subject": "Comune",
                "description": "Storno",
            },
            actor_id=1,
        )
    session.rollback()

    balances = service.save_opening_balances(
        session,
        fiscal_year=2026,
        bank=Decimal("120.50"),
        cash=Decimal("30.00"),
        actor_id=1,
    )
    assert balances == {"bank": Decimal("120.50"), "cash": Decimal("30.00")}
