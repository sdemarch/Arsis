"""Persistence operations for music-school lessons."""

from collections.abc import Sequence

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from arsis.generated.models import Course, Lesson, PersonRole


class LessonsRepository:
    def get_lesson(
        self, session: Session, lesson_id: int, *, include_archived: bool = False
    ) -> Lesson | None:
        statement = select(Lesson).where(Lesson.id == lesson_id)
        if not include_archived:
            statement = statement.where(Lesson.archived_at.is_(None))
        return session.scalar(statement)

    def list_lessons(
        self, session: Session, *, search: str | None = None, include_archived: bool = False
    ) -> Sequence[Lesson]:
        statement: Select[tuple[Lesson]] = select(Lesson).join(
            Course, Lesson.course_id == Course.id
        )
        if not include_archived:
            statement = statement.where(Lesson.archived_at.is_(None))
        if search and (query := search.strip()):
            pattern = f"%{query.casefold()}%"
            statement = statement.where(
                or_(func.lower(Lesson.topic).like(pattern), func.lower(Course.name).like(pattern))
            )
        return session.scalars(statement.order_by(Lesson.starts_at.desc(), Lesson.id.desc())).all()

    def has_active_course(self, session: Session, course_id: int) -> bool:
        return (
            session.scalar(
                select(Course.id).where(
                    Course.id == course_id,
                    Course.status == "active",
                    Course.archived_at.is_(None),
                )
            )
            is not None
        )

    def has_active_teacher(self, session: Session, person_id: int) -> bool:
        return (
            session.scalar(
                select(PersonRole.id).where(
                    PersonRole.person_id == person_id,
                    PersonRole.role_type == "teacher",
                    PersonRole.status == "active",
                    PersonRole.end_date.is_(None),
                    PersonRole.archived_at.is_(None),
                )
            )
            is not None
        )

    def add_lesson(self, session: Session, lesson: Lesson) -> Lesson:
        session.add(lesson)
        return lesson
