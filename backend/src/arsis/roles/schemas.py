"""Public HTTP contracts for the role catalogue."""

from pydantic import Field

from arsis.core.api_models import ApiModel


class RoleTypeCreateRequest(ApiModel):
    name: str = Field(min_length=1, max_length=100)
    plural_name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    display_order: int | None = Field(default=None, ge=0, le=100_000)


class RoleTypeUpdateRequest(ApiModel):
    version: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=100)
    plural_name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    display_order: int | None = Field(default=None, ge=0, le=100_000)


class RoleTypeResponse(ApiModel):
    id: int
    code: str
    name: str
    plural_name: str
    description: str | None
    is_system: bool
    display_order: int
    active_people: int = 0
    archived_at: str | None
    version: int
