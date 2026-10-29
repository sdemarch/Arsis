"""Persistence operations for activities."""

from collections.abc import Sequence

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from arsis.generated.models import Activity


class ActivitiesRepository:
    def get_activity(
        self, session: Session, activity_id: int, *, include_archived: bool = False
    ) -> Activity | None:
        statement = select(Activity).where(Activity.id == activity_id)
        if not include_archived:
            statement = statement.where(Activity.archived_at.is_(None))
        return session.scalar(statement)

    def list_activities(
        self, session: Session, *, search: str | None = None, include_archived: bool = False
    ) -> Sequence[Activity]:
        statement: Select[tuple[Activity]] = select(Activity)
        if not include_archived:
            statement = statement.where(Activity.archived_at.is_(None))
        if search and (query := search.strip()):
            pattern = f"%{query.casefold()}%"
            statement = statement.where(
                or_(
                    func.lower(Activity.title).like(pattern),
                    func.lower(Activity.location).like(pattern),
                )
            )
        return session.scalars(
            statement.order_by(Activity.starts_at.desc(), Activity.id.desc())
        ).all()

    def add_activity(self, session: Session, activity: Activity) -> Activity:
        session.add(activity)
        return activity
