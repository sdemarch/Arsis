"""Reimbursement snapshots for activity attendance (RB-18).

Amounts are computed once, when attendance or driver data is recorded, and stored on the
participant row: later changes to the rules or to a place apply only from then on.
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import cast

from arsis.activities.schemas import ActivityType
from arsis.generated.models import Activity, ActivityParticipant, Place
from arsis.settings.schemas import RefundRulesResponse

_CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def money(value: Decimal | int | None) -> Decimal:
    return Decimal(value or 0).quantize(_CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class MileageQuote:
    distance_km: int
    rate_per_km: Decimal
    bonus_pct: int
    mileage_amount: Decimal
    highway_amount: Decimal


class ReimbursementCalculator:
    def __init__(self, rules: RefundRulesResponse) -> None:
        self._rules = rules

    def flat_amount(self, activity_type: ActivityType) -> Decimal:
        return money(getattr(self._rules, activity_type))

    def mileage_applies(self, activity: Activity, place: Place | None) -> bool:
        return place is not None and activity.type in self._rules.mileage.enabled_types

    def mileage_quote(self, place: Place, passenger_count: int) -> MileageQuote:
        mileage = self._rules.mileage
        counted = min(max(passenger_count, 0), mileage.max_bonus_passengers)
        bonus_pct = counted * mileage.passenger_bonus_pct
        base = Decimal(place.distance_km) * mileage.rate_per_km
        return MileageQuote(
            distance_km=place.distance_km,
            rate_per_km=mileage.rate_per_km,
            bonus_pct=bonus_pct,
            mileage_amount=money(base * (100 + bonus_pct) / 100),
            highway_amount=money(place.highway_cost),
        )

    def apply(
        self, participant: ActivityParticipant, activity: Activity, place: Place | None
    ) -> None:
        """Store on the participant the amounts due under the current rules."""
        if participant.attendance != "present":
            participant.is_driver = False
            participant.passenger_count = None
            participant.refund_flat_amount = None
            _clear_mileage(participant)
            return
        participant.refund_flat_amount = self.flat_amount(cast(ActivityType, activity.type))
        if not participant.is_driver or place is None or not self.mileage_applies(activity, place):
            _clear_mileage(participant)
            return
        quote = self.mileage_quote(place, participant.passenger_count or 0)
        participant.refund_distance_km = quote.distance_km
        participant.refund_rate_per_km = quote.rate_per_km
        participant.refund_bonus_pct = quote.bonus_pct
        participant.refund_mileage_amount = quote.mileage_amount
        participant.refund_highway_amount = quote.highway_amount


def _clear_mileage(participant: ActivityParticipant) -> None:
    participant.refund_distance_km = None
    participant.refund_rate_per_km = None
    participant.refund_bonus_pct = None
    participant.refund_mileage_amount = None
    participant.refund_highway_amount = None


@dataclass(frozen=True)
class ReimbursementBreakdown:
    flat: Decimal = ZERO
    mileage: Decimal = ZERO
    highway: Decimal = ZERO

    @property
    def total(self) -> Decimal:
        return money(self.flat + self.mileage + self.highway)

    @classmethod
    def of(cls, participant: ActivityParticipant) -> ReimbursementBreakdown:
        if participant.attendance != "present":
            return cls()
        return cls(
            flat=money(participant.refund_flat_amount),
            mileage=money(participant.refund_mileage_amount),
            highway=money(participant.refund_highway_amount),
        )

    def __add__(self, other: ReimbursementBreakdown) -> ReimbursementBreakdown:
        return ReimbursementBreakdown(
            flat=self.flat + other.flat,
            mileage=self.mileage + other.mileage,
            highway=self.highway + other.highway,
        )
