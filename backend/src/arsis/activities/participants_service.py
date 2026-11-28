"""Attendance register of activities: every active person can be marked present."""

from collections.abc import Iterable, Sequence
from decimal import Decimal
from typing import TypedDict, cast

from sqlalchemy.orm import Session

from arsis.activities.participants_repository import ParticipantsRepository
from arsis.activities.reimbursements import (
    ZERO,
    ReimbursementBreakdown,
    ReimbursementCalculator,
    money,
)
from arsis.activities.repository import ActivitiesRepository
from arsis.activities.schemas import ActivityStatus, ActivityType, AttendanceStatus
from arsis.audit.service import record_audit_event
from arsis.core.database import transaction
from arsis.core.errors import ImportValidationError, ResourceNotFoundError
from arsis.core.time import utc_now_iso
from arsis.generated.models import Activity, ActivityParticipant, Person, Place
from arsis.milestones.service import MilestonesService
from arsis.places.repository import PlacesRepository
from arsis.settings.service import SettingsService

# person_id, attendance, is_driver (None: unchanged), passenger_count
AttendanceRow = tuple[int, str | None, bool | None, int | None]


class ActivityTotals(TypedDict):
    breakdown: ReimbursementBreakdown
    driver_count: int
    passenger_count: int


class ParticipationRow(TypedDict):
    activity_id: int
    title: str
    type: ActivityType
    starts_at: str
    status: ActivityStatus
    attendance: AttendanceStatus | None
    is_driver: bool
    passenger_count: int | None
    distance_km: int | None
    reimbursement_flat: Decimal
    reimbursement_mileage: Decimal
    reimbursement_highway: Decimal
    reimbursement_amount: Decimal


class RefundSummaryRow(TypedDict):
    person_id: int
    person_name: str
    rehearsal: Decimal
    concert: Decimal
    event: Decimal
    mileage: Decimal
    highway: Decimal
    distance_km: int
    total: Decimal


def _serialize(participant: ActivityParticipant | None, person: Person) -> dict[str, object]:
    """A register row; people with nothing recorded yet have no participant row."""
    if participant is None:
        return {
            "person_id": person.id,
            "person_name": f"{person.first_name} {person.last_name}",
            "attendance": None,
            "attendance_recorded_at": None,
            "version": 0,
        }
    breakdown = ReimbursementBreakdown.of(participant)
    return {
        "person_id": person.id,
        "person_name": f"{person.first_name} {person.last_name}",
        "attendance": participant.attendance,
        "attendance_recorded_at": participant.attendance_recorded_at,
        "is_driver": bool(participant.is_driver),
        "passenger_count": participant.passenger_count,
        "refund_flat_amount": breakdown.flat,
        "refund_distance_km": participant.refund_distance_km,
        "refund_bonus_pct": participant.refund_bonus_pct,
        "refund_mileage_amount": breakdown.mileage,
        "refund_highway_amount": breakdown.highway,
        "refund_total": breakdown.total,
        "version": participant.version,
    }


class ParticipantsService:
    def __init__(
        self,
        repository: ParticipantsRepository | None = None,
        activities: ActivitiesRepository | None = None,
        places: PlacesRepository | None = None,
        settings: SettingsService | None = None,
        milestones: MilestonesService | None = None,
    ) -> None:
        self._repository = repository or ParticipantsRepository()
        self._activities = activities or ActivitiesRepository()
        self._places = places or PlacesRepository()
        self._settings = settings or SettingsService()
        self._milestones = milestones or MilestonesService()

    def list_participants(self, session: Session, *, activity_id: int) -> list[dict[str, object]]:
        activity = self._get_activity(session, activity_id)
        return [
            _serialize(participant, person)
            for person, participant in self._repository.register(session, activity_id=activity.id)
        ]

    def counts(
        self, session: Session, *, activity_ids: Sequence[int]
    ) -> dict[int, tuple[int, int, int]]:
        return self._repository.counts(session, activity_ids=activity_ids)

    def totals(self, session: Session, *, activity_ids: Sequence[int]) -> dict[int, ActivityTotals]:
        """Recorded reimbursements, drivers and passengers per activity."""
        totals: dict[int, ActivityTotals] = {}
        for participant in self._repository.present_on_activities(
            session, activity_ids=activity_ids
        ):
            row = totals.setdefault(
                participant.activity_id,
                {"breakdown": ReimbursementBreakdown(), "driver_count": 0, "passenger_count": 0},
            )
            row["breakdown"] = row["breakdown"] + ReimbursementBreakdown.of(participant)
            if participant.is_driver:
                row["driver_count"] += 1
                row["passenger_count"] += participant.passenger_count or 0
        return totals

    def save_attendance(
        self,
        session: Session,
        *,
        activity_id: int,
        rows: Iterable[AttendanceRow],
        actor_id: int,
    ) -> int:
        with transaction(session):
            activity = self._get_activity(session, activity_id)
            register = {
                person.id: participant
                for person, participant in self._repository.register(
                    session, activity_id=activity.id
                )
            }
            participants = {
                person_id: participant
                for person_id, participant in register.items()
                if participant is not None
            }
            normalized: list[AttendanceRow] = []
            seen: set[int] = set()
            for person_id, attendance, is_driver, passenger_count in rows:
                if person_id in seen:
                    raise ImportValidationError(
                        "La stessa persona è presente più volte nel registro",
                        details={"person_id": person_id},
                    )
                if person_id not in register:
                    raise ImportValidationError(
                        "La persona non è attiva in anagrafica",
                        details={"person_id": person_id},
                    )
                seen.add(person_id)
                normalized.append((person_id, attendance, is_driver, passenger_count))
            calculator = ReimbursementCalculator(self._settings.get_refund_rules(session))
            place = self._place_of(session, activity)
            now = utc_now_iso()
            for person_id, attendance, is_driver, passenger_count in normalized:
                existing = participants.get(person_id)
                if existing is None:
                    if attendance is None:
                        continue
                    existing = self._open_row(
                        session, activity_id=activity.id, person_id=person_id, actor_id=actor_id
                    )
                    participants[person_id] = existing
                participant = existing
                driver = bool(participant.is_driver) if is_driver is None else is_driver
                if attendance != "present":
                    driver = False
                if not driver:
                    passengers = None
                elif is_driver is None and passenger_count is None:
                    passengers = participant.passenger_count
                else:
                    passengers = passenger_count or 0
                if (
                    participant.attendance == attendance
                    and bool(participant.is_driver) == driver
                    and participant.passenger_count == passengers
                ):
                    # Unchanged rows keep the reimbursement recorded at the time.
                    continue
                if participant.attendance != attendance:
                    participant.attendance = attendance
                    participant.attendance_recorded_at = now if attendance is not None else None
                    participant.attendance_recorded_by = (
                        actor_id if attendance is not None else None
                    )
                participant.is_driver = driver
                participant.passenger_count = passengers
                calculator.apply(participant, activity, place)
                participant.updated_by = actor_id
                participant.version += 1
            self._check_passengers(participants.values())
            session.flush()
            self.sync_milestones(session, actor_id=actor_id)
            record_audit_event(
                session,
                action="activity_attendance.recorded",
                entity_type="activity",
                entity_id=activity.id,
                user_id=actor_id,
                details={"rows": len(normalized)},
            )
        return len(normalized)

    def _open_row(
        self, session: Session, *, activity_id: int, person_id: int, actor_id: int
    ) -> ActivityParticipant:
        """The row holding a person's attendance, created on first recording."""
        participant = self._repository.get_by_person(
            session, activity_id=activity_id, person_id=person_id
        )
        if participant is None:
            participant = ActivityParticipant(
                activity_id=activity_id,
                person_id=person_id,
                source="manual",
                created_by=actor_id,
                updated_by=actor_id,
                # Bumped to 1 by the attendance write that follows (a new row always changes).
                version=0,
            )
            session.add(participant)
        else:
            # A row removed under the former convocation flow: start again from blank.
            participant.archived_at = None
            participant.archived_by = None
        participant.attendance = None
        participant.attendance_recorded_at = None
        participant.attendance_recorded_by = None
        participant.is_driver = False
        participant.passenger_count = None
        return participant

    def has_recorded_attendance(self, session: Session, *, activity_id: int) -> bool:
        return bool(self._repository.present_on_activities(session, activity_ids=[activity_id]))

    def recalculate(self, session: Session, *, activity: Activity, actor_id: int) -> int:
        """Re-snapshot present participants with the current rules (caller's transaction)."""
        calculator = ReimbursementCalculator(self._settings.get_refund_rules(session))
        place = self._place_of(session, activity)
        updated = 0
        for participant in self._repository.present_on_activities(
            session, activity_ids=[activity.id]
        ):
            calculator.apply(participant, activity, place)
            participant.updated_by = actor_id
            participant.version += 1
            updated += 1
        session.flush()
        self.sync_milestones(session, actor_id=actor_id)
        return updated

    def sync_milestones(self, session: Session, *, actor_id: int) -> None:
        """Log milestones reached or lost after attendance changes (RB-20, caller's transaction)."""
        self._milestones.sync_achievements(session, actor_id=actor_id)

    def _place_of(self, session: Session, activity: Activity) -> Place | None:
        if activity.place_id is None:
            return None
        return self._places.get_place(session, activity.place_id, active_only=False)

    @staticmethod
    def _check_passengers(participants: Iterable[ActivityParticipant]) -> None:
        present = [p for p in participants if p.attendance == "present"]
        drivers = [p for p in present if p.is_driver]
        passengers = sum(p.passenger_count or 0 for p in drivers)
        available = len(present) - len(drivers)
        if passengers > available:
            raise ImportValidationError(
                "I passeggeri indicati superano i presenti che non guidano",
                details={"passengers": passengers, "available": available},
            )

    def participations(self, session: Session, *, person_id: int) -> list[ParticipationRow]:
        return [
            self._participation(participant, activity)
            for participant, activity in self._repository.participations(
                session, person_id=person_id
            )
        ]

    @staticmethod
    def _participation(participant: ActivityParticipant, activity: Activity) -> ParticipationRow:
        breakdown = ReimbursementBreakdown.of(participant)
        return {
            "activity_id": activity.id,
            "title": activity.title,
            "type": cast(ActivityType, activity.type),
            "starts_at": activity.starts_at,
            "status": cast(ActivityStatus, activity.status),
            "attendance": cast(AttendanceStatus | None, participant.attendance),
            "is_driver": bool(participant.is_driver),
            "passenger_count": participant.passenger_count,
            "distance_km": participant.refund_distance_km,
            "reimbursement_flat": breakdown.flat,
            "reimbursement_mileage": breakdown.mileage,
            "reimbursement_highway": breakdown.highway,
            "reimbursement_amount": breakdown.total,
        }

    def refund_summary(self, session: Session) -> list[RefundSummaryRow]:
        rows: dict[int, RefundSummaryRow] = {}
        for participant, activity, person in self._repository.present_participations(session):
            row = rows.setdefault(
                person.id,
                {
                    "person_id": person.id,
                    "person_name": f"{person.first_name} {person.last_name}",
                    "rehearsal": ZERO,
                    "concert": ZERO,
                    "event": ZERO,
                    "mileage": ZERO,
                    "highway": ZERO,
                    "distance_km": 0,
                    "total": ZERO,
                },
            )
            breakdown = ReimbursementBreakdown.of(participant)
            activity_type = cast(ActivityType, activity.type)
            row[activity_type] = money(row[activity_type] + breakdown.flat)
            row["mileage"] = money(row["mileage"] + breakdown.mileage)
            row["highway"] = money(row["highway"] + breakdown.highway)
            row["distance_km"] += participant.refund_distance_km or 0
            row["total"] = money(row["total"] + breakdown.total)
        return list(rows.values())

    def _get_activity(self, session: Session, activity_id: int) -> Activity:
        activity = self._activities.get_activity(session, activity_id)
        if activity is None:
            raise ResourceNotFoundError("Attività", activity_id)
        return activity
