"""Persistence operations for milestones and their reset ledger."""

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from arsis.generated.models import Milestone, MilestoneAchievement, MilestoneReset, Person


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

    def open_achievements(
        self, session: Session, *, milestone_ids: Sequence[int]
    ) -> Sequence[MilestoneAchievement]:
        if not milestone_ids:
            return []
        return session.scalars(
            select(MilestoneAchievement)
            .where(
                MilestoneAchievement.milestone_id.in_(milestone_ids),
                MilestoneAchievement.status == "open",
            )
            .order_by(MilestoneAchievement.id)
        ).all()

    def achievement_for_reset(
        self, session: Session, *, reset_id: int
    ) -> MilestoneAchievement | None:
        return session.scalar(
            select(MilestoneAchievement).where(MilestoneAchievement.reset_id == reset_id)
        )

    def list_achievements(
        self,
        session: Session,
        *,
        status: str | None = None,
        milestone_id: int | None = None,
        person_id: int | None = None,
        limit: int = 200,
    ) -> Sequence[tuple[MilestoneAchievement, Milestone, Person]]:
        statement = (
            select(MilestoneAchievement, Milestone, Person)
            .join(Milestone, Milestone.id == MilestoneAchievement.milestone_id)
            .join(Person, Person.id == MilestoneAchievement.person_id)
        )
        if status is not None:
            statement = statement.where(MilestoneAchievement.status == status)
        if status == "open":
            # Archived milestones and people no longer have anything to celebrate.
            statement = statement.where(
                Milestone.archived_at.is_(None), Person.archived_at.is_(None)
            )
        if milestone_id is not None:
            statement = statement.where(MilestoneAchievement.milestone_id == milestone_id)
        if person_id is not None:
            statement = statement.where(MilestoneAchievement.person_id == person_id)
        rows = session.execute(
            statement.order_by(
                MilestoneAchievement.reached_at.desc(), MilestoneAchievement.id.desc()
            ).limit(limit)
        ).all()
        return [(achievement, milestone, person) for achievement, milestone, person in rows]

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
