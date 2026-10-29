"""Business operations for music-school courses."""

from collections.abc import Sequence

from sqlalchemy.orm import Session

from arsis.audit.service import record_audit_event
from arsis.core.database import transaction
from arsis.core.errors import ConflictError, ResourceNotFoundError
from arsis.core.time import utc_now_iso
from arsis.core.versioning import update_versioned
from arsis.generated.models import Course
from arsis.generated.schemas import CourseCreateDTO, CourseUpdateDTO
from arsis.school.repository import CoursesRepository


class CoursesService:
    def __init__(self, repository: CoursesRepository | None = None) -> None:
        self._repository = repository or CoursesRepository()

    def list_courses(
        self, session: Session, *, search: str | None = None, include_archived: bool = False
    ) -> Sequence[Course]:
        return self._repository.list_courses(
            session, search=search, include_archived=include_archived
        )

    def get_course(
        self, session: Session, course_id: int, *, include_archived: bool = False
    ) -> Course:
        course = self._repository.get_course(session, course_id, include_archived=include_archived)
        if course is None:
            raise ResourceNotFoundError("Corso", course_id)
        return course

    def create_course(self, session: Session, *, data: CourseCreateDTO, actor_id: int) -> Course:
        values = data.model_dump()
        values["status"] = values["status"] or "active"
        with transaction(session):
            self._validate_teacher(session, int(values["teacher_person_id"]))
            course = self._repository.add_course(
                session, Course(**values, created_by=actor_id, updated_by=actor_id)
            )
            session.flush()
            record_audit_event(
                session,
                action="course.created",
                entity_type="course",
                entity_id=course.id,
                user_id=actor_id,
            )
        return course

    def update_course(
        self,
        session: Session,
        *,
        course_id: int,
        data: CourseUpdateDTO,
        expected_version: int,
        actor_id: int,
    ) -> Course:
        values = data.model_dump(exclude_unset=True)
        with transaction(session):
            self.get_course(session, course_id)
            if "teacher_person_id" in values:
                teacher_person_id = values["teacher_person_id"]
                if teacher_person_id is None:
                    raise ValueError("L'insegnante del corso è obbligatorio")
                self._validate_teacher(session, int(teacher_person_id))
            if values:
                values["updated_by"] = actor_id
                update_versioned(
                    session,
                    Course.__table__,
                    resource_name="Corso",
                    resource_id=course_id,
                    expected_version=expected_version,
                    values=values,
                )
                record_audit_event(
                    session,
                    action="course.updated",
                    entity_type="course",
                    entity_id=course_id,
                    user_id=actor_id,
                    details={"fields": sorted(values)},
                )
            session.flush()
            session.expire_all()
            return self.get_course(session, course_id)

    def archive_course(
        self, session: Session, *, course_id: int, expected_version: int, actor_id: int
    ) -> Course:
        with transaction(session):
            self.get_course(session, course_id)
            update_versioned(
                session,
                Course.__table__,
                resource_name="Corso",
                resource_id=course_id,
                expected_version=expected_version,
                values={
                    "archived_at": utc_now_iso(),
                    "archived_by": actor_id,
                    "updated_by": actor_id,
                },
            )
            record_audit_event(
                session,
                action="course.archived",
                entity_type="course",
                entity_id=course_id,
                user_id=actor_id,
            )
            session.flush()
            session.expire_all()
            return self.get_course(session, course_id, include_archived=True)

    def _validate_teacher(self, session: Session, person_id: int) -> None:
        if not self._repository.has_active_teacher(session, person_id):
            raise ConflictError(
                "L'insegnante selezionato non ha un ruolo attivo", code="INVALID_COURSE_TEACHER"
            )
