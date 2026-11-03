from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from arsis.generated.models import Instrument, Section


class CataloguesRepository:
    def list_sections(
        self, session: Session, *, include_archived: bool = False
    ) -> Sequence[Section]:
        statement = select(Section)
        if not include_archived:
            statement = statement.where(Section.archived_at.is_(None))
        return session.scalars(
            statement.order_by(Section.display_order, func.lower(Section.name))
        ).all()

    def list_instruments(
        self, session: Session, *, include_archived: bool = False
    ) -> Sequence[Instrument]:
        statement = select(Instrument)
        if not include_archived:
            statement = statement.where(Instrument.archived_at.is_(None))
        return session.scalars(
            statement.order_by(Instrument.display_order, func.lower(Instrument.name))
        ).all()

    def get_section(
        self, session: Session, section_id: int, *, active_only: bool = False
    ) -> Section | None:
        statement = select(Section).where(Section.id == section_id, Section.archived_at.is_(None))
        if active_only:
            statement = statement.where(Section.is_active.is_(True))
        return session.scalar(statement)

    def get_instrument(self, session: Session, instrument_id: int) -> Instrument | None:
        return session.scalar(
            select(Instrument).where(
                Instrument.id == instrument_id, Instrument.archived_at.is_(None)
            )
        )

    def section_has_active_instruments(self, session: Session, section_id: int) -> bool:
        return (
            session.scalar(
                select(Instrument.id).where(
                    Instrument.section_id == section_id,
                    Instrument.is_active.is_(True),
                    Instrument.archived_at.is_(None),
                )
            )
            is not None
        )
