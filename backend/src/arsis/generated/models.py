"""Generated SQLAlchemy models. Do not edit by hand."""
# ruff: noqa

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

SCHEMA_FINGERPRINT = "77d9187285b63207"


class Base(DeclarativeBase):
    pass


class AccountingCategory(Base):
    __tablename__ = "accounting_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    direction: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    required_person_role: Mapped[str | None] = mapped_column(Text, ForeignKey('role_types.code', ondelete='RESTRICT'), primary_key=False, nullable=True)
    course_required: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('0'))
    color: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, primary_key=False, nullable=False, server_default=text('1'))
    display_order: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('0'))
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class AccountingMovement(Base):
    __tablename__ = "accounting_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    occurred_on: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    direction: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    account: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('accounting_categories.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(scale=2), primary_key=False, nullable=False)
    subject: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    person_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('people.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    course_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('courses.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    description: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    document_reference: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))
    is_highlighted: Mapped[bool] = mapped_column(Boolean, primary_key=False, nullable=False, server_default=text('0'))


class AccountingOpeningBalance(Base):
    __tablename__ = "accounting_opening_balances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    fiscal_year: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False)
    account: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(scale=2), primary_key=False, nullable=False)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    type: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    title: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    starts_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    ends_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    location: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    status: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text("'planned'"))
    reference_person_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('people.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))
    place_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('places.id', ondelete='RESTRICT'), primary_key=False, nullable=True)


class ActivityParticipant(Base):
    __tablename__ = "activity_participants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    activity_id: Mapped[int] = mapped_column(Integer, ForeignKey('activities.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey('people.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    source: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    attendance: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    attendance_recorded_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    attendance_recorded_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))
    is_driver: Mapped[bool] = mapped_column(Boolean, primary_key=False, nullable=False, server_default=text('0'))
    passenger_count: Mapped[int | None] = mapped_column(Integer, primary_key=False, nullable=True)
    refund_flat_amount: Mapped[Decimal | None] = mapped_column(Numeric(scale=2), primary_key=False, nullable=True)
    refund_distance_km: Mapped[int | None] = mapped_column(Integer, primary_key=False, nullable=True)
    refund_rate_per_km: Mapped[Decimal | None] = mapped_column(Numeric(scale=2), primary_key=False, nullable=True)
    refund_bonus_pct: Mapped[int | None] = mapped_column(Integer, primary_key=False, nullable=True)
    refund_mileage_amount: Mapped[Decimal | None] = mapped_column(Numeric(scale=2), primary_key=False, nullable=True)
    refund_highway_amount: Mapped[Decimal | None] = mapped_column(Numeric(scale=2), primary_key=False, nullable=True)


class AppSetting(Base):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(Text, primary_key=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text("'{}'"))
    description: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)


class AssociatedContact(Base):
    __tablename__ = "associated_contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey('people.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    contact_person_id: Mapped[int] = mapped_column(Integer, ForeignKey('people.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    relationship_type: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, primary_key=False, nullable=False, server_default=text('0'))
    is_payment_contact: Mapped[bool] = mapped_column(Boolean, primary_key=False, nullable=False, server_default=text('0'))
    notes: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    occurred_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    action: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    entity_type: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    entity_id: Mapped[int | None] = mapped_column(Integer, primary_key=False, nullable=True)
    request_id: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    details: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text("'{}'"))
    ip_address: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)


class CourseInstallmentTemplate(Base):
    __tablename__ = "course_installment_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey('courses.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    sequence_number: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(scale=2), primary_key=False, nullable=False)
    due_month: Mapped[int | None] = mapped_column(Integer, primary_key=False, nullable=True)
    due_day: Mapped[int | None] = mapped_column(Integer, primary_key=False, nullable=True)
    proposed_due_date: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    mode: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    category: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    instrument_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('instruments.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    teacher_person_id: Mapped[int] = mapped_column(Integer, ForeignKey('people.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    weekday: Mapped[int | None] = mapped_column(Integer, primary_key=False, nullable=True)
    start_time: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    end_time: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    annual_fee: Mapped[Decimal] = mapped_column(Numeric(scale=2), primary_key=False, nullable=False)
    color: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    valid_from: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    valid_to: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    status: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text("'active'"))
    notes: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class EnrollmentDiscount(Base):
    __tablename__ = "enrollment_discounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    enrollment_id: Mapped[int] = mapped_column(Integer, ForeignKey('enrollments.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    type: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(scale=2), primary_key=False, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class Enrollment(Base):
    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey('courses.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    student_person_id: Mapped[int] = mapped_column(Integer, ForeignKey('people.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    enrolled_on: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    starts_on: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    ends_on: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    status: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text("'active'"))
    notes: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class Instrument(Base):
    __tablename__ = "instruments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    section_id: Mapped[int] = mapped_column(Integer, ForeignKey('sections.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, primary_key=False, nullable=False, server_default=text('1'))
    display_order: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('0'))
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class LessonAttendance(Base):
    __tablename__ = "lesson_attendances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    lesson_id: Mapped[int] = mapped_column(Integer, ForeignKey('lessons.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    student_person_id: Mapped[int] = mapped_column(Integer, ForeignKey('people.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    attendance: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    recorded_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    recorded_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey('courses.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    teacher_person_id: Mapped[int] = mapped_column(Integer, ForeignKey('people.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    starts_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    ends_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    topic: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    status: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text("'planned'"))
    notes: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    person_role_id: Mapped[int] = mapped_column(Integer, ForeignKey('person_roles.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    membership_number: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    membership_start_date: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    membership_end_date: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    annual_fee: Mapped[Decimal | None] = mapped_column(Numeric(scale=2), primary_key=False, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class MilestoneAchievement(Base):
    __tablename__ = "milestone_achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    milestone_id: Mapped[int] = mapped_column(Integer, ForeignKey('milestones.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey('people.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    reached_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    progress: Mapped[Decimal] = mapped_column(Numeric(scale=2), primary_key=False, nullable=False)
    status: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text("'open'"))
    reset_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('milestone_resets.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    closed_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)


class MilestoneReset(Base):
    __tablename__ = "milestone_resets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    milestone_id: Mapped[int] = mapped_column(Integer, ForeignKey('milestones.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey('people.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    consumed: Mapped[Decimal] = mapped_column(Numeric(scale=2), primary_key=False, nullable=False)
    progress_before: Mapped[Decimal] = mapped_column(Numeric(scale=2), primary_key=False, nullable=False)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)


class Milestone(Base):
    __tablename__ = "milestones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    metric: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    threshold: Mapped[Decimal] = mapped_column(Numeric(scale=2), primary_key=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class MusicianInstrument(Base):
    __tablename__ = "musician_instruments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    musician_id: Mapped[int] = mapped_column(Integer, ForeignKey('musicians.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    instrument_id: Mapped[int] = mapped_column(Integer, ForeignKey('instruments.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, primary_key=False, nullable=False, server_default=text('0'))
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)


class Musician(Base):
    __tablename__ = "musicians"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    person_role_id: Mapped[int] = mapped_column(Integer, ForeignKey('person_roles.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    joined_on: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    left_on: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    first_name: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    last_name: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    birth_date: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    birth_place: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    tax_code: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    residence_address: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    email: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    phone: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    photo_key: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class PersonRole(Base):
    __tablename__ = "person_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey('people.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    role_type: Mapped[str] = mapped_column(Text, ForeignKey('role_types.code', ondelete='RESTRICT'), primary_key=False, nullable=False)
    start_date: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    end_date: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    status: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text("'active'"))
    notes: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class Place(Base):
    __tablename__ = "places"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    address: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    distance_km: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('0'))
    highway_cost: Mapped[Decimal] = mapped_column(Numeric(scale=2), primary_key=False, nullable=False, server_default=text('0'))
    notes: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class RefreshSession(Base):
    __tablename__ = "refresh_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=False, nullable=False)
    token_hash: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    expires_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    revoked_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    client_info: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))


class RoleType(Base):
    __tablename__ = "role_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    code: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    name: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    plural_name: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, primary_key=False, nullable=False, server_default=text('0'))
    display_order: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('0'))
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, primary_key=False, nullable=False, server_default=text('1'))
    display_order: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('0'))
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    person_role_id: Mapped[int] = mapped_column(Integer, ForeignKey('person_roles.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    person_role_id: Mapped[int] = mapped_column(Integer, ForeignKey('person_roles.id', ondelete='RESTRICT'), primary_key=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    email: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, primary_key=False, nullable=False, server_default=text('1'))
    last_login_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    created_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    updated_at: Mapped[str] = mapped_column(Text, primary_key=False, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    archived_at: Mapped[str | None] = mapped_column(Text, primary_key=False, nullable=True)
    archived_by: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=False, nullable=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=False, nullable=False, server_default=text('1'))


__all__ = ['Base', 'SCHEMA_FINGERPRINT', 'AccountingCategory', 'AccountingMovement', 'AccountingOpeningBalance', 'Activity', 'ActivityParticipant', 'AppSetting', 'AssociatedContact', 'AuditEvent', 'CourseInstallmentTemplate', 'Course', 'EnrollmentDiscount', 'Enrollment', 'Instrument', 'LessonAttendance', 'Lesson', 'Member', 'MilestoneAchievement', 'MilestoneReset', 'Milestone', 'MusicianInstrument', 'Musician', 'Person', 'PersonRole', 'Place', 'RefreshSession', 'RoleType', 'Section', 'Student', 'Teacher', 'User']
