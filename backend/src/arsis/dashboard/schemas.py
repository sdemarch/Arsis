"""Public HTTP contracts for the home dashboard."""

from typing import Literal

from arsis.core.api_models import ApiModel


class PeopleSummary(ApiModel):
    active: int
    members: int
    musicians: int
    students: int
    teachers: int
    sections: int


class SchoolSummary(ApiModel):
    active_courses: int
    active_enrollments: int
    enrolled_students: int
    lessons_this_month: int
    attendance_rate: float | None


class UpcomingActivity(ApiModel):
    id: int
    title: str
    type: Literal["rehearsal", "concert", "event"]
    status: Literal["planned", "confirmed", "cancelled", "completed"]
    starts_at: str
    location: str | None
    participant_count: int


class TodayLesson(ApiModel):
    id: int
    course_id: int
    course_name: str
    course_color: str
    teacher_name: str
    starts_at: str
    ends_at: str | None
    status: Literal["planned", "completed", "cancelled"]
    students: int
    recorded: int


class CourseStudents(ApiModel):
    course_id: int
    students: int


class DashboardSummary(ApiModel):
    date: str
    people: PeopleSummary
    school: SchoolSummary
    upcoming_activities: list[UpcomingActivity]
    today_lessons: list[TodayLesson]
    course_students: list[CourseStudents]
