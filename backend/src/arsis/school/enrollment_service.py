"""Business operations for course enrollments."""

from collections.abc import Sequence

from sqlalchemy.orm import Session

from arsis.audit.service import record_audit_event
from arsis.core.database import transaction
from arsis.core.errors import ConflictError, ResourceNotFoundError
from arsis.core.time import utc_now_iso
from arsis.core.versioning import update_versioned
from arsis.generated.models import Enrollment
from arsis.generated.schemas import EnrollmentCreateDTO, EnrollmentUpdateDTO
from arsis.school.enrollment_repository import EnrollmentsRepository


class EnrollmentsService:
    def __init__(self, repository: EnrollmentsRepository | None = None) -> None:
        self._repository = repository or EnrollmentsRepository()

    def list_enrollments(
        self, session: Session, *, search: str | None = None, include_archived: bool = False
    ) -> Sequence[Enrollment]:
        return self._repository.list_enrollments(
            session, search=search, include_archived=include_archived
        )

    def get_enrollment(
        self, session: Session, enrollment_id: int, *, include_archived: bool = False
    ) -> Enrollment:
        enrollment = self._repository.get_enrollment(
            session, enrollment_id, include_archived=include_archived
        )
        if enrollment is None:
            raise ResourceNotFoundError("Iscrizione", enrollment_id)
        return enrollment

    def create_enrollment(
        self, session: Session, *, data: EnrollmentCreateDTO, actor_id: int
    ) -> Enrollment:
        values = data.model_dump()
        values["status"] = values["status"] or "active"
        self._validate_dates(str(values["starts_on"]), values["ends_on"])
        with transaction(session):
            self._validate_relations(
                session,
                course_id=int(values["course_id"]),
                student_person_id=int(values["student_person_id"]),
                starts_on=str(values["starts_on"]),
                status=str(values["status"]),
                ends_on=values["ends_on"],
            )
            enrollment = self._repository.add_enrollment(
                session, Enrollment(**values, created_by=actor_id, updated_by=actor_id)
            )
            session.flush()
            record_audit_event(
                session,
                action="enrollment.created",
                entity_type="enrollment",
                entity_id=enrollment.id,
                user_id=actor_id,
            )
        return enrollment

    def update_enrollment(
        self,
        session: Session,
        *,
        enrollment_id: int,
        data: EnrollmentUpdateDTO,
        expected_version: int,
        actor_id: int,
    ) -> Enrollment:
        values = data.model_dump(exclude_unset=True)
        with transaction(session):
            enrollment = self.get_enrollment(session, enrollment_id)
            course_id = int(values.get("course_id", enrollment.course_id))
            student_person_id = int(values.get("student_person_id", enrollment.student_person_id))
            starts_on = str(values.get("starts_on", enrollment.starts_on))
            ends_on = values.get("ends_on", enrollment.ends_on)
            status = str(values.get("status", enrollment.status))
            self._validate_dates(starts_on, ends_on)
            self._validate_relations(
                session,
                course_id=course_id,
                student_person_id=student_person_id,
                starts_on=starts_on,
                status=status,
                ends_on=ends_on,
                exclude_enrollment_id=enrollment_id,
            )
            if values:
                values["updated_by"] = actor_id
                update_versioned(
                    session,
                    Enrollment.__table__,
                    resource_name="Iscrizione",
                    resource_id=enrollment_id,
                    expected_version=expected_version,
                    values=values,
                )
                record_audit_event(
                    session,
                    action="enrollment.updated",
                    entity_type="enrollment",
                    entity_id=enrollment_id,
                    user_id=actor_id,
                    details={"fields": sorted(values)},
                )
            session.flush()
            session.expire_all()
            return self.get_enrollment(session, enrollment_id)

    def archive_enrollment(
        self, session: Session, *, enrollment_id: int, expected_version: int, actor_id: int
    ) -> Enrollment:
        with transaction(session):
            self.get_enrollment(session, enrollment_id)
            update_versioned(
                session,
                Enrollment.__table__,
                resource_name="Iscrizione",
                resource_id=enrollment_id,
                expected_version=expected_version,
                values={
                    "archived_at": utc_now_iso(),
                    "archived_by": actor_id,
                    "updated_by": actor_id,
                },
            )
            record_audit_event(
                session,
                action="enrollment.archived",
                entity_type="enrollment",
                entity_id=enrollment_id,
                user_id=actor_id,
            )
            session.flush()
            session.expire_all()
            return self.get_enrollment(session, enrollment_id, include_archived=True)

    def _validate_relations(
        self,
        session: Session,
        *,
        course_id: int,
        student_person_id: int,
        starts_on: str,
        status: str,
        ends_on: str | None,
        exclude_enrollment_id: int | None = None,
    ) -> None:
        if self._repository.get_active_course(session, course_id) is None:
            raise ConflictError(
                "Il corso selezionato non è attivo", code="INVALID_ENROLLMENT_COURSE"
            )
        if not self._repository.has_student_role(
            session, person_id=student_person_id, on_date=starts_on
        ):
            raise ConflictError(
                "L'allievo selezionato non ha un ruolo attivo alla data di inizio",
                code="INVALID_ENROLLMENT_STUDENT",
            )
        if (
            status == "active"
            and ends_on is None
            and self._repository.has_open_active_enrollment(
                session,
                course_id=course_id,
                student_person_id=student_person_id,
                exclude_enrollment_id=exclude_enrollment_id,
            )
        ):
            raise ConflictError(
                "L'allievo è già iscritto al corso", code="ACTIVE_ENROLLMENT_EXISTS"
            )

    @staticmethod
    def _validate_dates(starts_on: str, ends_on: str | None) -> None:
        if ends_on is not None and ends_on < starts_on:
            raise ValueError("La data di fine non può precedere la data di inizio")
