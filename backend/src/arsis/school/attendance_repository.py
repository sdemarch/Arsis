"""Queries supporting the lesson attendance register."""

from collections.abc import Sequence
from typing import cast

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from arsis.generated.models import Enrollment, Lesson, LessonAttendance, Person


class AttendanceRepository:
    def get_lesson(self, session: Session, lesson_id: int) -> Lesson | None:
        return session.scalar(
            select(Lesson).where(Lesson.id == lesson_id, Lesson.archived_at.is_(None))
        )

    def list_roster(
        self, session: Session, *, lesson: Lesson
    ) -> Sequence[tuple[Enrollment, Person, LessonAttendance | None]]:
        lesson_date = lesson.starts_at[:10]
        statement = (
            select(Enrollment, Person, LessonAttendance)
            .join(Person, Person.id == Enrollment.student_person_id)
            .outerjoin(
                LessonAttendance,
                and_(
                    LessonAttendance.lesson_id == lesson.id,
                    LessonAttendance.student_person_id == Enrollment.student_person_id,
                    LessonAttendance.archived_at.is_(None),
                ),
            )
            .where(
                Enrollment.course_id == lesson.course_id,
                Enrollment.archived_at.is_(None),
                Enrollment.status.in_(("active", "completed")),
                Enrollment.starts_on <= lesson_date,
                (Enrollment.ends_on.is_(None) | (Enrollment.ends_on >= lesson_date)),
            )
            .order_by(Person.last_name, Person.first_name, Person.id)
        )
        rows = session.execute(statement).all()
        return cast(Sequence[tuple[Enrollment, Person, LessonAttendance | None]], rows)

    def get_records_by_student(
        self, session: Session, *, lesson_id: int
    ) -> dict[int, LessonAttendance]:
        records = session.scalars(
            select(LessonAttendance).where(
                LessonAttendance.lesson_id == lesson_id,
                LessonAttendance.archived_at.is_(None),
            )
        ).all()
        return {record.student_person_id: record for record in records}
