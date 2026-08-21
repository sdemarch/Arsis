"""Generated Pydantic persistence DTOs. Do not edit by hand."""
# ruff: noqa

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict

SCHEMA_FINGERPRINT = "ede14014cdb9bec6"


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
    reference_person_id: str | None = None
    notes: str | None = None


class ActivityUpdateDTO(GeneratedDTO):
    type: str | None = None
    title: str | None = None
    description: str | None = None
    starts_at: str | None = None
    ends_at: str | None = None
    location: str | None = None
    status: str | None = None
    reference_person_id: str | None = None
    notes: str | None = None


class ActivityReadDTO(GeneratedDTO):
    id: str
    type: str
    title: str
    description: str | None
    starts_at: str
    ends_at: str | None
    location: str | None
    status: str
    reference_person_id: str | None
    notes: str | None
    created_at: str
    created_by: str | None
    updated_at: str
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None
    version: int


class ActivityParticipantCreateDTO(GeneratedDTO):
    activity_id: str
    person_id: str
    source: str
    attendance: str | None = None
    attendance_recorded_at: str | None = None
    attendance_recorded_by: str | None = None


class ActivityParticipantUpdateDTO(GeneratedDTO):
    activity_id: str | None = None
    person_id: str | None = None
    source: str | None = None
    attendance: str | None = None
    attendance_recorded_at: str | None = None
    attendance_recorded_by: str | None = None


class ActivityParticipantReadDTO(GeneratedDTO):
    id: str
    activity_id: str
    person_id: str
    source: str
    attendance: str | None
    attendance_recorded_at: str | None
    attendance_recorded_by: str | None
    created_at: str
    created_by: str | None
    updated_at: str
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None
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
    created_by: str | None
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None


class AssociatedContactCreateDTO(GeneratedDTO):
    person_id: str
    contact_person_id: str
    relationship_type: str
    is_primary: bool | None = None
    is_payment_contact: bool | None = None
    notes: str | None = None


class AssociatedContactUpdateDTO(GeneratedDTO):
    person_id: str | None = None
    contact_person_id: str | None = None
    relationship_type: str | None = None
    is_primary: bool | None = None
    is_payment_contact: bool | None = None
    notes: str | None = None


class AssociatedContactReadDTO(GeneratedDTO):
    id: str
    person_id: str
    contact_person_id: str
    relationship_type: str
    is_primary: bool
    is_payment_contact: bool
    notes: str | None
    created_at: str
    created_by: str | None
    updated_at: str
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None
    version: int


class AuditEventCreateDTO(GeneratedDTO):
    occurred_at: str | None = None
    user_id: str | None = None
    action: str
    entity_type: str
    entity_id: str | None = None
    request_id: str | None = None
    details: str | None = None
    ip_address: str | None = None


class AuditEventUpdateDTO(GeneratedDTO):
    occurred_at: str | None = None
    user_id: str | None = None
    action: str | None = None
    entity_type: str | None = None
    entity_id: str | None = None
    request_id: str | None = None
    details: str | None = None
    ip_address: str | None = None


class AuditEventReadDTO(GeneratedDTO):
    id: str
    occurred_at: str
    user_id: str | None
    action: str
    entity_type: str
    entity_id: str | None
    request_id: str | None
    details: str
    ip_address: str | None


class CourseInstallmentTemplateCreateDTO(GeneratedDTO):
    course_id: str
    sequence_number: int
    description: str | None = None
    amount: Decimal
    due_month: int | None = None
    due_day: int | None = None
    proposed_due_date: str | None = None


class CourseInstallmentTemplateUpdateDTO(GeneratedDTO):
    course_id: str | None = None
    sequence_number: int | None = None
    description: str | None = None
    amount: Decimal | None = None
    due_month: int | None = None
    due_day: int | None = None
    proposed_due_date: str | None = None


class CourseInstallmentTemplateReadDTO(GeneratedDTO):
    id: str
    course_id: str
    sequence_number: int
    description: str | None
    amount: Decimal
    due_month: int | None
    due_day: int | None
    proposed_due_date: str | None
    created_at: str
    created_by: str | None
    updated_at: str
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None
    version: int


class CourseCreateDTO(GeneratedDTO):
    name: str
    description: str | None = None
    mode: str
    category: str
    instrument_id: str | None = None
    teacher_person_id: str
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
    instrument_id: str | None = None
    teacher_person_id: str | None = None
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
    id: str
    name: str
    description: str | None
    mode: str
    category: str
    instrument_id: str | None
    teacher_person_id: str
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
    created_by: str | None
    updated_at: str
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None
    version: int


class EnrollmentDiscountCreateDTO(GeneratedDTO):
    enrollment_id: str
    type: str
    value: Decimal
    reason: str | None = None


class EnrollmentDiscountUpdateDTO(GeneratedDTO):
    enrollment_id: str | None = None
    type: str | None = None
    value: Decimal | None = None
    reason: str | None = None


class EnrollmentDiscountReadDTO(GeneratedDTO):
    id: str
    enrollment_id: str
    type: str
    value: Decimal
    reason: str | None
    created_at: str
    created_by: str | None
    updated_at: str
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None
    version: int


class EnrollmentCreateDTO(GeneratedDTO):
    course_id: str
    student_person_id: str
    enrolled_on: str
    starts_on: str
    ends_on: str | None = None
    status: str | None = None
    notes: str | None = None


class EnrollmentUpdateDTO(GeneratedDTO):
    course_id: str | None = None
    student_person_id: str | None = None
    enrolled_on: str | None = None
    starts_on: str | None = None
    ends_on: str | None = None
    status: str | None = None
    notes: str | None = None


class EnrollmentReadDTO(GeneratedDTO):
    id: str
    course_id: str
    student_person_id: str
    enrolled_on: str
    starts_on: str
    ends_on: str | None
    status: str
    notes: str | None
    created_at: str
    created_by: str | None
    updated_at: str
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None
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
    id: str
    name: str
    is_active: bool
    display_order: int
    created_at: str
    created_by: str | None
    updated_at: str
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None
    version: int


class LessonAttendanceCreateDTO(GeneratedDTO):
    lesson_id: str
    student_person_id: str
    attendance: str | None = None
    recorded_at: str | None = None
    recorded_by: str | None = None


class LessonAttendanceUpdateDTO(GeneratedDTO):
    lesson_id: str | None = None
    student_person_id: str | None = None
    attendance: str | None = None
    recorded_at: str | None = None
    recorded_by: str | None = None


class LessonAttendanceReadDTO(GeneratedDTO):
    id: str
    lesson_id: str
    student_person_id: str
    attendance: str | None
    recorded_at: str | None
    recorded_by: str | None
    created_at: str
    created_by: str | None
    updated_at: str
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None
    version: int


class LessonCreateDTO(GeneratedDTO):
    course_id: str
    teacher_person_id: str
    starts_at: str
    ends_at: str | None = None
    topic: str | None = None
    status: str | None = None
    notes: str | None = None


class LessonUpdateDTO(GeneratedDTO):
    course_id: str | None = None
    teacher_person_id: str | None = None
    starts_at: str | None = None
    ends_at: str | None = None
    topic: str | None = None
    status: str | None = None
    notes: str | None = None


class LessonReadDTO(GeneratedDTO):
    id: str
    course_id: str
    teacher_person_id: str
    starts_at: str
    ends_at: str | None
    topic: str | None
    status: str
    notes: str | None
    created_at: str
    created_by: str | None
    updated_at: str
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None
    version: int


class MemberCreateDTO(GeneratedDTO):
    person_role_id: str
    membership_number: str | None = None
    membership_start_date: str
    membership_end_date: str | None = None
    annual_fee: Decimal | None = None
    notes: str | None = None


class MemberUpdateDTO(GeneratedDTO):
    person_role_id: str | None = None
    membership_number: str | None = None
    membership_start_date: str | None = None
    membership_end_date: str | None = None
    annual_fee: Decimal | None = None
    notes: str | None = None


class MemberReadDTO(GeneratedDTO):
    id: str
    person_role_id: str
    membership_number: str | None
    membership_start_date: str
    membership_end_date: str | None
    annual_fee: Decimal | None
    notes: str | None
    created_at: str
    created_by: str | None
    updated_at: str
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None
    version: int


class MusicianInstrumentCreateDTO(GeneratedDTO):
    musician_id: str
    instrument_id: str
    is_primary: bool | None = None


class MusicianInstrumentUpdateDTO(GeneratedDTO):
    musician_id: str | None = None
    instrument_id: str | None = None
    is_primary: bool | None = None


class MusicianInstrumentReadDTO(GeneratedDTO):
    id: str
    musician_id: str
    instrument_id: str
    is_primary: bool
    created_at: str
    created_by: str | None


class MusicianSectionCreateDTO(GeneratedDTO):
    musician_id: str
    section_id: str


class MusicianSectionUpdateDTO(GeneratedDTO):
    musician_id: str | None = None
    section_id: str | None = None


class MusicianSectionReadDTO(GeneratedDTO):
    id: str
    musician_id: str
    section_id: str
    created_at: str
    created_by: str | None


class MusicianCreateDTO(GeneratedDTO):
    person_role_id: str
    joined_on: str
    left_on: str | None = None
    notes: str | None = None


class MusicianUpdateDTO(GeneratedDTO):
    person_role_id: str | None = None
    joined_on: str | None = None
    left_on: str | None = None
    notes: str | None = None


class MusicianReadDTO(GeneratedDTO):
    id: str
    person_role_id: str
    joined_on: str
    left_on: str | None
    notes: str | None
    created_at: str
    created_by: str | None
    updated_at: str
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None
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
    id: str
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
    created_by: str | None
    updated_at: str
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None
    version: int


class PersonRoleCreateDTO(GeneratedDTO):
    person_id: str
    role_type: str
    start_date: str
    end_date: str | None = None
    status: str | None = None
    notes: str | None = None


class PersonRoleUpdateDTO(GeneratedDTO):
    person_id: str | None = None
    role_type: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    status: str | None = None
    notes: str | None = None


class PersonRoleReadDTO(GeneratedDTO):
    id: str
    person_id: str
    role_type: str
    start_date: str
    end_date: str | None
    status: str
    notes: str | None
    created_at: str
    created_by: str | None
    updated_at: str
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None
    version: int


class RefreshSessionCreateDTO(GeneratedDTO):
    user_id: str
    token_hash: str
    expires_at: str
    revoked_at: str | None = None
    client_info: str | None = None


class RefreshSessionUpdateDTO(GeneratedDTO):
    user_id: str | None = None
    token_hash: str | None = None
    expires_at: str | None = None
    revoked_at: str | None = None
    client_info: str | None = None


class RefreshSessionReadDTO(GeneratedDTO):
    id: str
    user_id: str
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
    id: str
    name: str
    is_active: bool
    display_order: int
    created_at: str
    created_by: str | None
    updated_at: str
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None
    version: int


class StudentCreateDTO(GeneratedDTO):
    person_role_id: str
    notes: str | None = None


class StudentUpdateDTO(GeneratedDTO):
    person_role_id: str | None = None
    notes: str | None = None


class StudentReadDTO(GeneratedDTO):
    id: str
    person_role_id: str
    notes: str | None
    created_at: str
    created_by: str | None
    updated_at: str
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None
    version: int


class TeacherCreateDTO(GeneratedDTO):
    person_role_id: str
    notes: str | None = None


class TeacherUpdateDTO(GeneratedDTO):
    person_role_id: str | None = None
    notes: str | None = None


class TeacherReadDTO(GeneratedDTO):
    id: str
    person_role_id: str
    notes: str | None
    created_at: str
    created_by: str | None
    updated_at: str
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None
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
    id: str
    email: str
    password_hash: str
    display_name: str
    is_active: bool
    last_login_at: str | None
    created_at: str
    created_by: str | None
    updated_at: str
    updated_by: str | None
    archived_at: str | None
    archived_by: str | None
    version: int


__all__ = ['GeneratedDTO', 'SCHEMA_FINGERPRINT', 'ActivityCreateDTO', 'ActivityUpdateDTO', 'ActivityReadDTO', 'ActivityParticipantCreateDTO', 'ActivityParticipantUpdateDTO', 'ActivityParticipantReadDTO', 'AppSettingCreateDTO', 'AppSettingUpdateDTO', 'AppSettingReadDTO', 'AssociatedContactCreateDTO', 'AssociatedContactUpdateDTO', 'AssociatedContactReadDTO', 'AuditEventCreateDTO', 'AuditEventUpdateDTO', 'AuditEventReadDTO', 'CourseInstallmentTemplateCreateDTO', 'CourseInstallmentTemplateUpdateDTO', 'CourseInstallmentTemplateReadDTO', 'CourseCreateDTO', 'CourseUpdateDTO', 'CourseReadDTO', 'EnrollmentDiscountCreateDTO', 'EnrollmentDiscountUpdateDTO', 'EnrollmentDiscountReadDTO', 'EnrollmentCreateDTO', 'EnrollmentUpdateDTO', 'EnrollmentReadDTO', 'InstrumentCreateDTO', 'InstrumentUpdateDTO', 'InstrumentReadDTO', 'LessonAttendanceCreateDTO', 'LessonAttendanceUpdateDTO', 'LessonAttendanceReadDTO', 'LessonCreateDTO', 'LessonUpdateDTO', 'LessonReadDTO', 'MemberCreateDTO', 'MemberUpdateDTO', 'MemberReadDTO', 'MusicianInstrumentCreateDTO', 'MusicianInstrumentUpdateDTO', 'MusicianInstrumentReadDTO', 'MusicianSectionCreateDTO', 'MusicianSectionUpdateDTO', 'MusicianSectionReadDTO', 'MusicianCreateDTO', 'MusicianUpdateDTO', 'MusicianReadDTO', 'PersonCreateDTO', 'PersonUpdateDTO', 'PersonReadDTO', 'PersonRoleCreateDTO', 'PersonRoleUpdateDTO', 'PersonRoleReadDTO', 'RefreshSessionCreateDTO', 'RefreshSessionUpdateDTO', 'RefreshSessionReadDTO', 'SectionCreateDTO', 'SectionUpdateDTO', 'SectionReadDTO', 'StudentCreateDTO', 'StudentUpdateDTO', 'StudentReadDTO', 'TeacherCreateDTO', 'TeacherUpdateDTO', 'TeacherReadDTO', 'UserCreateDTO', 'UserUpdateDTO', 'UserReadDTO']
