from decimal import Decimal

import pytest

from arsis.activities.reimbursements import ReimbursementCalculator
from arsis.generated.models import Place
from arsis.settings.schemas import MileageRules, RefundRulesResponse


def _calculator(rate: str = "0.25", pct: int = 10, cap: int = 4) -> ReimbursementCalculator:
    return ReimbursementCalculator(
        RefundRulesResponse(
            rehearsal=Decimal("0"),
            concert=Decimal("0"),
            event=Decimal("0"),
            mileage=MileageRules(
                rate_per_km=Decimal(rate), passenger_bonus_pct=pct, max_bonus_passengers=cap
            ),
            version=1,
        )
    )


@pytest.mark.parametrize(
    "passengers, bonus, amount",
    [(0, 0, "21.00"), (1, 10, "23.10"), (4, 40, "29.40"), (9, 40, "29.40")],
)
def test_passenger_bonus_is_capped(passengers: int, bonus: int, amount: str) -> None:
    quote = _calculator().mileage_quote(
        Place(distance_km=84, highway_cost=Decimal("3")), passengers
    )
    assert quote.bonus_pct == bonus
    assert quote.mileage_amount == Decimal(amount)
    assert quote.highway_amount == Decimal("3.00")


def test_amounts_are_rounded_half_up_to_the_cent() -> None:
    # 13 km × 0.33 = 4.29; × 1.15 = 4.9335 → 4.93. 15 km × 0.33 × 1.15 = 5.6925 → 5.69
    calculator = _calculator(rate="0.33", pct=15)
    assert calculator.mileage_quote(Place(distance_km=13, highway_cost=0), 1).mileage_amount == (
        Decimal("4.93")
    )
    # 5 km × 0.25 × 1.10 = 1.375 → 1.38
    assert _calculator().mileage_quote(
        Place(distance_km=5, highway_cost=0), 1
    ).mileage_amount == Decimal("1.38")
