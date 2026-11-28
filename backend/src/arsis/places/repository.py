from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from arsis.generated.models import Place


class PlacesRepository:
    def list_places(self, session: Session, *, include_archived: bool = False) -> Sequence[Place]:
        statement = select(Place)
        if not include_archived:
            statement = statement.where(Place.archived_at.is_(None))
        return session.scalars(statement.order_by(func.lower(Place.name), Place.id)).all()

    def get_place(
        self, session: Session, place_id: int, *, active_only: bool = True
    ) -> Place | None:
        statement = select(Place).where(Place.id == place_id)
        if active_only:
            statement = statement.where(Place.archived_at.is_(None))
        return session.scalar(statement)

    def name_taken(self, session: Session, name: str, *, exclude_id: int | None = None) -> bool:
        statement = select(Place.id).where(
            func.lower(Place.name) == name.strip().lower(), Place.archived_at.is_(None)
        )
        if exclude_id is not None:
            statement = statement.where(Place.id != exclude_id)
        return session.scalar(statement) is not None
