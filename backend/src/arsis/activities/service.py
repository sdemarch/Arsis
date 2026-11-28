"""Business operations for activities."""

from collections.abc import Sequence
from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from arsis.activities.participants_service import ParticipantsService
from arsis.activities.recurrence import (
    RecurrenceRule,
    build_rule,
    describe,
    occurrence_dates,
)
from arsis.activities.repository import ActivitiesRepository
from arsis.audit.service import record_audit_event
from arsis.core.database import transaction
from arsis.core.errors import ConflictError, ImportValidationError, ResourceNotFoundError
from arsis.core.time import utc_now_iso
from arsis.core.versioning import update_versioned
from arsis.generated.models import Activity, ActivitySeries
from arsis.generated.schemas import ActivityCreateDTO, ActivityUpdateDTO
from arsis.places.repository import PlacesRepository

# Changing these on an activity with recorded attendance changes the reimbursements due.
_REFUND_FIELDS = ("type", "place_id")


def series_rule(series: ActivitySeries) -> RecurrenceRule:
    weekdays = tuple(int(day) for day in (series.weekdays or "").split(",") if day)
    return RecurrenceRule(
        frequency="weekly" if series.frequency == "weekly" else "monthly",
        interval=series.interval_count,
        starts_on=date.fromisoformat(series.starts_on),
        ends_on=date.fromisoformat(series.ends_on),
        weekdays=weekdays,
    )


def series_summary(series: ActivitySeries, occurrence_count: int) -> dict[str, Any]:
    rule = series_rule(series)
    return {
        "id": series.id,
        "frequency": rule.frequency,
        "interval": rule.interval,
        "weekdays": list(rule.weekdays),
        "starts_on": series.starts_on,
        "ends_on": series.ends_on,
        "description": describe(rule),
        "occurrence_count": occurrence_count,
        "position": 0,
    }


def _check_occurrences(dates: Sequence[str], occurrences: Sequence[str]) -> None:
    """The browser sends one timestamp per rule date, with its own UTC offset."""
    for starts_at in occurrences:
        try:
            parsed = datetime.fromisoformat(starts_at)
        except ValueError as exc:
            raise ImportValidationError(
                "Data di un'attività della serie non valida", details={"starts_at": starts_at}
            ) from exc
        if parsed.tzinfo is None:
            raise ImportValidationError(
                "Le date della serie devono indicare il fuso orario",
                details={"starts_at": starts_at},
            )
    if [starts_at[:10] for starts_at in occurrences] != list(dates):
        raise ImportValidationError(
            "Le date inviate non corrispondono alla regola di ricorrenza: aggiorna l'anteprima",
            details={"expected": list(dates)},
        )


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
            return self._apply_update(
                session,
                activity_id=activity_id,
                values=values,
                expected_version=expected_version,
                actor_id=actor_id,
                recalculate_refunds=recalculate_refunds,
            )

    def _apply_update(
        self,
        session: Session,
        *,
        activity_id: int,
        values: dict[str, Any],
        expected_version: int,
        actor_id: int,
        recalculate_refunds: bool,
    ) -> Activity:
        """Update one activity inside the caller's transaction (also used by series)."""
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

    # Recurring series (RB-22) ---------------------------------------------------------

    def preview_series(self, *, starts_on: str, recurrence: dict[str, Any]) -> RecurrenceRule:
        return self._rule(starts_on, recurrence)

    def create_series(
        self,
        session: Session,
        *,
        values: dict[str, Any],
        starts_on: str,
        recurrence: dict[str, Any],
        occurrences: Sequence[str],
        actor_id: int,
    ) -> tuple[ActivitySeries, list[Activity]]:
        rule = self._rule(starts_on, recurrence)
        dates = [day.isoformat() for day in occurrence_dates(rule)]
        _check_occurrences(dates, occurrences)
        with transaction(session):
            self._require_active_place(session, values.get("place_id"))
            series = ActivitySeries(
                frequency=rule.frequency,
                interval_count=rule.interval,
                weekdays=rule.weekdays_text(),
                starts_on=rule.starts_on.isoformat(),
                ends_on=rule.ends_on.isoformat(),
                created_by=actor_id,
                updated_by=actor_id,
            )
            session.add(series)
            session.flush()
            created = []
            fields = {**values, "status": values.get("status") or "planned"}
            for starts_at in occurrences:
                activity = Activity(
                    **fields,
                    starts_at=starts_at,
                    series_id=series.id,
                    created_by=actor_id,
                    updated_by=actor_id,
                )
                self._repository.add_activity(session, activity)
                created.append(activity)
            session.flush()
            record_audit_event(
                session,
                action="activity_series.created",
                entity_type="activity_series",
                entity_id=series.id,
                user_id=actor_id,
                details={"occurrences": len(created), "rule": describe(rule)},
            )
        return series, created

    def get_series(self, session: Session, series_id: int) -> ActivitySeries:
        series = self._repository.get_series(session, series_id)
        if series is None:
            raise ResourceNotFoundError("Serie di attività", series_id)
        return series

    def series_occurrences(self, session: Session, series_id: int) -> Sequence[Activity]:
        return self._repository.series_occurrences(session, series_id)

    def update_following(
        self,
        session: Session,
        *,
        activity_id: int,
        values: dict[str, Any],
        actor_id: int,
        recalculate_refunds: bool,
    ) -> int:
        """Apply the same changes to an occurrence and all the following ones."""
        with transaction(session):
            targets = self._following(session, activity_id, include_self=True)
            for target in targets:
                self._apply_update(
                    session,
                    activity_id=target.id,
                    values=dict(values),
                    expected_version=target.version,
                    actor_id=actor_id,
                    recalculate_refunds=recalculate_refunds,
                )
            return len(targets)

    def end_series_after(
        self, session: Session, *, activity_id: int, actor_id: int
    ) -> tuple[int, int]:
        """Archive the occurrences after this one, keeping those with recorded attendance."""
        with transaction(session):
            activity = self.get_activity(session, activity_id)
            following = self._following(session, activity_id, include_self=False)
            counts = self._participants.counts(
                session, activity_ids=[item.id for item in following]
            )
            archived = kept = 0
            last_kept = activity.starts_at
            for item in following:
                if counts.get(item.id, (0, 0, 0))[0]:
                    kept += 1
                    last_kept = max(last_kept, item.starts_at)
                    continue
                update_versioned(
                    session,
                    Activity.__table__,
                    resource_name="Attività",
                    resource_id=item.id,
                    expected_version=item.version,
                    values={
                        "archived_at": utc_now_iso(),
                        "archived_by": actor_id,
                        "updated_by": actor_id,
                    },
                )
                archived += 1
            series = self.get_series(session, int(activity.series_id or 0))
            update_versioned(
                session,
                ActivitySeries.__table__,
                resource_name="Serie di attività",
                resource_id=series.id,
                expected_version=series.version,
                values={"ends_on": last_kept[:10], "updated_by": actor_id},
            )
            record_audit_event(
                session,
                action="activity_series.ended",
                entity_type="activity_series",
                entity_id=series.id,
                user_id=actor_id,
                details={"after_activity_id": activity_id, "archived": archived, "kept": kept},
            )
            session.flush()
            session.expire_all()
            return archived, kept

    def series_summaries(
        self, session: Session, activities: Sequence[Activity]
    ) -> dict[int, dict[str, Any]]:
        """Series summary for each activity that belongs to one, keyed by activity id."""
        by_series: dict[int, list[Activity]] = {}
        for activity in activities:
            if activity.series_id is not None:
                by_series.setdefault(activity.series_id, []).append(activity)
        summaries: dict[int, dict[str, Any]] = {}
        for series_id, members in by_series.items():
            series = self._repository.get_series(session, series_id)
            if series is None:
                continue
            occurrences = [
                item.id for item in self._repository.series_occurrences(session, series_id)
            ]
            base = series_summary(series, len(occurrences))
            for member in members:
                position = occurrences.index(member.id) + 1 if member.id in occurrences else 0
                summaries[member.id] = {**base, "position": position}
        return summaries

    def _following(
        self, session: Session, activity_id: int, *, include_self: bool
    ) -> list[Activity]:
        activity = self.get_activity(session, activity_id)
        if activity.series_id is None:
            raise ConflictError(
                "L'attività non fa parte di una serie", code="ACTIVITY_NOT_IN_SERIES"
            )
        return [
            item
            for item in self._repository.series_occurrences(session, activity.series_id)
            if (item.starts_at, item.id) > (activity.starts_at, activity.id)
            or (include_self and item.id == activity.id)
        ]

    @staticmethod
    def _rule(starts_on: str, recurrence: dict[str, Any]) -> RecurrenceRule:
        try:
            return build_rule(
                frequency=recurrence["frequency"],
                interval=recurrence.get("interval", 1),
                starts_on=date.fromisoformat(starts_on),
                ends_on=date.fromisoformat(recurrence["ends_on"]),
                weekdays=recurrence.get("weekdays"),
            )
        except ValueError as exc:
            raise ImportValidationError(str(exc)) from exc

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
            # Its attendance no longer counts: milestones it completed may be revoked.
            self._participants.sync_milestones(session, actor_id=actor_id)
            return self.get_activity(session, activity_id, include_archived=True)

    def _require_active_place(self, session: Session, place_id: int | None) -> None:
        if place_id is not None and self._places.get_place(session, place_id) is None:
            raise ConflictError("Il luogo selezionato non è attivo", code="INVALID_ACTIVITY_PLACE")
