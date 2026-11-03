from pydantic import Field

from arsis.core.api_models import ApiModel


class SectionCreateRequest(ApiModel):
    name: str = Field(min_length=1, max_length=100)
    display_order: int = Field(default=0, ge=0)


class SectionUpdateRequest(ApiModel):
    version: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=100)
    display_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class SectionResponse(SectionCreateRequest):
    id: int
    is_active: bool
    archived_at: str | None
    version: int


class InstrumentCreateRequest(ApiModel):
    name: str = Field(min_length=1, max_length=100)
    section_id: int = Field(ge=1)
    display_order: int = Field(default=0, ge=0)


class InstrumentUpdateRequest(ApiModel):
    version: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=100)
    section_id: int | None = Field(default=None, ge=1)
    display_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class InstrumentResponse(InstrumentCreateRequest):
    id: int
    is_active: bool
    archived_at: str | None
    version: int
