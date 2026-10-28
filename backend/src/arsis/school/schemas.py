from decimal import Decimal
from typing import Literal

from pydantic import Field

from arsis.core.api_models import ApiModel


class CourseCreateRequest(ApiModel):
    name: str = Field(min_length=1, max_length=200)
    mode: Literal['individual', 'group']
    category: Literal['instrument', 'ensemble']
    teacher_person_id: int = Field(ge=1)
    annual_fee: Decimal = Field(ge=0)
    color: str = Field(pattern=r'^#[0-9A-Fa-f]{6}$')
    instrument_id: int | None = Field(default=None, ge=1)
    description: str | None = None
    weekday: int | None = Field(default=None, ge=1, le=7)
    start_time: str | None = None
    end_time: str | None = None
    valid_from: str | None = None
    valid_to: str | None = None
    status: Literal['active', 'inactive'] | None = None
    notes: str | None = None


class CourseUpdateRequest(CourseCreateRequest):
    version: int = Field(ge=1)


class CourseResponse(CourseCreateRequest):
    id: int
    status: Literal['active', 'inactive']
    created_at: str
    updated_at: str
    archived_at: str | None
    version: int
