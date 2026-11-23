"""Business operations for people and their roles."""

from collections.abc import Sequence
from copy import copy
from io import BytesIO

from openpyxl import Workbook, load_workbook  # type: ignore[import-untyped]
from sqlalchemy.orm import Session

from arsis.audit.service import record_audit_event
from arsis.core.database import transaction
from arsis.core.errors import ConflictError, ImportValidationError, ResourceNotFoundError
from arsis.core.time import utc_now_iso
from arsis.core.versioning import update_versioned
from arsis.generated.models import Person, PersonRole
from arsis.generated.schemas import (
    PersonCreateDTO,
    PersonRoleCreateDTO,
    PersonRoleUpdateDTO,
    PersonUpdateDTO,
)
from arsis.people.repository import PeopleRepository

_ROLE_DEFINITIONS: dict[str, tuple[str, tuple[str, ...]]] = {
    "member": ("Socio", ("socio",)),
    "musician": ("Musicante", ("musicante",)),
    "student": ("Allievo", ("allievo",)),
    "teacher": ("Insegnante", ("insegnante",)),
}
_ROLE_TYPES = set(_ROLE_DEFINITIONS)
_ROLE_STATUSES = {"active", "inactive"}
_ROLE_ALIASES = {
    alias: role_type
    for role_type, definition in _ROLE_DEFINITIONS.items()
    for alias in (role_type, *definition[1])
}
_IMPORT_HEADERS = {"first_name", "last_name"}
_MAX_IMPORT_BYTES = 5 * 1024 * 1024


class PeopleService:
    def __init__(self, repository: PeopleRepository | None = None) -> None:
        self._repository = repository or PeopleRepository()

    def list_people(
        self,
        session: Session,
        *,
        search: str | None = None,
        include_archived: bool = False,
    ) -> Sequence[Person]:
        return self._repository.list_people(
            session, search=search, include_archived=include_archived
        )

    def get_person(self, session: Session, person_id: int) -> Person:
        person = self._repository.get_person(session, person_id)
        if person is None:
            raise ResourceNotFoundError("Persona", person_id)
        return person

    def create_person(
        self, session: Session, *, data: PersonCreateDTO, actor_id: int, roles: Sequence[str] = ()
    ) -> Person:
        normalized_roles = self._validate_roles(roles)
        with transaction(session):
            person = self._repository.add_person(
                session,
                Person(
                    **data.model_dump(),
                    created_by=actor_id,
                    updated_by=actor_id,
                ),
            )
            session.flush()
            for role_type in normalized_roles:
                self._repository.add_role(
                    session,
                    PersonRole(
                        person_id=person.id,
                        role_type=role_type,
                        start_date=utc_now_iso()[:10],
                        status="active",
                        created_by=actor_id,
                        updated_by=actor_id,
                    ),
                )
            record_audit_event(
                session,
                action="person.created",
                entity_type="person",
                entity_id=person.id,
                user_id=actor_id,
            )
        return person

    def import_excel(self, session: Session, *, content: bytes, actor_id: int) -> int:
        if len(content) > _MAX_IMPORT_BYTES:
            raise ImportValidationError("Il file Excel supera la dimensione massima di 5 MB")
        rows = self._parse_excel(content)
        with transaction(session):
            for data, roles in rows:
                person = self._repository.add_person(
                    session, Person(**data.model_dump(), created_by=actor_id, updated_by=actor_id)
                )
                session.flush()
                for role_type in roles:
                    self._repository.add_role(
                        session,
                        PersonRole(
                            person_id=person.id, role_type=role_type,
                            start_date=utc_now_iso()[:10], status="active",
                            created_by=actor_id, updated_by=actor_id,
                        ),
                    )
                record_audit_event(
                    session, action="person.imported", entity_type="person", entity_id=person.id,
                    user_id=actor_id,
                )
        return len(rows)

    def build_import_template(self) -> bytes:
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Anagrafiche"
        headers = [
            "first_name", "last_name", "birth_date", "birth_place", "tax_code",
            "residence_address", "email", "phone", "notes", "roles",
        ]
        worksheet.append(headers)
        worksheet.append(["Mario", "Rossi", "", "", "", "", "", "", "", "member, musician"])
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = "A1:J2"
        for cell in worksheet[1]:
            font = copy(cell.font)
            font.bold = True
            cell.font = font
        for column in worksheet.columns:
            letter = column[0].column_letter
            worksheet.column_dimensions[letter].width = 20

        legend = workbook.create_sheet("Legenda")
        legend.append(["Campo", "Indicazioni"])
        legend.append(["first_name", "Obbligatorio: nome della persona"])
        legend.append(["last_name", "Obbligatorio: cognome della persona"])
        legend.append(["birth_date", "Facoltativo: data nel formato AAAA-MM-GG"])
        legend.append(
            ["roles", "Facoltativo: uno o più ruoli, separati da virgola o punto e virgola"]
        )
        legend.append([])
        legend.append(["Ruolo ammesso", "Valore tecnico"])
        for role_type, definition in _ROLE_DEFINITIONS.items():
            legend.append([definition[0], role_type])
        legend.freeze_panes = "A2"
        legend.column_dimensions["A"].width = 28
        legend.column_dimensions["B"].width = 70
        for row_number in (1, 7):
            for cell in legend[row_number]:
                font = copy(cell.font)
                font.bold = True
                cell.font = font
        output = BytesIO()
        workbook.save(output)
        return output.getvalue()

    def update_person(
        self,
        session: Session,
        *,
        person_id: int,
        data: PersonUpdateDTO,
        expected_version: int,
        actor_id: int,
    ) -> Person:
        values = data.model_dump(exclude_unset=True)
        with transaction(session):
            self.get_person(session, person_id)
            if values:
                values["updated_by"] = actor_id
                update_versioned(
                    session,
                    Person.__table__,
                    resource_name="Persona",
                    resource_id=person_id,
                    expected_version=expected_version,
                    values=values,
                )
                record_audit_event(
                    session,
                    action="person.updated",
                    entity_type="person",
                    entity_id=person_id,
                    user_id=actor_id,
                    details={"fields": sorted(values)},
                )
            session.flush()
            session.expire_all()
            person = self._repository.get_person(session, person_id)
            assert person is not None
        return person

    def archive_person(
        self, session: Session, *, person_id: int, expected_version: int, actor_id: int
    ) -> Person:
        with transaction(session):
            self.get_person(session, person_id)
            update_versioned(
                session,
                Person.__table__,
                resource_name="Persona",
                resource_id=person_id,
                expected_version=expected_version,
                values={
                    "archived_at": utc_now_iso(),
                    "archived_by": actor_id,
                    "updated_by": actor_id,
                },
            )
            record_audit_event(
                session,
                action="person.archived",
                entity_type="person",
                entity_id=person_id,
                user_id=actor_id,
            )
            session.flush()
            session.expire_all()
            person = self._repository.get_person(
                session, person_id, include_archived=True
            )
            assert person is not None
        return person

    def list_roles(
        self, session: Session, *, person_id: int, include_archived: bool = False
    ) -> Sequence[PersonRole]:
        self.get_person(session, person_id)
        return self._repository.list_roles(
            session, person_id=person_id, include_archived=include_archived
        )

    def create_role(
        self, session: Session, *, data: PersonRoleCreateDTO, actor_id: int
    ) -> PersonRole:
        status = data.status or "active"
        self._validate_role_values(data.role_type, status, data.start_date, data.end_date)
        with transaction(session):
            self.get_person(session, data.person_id)
            if status == "active" and data.end_date is None and self._repository.has_active_role(
                session, person_id=data.person_id, role_type=data.role_type
            ):
                raise ConflictError(
                    "La persona ha già questo ruolo attivo", code="ACTIVE_ROLE_EXISTS"
                )
            role = self._repository.add_role(
                session,
                PersonRole(
                    **data.model_dump(exclude={"status"}),
                    status=status,
                    created_by=actor_id,
                    updated_by=actor_id,
                ),
            )
            session.flush()
            record_audit_event(
                session,
                action="person_role.created",
                entity_type="person_role",
                entity_id=role.id,
                user_id=actor_id,
            )
        return role

    def update_role(
        self,
        session: Session,
        *,
        role_id: int,
        data: PersonRoleUpdateDTO,
        expected_version: int,
        actor_id: int,
    ) -> PersonRole:
        values = data.model_dump(exclude_unset=True)
        with transaction(session):
            role = self._repository.get_role(session, role_id)
            if role is None:
                raise ResourceNotFoundError("Ruolo persona", role_id)
            if "status" in values and values["status"] is None:
                raise ValueError("Lo stato ruolo non può essere nullo")
            if "role_type" in values and values["role_type"] is None:
                raise ValueError("Il tipo ruolo non può essere nullo")
            person_id = int(values.get("person_id", role.person_id))
            if person_id != role.person_id:
                self.get_person(session, person_id)
            self._validate_role_values(
                str(values.get("role_type", role.role_type)),
                str(values.get("status", role.status)),
                str(values.get("start_date", role.start_date)),
                values.get("end_date", role.end_date),
            )
            if (
                str(values.get("status", role.status)) == "active"
                and values.get("end_date", role.end_date) is None
                and self._repository.has_active_role(
                    session,
                    person_id=person_id,
                    role_type=str(values.get("role_type", role.role_type)),
                    exclude_role_id=role_id,
                )
            ):
                raise ConflictError(
                    "La persona ha già questo ruolo attivo", code="ACTIVE_ROLE_EXISTS"
                )
            if values:
                values["updated_by"] = actor_id
                update_versioned(
                    session,
                    PersonRole.__table__,
                    resource_name="Ruolo persona",
                    resource_id=role_id,
                    expected_version=expected_version,
                    values=values,
                )
                record_audit_event(
                    session,
                    action="person_role.updated",
                    entity_type="person_role",
                    entity_id=role_id,
                    user_id=actor_id,
                    details={"fields": sorted(values)},
                )
            session.flush()
            session.expire_all()
            updated = self._repository.get_role(session, role_id)
            assert updated is not None
        return updated

    def archive_role(
        self, session: Session, *, role_id: int, expected_version: int, actor_id: int
    ) -> PersonRole:
        with transaction(session):
            role = self._repository.get_role(session, role_id)
            if role is None:
                raise ResourceNotFoundError("Ruolo persona", role_id)
            update_versioned(
                session,
                PersonRole.__table__,
                resource_name="Ruolo persona",
                resource_id=role_id,
                expected_version=expected_version,
                values={
                    "archived_at": utc_now_iso(),
                    "archived_by": actor_id,
                    "updated_by": actor_id,
                },
            )
            record_audit_event(
                session,
                action="person_role.archived",
                entity_type="person_role",
                entity_id=role_id,
                user_id=actor_id,
            )
            session.flush()
            session.expire_all()
            archived = self._repository.get_role(session, role_id, include_archived=True)
            assert archived is not None
        return archived

    @staticmethod
    def _validate_role_values(
        role_type: str, status: str | None, start_date: str, end_date: str | None
    ) -> None:
        if role_type not in _ROLE_TYPES:
            raise ValueError("Tipo ruolo non valido")
        if status is not None and status not in _ROLE_STATUSES:
            raise ValueError("Stato ruolo non valido")
        if end_date is not None and end_date < start_date:
            raise ValueError("La data di fine non può precedere la data di inizio")

    @staticmethod
    def _validate_roles(roles: Sequence[str]) -> list[str]:
        normalized = []
        for role in roles:
            canonical = _ROLE_ALIASES.get(role.strip().casefold())
            if canonical is None:
                raise ValueError("Tipo ruolo non valido")
            if canonical not in normalized:
                normalized.append(canonical)
        return normalized

    def _parse_excel(self, content: bytes) -> list[tuple[PersonCreateDTO, list[str]]]:
        try:
            workbook = load_workbook(BytesIO(content), read_only=True, data_only=True)
            values = workbook.active.iter_rows(values_only=True)
            headers = next(values, None)
        except Exception as exc:
            raise ImportValidationError("Il file Excel non è leggibile") from exc
        if headers is None:
            raise ImportValidationError("Il file Excel non contiene intestazioni")
        normalized_headers = [
            str(value).strip().casefold() if value is not None else "" for value in headers
        ]
        if not _IMPORT_HEADERS.issubset(normalized_headers):
            raise ImportValidationError("Il file deve contenere le colonne first_name e last_name")
        imported: list[tuple[PersonCreateDTO, list[str]]] = []
        for row_number, values_row in enumerate(values, start=2):
            row = {
                header: values_row[index] if index < len(values_row) else None
                for index, header in enumerate(normalized_headers) if header
            }
            if not any(value is not None and str(value).strip() for value in row.values()):
                continue
            try:
                first_name = self._string_cell(row, "first_name")
                last_name = self._string_cell(row, "last_name")
                if first_name is None or last_name is None:
                    raise ValueError("Nome e cognome sono obbligatori")
                data = PersonCreateDTO(
                    first_name=first_name,
                    last_name=last_name,
                    birth_date=self._string_cell(row, "birth_date"),
                    birth_place=self._string_cell(row, "birth_place"),
                    tax_code=self._string_cell(row, "tax_code"),
                    residence_address=self._string_cell(row, "residence_address"),
                    email=self._string_cell(row, "email"),
                    phone=self._string_cell(row, "phone"),
                    notes=self._string_cell(row, "notes"),
                )
            except Exception as exc:
                raise ImportValidationError(
                    "Riga anagrafica non valida", details={"row": row_number}
                ) from exc
            raw_roles = "" if row.get("roles") is None else str(row["roles"])
            try:
                roles = self._validate_roles(
                    [item for item in raw_roles.replace(";", ",").split(",") if item.strip()]
                )
            except ValueError as exc:
                raise ImportValidationError(
                    "Ruolo non valido", details={"row": row_number}
                ) from exc
            imported.append((data, roles))
        if not imported:
            raise ImportValidationError("Il file non contiene anagrafiche")
        return imported

    @staticmethod
    def _string_cell(row: dict[str, object | None], field: str) -> str | None:
        value = row.get(field)
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None
