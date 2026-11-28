"""Milestones on attendance and reimbursements, and their per-person resets (RB-19).

Progress is derived from recorded attendance and its reimbursement snapshot, so a new
milestone counts the whole history. A reset consumes one threshold from a person's
progress and keeps the excess.

Every time a person covers a threshold an *achievement* is logged (RB-20). Achievements
stay open until a reset consumes them, or are revoked when progress drops below them
(attendance removed, activity archived, threshold raised). ``sync_achievements`` keeps
the log aligned and runs inside every write that can change progress.
"""

from collections import defaultdict
from collections.abc import Sequence
from decimal import Decimal
from typing import Any, TypedDict

from sqlalchemy.orm import Session

from arsis.activities.participants_repository import ParticipantsRepository
from arsis.activities.reimbursements import ReimbursementBreakdown, money
from arsis.audit.service import record_audit_event
from arsis.core.database import transaction
from arsis.core.errors import ConflictError, ImportValidationError, ResourceNotFoundError
from arsis.core.time import utc_now_iso
from arsis.core.versioning import update_versioned
from arsis.generated.models import Milestone, MilestoneAchievement, MilestoneReset, Person
from arsis.generated.schemas import MilestoneCreateDTO, MilestoneUpdateDTO
from arsis.milestones.repository import MilestonesRepository
from arsis.milestones.schemas import COUNT_METRICS

_ONE = Decimal(1)
_ZERO = Decimal(0)
_TYPE_METRICS = {
    "rehearsal": "rehearsal_count",
    "concert": "concert_count",
    "event": "event_count",
}


class ProgressRow(TypedDict):
    person_id: int
    person_name: str
    progress: Decimal
    remaining: Decimal
    times_reached: int
    reached_at: str | None
    last_reset_id: int | None
    last_reset_at: str | None


class AchievementRow(TypedDict):
    id: int
    milestone_id: int
    milestone_name: str
    metric: str
    threshold: Decimal
    person_id: int
    person_name: str
    reached_at: str
    progress: Decimal
    status: str
    closed_at: str | None
    reset_id: int | None


class BoardEntry(TypedDict):
    milestone: Milestone
    reached: list[ProgressRow]
    in_progress: list[ProgressRow]


class _Totals:
    """Lifetime metric values per active person."""

    def __init__(self) -> None:
        self.names: dict[int, str] = {}
        self.values: dict[int, dict[str, Decimal]] = defaultdict(lambda: defaultdict(Decimal))


def progress_of(total: Decimal, consumed: Decimal, threshold: Decimal) -> tuple[Decimal, int]:
    """Current progress and how many times the threshold is covered."""
    progress = money(max(total - consumed, _ZERO))
    return progress, int(progress // threshold)


class MilestonesService:
    def __init__(
        self,
        repository: MilestonesRepository | None = None,
        participants: ParticipantsRepository | None = None,
    ) -> None:
        self._repository = repository or MilestonesRepository()
        self._participants = participants or ParticipantsRepository()

    # Configuration ------------------------------------------------------------------

    def list_milestones(
        self, session: Session, *, include_archived: bool = False
    ) -> Sequence[Milestone]:
        return self._repository.list_milestones(session, include_archived=include_archived)

    def get_milestone(self, session: Session, milestone_id: int) -> Milestone:
        milestone = self._repository.get_milestone(session, milestone_id, active_only=False)
        if milestone is None:
            raise ResourceNotFoundError("Obiettivo", milestone_id)
        return milestone

    def create_milestone(
        self, session: Session, *, data: MilestoneCreateDTO, actor_id: int
    ) -> Milestone:
        values = data.model_dump(exclude_none=True)
        values["name"] = values["name"].strip()
        values["threshold"] = money(values["threshold"])
        _check_threshold(values["metric"], values["threshold"])
        with transaction(session):
            self._require_unique_name(session, values["name"])
            milestone = Milestone(**values, created_by=actor_id, updated_by=actor_id)
            session.add(milestone)
            session.flush()
            record_audit_event(
                session,
                action="milestone.created",
                entity_type="milestone",
                entity_id=milestone.id,
                user_id=actor_id,
            )
            # History counts: whoever is already past the threshold is logged now.
            self.sync_achievements(session, actor_id=actor_id)
        return milestone

    def update_milestone(
        self,
        session: Session,
        *,
        milestone_id: int,
        data: MilestoneUpdateDTO,
        expected_version: int,
        actor_id: int,
    ) -> Milestone:
        values: dict[str, Any] = data.model_dump(exclude_unset=True)
        for required in ("name", "metric", "threshold"):
            if required in values and values[required] is None:
                values.pop(required)
        if "threshold" in values:
            values["threshold"] = money(values["threshold"])
        with transaction(session):
            current = self._get_active(session, milestone_id)
            _check_threshold(
                values.get("metric", current.metric), values.get("threshold", current.threshold)
            )
            if "name" in values:
                values["name"] = values["name"].strip()
                self._require_unique_name(session, values["name"], exclude_id=milestone_id)
            self._update(session, milestone_id, values, expected_version, actor_id, "updated")
            self.sync_achievements(session, actor_id=actor_id)
            return self.get_milestone(session, milestone_id)

    def archive_milestone(
        self, session: Session, *, milestone_id: int, expected_version: int, actor_id: int
    ) -> Milestone:
        with transaction(session):
            self._get_active(session, milestone_id)
            self._update(
                session,
                milestone_id,
                {"archived_at": utc_now_iso(), "archived_by": actor_id},
                expected_version,
                actor_id,
                "archived",
            )
            return self.get_milestone(session, milestone_id)

    # Board and resets ---------------------------------------------------------------

    def board(
        self, session: Session, *, milestone_ids: Sequence[int] | None = None
    ) -> list[BoardEntry]:
        milestones = [
            milestone
            for milestone in self._repository.list_milestones(session)
            if milestone_ids is None or milestone.id in milestone_ids
        ]
        ids = [milestone.id for milestone in milestones]
        totals = self._totals(session)
        resets = self._resets_by_key(session, ids)
        first_open: dict[tuple[int, int], str] = {}
        for row in self._repository.open_achievements(session, milestone_ids=ids):
            first_open.setdefault((row.milestone_id, row.person_id), row.reached_at)
        return [self._entry(milestone, totals, resets, first_open) for milestone in milestones]

    def achievements(
        self,
        session: Session,
        *,
        status: str | None = None,
        milestone_id: int | None = None,
        person_id: int | None = None,
        limit: int = 200,
    ) -> list[AchievementRow]:
        return [
            _achievement_row(achievement, milestone, person)
            for achievement, milestone, person in self._repository.list_achievements(
                session, status=status, milestone_id=milestone_id, person_id=person_id, limit=limit
            )
        ]

    def sync_achievements(self, session: Session, *, actor_id: int | None) -> int:
        """Align the achievement log with current progress (caller's transaction).

        Opens one achievement per threshold newly covered and revokes the newest open ones
        when progress no longer covers them. Returns the number of rows changed.
        """
        milestones = self._repository.list_milestones(session)
        if not milestones:
            return 0
        ids = [milestone.id for milestone in milestones]
        totals = self._totals(session)
        resets = self._resets_by_key(session, ids)
        open_rows: dict[tuple[int, int], list[MilestoneAchievement]] = {}
        for row in self._repository.open_achievements(session, milestone_ids=ids):
            open_rows.setdefault((row.milestone_id, row.person_id), []).append(row)
        now = utc_now_iso()
        changed = 0
        for milestone in milestones:
            own_resets = resets.get(milestone.id, {})
            people = set(totals.names) | {pid for mid, pid in open_rows if mid == milestone.id}
            for person_id in sorted(people):
                consumed = sum((r.consumed for r in own_resets.get(person_id, [])), _ZERO)
                # People no longer active (or with no attendance left) cover nothing.
                active = person_id in totals.names
                total = totals.values[person_id][milestone.metric] if active else _ZERO
                progress, times = progress_of(total, consumed, milestone.threshold)
                current = open_rows.get((milestone.id, person_id), [])
                for _ in range(times - len(current)):
                    session.add(
                        MilestoneAchievement(
                            milestone_id=milestone.id,
                            person_id=person_id,
                            reached_at=now,
                            progress=progress,
                            created_by=actor_id,
                        )
                    )
                    record_audit_event(
                        session,
                        action="milestone.reached",
                        entity_type="milestone",
                        entity_id=milestone.id,
                        user_id=actor_id,
                        details={"person_id": person_id, "progress": str(progress)},
                    )
                    changed += 1
                for row in reversed(current[times:]):
                    row.status = "revoked"
                    row.closed_at = now
                    record_audit_event(
                        session,
                        action="milestone.revoked",
                        entity_type="milestone",
                        entity_id=milestone.id,
                        user_id=actor_id,
                        details={"person_id": person_id, "achievement_id": row.id},
                    )
                    changed += 1
        if changed:
            session.flush()
        return changed

    def reset(
        self, session: Session, *, milestone_id: int, person_ids: Sequence[int], actor_id: int
    ) -> BoardEntry:
        with transaction(session):
            milestone = self._get_active(session, milestone_id)
            self.sync_achievements(session, actor_id=actor_id)
            open_rows: dict[int, list[MilestoneAchievement]] = {}
            for achievement in self._repository.open_achievements(
                session, milestone_ids=[milestone.id]
            ):
                open_rows.setdefault(achievement.person_id, []).append(achievement)
            totals = self._totals(session)
            resets = self._resets_by_key(session, [milestone.id]).get(milestone.id, {})
            for person_id in dict.fromkeys(person_ids):
                if person_id not in totals.names:
                    raise ImportValidationError(
                        "La persona non è attiva in anagrafica", details={"person_id": person_id}
                    )
                consumed = sum((r.consumed for r in resets.get(person_id, [])), _ZERO)
                total = totals.values[person_id][milestone.metric]
                progress, times = progress_of(total, consumed, milestone.threshold)
                if times < 1:
                    raise ConflictError(
                        f"{totals.names[person_id]} non ha ancora raggiunto l'obiettivo",
                        code="MILESTONE_NOT_REACHED",
                        details={"person_id": person_id, "progress": str(progress)},
                    )
                reset_row = MilestoneReset(
                    milestone_id=milestone.id,
                    person_id=person_id,
                    consumed=milestone.threshold,
                    progress_before=progress,
                    created_by=actor_id,
                )
                session.add(reset_row)
                session.flush()
                # The reset consumes the oldest open achievement.
                pending = open_rows.get(person_id)
                if pending:
                    oldest = pending.pop(0)
                    oldest.status = "reset"
                    oldest.reset_id = reset_row.id
                    oldest.closed_at = utc_now_iso()
            session.flush()
            self.sync_achievements(session, actor_id=actor_id)
            record_audit_event(
                session,
                action="milestone.reset",
                entity_type="milestone",
                entity_id=milestone.id,
                user_id=actor_id,
                details={"person_ids": sorted(set(person_ids))},
            )
        return self.board(session, milestone_ids=[milestone_id])[0]

    def undo_reset(
        self, session: Session, *, milestone_id: int, reset_id: int, actor_id: int
    ) -> BoardEntry:
        with transaction(session):
            self._get_active(session, milestone_id)
            row = self._repository.get_reset(session, milestone_id=milestone_id, reset_id=reset_id)
            if row is None:
                raise ResourceNotFoundError("Azzeramento", reset_id)
            row.archived_at = utc_now_iso()
            row.archived_by = actor_id
            achievement = self._repository.achievement_for_reset(session, reset_id=row.id)
            if achievement is not None:
                # The achievement the reset had consumed is open again, with its date.
                achievement.status = "open"
                achievement.reset_id = None
                achievement.closed_at = None
            session.flush()
            self.sync_achievements(session, actor_id=actor_id)
            record_audit_event(
                session,
                action="milestone.reset_undone",
                entity_type="milestone",
                entity_id=milestone_id,
                user_id=actor_id,
                details={"reset_id": reset_id, "person_id": row.person_id},
            )
        return self.board(session, milestone_ids=[milestone_id])[0]

    # Internals ----------------------------------------------------------------------

    def _totals(self, session: Session) -> _Totals:
        totals = _Totals()
        for participant, activity, person in self._participants.present_participations(session):
            if person.archived_at is not None:
                continue
            totals.names[person.id] = f"{person.first_name} {person.last_name}"
            values = totals.values[person.id]
            values["attendance_count"] += _ONE
            type_metric = _TYPE_METRICS.get(activity.type)
            if type_metric is not None:
                values[type_metric] += _ONE
            values["reimbursement_total"] += ReimbursementBreakdown.of(participant).total
        return totals

    def _resets_by_key(
        self, session: Session, milestone_ids: Sequence[int]
    ) -> dict[int, dict[int, list[MilestoneReset]]]:
        """Active resets by milestone, then person, oldest first."""
        grouped: dict[int, dict[int, list[MilestoneReset]]] = {}
        for row in self._repository.active_resets(session, milestone_ids=milestone_ids):
            grouped.setdefault(row.milestone_id, {}).setdefault(row.person_id, []).append(row)
        return grouped

    def _entry(
        self,
        milestone: Milestone,
        totals: _Totals,
        resets: dict[int, dict[int, list[MilestoneReset]]],
        first_open: dict[tuple[int, int], str],
    ) -> BoardEntry:
        own = resets.get(milestone.id, {})
        reached: list[ProgressRow] = []
        in_progress: list[ProgressRow] = []
        for person_id, name in totals.names.items():
            person_resets = own.get(person_id, [])
            consumed = sum((r.consumed for r in person_resets), _ZERO)
            total = totals.values[person_id][milestone.metric]
            progress, times = progress_of(total, consumed, milestone.threshold)
            if progress <= 0 and not person_resets:
                continue
            last = person_resets[-1] if person_resets else None
            row: ProgressRow = {
                "person_id": person_id,
                "person_name": name,
                "progress": progress,
                "remaining": money(max(milestone.threshold - progress, _ZERO)),
                "times_reached": times,
                "reached_at": first_open.get((milestone.id, person_id)) if times >= 1 else None,
                "last_reset_id": last.id if last else None,
                "last_reset_at": last.created_at if last else None,
            }
            (reached if times >= 1 else in_progress).append(row)
        reached.sort(
            key=lambda r: (-r["times_reached"], -r["progress"], r["person_name"].casefold())
        )
        in_progress.sort(key=lambda r: (-r["progress"], r["person_name"].casefold()))
        return {"milestone": milestone, "reached": reached, "in_progress": in_progress}

    def _get_active(self, session: Session, milestone_id: int) -> Milestone:
        milestone = self._repository.get_milestone(session, milestone_id)
        if milestone is None:
            raise ResourceNotFoundError("Obiettivo", milestone_id)
        return milestone

    def _require_unique_name(
        self, session: Session, name: str, *, exclude_id: int | None = None
    ) -> None:
        if self._repository.name_taken(session, name, exclude_id=exclude_id):
            raise ConflictError(
                "Esiste già un obiettivo con questo nome", code="MILESTONE_NAME_TAKEN"
            )

    def _update(
        self,
        session: Session,
        milestone_id: int,
        values: dict[str, Any],
        expected_version: int,
        actor_id: int,
        action: str,
    ) -> None:
        if not values:
            return
        values["updated_by"] = actor_id
        update_versioned(
            session,
            Milestone.__table__,
            resource_name="Obiettivo",
            resource_id=milestone_id,
            expected_version=expected_version,
            values=values,
        )
        record_audit_event(
            session,
            action=f"milestone.{action}",
            entity_type="milestone",
            entity_id=milestone_id,
            user_id=actor_id,
            details={"fields": sorted(values)},
        )
        session.flush()
        session.expire_all()


def _achievement_row(
    achievement: MilestoneAchievement, milestone: Milestone, person: Person
) -> AchievementRow:
    return {
        "id": achievement.id,
        "milestone_id": milestone.id,
        "milestone_name": milestone.name,
        "metric": milestone.metric,
        "threshold": milestone.threshold,
        "person_id": person.id,
        "person_name": f"{person.first_name} {person.last_name}",
        "reached_at": achievement.reached_at,
        "progress": achievement.progress,
        "status": achievement.status,
        "closed_at": achievement.closed_at,
        "reset_id": achievement.reset_id,
    }


def _check_threshold(metric: str, threshold: Decimal) -> None:
    if metric in COUNT_METRICS and threshold != threshold.to_integral_value():
        raise ImportValidationError(
            "Per gli obiettivi sulle presenze la soglia deve essere un numero intero",
            details={"threshold": str(threshold)},
        )
