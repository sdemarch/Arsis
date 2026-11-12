"""Persistence operations for activity participants and their attendance."""

from collections.abc import Sequence

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from arsis.generated.models import Activity, ActivityParticipant, Person, PersonRole


class ParticipantsRepository:
    def list_participants(
        self, session: Session, *, activity_id: int
    ) -> Sequence[tuple[ActivityParticipant, Person]]:
        rows = session.execute(
            select(ActivityParticipant, Person)
            .join(Person, Person.id == ActivityParticipant.person_id)
            .where(
                ActivityParticipant.activity_id == activity_id,
                ActivityParticipant.archived_at.is_(None),
            )
            .order_by(func.lower(Person.last_name), func.lower(Person.first_name), Person.id)
        ).all()
        return [(participant, person) for participant, person in rows]

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

    def person_ids_on_activity(self, session: Session, *, activity_id: int) -> set[int]:
        """Everyone with a row on the activity, removed participants included."""
        return set(
            session.scalars(
                select(ActivityParticipant.person_id).where(
                    ActivityParticipant.activity_id == activity_id
                )
            )
        )

    def active_musician_ids(self, session: Session, *, on_date: str) -> Sequence[int]:
        return session.scalars(
            select(Person.id)
            .join(PersonRole, PersonRole.person_id == Person.id)
            .where(
                Person.archived_at.is_(None),
                PersonRole.role_type == "musician",
                PersonRole.status == "active",
                PersonRole.archived_at.is_(None),
                PersonRole.start_date <= on_date,
                or_(PersonRole.end_date.is_(None), PersonRole.end_date >= on_date),
            )
            .distinct()
            .order_by(Person.id)
        ).all()

    def get_active_person(self, session: Session, person_id: int) -> Person | None:
        return session.scalar(
            select(Person).where(Person.id == person_id, Person.archived_at.is_(None))
        )

    def counts(
        self, session: Session, *, activity_ids: Sequence[int]
    ) -> dict[int, tuple[int, int, int]]:
        """Participants, present and absent per activity."""
        if not activity_ids:
            return {}
        rows = session.execute(
            select(
                ActivityParticipant.activity_id,
                func.count(),
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
