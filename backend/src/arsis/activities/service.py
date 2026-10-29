"""Business operations for activities."""

from collections.abc import Sequence

from sqlalchemy.orm import Session

from arsis.activities.repository import ActivitiesRepository
from arsis.audit.service import record_audit_event
from arsis.core.database import transaction
from arsis.core.errors import ResourceNotFoundError
from arsis.core.time import utc_now_iso
from arsis.core.versioning import update_versioned
from arsis.generated.models import Activity
from arsis.generated.schemas import ActivityCreateDTO, ActivityUpdateDTO


class ActivitiesService:
    def __init__(self, repository: ActivitiesRepository | None = None) -> None:
        self._repository = repository or ActivitiesRepository()

    def list_activities(
        self, session: Session, *, search: str | None = None, include_archived: bool = False
    ) -> Sequence[Activity]:
        return self._repository.list_activities(
            session, search=search, include_archived=include_archived
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
    ) -> Activity:
        values = data.model_dump(exclude_unset=True)
        with transaction(session):
            self.get_activity(session, activity_id)
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
            return self.get_activity(session, activity_id)

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
