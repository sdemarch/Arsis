from collections.abc import Sequence
from typing import Any

from sqlalchemy.orm import Session

from arsis.audit.service import record_audit_event
from arsis.core.database import transaction
from arsis.core.errors import ConflictError, ResourceNotFoundError
from arsis.core.time import utc_now_iso
from arsis.core.versioning import update_versioned
from arsis.generated.models import Place
from arsis.generated.schemas import PlaceCreateDTO, PlaceUpdateDTO
from arsis.places.repository import PlacesRepository


class PlacesService:
    def __init__(self, repository: PlacesRepository | None = None) -> None:
        self._repository = repository or PlacesRepository()

    def list_places(self, session: Session, *, include_archived: bool = False) -> Sequence[Place]:
        return self._repository.list_places(session, include_archived=include_archived)

    def get_place(self, session: Session, place_id: int) -> Place:
        place = self._repository.get_place(session, place_id, active_only=False)
        if place is None:
            raise ResourceNotFoundError("Luogo", place_id)
        return place

    def require_active_place(self, session: Session, place_id: int) -> Place:
        place = self._repository.get_place(session, place_id)
        if place is None:
            raise ConflictError("Il luogo selezionato non è attivo", code="INVALID_ACTIVITY_PLACE")
        return place

    def create_place(self, session: Session, *, data: PlaceCreateDTO, actor_id: int) -> Place:
        values = data.model_dump(exclude_none=True)
        values["name"] = values["name"].strip()
        with transaction(session):
            self._require_unique_name(session, values["name"])
            place = Place(**values, created_by=actor_id, updated_by=actor_id)
            session.add(place)
            session.flush()
            record_audit_event(
                session,
                action="place.created",
                entity_type="place",
                entity_id=place.id,
                user_id=actor_id,
            )
        return place

    def update_place(
        self,
        session: Session,
        *,
        place_id: int,
        data: PlaceUpdateDTO,
        expected_version: int,
        actor_id: int,
    ) -> Place:
        values: dict[str, Any] = data.model_dump(exclude_unset=True)
        for required in ("name", "distance_km", "highway_cost"):
            if required in values and values[required] is None:
                values.pop(required)
        with transaction(session):
            self._get_active(session, place_id)
            if "name" in values:
                values["name"] = values["name"].strip()
                self._require_unique_name(session, values["name"], exclude_id=place_id)
            self._update(session, place_id, values, expected_version, actor_id, action="updated")
            return self.get_place(session, place_id)

    def archive_place(
        self, session: Session, *, place_id: int, expected_version: int, actor_id: int
    ) -> Place:
        with transaction(session):
            self._get_active(session, place_id)
            self._update(
                session,
                place_id,
                {"archived_at": utc_now_iso(), "archived_by": actor_id},
                expected_version,
                actor_id,
                action="archived",
            )
            return self.get_place(session, place_id)

    def _update(
        self,
        session: Session,
        place_id: int,
        values: dict[str, Any],
        expected_version: int,
        actor_id: int,
        *,
        action: str,
    ) -> None:
        if not values:
            return
        values["updated_by"] = actor_id
        update_versioned(
            session,
            Place.__table__,
            resource_name="Luogo",
            resource_id=place_id,
            expected_version=expected_version,
            values=values,
        )
        record_audit_event(
            session,
            action=f"place.{action}",
            entity_type="place",
            entity_id=place_id,
            user_id=actor_id,
            details={"fields": sorted(values)},
        )
        session.flush()
        session.expire_all()

    def _get_active(self, session: Session, place_id: int) -> Place:
        place = self._repository.get_place(session, place_id)
        if place is None:
            raise ResourceNotFoundError("Luogo", place_id)
        return place

    def _require_unique_name(
        self, session: Session, name: str, *, exclude_id: int | None = None
    ) -> None:
        if self._repository.name_taken(session, name, exclude_id=exclude_id):
            raise ConflictError("Esiste già un luogo con questo nome", code="PLACE_NAME_TAKEN")
