"""Generated Pydantic persistence DTOs. Do not edit by hand."""
# ruff: noqa

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict

SCHEMA_FINGERPRINT = "3f9476bdd9d7adcc"


class GeneratedDTO(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)


class ActivityCreateDTO(GeneratedDTO):
    type: str
    title: str
    description: str | None = None
    starts_at: str
    ends_at: str | None = None
    location: str | None = None
    status: str | None = None
    reference_person_id: int | None = None
    notes: str | None = None


class ActivityUpdateDTO(GeneratedDTO):
    type: str | None = None
    title: str | None = None
    description: str | None = None
    starts_at: str | None = None
    ends_at: str | None = None
    location: str | None = None
    status: str | None = None
    reference_person_id: int | None = None
    notes: str | None = None


class ActivityReadDTO(GeneratedDTO):
    id: int
    type: str
    title: str
    description: str | None
    starts_at: str
    ends_at: str | None
    location: str | None
    status: str
    reference_person_id: int | None
    notes: str | None
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int


class ActivityParticipantCreateDTO(GeneratedDTO):
    activity_id: int
    person_id: int
    source: str
    attendance: str | None = None
    attendance_recorded_at: str | None = None
    attendance_recorded_by: int | None = None


class ActivityParticipantUpdateDTO(GeneratedDTO):
    activity_id: int | None = None
    person_id: int | None = None
    source: str | None = None
    attendance: str | None = None
    attendance_recorded_at: str | None = None
    attendance_recorded_by: int | None = None


class ActivityParticipantReadDTO(GeneratedDTO):
    id: int
    activity_id: int
    person_id: int
    source: str
    attendance: str | None
    attendance_recorded_at: str | None
    attendance_recorded_by: int | None
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int


class AppSettingCreateDTO(GeneratedDTO):
    key: str
    value: str | None = None
    description: str | None = None


class AppSettingUpdateDTO(GeneratedDTO):
    value: str | None = None
    description: str | None = None


class AppSettingReadDTO(GeneratedDTO):
    key: str
    value: str
    description: str | None
    version: int
    created_at: str
    updated_at: str
    created_by: int | None
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None


class AssociatedContactCreateDTO(GeneratedDTO):
    person_id: int
    contact_person_id: int
    relationship_type: str
    is_primary: bool | None = None
    is_payment_contact: bool | None = None
    notes: str | None = None


class AssociatedContactUpdateDTO(GeneratedDTO):
    person_id: int | None = None
    contact_person_id: int | None = None
    relationship_type: str | None = None
    is_primary: bool | None = None
    is_payment_contact: bool | None = None
    notes: str | None = None


class AssociatedContactReadDTO(GeneratedDTO):
    id: int
    person_id: int
    contact_person_id: int
    relationship_type: str
    is_primary: bool
    is_payment_contact: bool
    notes: str | None
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int


class AuditEventCreateDTO(GeneratedDTO):
    occurred_at: str | None = None
    user_id: int | None = None
    action: str
    entity_type: str
    entity_id: int | None = None
    request_id: str | None = None
    details: str | None = None
    ip_address: str | None = None


class AuditEventUpdateDTO(GeneratedDTO):
    occurred_at: str | None = None
    user_id: int | None = None
    action: str | None = None
    entity_type: str | None = None
    entity_id: int | None = None
    request_id: str | None = None
    details: str | None = None
    ip_address: str | None = None


class AuditEventReadDTO(GeneratedDTO):
    id: int
    occurred_at: str
    user_id: int | None
    action: str
    entity_type: str
    entity_id: int | None
    request_id: str | None
    details: str
    ip_address: str | None


class CourseInstallmentTemplateCreateDTO(GeneratedDTO):
    course_id: int
    sequence_number: int
    description: str | None = None
    amount: Decimal
    due_month: int | None = None
    due_day: int | None = None
    proposed_due_date: str | None = None


class CourseInstallmentTemplateUpdateDTO(GeneratedDTO):
    course_id: int | None = None
    sequence_number: int | None = None
    description: str | None = None
    amount: Decimal | None = None
    due_month: int | None = None
    due_day: int | None = None
    proposed_due_date: str | None = None


class CourseInstallmentTemplateReadDTO(GeneratedDTO):
    id: int
    course_id: int
    sequence_number: int
    description: str | None
    amount: Decimal
    due_month: int | None
    due_day: int | None
    proposed_due_date: str | None
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int


class CourseCreateDTO(GeneratedDTO):
    name: str
    description: str | None = None
    mode: str
    category: str
    instrument_id: int | None = None
    teacher_person_id: int
    weekday: int | None = None
    start_time: str | None = None
    end_time: str | None = None
    annual_fee: Decimal
    color: str
    valid_from: str | None = None
    valid_to: str | None = None
    status: str | None = None
    notes: str | None = None


class CourseUpdateDTO(GeneratedDTO):
    name: str | None = None
    description: str | None = None
    mode: str | None = None
    category: str | None = None
    instrument_id: int | None = None
    teacher_person_id: int | None = None
    weekday: int | None = None
    start_time: str | None = None
    end_time: str | None = None
    annual_fee: Decimal | None = None
    color: str | None = None
    valid_from: str | None = None
    valid_to: str | None = None
    status: str | None = None
    notes: str | None = None


class CourseReadDTO(GeneratedDTO):
    id: int
    name: str
    description: str | None
    mode: str
    category: str
    instrument_id: int | None
    teacher_person_id: int
    weekday: int | None
    start_time: str | None
    end_time: str | None
    annual_fee: Decimal
    color: str
    valid_from: str | None
    valid_to: str | None
    status: str
    notes: str | None
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int


class EnrollmentDiscountCreateDTO(GeneratedDTO):
    enrollment_id: int
    type: str
    value: Decimal
    reason: str | None = None


class EnrollmentDiscountUpdateDTO(GeneratedDTO):
    enrollment_id: int | None = None
    type: str | None = None
    value: Decimal | None = None
    reason: str | None = None


class EnrollmentDiscountReadDTO(GeneratedDTO):
    id: int
    enrollment_id: int
    type: str
    value: Decimal
    reason: str | None
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int


class EnrollmentCreateDTO(GeneratedDTO):
    course_id: int
    student_person_id: int
    enrolled_on: str
    starts_on: str
    ends_on: str | None = None
    status: str | None = None
    notes: str | None = None


class EnrollmentUpdateDTO(GeneratedDTO):
    course_id: int | None = None
    student_person_id: int | None = None
    enrolled_on: str | None = None
    starts_on: str | None = None
    ends_on: str | None = None
    status: str | None = None
    notes: str | None = None


class EnrollmentReadDTO(GeneratedDTO):
    id: int
    course_id: int
    student_person_id: int
    enrolled_on: str
    starts_on: str
    ends_on: str | None
    status: str
    notes: str | None
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int


class InstrumentCreateDTO(GeneratedDTO):
    name: str
    is_active: bool | None = None
    display_order: int | None = None


class InstrumentUpdateDTO(GeneratedDTO):
    name: str | None = None
    is_active: bool | None = None
    display_order: int | None = None


class InstrumentReadDTO(GeneratedDTO):
    id: int
    name: str
    is_active: bool
    display_order: int
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int


class LessonAttendanceCreateDTO(GeneratedDTO):
    lesson_id: int
    student_person_id: int
    attendance: str | None = None
    recorded_at: str | None = None
    recorded_by: int | None = None


class LessonAttendanceUpdateDTO(GeneratedDTO):
    lesson_id: int | None = None
    student_person_id: int | None = None
    attendance: str | None = None
    recorded_at: str | None = None
    recorded_by: int | None = None


class LessonAttendanceReadDTO(GeneratedDTO):
    id: int
    lesson_id: int
    student_person_id: int
    attendance: str | None
    recorded_at: str | None
    recorded_by: int | None
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int


class LessonCreateDTO(GeneratedDTO):
    course_id: int
    teacher_person_id: int
    starts_at: str
    ends_at: str | None = None
    topic: str | None = None
    status: str | None = None
    notes: str | None = None


class LessonUpdateDTO(GeneratedDTO):
    course_id: int | None = None
    teacher_person_id: int | None = None
    starts_at: str | None = None
    ends_at: str | None = None
    topic: str | None = None
    status: str | None = None
    notes: str | None = None


class LessonReadDTO(GeneratedDTO):
    id: int
    course_id: int
    teacher_person_id: int
    starts_at: str
    ends_at: str | None
    topic: str | None
    status: str
    notes: str | None
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int


class MemberCreateDTO(GeneratedDTO):
    person_role_id: int
    membership_number: str | None = None
    membership_start_date: str
    membership_end_date: str | None = None
    annual_fee: Decimal | None = None
    notes: str | None = None


class MemberUpdateDTO(GeneratedDTO):
    person_role_id: int | None = None
    membership_number: str | None = None
    membership_start_date: str | None = None
    membership_end_date: str | None = None
    annual_fee: Decimal | None = None
    notes: str | None = None


class MemberReadDTO(GeneratedDTO):
    id: int
    person_role_id: int
    membership_number: str | None
    membership_start_date: str
    membership_end_date: str | None
    annual_fee: Decimal | None
    notes: str | None
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int


class MusicianInstrumentCreateDTO(GeneratedDTO):
    musician_id: int
    instrument_id: int
    is_primary: bool | None = None


class MusicianInstrumentUpdateDTO(GeneratedDTO):
    musician_id: int | None = None
    instrument_id: int | None = None
    is_primary: bool | None = None


class MusicianInstrumentReadDTO(GeneratedDTO):
    id: int
    musician_id: int
    instrument_id: int
    is_primary: bool
    created_at: str
    created_by: int | None


class MusicianSectionCreateDTO(GeneratedDTO):
    musician_id: int
    section_id: int


class MusicianSectionUpdateDTO(GeneratedDTO):
    musician_id: int | None = None
    section_id: int | None = None


class MusicianSectionReadDTO(GeneratedDTO):
    id: int
    musician_id: int
    section_id: int
    created_at: str
    created_by: int | None


class MusicianCreateDTO(GeneratedDTO):
    person_role_id: int
    joined_on: str
    left_on: str | None = None
    notes: str | None = None


class MusicianUpdateDTO(GeneratedDTO):
    person_role_id: int | None = None
    joined_on: str | None = None
    left_on: str | None = None
    notes: str | None = None


class MusicianReadDTO(GeneratedDTO):
    id: int
    person_role_id: int
    joined_on: str
    left_on: str | None
    notes: str | None
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int


class PersonCreateDTO(GeneratedDTO):
    first_name: str
    last_name: str
    birth_date: str | None = None
    birth_place: str | None = None
    tax_code: str | None = None
    residence_address: str | None = None
    email: str | None = None
    phone: str | None = None
    photo_key: str | None = None
    notes: str | None = None


class PersonUpdateDTO(GeneratedDTO):
    first_name: str | None = None
    last_name: str | None = None
    birth_date: str | None = None
    birth_place: str | None = None
    tax_code: str | None = None
    residence_address: str | None = None
    email: str | None = None
    phone: str | None = None
    photo_key: str | None = None
    notes: str | None = None


class PersonReadDTO(GeneratedDTO):
    id: int
    first_name: str
    last_name: str
    birth_date: str | None
    birth_place: str | None
    tax_code: str | None
    residence_address: str | None
    email: str | None
    phone: str | None
    photo_key: str | None
    notes: str | None
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int


class PersonRoleCreateDTO(GeneratedDTO):
    person_id: int
    role_type: str
    start_date: str
    end_date: str | None = None
    status: str | None = None
    notes: str | None = None


class PersonRoleUpdateDTO(GeneratedDTO):
    person_id: int | None = None
    role_type: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    status: str | None = None
    notes: str | None = None


class PersonRoleReadDTO(GeneratedDTO):
    id: int
    person_id: int
    role_type: str
    start_date: str
    end_date: str | None
    status: str
    notes: str | None
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int


class RefreshSessionCreateDTO(GeneratedDTO):
    user_id: int
    token_hash: str
    expires_at: str
    revoked_at: str | None = None
    client_info: str | None = None


class RefreshSessionUpdateDTO(GeneratedDTO):
    user_id: int | None = None
    token_hash: str | None = None
    expires_at: str | None = None
    revoked_at: str | None = None
    client_info: str | None = None


class RefreshSessionReadDTO(GeneratedDTO):
    id: int
    user_id: int
    token_hash: str
    expires_at: str
    revoked_at: str | None
    client_info: str | None
    created_at: str


class SectionCreateDTO(GeneratedDTO):
    name: str
    is_active: bool | None = None
    display_order: int | None = None


class SectionUpdateDTO(GeneratedDTO):
    name: str | None = None
    is_active: bool | None = None
    display_order: int | None = None


class SectionReadDTO(GeneratedDTO):
    id: int
    name: str
    is_active: bool
    display_order: int
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int


class StudentCreateDTO(GeneratedDTO):
    person_role_id: int
    notes: str | None = None


class StudentUpdateDTO(GeneratedDTO):
    person_role_id: int | None = None
    notes: str | None = None


class StudentReadDTO(GeneratedDTO):
    id: int
    person_role_id: int
    notes: str | None
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int


class TeacherCreateDTO(GeneratedDTO):
    person_role_id: int
    notes: str | None = None


class TeacherUpdateDTO(GeneratedDTO):
    person_role_id: int | None = None
    notes: str | None = None


class TeacherReadDTO(GeneratedDTO):
    id: int
    person_role_id: int
    notes: str | None
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int


class UserCreateDTO(GeneratedDTO):
    email: str
    password_hash: str
    display_name: str
    is_active: bool | None = None
    last_login_at: str | None = None


class UserUpdateDTO(GeneratedDTO):
    email: str | None = None
    password_hash: str | None = None
    display_name: str | None = None
    is_active: bool | None = None
    last_login_at: str | None = None


class UserReadDTO(GeneratedDTO):
    id: int
    email: str
    password_hash: str
    display_name: str
    is_active: bool
    last_login_at: str | None
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int


__all__ = ['GeneratedDTO', 'SCHEMA_FINGERPRINT', 'ActivityCreateDTO', 'ActivityUpdateDTO', 'ActivityReadDTO', 'ActivityParticipantCreateDTO', 'ActivityParticipantUpdateDTO', 'ActivityParticipantReadDTO', 'AppSettingCreateDTO', 'AppSettingUpdateDTO', 'AppSettingReadDTO', 'AssociatedContactCreateDTO', 'AssociatedContactUpdateDTO', 'AssociatedContactReadDTO', 'AuditEventCreateDTO', 'AuditEventUpdateDTO', 'AuditEventReadDTO', 'CourseInstallmentTemplateCreateDTO', 'CourseInstallmentTemplateUpdateDTO', 'CourseInstallmentTemplateReadDTO', 'CourseCreateDTO', 'CourseUpdateDTO', 'CourseReadDTO', 'EnrollmentDiscountCreateDTO', 'EnrollmentDiscountUpdateDTO', 'EnrollmentDiscountReadDTO', 'EnrollmentCreateDTO', 'EnrollmentUpdateDTO', 'EnrollmentReadDTO', 'InstrumentCreateDTO', 'InstrumentUpdateDTO', 'InstrumentReadDTO', 'LessonAttendanceCreateDTO', 'LessonAttendanceUpdateDTO', 'LessonAttendanceReadDTO', 'LessonCreateDTO', 'LessonUpdateDTO', 'LessonReadDTO', 'MemberCreateDTO', 'MemberUpdateDTO', 'MemberReadDTO', 'MusicianInstrumentCreateDTO', 'MusicianInstrumentUpdateDTO', 'MusicianInstrumentReadDTO', 'MusicianSectionCreateDTO', 'MusicianSectionUpdateDTO', 'MusicianSectionReadDTO', 'MusicianCreateDTO', 'MusicianUpdateDTO', 'MusicianReadDTO', 'PersonCreateDTO', 'PersonUpdateDTO', 'PersonReadDTO', 'PersonRoleCreateDTO', 'PersonRoleUpdateDTO', 'PersonRoleReadDTO', 'RefreshSessionCreateDTO', 'RefreshSessionUpdateDTO', 'RefreshSessionReadDTO', 'SectionCreateDTO', 'SectionUpdateDTO', 'SectionReadDTO', 'StudentCreateDTO', 'StudentUpdateDTO', 'StudentReadDTO', 'TeacherCreateDTO', 'TeacherUpdateDTO', 'TeacherReadDTO', 'UserCreateDTO', 'UserUpdateDTO', 'UserReadDTO']
