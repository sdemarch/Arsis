"""Persistence operations for music-school courses."""

from collections.abc import Sequence

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from arsis.generated.models import Course, PersonRole


class CoursesRepository:
    def get_course(
        self, session: Session, course_id: int, *, include_archived: bool = False
    ) -> Course | None:
        statement = select(Course).where(Course.id == course_id)
        if not include_archived:
            statement = statement.where(Course.archived_at.is_(None))
        return session.scalar(statement)

    def list_courses(
        self, session: Session, *, search: str | None = None, include_archived: bool = False
    ) -> Sequence[Course]:
        statement: Select[tuple[Course]] = select(Course)
        if not include_archived:
            statement = statement.where(Course.archived_at.is_(None))
        if search and (query := search.strip()):
            pattern = f"%{query.casefold()}%"
            statement = statement.where(
                or_(
                    func.lower(Course.name).like(pattern),
                    func.lower(Course.description).like(pattern),
                )
            )
        return session.scalars(statement.order_by(func.lower(Course.name), Course.id)).all()

    def has_active_teacher(self, session: Session, person_id: int) -> bool:
        statement = select(PersonRole.id).where(
            PersonRole.person_id == person_id,
            PersonRole.role_type == "teacher",
            PersonRole.status == "active",
            PersonRole.end_date.is_(None),
            PersonRole.archived_at.is_(None),
        )
        return session.scalar(statement) is not None

    def add_course(self, session: Session, course: Course) -> Course:
        session.add(course)
        return course
