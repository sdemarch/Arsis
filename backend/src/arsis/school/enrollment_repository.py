"""Persistence operations for course enrollments."""

from collections.abc import Sequence

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from arsis.generated.models import Course, Enrollment, Person, PersonRole


class EnrollmentsRepository:
    def get_enrollment(
        self, session: Session, enrollment_id: int, *, include_archived: bool = False
    ) -> Enrollment | None:
        statement = select(Enrollment).where(Enrollment.id == enrollment_id)
        if not include_archived:
            statement = statement.where(Enrollment.archived_at.is_(None))
        return session.scalar(statement)

    def list_enrollments(
        self, session: Session, *, search: str | None = None, include_archived: bool = False
    ) -> Sequence[Enrollment]:
        statement: Select[tuple[Enrollment]] = select(Enrollment)
        if not include_archived:
            statement = statement.where(Enrollment.archived_at.is_(None))
        if search and (query := search.strip()):
            pattern = f"%{query.casefold()}%"
            statement = (
                statement.join(Course, Enrollment.course_id == Course.id)
                .join(Person, Enrollment.student_person_id == Person.id)
                .where(
                    or_(
                        func.lower(Course.name).like(pattern),
                        func.lower(Person.first_name).like(pattern),
                        func.lower(Person.last_name).like(pattern),
                    )
                )
            )
        return session.scalars(
            statement.order_by(Enrollment.starts_on.desc(), Enrollment.id.desc())
        ).all()

    def get_active_course(self, session: Session, course_id: int) -> Course | None:
        return session.scalar(
            select(Course).where(
                Course.id == course_id, Course.status == "active", Course.archived_at.is_(None)
            )
        )

    def has_student_role(self, session: Session, *, person_id: int, on_date: str) -> bool:
        return (
            session.scalar(
                select(PersonRole.id).where(
                    PersonRole.person_id == person_id,
                    PersonRole.role_type == "student",
                    PersonRole.status == "active",
                    PersonRole.archived_at.is_(None),
                    PersonRole.start_date <= on_date,
                    or_(PersonRole.end_date.is_(None), PersonRole.end_date >= on_date),
                )
            )
            is not None
        )

    def has_open_active_enrollment(
        self,
        session: Session,
        *,
        course_id: int,
        student_person_id: int,
        exclude_enrollment_id: int | None = None,
    ) -> bool:
        statement = select(Enrollment.id).where(
            Enrollment.course_id == course_id,
            Enrollment.student_person_id == student_person_id,
            Enrollment.status == "active",
            Enrollment.ends_on.is_(None),
            Enrollment.archived_at.is_(None),
        )
        if exclude_enrollment_id is not None:
            statement = statement.where(Enrollment.id != exclude_enrollment_id)
        return session.scalar(statement) is not None

    def add_enrollment(self, session: Session, enrollment: Enrollment) -> Enrollment:
        session.add(enrollment)
        return enrollment
