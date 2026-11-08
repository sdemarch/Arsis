from collections.abc import Sequence
from typing import Any

from sqlalchemy.orm import Session

from arsis.audit.service import record_audit_event
from arsis.catalogues.repository import CataloguesRepository
from arsis.core.database import transaction
from arsis.core.errors import ConflictError, ResourceNotFoundError
from arsis.core.time import utc_now_iso
from arsis.core.versioning import update_versioned
from arsis.generated.models import Instrument, Section
from arsis.generated.schemas import (
    InstrumentCreateDTO,
    InstrumentUpdateDTO,
    SectionCreateDTO,
    SectionUpdateDTO,
)


class CataloguesService:
    def __init__(self, repository: CataloguesRepository | None = None) -> None:
        self._repository = repository or CataloguesRepository()

    def list_sections(self, session: Session) -> Sequence[Section]:
        return self._repository.list_sections(session)

    def list_instruments(self, session: Session) -> Sequence[Instrument]:
        return self._repository.list_instruments(session)

    def create_section(self, session: Session, *, data: SectionCreateDTO, actor_id: int) -> Section:
        values = data.model_dump(exclude_none=True)
        values.setdefault("is_active", True)
        with transaction(session):
            section = Section(**values, created_by=actor_id, updated_by=actor_id)
            session.add(section)
            session.flush()
            record_audit_event(
                session,
                action="section.created",
                entity_type="section",
                entity_id=section.id,
                user_id=actor_id,
            )
        return section

    def create_instrument(
        self, session: Session, *, data: InstrumentCreateDTO, actor_id: int
    ) -> Instrument:
        values = data.model_dump(exclude_none=True)
        values.setdefault("is_active", True)
        with transaction(session):
            self._require_active_section(session, int(values["section_id"]))
            instrument = Instrument(**values, created_by=actor_id, updated_by=actor_id)
            session.add(instrument)
            session.flush()
            record_audit_event(
                session,
                action="instrument.created",
                entity_type="instrument",
                entity_id=instrument.id,
                user_id=actor_id,
            )
        return instrument

    def update_section(
        self,
        session: Session,
        *,
        section_id: int,
        data: SectionUpdateDTO,
        expected_version: int,
        actor_id: int,
    ) -> Section:
        values = data.model_dump(exclude_unset=True)
        with transaction(session):
            self._get_section(session, section_id)
            if values.get("is_active") is False and self._repository.section_has_active_instruments(
                session, section_id
            ):
                raise ConflictError(
                    "Disattivare prima gli strumenti della sezione",
                    code="SECTION_HAS_ACTIVE_INSTRUMENTS",
                )
            self._update(
                session, Section, "Sezione", section_id, values, expected_version, actor_id
            )
            return self._get_section(session, section_id)

    def update_instrument(
        self,
        session: Session,
        *,
        instrument_id: int,
        data: InstrumentUpdateDTO,
        expected_version: int,
        actor_id: int,
    ) -> Instrument:
        values = data.model_dump(exclude_unset=True)
        with transaction(session):
            self._get_instrument(session, instrument_id)
            if "section_id" in values and values["section_id"] is not None:
                self._require_active_section(session, int(values["section_id"]))
            self._update(
                session, Instrument, "Strumento", instrument_id, values, expected_version, actor_id
            )
            return self._get_instrument(session, instrument_id)

    def archive_section(
        self, session: Session, *, section_id: int, expected_version: int, actor_id: int
    ) -> Section:
        with transaction(session):
            self._get_section(session, section_id)
            if self._repository.section_has_active_instruments(session, section_id):
                raise ConflictError(
                    "Disattivare prima gli strumenti della sezione",
                    code="SECTION_HAS_ACTIVE_INSTRUMENTS",
                )
            self._archive(session, Section, "Sezione", section_id, expected_version, actor_id)
            section = session.get(Section, section_id)
            if section is None:  # pragma: no cover - protected by _get_section
                raise ResourceNotFoundError("Sezione", section_id)
            return section

    def archive_instrument(
        self, session: Session, *, instrument_id: int, expected_version: int, actor_id: int
    ) -> Instrument:
        with transaction(session):
            self._get_instrument(session, instrument_id)
            self._archive(
                session, Instrument, "Strumento", instrument_id, expected_version, actor_id
            )
            instrument = session.get(Instrument, instrument_id)
            if instrument is None:  # pragma: no cover - protected by _get_instrument
                raise ResourceNotFoundError("Strumento", instrument_id)
            return instrument

    def _archive(
        self,
        session: Session,
        model: type[Any],
        resource_name: str,
        resource_id: int,
        expected_version: int,
        actor_id: int,
    ) -> None:
        self._update(
            session,
            model,
            resource_name,
            resource_id,
            {"is_active": False, "archived_at": utc_now_iso(), "archived_by": actor_id},
            expected_version,
            actor_id,
            action="archived",
        )

    def _update(
        self,
        session: Session,
        model: type[Any],
        resource_name: str,
        resource_id: int,
        values: dict[str, Any],
        expected_version: int,
        actor_id: int,
        *,
        action: str = "updated",
    ) -> None:
        if not values:
            return
        values["updated_by"] = actor_id
        update_versioned(
            session,
            model.__table__,
            resource_name=resource_name,
            resource_id=resource_id,
            expected_version=expected_version,
            values=values,
        )
        record_audit_event(
            session,
            action=f"{resource_name.lower()}.{action}",
            entity_type=resource_name.lower(),
            entity_id=resource_id,
            user_id=actor_id,
            details={"fields": sorted(values)},
        )
        session.flush()
        session.expire_all()

    def _get_section(self, session: Session, section_id: int) -> Section:
        section = self._repository.get_section(session, section_id)
        if section is None:
            raise ResourceNotFoundError("Sezione", section_id)
        return section

    def _get_instrument(self, session: Session, instrument_id: int) -> Instrument:
        instrument = self._repository.get_instrument(session, instrument_id)
        if instrument is None:
            raise ResourceNotFoundError("Strumento", instrument_id)
        return instrument

    def _require_active_section(self, session: Session, section_id: int) -> None:
        if self._repository.get_section(session, section_id, active_only=True) is None:
            raise ConflictError(
                "La sezione selezionata non è attiva", code="INVALID_INSTRUMENT_SECTION"
            )
