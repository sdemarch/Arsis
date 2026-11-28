"""Configurable person roles (RB-21).

The four built-in roles (member, musician, student, teacher) keep their codes and the
behaviour tied to them; they can be renamed and reordered but not archived. Custom roles
can be added, renamed and archived once nobody holds them and no active accounting
category requires them. Codes never change: assignments and categories refer to them.
"""

import re
import unicodedata
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from arsis.audit.service import record_audit_event
from arsis.core.database import transaction
from arsis.core.errors import ConflictError, ResourceNotFoundError
from arsis.core.time import utc_now_iso
from arsis.core.versioning import update_versioned
from arsis.generated.models import RoleType
from arsis.roles.repository import RoleTypesRepository

_MAX_CODE = 50


@dataclass(frozen=True)
class RoleCatalogue:
    """Snapshot of the role catalogue, for validation within one operation."""

    roles: tuple[RoleType, ...]

    @property
    def active(self) -> tuple[RoleType, ...]:
        return tuple(role for role in self.roles if role.archived_at is None)

    def is_assignable(self, code: str) -> bool:
        return any(role.code == code for role in self.active)

    def exists(self, code: str) -> bool:
        return any(role.code == code for role in self.roles)

    def resolve(self, value: str) -> str | None:
        """Code of an active role from its code, name or plural name (any case)."""
        wanted = value.strip().casefold()
        for role in self.active:
            if wanted in {role.code, role.name.casefold(), role.plural_name.casefold()}:
                return role.code
        return None


def slugify(name: str) -> str:
    """ASCII code for a role name: 'Maestro di Banda' -> 'maestro-di-banda'."""
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")
    if not slug or not slug[0].isalpha():
        slug = f"ruolo-{slug}".rstrip("-")
    return slug[:_MAX_CODE].rstrip("-")


class RoleTypesService:
    def __init__(self, repository: RoleTypesRepository | None = None) -> None:
        self._repository = repository or RoleTypesRepository()

    def catalogue(self, session: Session) -> RoleCatalogue:
        return RoleCatalogue(
            tuple(self._repository.list_role_types(session, include_archived=True))
        )

    def list_role_types(
        self, session: Session, *, include_archived: bool = False
    ) -> list[tuple[RoleType, int]]:
        counts = self._repository.active_assignment_counts(session, on_date=utc_now_iso()[:10])
        return [
            (role, counts.get(role.code, 0))
            for role in self._repository.list_role_types(session, include_archived=include_archived)
        ]

    def get_role_type(self, session: Session, role_type_id: int) -> tuple[RoleType, int]:
        role = self._repository.get_role_type(session, role_type_id, active_only=False)
        if role is None:
            raise ResourceNotFoundError("Ruolo", role_type_id)
        counts = self._repository.active_assignment_counts(session, on_date=utc_now_iso()[:10])
        return role, counts.get(role.code, 0)

    def create_role_type(
        self,
        session: Session,
        *,
        name: str,
        plural_name: str,
        description: str | None,
        display_order: int | None,
        actor_id: int,
    ) -> RoleType:
        name, plural_name = name.strip(), plural_name.strip()
        with transaction(session):
            self._require_unique_name(session, name)
            role = RoleType(
                code=self._new_code(session, name),
                name=name,
                plural_name=plural_name,
                description=(description or "").strip() or None,
                is_system=False,
                display_order=(
                    display_order
                    if display_order is not None
                    else self._repository.next_display_order(session)
                ),
                created_by=actor_id,
                updated_by=actor_id,
            )
            session.add(role)
            session.flush()
            record_audit_event(
                session,
                action="role_type.created",
                entity_type="role_type",
                entity_id=role.id,
                user_id=actor_id,
                details={"code": role.code},
            )
        return role

    def update_role_type(
        self,
        session: Session,
        *,
        role_type_id: int,
        values: dict[str, Any],
        expected_version: int,
        actor_id: int,
    ) -> RoleType:
        for required in ("name", "plural_name", "display_order"):
            if required in values and values[required] is None:
                values.pop(required)
        for field in ("name", "plural_name"):
            if field in values:
                values[field] = values[field].strip()
        if "description" in values:
            values["description"] = (values["description"] or "").strip() or None
        with transaction(session):
            self._get_active(session, role_type_id)
            if "name" in values:
                self._require_unique_name(session, values["name"], exclude_id=role_type_id)
            self._update(session, role_type_id, values, expected_version, actor_id, "updated")
            return self._get(session, role_type_id)

    def archive_role_type(
        self, session: Session, *, role_type_id: int, expected_version: int, actor_id: int
    ) -> RoleType:
        with transaction(session):
            role = self._get_active(session, role_type_id)
            if role.is_system:
                raise ConflictError(
                    "I ruoli predefiniti non si possono archiviare: puoi rinominarli",
                    code="ROLE_TYPE_SYSTEM",
                )
            holders = self._repository.active_assignment_counts(
                session, on_date=utc_now_iso()[:10]
            ).get(role.code, 0)
            if holders:
                raise ConflictError(
                    f"{holders} {'persona ha' if holders == 1 else 'persone hanno'} ancora "
                    f"il ruolo {role.name}: chiudi prima i ruoli attivi",
                    code="ROLE_TYPE_IN_USE",
                    details={"active_people": holders},
                )
            categories = self._repository.categories_requiring(session, role.code)
            if categories:
                raise ConflictError(
                    "Il ruolo è richiesto dalle categorie contabili: " + ", ".join(categories),
                    code="ROLE_TYPE_IN_USE",
                    details={"categories": list(categories)},
                )
            self._update(
                session,
                role_type_id,
                {"archived_at": utc_now_iso(), "archived_by": actor_id},
                expected_version,
                actor_id,
                "archived",
            )
            return self._get(session, role_type_id)

    def require_assignable(self, session: Session, code: str) -> None:
        """For callers outside this module (e.g. accounting categories)."""
        if not self.catalogue(session).is_assignable(code):
            raise ConflictError("Il ruolo indicato non è attivo", code="INVALID_ROLE_TYPE")

    def _new_code(self, session: Session, name: str) -> str:
        base = slugify(name)
        code, suffix = base, 2
        while self._repository.code_taken(session, code):
            tail = f"-{suffix}"
            code = f"{base[: _MAX_CODE - len(tail)]}{tail}"
            suffix += 1
        return code

    def _get(self, session: Session, role_type_id: int) -> RoleType:
        role = self._repository.get_role_type(session, role_type_id, active_only=False)
        if role is None:
            raise ResourceNotFoundError("Ruolo", role_type_id)
        return role

    def _get_active(self, session: Session, role_type_id: int) -> RoleType:
        role = self._repository.get_role_type(session, role_type_id)
        if role is None:
            raise ResourceNotFoundError("Ruolo", role_type_id)
        return role

    def _require_unique_name(
        self, session: Session, name: str, *, exclude_id: int | None = None
    ) -> None:
        if self._repository.name_taken(session, name, exclude_id=exclude_id):
            raise ConflictError("Esiste già un ruolo con questo nome", code="ROLE_TYPE_NAME_TAKEN")

    def _update(
        self,
        session: Session,
        role_type_id: int,
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
            RoleType.__table__,
            resource_name="Ruolo",
            resource_id=role_type_id,
            expected_version=expected_version,
            values=values,
        )
        record_audit_event(
            session,
            action=f"role_type.{action}",
            entity_type="role_type",
            entity_id=role_type_id,
            user_id=actor_id,
            details={"fields": sorted(values)},
        )
        session.flush()
        session.expire_all()
