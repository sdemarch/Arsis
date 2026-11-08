"""Convocation and attendance of activity participants."""

from collections.abc import Iterable, Sequence

from sqlalchemy.orm import Session

from arsis.activities.participants_repository import ParticipantsRepository
from arsis.activities.repository import ActivitiesRepository
from arsis.audit.service import record_audit_event
from arsis.core.database import transaction
from arsis.core.errors import ConflictError, ImportValidationError, ResourceNotFoundError
from arsis.core.time import utc_now_iso
from arsis.generated.models import Activity, ActivityParticipant, Person

AttendanceRow = tuple[int, str | None]


def _serialize(participant: ActivityParticipant, person: Person) -> dict[str, object]:
    return {
        "person_id": person.id,
        "person_name": f"{person.first_name} {person.last_name}",
        "source": participant.source,
        "attendance": participant.attendance,
        "attendance_recorded_at": participant.attendance_recorded_at,
        "version": participant.version,
    }


class ParticipantsService:
    def __init__(
        self,
        repository: ParticipantsRepository | None = None,
        activities: ActivitiesRepository | None = None,
    ) -> None:
        self._repository = repository or ParticipantsRepository()
        self._activities = activities or ActivitiesRepository()

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
            for person_id, attendance in rows:
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
                normalized.append((person_id, attendance))
            now = utc_now_iso()
            for person_id, attendance in normalized:
                participant = participants[person_id]
                if participant.attendance == attendance:
                    continue
                participant.attendance = attendance
                participant.attendance_recorded_at = now if attendance is not None else None
                participant.attendance_recorded_by = actor_id if attendance is not None else None
                participant.updated_by = actor_id
                participant.version += 1
            record_audit_event(
                session,
                action="activity_attendance.recorded",
                entity_type="activity",
                entity_id=activity.id,
                user_id=actor_id,
                details={"rows": len(normalized)},
            )
        return len(normalized)

    def participations(self, session: Session, *, person_id: int) -> list[dict[str, object]]:
        return [
            {
                "activity_id": activity.id,
                "title": activity.title,
                "type": activity.type,
                "starts_at": activity.starts_at,
                "status": activity.status,
                "source": participant.source,
                "attendance": participant.attendance,
            }
            for participant, activity in self._repository.participations(
                session, person_id=person_id
            )
        ]

    def _get_activity(self, session: Session, activity_id: int) -> Activity:
        activity = self._activities.get_activity(session, activity_id)
        if activity is None:
            raise ResourceNotFoundError("Attività", activity_id)
        return activity
