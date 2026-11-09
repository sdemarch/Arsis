"""Read-only figures for the home dashboard and the school overview."""

from datetime import date
from typing import Any

from sqlalchemy import ColumnElement, and_, func, or_, select
from sqlalchemy.orm import Session

from arsis.generated.models import (
    Activity,
    ActivityParticipant,
    Course,
    Enrollment,
    Lesson,
    LessonAttendance,
    Person,
    PersonRole,
    Section,
)

UPCOMING_ACTIVITIES = 5


def _local_date(column: Any) -> ColumnElement[str]:
    # Timestamps keep the local date in their first ten characters.
    return func.substr(column, 1, 10)


def _enrollment_open_on(day: str) -> ColumnElement[bool]:
    return and_(
        Enrollment.archived_at.is_(None),
        Enrollment.status == "active",
        Enrollment.starts_on <= day,
        or_(Enrollment.ends_on.is_(None), Enrollment.ends_on >= day),
    )


def _count(session: Session, statement: Any) -> int:
    return int(session.scalar(statement) or 0)


class DashboardService:
    def summary(self, session: Session, *, today: date) -> dict[str, Any]:
        day = today.isoformat()
        return {
            "date": day,
            "people": self._people(session, day),
            "school": self._school(session, day),
            "upcoming_activities": self._upcoming_activities(session, day),
            "today_lessons": self._today_lessons(session, day),
            "course_students": [
                {"course_id": course_id, "students": students}
                for course_id, students in session.execute(
                    select(
                        Enrollment.course_id,
                        func.count(func.distinct(Enrollment.student_person_id)),
                    )
                    .where(_enrollment_open_on(day))
                    .group_by(Enrollment.course_id)
                    .order_by(Enrollment.course_id)
                ).all()
            ],
        }

    def _people(self, session: Session, day: str) -> dict[str, int]:
        role_counts: dict[str, int] = {
            role_type: count
            for role_type, count in session.execute(
                select(PersonRole.role_type, func.count(func.distinct(PersonRole.person_id)))
                .join(Person, Person.id == PersonRole.person_id)
                .where(
                    Person.archived_at.is_(None),
                    PersonRole.archived_at.is_(None),
                    PersonRole.status == "active",
                    PersonRole.start_date <= day,
                    or_(PersonRole.end_date.is_(None), PersonRole.end_date >= day),
                )
                .group_by(PersonRole.role_type)
            ).all()
        }
        return {
            "active": _count(
                session,
                select(func.count()).select_from(Person).where(Person.archived_at.is_(None)),
            ),
            "members": role_counts.get("member", 0),
            "musicians": role_counts.get("musician", 0),
            "students": role_counts.get("student", 0),
            "teachers": role_counts.get("teacher", 0),
            "sections": _count(
                session,
                select(func.count())
                .select_from(Section)
                .where(Section.is_active.is_(True), Section.archived_at.is_(None)),
            ),
        }

    def _school(self, session: Session, day: str) -> dict[str, Any]:
        month_lessons = and_(
            Lesson.archived_at.is_(None),
            Lesson.status != "cancelled",
            func.substr(Lesson.starts_at, 1, 7) == day[:7],
        )
        present, recorded = session.execute(
            select(
                func.count().filter(LessonAttendance.attendance == "present"),
                func.count().filter(LessonAttendance.attendance.is_not(None)),
            )
            .join(Lesson, Lesson.id == LessonAttendance.lesson_id)
            .where(month_lessons, LessonAttendance.archived_at.is_(None))
        ).one()
        return {
            "active_courses": _count(
                session,
                select(func.count())
                .select_from(Course)
                .where(Course.archived_at.is_(None), Course.status == "active"),
            ),
            "active_enrollments": _count(
                session,
                select(func.count()).select_from(Enrollment).where(_enrollment_open_on(day)),
            ),
            "enrolled_students": _count(
                session,
                select(func.count(func.distinct(Enrollment.student_person_id))).where(
                    _enrollment_open_on(day)
                ),
            ),
            "lessons_this_month": _count(
                session, select(func.count()).select_from(Lesson).where(month_lessons)
            ),
            "attendance_rate": round(present / recorded, 3) if recorded else None,
        }

    def _upcoming_activities(self, session: Session, day: str) -> list[dict[str, Any]]:
        participants = (
            select(func.count())
            .where(
                ActivityParticipant.activity_id == Activity.id,
                ActivityParticipant.archived_at.is_(None),
            )
            .correlate(Activity)
            .scalar_subquery()
        )
        rows = session.execute(
            select(Activity, participants)
            .where(
                Activity.archived_at.is_(None),
                Activity.status != "cancelled",
                _local_date(Activity.starts_at) >= day,
            )
            .order_by(Activity.starts_at, Activity.id)
            .limit(UPCOMING_ACTIVITIES)
        ).all()
        return [
            {
                "id": activity.id,
                "title": activity.title,
                "type": activity.type,
                "status": activity.status,
                "starts_at": activity.starts_at,
                "location": activity.location,
                "participant_count": count,
            }
            for activity, count in rows
        ]

    def _today_lessons(self, session: Session, day: str) -> list[dict[str, Any]]:
        students = (
            select(func.count(func.distinct(Enrollment.student_person_id)))
            .where(Enrollment.course_id == Lesson.course_id, _enrollment_open_on(day))
            .correlate(Lesson)
            .scalar_subquery()
        )
        recorded = (
            select(func.count())
            .where(
                LessonAttendance.lesson_id == Lesson.id,
                LessonAttendance.archived_at.is_(None),
                LessonAttendance.attendance.is_not(None),
            )
            .correlate(Lesson)
            .scalar_subquery()
        )
        rows = session.execute(
            select(Lesson, Course, Person, students, recorded)
            .join(Course, Course.id == Lesson.course_id)
            .join(Person, Person.id == Lesson.teacher_person_id)
            .where(Lesson.archived_at.is_(None), _local_date(Lesson.starts_at) == day)
            .order_by(Lesson.starts_at, Lesson.id)
        ).all()
        return [
            {
                "id": lesson.id,
                "course_id": course.id,
                "course_name": course.name,
                "course_color": course.color,
                "teacher_name": f"{teacher.first_name} {teacher.last_name}",
                "starts_at": lesson.starts_at,
                "ends_at": lesson.ends_at,
                "status": lesson.status,
                "students": student_count,
                "recorded": recorded_count,
            }
            for lesson, course, teacher, student_count, recorded_count in rows
        ]
