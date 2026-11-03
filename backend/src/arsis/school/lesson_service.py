"""Business operations for music-school lessons."""

from collections.abc import Sequence

from sqlalchemy.orm import Session

from arsis.audit.service import record_audit_event
from arsis.core.database import transaction
from arsis.core.errors import ConflictError, ResourceNotFoundError
from arsis.core.time import utc_now_iso
from arsis.core.versioning import update_versioned
from arsis.generated.models import Lesson
from arsis.generated.schemas import LessonCreateDTO, LessonUpdateDTO
from arsis.school.lesson_repository import LessonsRepository


class LessonsService:
    def __init__(self, repository: LessonsRepository | None = None) -> None:
        self._repository = repository or LessonsRepository()

    def list_lessons(
        self, session: Session, *, search: str | None = None, include_archived: bool = False
    ) -> Sequence[Lesson]:
        return self._repository.list_lessons(
            session, search=search, include_archived=include_archived
        )

    def get_lesson(
        self, session: Session, lesson_id: int, *, include_archived: bool = False
    ) -> Lesson:
        lesson = self._repository.get_lesson(session, lesson_id, include_archived=include_archived)
        if lesson is None:
            raise ResourceNotFoundError("Lezione", lesson_id)
        return lesson

    def create_lesson(self, session: Session, *, data: LessonCreateDTO, actor_id: int) -> Lesson:
        values = data.model_dump()
        values["status"] = values["status"] or "planned"
        self._validate_schedule(str(values["starts_at"]), values["ends_at"])
        with transaction(session):
            self._validate_relations(
                session,
                course_id=int(values["course_id"]),
                teacher_person_id=int(values["teacher_person_id"]),
            )
            lesson = self._repository.add_lesson(
                session, Lesson(**values, created_by=actor_id, updated_by=actor_id)
            )
            session.flush()
            record_audit_event(
                session,
                action="lesson.created",
                entity_type="lesson",
                entity_id=lesson.id,
                user_id=actor_id,
            )
        return lesson

    def update_lesson(
        self,
        session: Session,
        *,
        lesson_id: int,
        data: LessonUpdateDTO,
        expected_version: int,
        actor_id: int,
    ) -> Lesson:
        values = data.model_dump(exclude_unset=True)
        with transaction(session):
            lesson = self.get_lesson(session, lesson_id)
            course_id = int(values.get("course_id", lesson.course_id))
            teacher_person_id = int(values.get("teacher_person_id", lesson.teacher_person_id))
            starts_at = str(values.get("starts_at", lesson.starts_at))
            ends_at = values.get("ends_at", lesson.ends_at)
            self._validate_schedule(starts_at, ends_at)
            self._validate_relations(
                session, course_id=course_id, teacher_person_id=teacher_person_id
            )
            if values:
                values["updated_by"] = actor_id
                update_versioned(
                    session,
                    Lesson.__table__,
                    resource_name="Lezione",
                    resource_id=lesson_id,
                    expected_version=expected_version,
                    values=values,
                )
                record_audit_event(
                    session,
                    action="lesson.updated",
                    entity_type="lesson",
                    entity_id=lesson_id,
                    user_id=actor_id,
                    details={"fields": sorted(values)},
                )
            session.flush()
            session.expire_all()
            return self.get_lesson(session, lesson_id)

    def archive_lesson(
        self, session: Session, *, lesson_id: int, expected_version: int, actor_id: int
    ) -> Lesson:
        with transaction(session):
            self.get_lesson(session, lesson_id)
            update_versioned(
                session,
                Lesson.__table__,
                resource_name="Lezione",
                resource_id=lesson_id,
                expected_version=expected_version,
                values={
                    "archived_at": utc_now_iso(),
                    "archived_by": actor_id,
                    "updated_by": actor_id,
                },
            )
            record_audit_event(
                session,
                action="lesson.archived",
                entity_type="lesson",
                entity_id=lesson_id,
                user_id=actor_id,
            )
            session.flush()
            session.expire_all()
            return self.get_lesson(session, lesson_id, include_archived=True)

    def _validate_relations(
        self, session: Session, *, course_id: int, teacher_person_id: int
    ) -> None:
        if not self._repository.has_active_course(session, course_id):
            raise ConflictError("Il corso selezionato non è attivo", code="INVALID_LESSON_COURSE")
        if not self._repository.has_active_teacher(session, teacher_person_id):
            raise ConflictError(
                "L'insegnante selezionato non ha un ruolo attivo", code="INVALID_LESSON_TEACHER"
            )

    @staticmethod
    def _validate_schedule(starts_at: str, ends_at: str | None) -> None:
        if ends_at is not None and ends_at <= starts_at:
            raise ConflictError(
                "La fine della lezione deve essere successiva all'inizio",
                code="INVALID_LESSON_SCHEDULE",
            )
