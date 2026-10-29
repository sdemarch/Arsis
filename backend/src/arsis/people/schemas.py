"""Public HTTP contracts for the people registry."""

from pydantic import Field

from arsis.core.api_models import ApiModel


class PersonCreateRequest(ApiModel):
    first_name: str = Field(min_length=1, max_length=200)
    last_name: str = Field(min_length=1, max_length=200)
    birth_date: str | None = None
    birth_place: str | None = None
    tax_code: str | None = None
    residence_address: str | None = None
    email: str | None = None
    phone: str | None = None
    photo_key: str | None = None
    notes: str | None = None


class PersonUpdateRequest(ApiModel):
    version: int = Field(ge=1)
    first_name: str | None = Field(default=None, min_length=1, max_length=200)
    last_name: str | None = Field(default=None, min_length=1, max_length=200)
    birth_date: str | None = None
    birth_place: str | None = None
    tax_code: str | None = None
    residence_address: str | None = None
    email: str | None = None
    phone: str | None = None
    photo_key: str | None = None
    notes: str | None = None


class PersonResponse(ApiModel):
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


class PersonRoleCreateRequest(ApiModel):
    role_type: str = Field(min_length=1, max_length=50)
    start_date: str = Field(min_length=10, max_length=10)
    end_date: str | None = Field(default=None, min_length=10, max_length=10)
    status: str | None = Field(default=None, min_length=1, max_length=20)
    notes: str | None = None


class PersonRoleUpdateRequest(ApiModel):
    version: int = Field(ge=1)
    person_id: int | None = Field(default=None, ge=1)
    role_type: str | None = Field(default=None, min_length=1, max_length=50)
    start_date: str | None = Field(default=None, min_length=10, max_length=10)
    end_date: str | None = Field(default=None, min_length=10, max_length=10)
    status: str | None = Field(default=None, min_length=1, max_length=20)
    notes: str | None = None


class PersonRoleResponse(ApiModel):
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
