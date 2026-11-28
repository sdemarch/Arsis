"""Business operations for activities."""

from collections.abc import Sequence

from sqlalchemy.orm import Session

from arsis.activities.participants_service import ParticipantsService
from arsis.activities.repository import ActivitiesRepository
from arsis.audit.service import record_audit_event
from arsis.core.database import transaction
from arsis.core.errors import ConflictError, ResourceNotFoundError
from arsis.core.time import utc_now_iso
from arsis.core.versioning import update_versioned
from arsis.generated.models import Activity
from arsis.generated.schemas import ActivityCreateDTO, ActivityUpdateDTO
from arsis.places.repository import PlacesRepository

# Changing these on an activity with recorded attendance changes the reimbursements due.
_REFUND_FIELDS = ("type", "place_id")


class ActivitiesService:
    def __init__(
        self,
        repository: ActivitiesRepository | None = None,
        participants: ParticipantsService | None = None,
        places: PlacesRepository | None = None,
    ) -> None:
        self._repository = repository or ActivitiesRepository()
        self._participants = participants or ParticipantsService()
        self._places = places or PlacesRepository()

    def list_activities(
        self,
        session: Session,
        *,
        search: str | None = None,
        include_archived: bool = False,
        starts_from: str | None = None,
        starts_to: str | None = None,
    ) -> Sequence[Activity]:
        return self._repository.list_activities(
            session,
            search=search,
            include_archived=include_archived,
            starts_from=starts_from,
            starts_to=starts_to,
        )

    def get_activity(
        self, session: Session, activity_id: int, *, include_archived: bool = False
    ) -> Activity:
        activity = self._repository.get_activity(
            session, activity_id, include_archived=include_archived
        )
        if activity is None:
            raise ResourceNotFoundError("Attività", activity_id)
        return activity

    def create_activity(
        self, session: Session, *, data: ActivityCreateDTO, actor_id: int
    ) -> Activity:
        with transaction(session):
            values = data.model_dump()
            values["status"] = values["status"] or "planned"
            self._require_active_place(session, values.get("place_id"))
            activity = self._repository.add_activity(
                session, Activity(**values, created_by=actor_id, updated_by=actor_id)
            )
            session.flush()
            record_audit_event(
                session,
                action="activity.created",
                entity_type="activity",
                entity_id=activity.id,
                user_id=actor_id,
            )
        return activity

    def update_activity(
        self,
        session: Session,
        *,
        activity_id: int,
        data: ActivityUpdateDTO,
        expected_version: int,
        actor_id: int,
        recalculate_refunds: bool = False,
    ) -> Activity:
        values = data.model_dump(exclude_unset=True)
        with transaction(session):
            current = self.get_activity(session, activity_id)
            if values.get("place_id") is not None and values["place_id"] != current.place_id:
                self._require_active_place(session, values["place_id"])
            refund_change = any(
                field in values and values[field] != getattr(current, field)
                for field in _REFUND_FIELDS
            )
            needs_recalculation = refund_change and self._participants.has_recorded_attendance(
                session, activity_id=activity_id
            )
            if needs_recalculation and not recalculate_refunds:
                raise ConflictError(
                    "L'attività ha presenze registrate: confermare il ricalcolo dei rimborsi "
                    "con le regole correnti",
                    code="ACTIVITY_REFUNDS_RECALCULATION_REQUIRED",
                )
            if values:
                values["updated_by"] = actor_id
                update_versioned(
                    session,
                    Activity.__table__,
                    resource_name="Attività",
                    resource_id=activity_id,
                    expected_version=expected_version,
                    values=values,
                )
                record_audit_event(
                    session,
                    action="activity.updated",
                    entity_type="activity",
                    entity_id=activity_id,
                    user_id=actor_id,
                    details={"fields": sorted(values)},
                )
            session.flush()
            session.expire_all()
            activity = self.get_activity(session, activity_id)
            if needs_recalculation:
                recalculated = self._participants.recalculate(
                    session, activity=activity, actor_id=actor_id
                )
                record_audit_event(
                    session,
                    action="activity_refunds.recalculated",
                    entity_type="activity",
                    entity_id=activity_id,
                    user_id=actor_id,
                    details={"participants": recalculated},
                )
                session.flush()
            return activity

    def archive_activity(
        self, session: Session, *, activity_id: int, expected_version: int, actor_id: int
    ) -> Activity:
        with transaction(session):
            self.get_activity(session, activity_id)
            update_versioned(
                session,
                Activity.__table__,
                resource_name="Attività",
                resource_id=activity_id,
                expected_version=expected_version,
                values={
                    "archived_at": utc_now_iso(),
                    "archived_by": actor_id,
                    "updated_by": actor_id,
                },
            )
            record_audit_event(
                session,
                action="activity.archived",
                entity_type="activity",
                entity_id=activity_id,
                user_id=actor_id,
            )
            session.flush()
            session.expire_all()
            return self.get_activity(session, activity_id, include_archived=True)

    def _require_active_place(self, session: Session, place_id: int | None) -> None:
        if place_id is not None and self._places.get_place(session, place_id) is None:
            raise ConflictError("Il luogo selezionato non è attivo", code="INVALID_ACTIVITY_PLACE")
