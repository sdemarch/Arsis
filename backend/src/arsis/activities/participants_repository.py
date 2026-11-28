"""Persistence operations for activity participants and their attendance."""

from collections.abc import Sequence

from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.orm import Session

from arsis.generated.models import Activity, ActivityParticipant, Person


class ParticipantsRepository:
    def register(
        self, session: Session, *, activity_id: int
    ) -> Sequence[tuple[Person, ActivityParticipant | None]]:
        """Every active person, plus archived ones with attendance already recorded."""
        rows = session.execute(
            select(Person, ActivityParticipant)
            .outerjoin(
                ActivityParticipant,
                and_(
                    ActivityParticipant.person_id == Person.id,
                    ActivityParticipant.activity_id == activity_id,
                    ActivityParticipant.archived_at.is_(None),
                ),
            )
            .where(or_(Person.archived_at.is_(None), ActivityParticipant.attendance.is_not(None)))
            .order_by(func.lower(Person.last_name), func.lower(Person.first_name), Person.id)
        ).all()
        return [(person, participant) for person, participant in rows]

    def get_by_person(
        self, session: Session, *, activity_id: int, person_id: int
    ) -> ActivityParticipant | None:
        """The participant row for a person, including one removed earlier."""
        return session.scalar(
            select(ActivityParticipant).where(
                ActivityParticipant.activity_id == activity_id,
                ActivityParticipant.person_id == person_id,
            )
        )

    def counts(
        self, session: Session, *, activity_ids: Sequence[int]
    ) -> dict[int, tuple[int, int, int]]:
        """Recorded attendance, present and absent per activity."""
        if not activity_ids:
            return {}
        rows = session.execute(
            select(
                ActivityParticipant.activity_id,
                func.count(ActivityParticipant.attendance),
                func.sum(case((ActivityParticipant.attendance == "present", 1), else_=0)),
                func.sum(case((ActivityParticipant.attendance == "absent", 1), else_=0)),
            )
            .where(
                ActivityParticipant.activity_id.in_(activity_ids),
                ActivityParticipant.archived_at.is_(None),
            )
            .group_by(ActivityParticipant.activity_id)
        ).all()
        return {
            activity_id: (int(total), int(present or 0), int(absent or 0))
            for activity_id, total, present, absent in rows
        }

    def present_on_activities(
        self, session: Session, *, activity_ids: Sequence[int]
    ) -> Sequence[ActivityParticipant]:
        if not activity_ids:
            return []
        return session.scalars(
            select(ActivityParticipant).where(
                ActivityParticipant.activity_id.in_(activity_ids),
                ActivityParticipant.attendance == "present",
                ActivityParticipant.archived_at.is_(None),
            )
        ).all()

    def participations(
        self, session: Session, *, person_id: int
    ) -> Sequence[tuple[ActivityParticipant, Activity]]:
        rows = session.execute(
            select(ActivityParticipant, Activity)
            .join(Activity, Activity.id == ActivityParticipant.activity_id)
            .where(
                ActivityParticipant.person_id == person_id,
                ActivityParticipant.archived_at.is_(None),
                Activity.archived_at.is_(None),
            )
            .order_by(Activity.starts_at.desc(), Activity.id.desc())
        ).all()
        return [(participant, activity) for participant, activity in rows]

    def present_participations(
        self, session: Session
    ) -> Sequence[tuple[ActivityParticipant, Activity, Person]]:
        rows = session.execute(
            select(ActivityParticipant, Activity, Person)
            .join(Activity, Activity.id == ActivityParticipant.activity_id)
            .join(Person, Person.id == ActivityParticipant.person_id)
            .where(
                ActivityParticipant.attendance == "present",
                ActivityParticipant.archived_at.is_(None),
                Activity.archived_at.is_(None),
            )
            .order_by(func.lower(Person.last_name), func.lower(Person.first_name), Person.id)
        ).all()
        return [(participant, activity, person) for participant, activity, person in rows]
