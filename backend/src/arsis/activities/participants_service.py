"""Convocation and attendance of activity participants."""

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
from arsis.core.errors import ConflictError, ImportValidationError, ResourceNotFoundError
from arsis.core.time import utc_now_iso
from arsis.generated.models import Activity, ActivityParticipant, Person, Place
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
    source: str
    attendance: AttendanceStatus | None
    is_driver: bool
    passenger_count: int | None
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


def _serialize(participant: ActivityParticipant, person: Person) -> dict[str, object]:
    breakdown = ReimbursementBreakdown.of(participant)
    return {
        "person_id": person.id,
        "person_name": f"{person.first_name} {person.last_name}",
        "source": participant.source,
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
    ) -> None:
        self._repository = repository or ParticipantsRepository()
        self._activities = activities or ActivitiesRepository()
        self._places = places or PlacesRepository()
        self._settings = settings or SettingsService()

    def list_participants(self, session: Session, *, activity_id: int) -> list[dict[str, object]]:
        activity = self._get_activity(session, activity_id)
        return [
            _serialize(participant, person)
            for participant, person in self._repository.list_participants(
                session, activity_id=activity.id
            )
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

    def convoke_musicians(self, session: Session, *, activity: Activity, actor_id: int) -> int:
        """Add the musicians active on the activity date who are not on it yet.

        People removed by hand keep their (archived) row and are not added back.
        Runs inside the caller's transaction.
        """
        known = self._repository.person_ids_on_activity(session, activity_id=activity.id)
        added = 0
        for person_id in self._repository.active_musician_ids(
            session, on_date=activity.starts_at[:10]
        ):
            if person_id in known:
                continue
            session.add(
                ActivityParticipant(
                    activity_id=activity.id,
                    person_id=person_id,
                    source="automatic",
                    created_by=actor_id,
                    updated_by=actor_id,
                )
            )
            added += 1
        return added

    def refresh_musicians(self, session: Session, *, activity_id: int, actor_id: int) -> int:
        with transaction(session):
            activity = self._get_activity(session, activity_id)
            added = self.convoke_musicians(session, activity=activity, actor_id=actor_id)
            record_audit_event(
                session,
                action="activity_participants.musicians_added",
                entity_type="activity",
                entity_id=activity.id,
                user_id=actor_id,
                details={"added": added},
            )
        return added

    def add_participant(
        self, session: Session, *, activity_id: int, person_id: int, actor_id: int
    ) -> dict[str, object]:
        with transaction(session):
            activity = self._get_activity(session, activity_id)
            person = self._repository.get_active_person(session, person_id)
            if person is None:
                raise ConflictError(
                    "La persona selezionata non è attiva", code="INVALID_ACTIVITY_PARTICIPANT"
                )
            participant = self._repository.get_by_person(
                session, activity_id=activity.id, person_id=person_id
            )
            if participant is not None and participant.archived_at is None:
                raise ConflictError(
                    "La persona è già tra i partecipanti", code="ACTIVITY_PARTICIPANT_EXISTS"
                )
            if participant is None:
                participant = ActivityParticipant(
                    activity_id=activity.id,
                    person_id=person_id,
                    source="manual",
                    created_by=actor_id,
                    updated_by=actor_id,
                )
                session.add(participant)
            else:
                participant.source = "manual"
                participant.archived_at = None
                participant.archived_by = None
                participant.updated_by = actor_id
                participant.version += 1
            session.flush()
            record_audit_event(
                session,
                action="activity_participant.added",
                entity_type="activity",
                entity_id=activity.id,
                user_id=actor_id,
                details={"person_id": person_id},
            )
            return _serialize(participant, person)

    def remove_participant(
        self, session: Session, *, activity_id: int, person_id: int, actor_id: int
    ) -> None:
        with transaction(session):
            activity = self._get_activity(session, activity_id)
            participant = self._repository.get_by_person(
                session, activity_id=activity.id, person_id=person_id
            )
            if participant is None or participant.archived_at is not None:
                raise ResourceNotFoundError("Partecipante", person_id)
            participant.archived_at = utc_now_iso()
            participant.archived_by = actor_id
            participant.updated_by = actor_id
            participant.version += 1
            record_audit_event(
                session,
                action="activity_participant.removed",
                entity_type="activity",
                entity_id=activity.id,
                user_id=actor_id,
                details={"person_id": person_id},
            )

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
            participants = {
                participant.person_id: participant
                for participant, _ in self._repository.list_participants(
                    session, activity_id=activity.id
                )
            }
            normalized: list[AttendanceRow] = []
            seen: set[int] = set()
            for person_id, attendance, is_driver, passenger_count in rows:
                if person_id in seen:
                    raise ImportValidationError(
                        "La stessa persona è presente più volte nel registro",
                        details={"person_id": person_id},
                    )
                if person_id not in participants:
                    raise ImportValidationError(
                        "La persona non è tra i partecipanti dell'attività",
                        details={"person_id": person_id},
                    )
                seen.add(person_id)
                normalized.append((person_id, attendance, is_driver, passenger_count))
            calculator = ReimbursementCalculator(self._settings.get_refund_rules(session))
            place = self._place_of(session, activity)
            now = utc_now_iso()
            for person_id, attendance, is_driver, passenger_count in normalized:
                participant = participants[person_id]
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
            record_audit_event(
                session,
                action="activity_attendance.recorded",
                entity_type="activity",
                entity_id=activity.id,
                user_id=actor_id,
                details={"rows": len(normalized)},
            )
        return len(normalized)

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
        return updated

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
            {
                "activity_id": activity.id,
                "title": activity.title,
                "type": cast(ActivityType, activity.type),
                "starts_at": activity.starts_at,
                "status": cast(ActivityStatus, activity.status),
                "source": participant.source,
                "attendance": cast(AttendanceStatus | None, participant.attendance),
                "is_driver": bool(participant.is_driver),
                "passenger_count": participant.passenger_count,
                "reimbursement_amount": ReimbursementBreakdown.of(participant).total,
            }
            for participant, activity in self._repository.participations(
                session, person_id=person_id
            )
        ]

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
