from decimal import Decimal
from typing import Literal

from pydantic import Field

from arsis.core.api_models import ApiModel, Money


class CourseCreateRequest(ApiModel):
    name: str = Field(min_length=1, max_length=200)
    mode: Literal["individual", "group"]
    category: Literal["instrument", "ensemble"]
    teacher_person_id: int = Field(ge=1)
    annual_fee: Decimal = Field(ge=0)
    color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    instrument_id: int | None = Field(default=None, ge=1)
    description: str | None = None
    weekday: int | None = Field(default=None, ge=1, le=7)
    start_time: str | None = None
    end_time: str | None = None
    valid_from: str | None = None
    valid_to: str | None = None
    status: Literal["active", "inactive"] | None = None
    notes: str | None = None


class CourseUpdateRequest(ApiModel):
    version: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    mode: Literal["individual", "group"] | None = None
    category: Literal["instrument", "ensemble"] | None = None
    teacher_person_id: int | None = Field(default=None, ge=1)
    annual_fee: Decimal | None = Field(default=None, ge=0)
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    instrument_id: int | None = Field(default=None, ge=1)
    description: str | None = None
    weekday: int | None = Field(default=None, ge=1, le=7)
    start_time: str | None = None
    end_time: str | None = None
    valid_from: str | None = None
    valid_to: str | None = None
    status: Literal["active", "inactive"] | None = None
    notes: str | None = None


class CourseResponse(CourseCreateRequest):
    annual_fee: Money
    id: int
    status: Literal["active", "inactive"]
    created_at: str
    updated_at: str
    archived_at: str | None
    version: int


EnrollmentStatus = Literal["active", "completed", "cancelled"]


class EnrollmentCreateRequest(ApiModel):
    course_id: int = Field(ge=1)
    student_person_id: int = Field(ge=1)
    enrolled_on: str = Field(min_length=10, max_length=10)
    starts_on: str = Field(min_length=10, max_length=10)
    ends_on: str | None = Field(default=None, min_length=10, max_length=10)
    status: EnrollmentStatus | None = None
    notes: str | None = None


class EnrollmentUpdateRequest(ApiModel):
    version: int = Field(ge=1)
    course_id: int | None = Field(default=None, ge=1)
    student_person_id: int | None = Field(default=None, ge=1)
    enrolled_on: str | None = Field(default=None, min_length=10, max_length=10)
    starts_on: str | None = Field(default=None, min_length=10, max_length=10)
    ends_on: str | None = Field(default=None, min_length=10, max_length=10)
    status: EnrollmentStatus | None = None
    notes: str | None = None


class EnrollmentResponse(EnrollmentCreateRequest):
    id: int
    status: EnrollmentStatus
    created_at: str
    updated_at: str
    archived_at: str | None
    version: int


LessonStatus = Literal["planned", "completed", "cancelled"]


class LessonCreateRequest(ApiModel):
    course_id: int = Field(ge=1)
    teacher_person_id: int = Field(ge=1)
    starts_at: str = Field(min_length=16, max_length=40)
    ends_at: str | None = Field(default=None, min_length=16, max_length=40)
    topic: str | None = Field(default=None, max_length=300)
    status: LessonStatus | None = None
    notes: str | None = None


class LessonUpdateRequest(ApiModel):
    version: int = Field(ge=1)
    course_id: int | None = Field(default=None, ge=1)
    teacher_person_id: int | None = Field(default=None, ge=1)
    starts_at: str | None = Field(default=None, min_length=16, max_length=40)
    ends_at: str | None = Field(default=None, min_length=16, max_length=40)
    topic: str | None = Field(default=None, max_length=300)
    status: LessonStatus | None = None
    notes: str | None = None


class LessonResponse(LessonCreateRequest):
    id: int
    status: LessonStatus
    created_at: str
    updated_at: str
    archived_at: str | None
    version: int


AttendanceStatus = Literal["present", "absent"]


class AttendanceWrite(ApiModel):
    student_person_id: int = Field(ge=1)
    attendance: AttendanceStatus | None = None


class AttendanceBulkRequest(ApiModel):
    rows: list[AttendanceWrite] = Field(min_length=1, max_length=500)


class LessonAttendanceResponse(AttendanceWrite):
    student_name: str
    recorded_at: str | None
    version: int | None


class AttendanceImportResponse(ApiModel):
    lesson_id: int
    processed_rows: int
