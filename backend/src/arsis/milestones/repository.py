"""Persistence operations for milestones and their reset ledger."""

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from arsis.generated.models import Milestone, MilestoneReset


class MilestonesRepository:
    def list_milestones(
        self, session: Session, *, include_archived: bool = False
    ) -> Sequence[Milestone]:
        statement = select(Milestone)
        if not include_archived:
            statement = statement.where(Milestone.archived_at.is_(None))
        return session.scalars(statement.order_by(func.lower(Milestone.name), Milestone.id)).all()

    def get_milestone(
        self, session: Session, milestone_id: int, *, active_only: bool = True
    ) -> Milestone | None:
        statement = select(Milestone).where(Milestone.id == milestone_id)
        if active_only:
            statement = statement.where(Milestone.archived_at.is_(None))
        return session.scalar(statement)

    def name_taken(self, session: Session, name: str, *, exclude_id: int | None = None) -> bool:
        statement = select(Milestone.id).where(
            func.lower(Milestone.name) == name.strip().lower(), Milestone.archived_at.is_(None)
        )
        if exclude_id is not None:
            statement = statement.where(Milestone.id != exclude_id)
        return session.scalar(statement) is not None

    def active_resets(
        self, session: Session, *, milestone_ids: Sequence[int]
    ) -> Sequence[MilestoneReset]:
        if not milestone_ids:
            return []
        return session.scalars(
            select(MilestoneReset)
            .where(
                MilestoneReset.milestone_id.in_(milestone_ids),
                MilestoneReset.archived_at.is_(None),
            )
            .order_by(MilestoneReset.id)
        ).all()

    def get_reset(
        self, session: Session, *, milestone_id: int, reset_id: int
    ) -> MilestoneReset | None:
        return session.scalar(
            select(MilestoneReset).where(
                MilestoneReset.id == reset_id,
                MilestoneReset.milestone_id == milestone_id,
                MilestoneReset.archived_at.is_(None),
            )
        )
