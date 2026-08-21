from arsis.generated.models import (
    SCHEMA_FINGERPRINT as MODEL_FINGERPRINT,
)
from arsis.generated.models import Base, Person, PersonRole
from arsis.generated.schemas import (
    SCHEMA_FINGERPRINT as DTO_FINGERPRINT,
)
from arsis.generated.schemas import AppSettingUpdateDTO, PersonCreateDTO, PersonUpdateDTO

EXPECTED_TABLES = {
    "activities",
    "activity_participants",
    "app_settings",
    "associated_contacts",
    "audit_events",
    "course_installment_templates",
    "courses",
    "enrollment_discounts",
    "enrollments",
    "instruments",
    "lesson_attendances",
    "lessons",
    "members",
    "musician_instruments",
    "musician_sections",
    "musicians",
    "people",
    "person_roles",
    "refresh_sessions",
    "sections",
    "students",
    "teachers",
    "users",
}


def test_generated_models_cover_the_application_schema() -> None:
    assert set(Base.metadata.tables) == EXPECTED_TABLES
    assert MODEL_FINGERPRINT == DTO_FINGERPRINT


def test_generated_models_preserve_column_and_foreign_key_metadata() -> None:
    assert Person.__table__.c.first_name.nullable is False
    assert Person.__table__.c.email.nullable is True
    person_foreign_key = next(iter(PersonRole.__table__.c.person_id.foreign_keys))
    assert person_foreign_key.target_fullname == "people.id"


def test_generated_create_and_update_dtos_have_expected_semantics() -> None:
    create_dto = PersonCreateDTO(first_name="Mario", last_name="Rossi")
    assert create_dto.model_dump(exclude_unset=True) == {
        "first_name": "Mario",
        "last_name": "Rossi",
    }

    update_dto = PersonUpdateDTO(email="mario.rossi@example.it")
    assert update_dto.model_dump(exclude_unset=True) == {
        "email": "mario.rossi@example.it"
    }
    assert "key" not in AppSettingUpdateDTO.model_fields
