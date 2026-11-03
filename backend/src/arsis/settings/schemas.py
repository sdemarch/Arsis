from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator

from arsis.auth.schemas import normalize_email
from arsis.core.api_models import ApiModel


class GeneralSettingsResponse(ApiModel):
    organization_name: str
    organization_name_version: int
    archive_google_drive_url: str
    archive_google_drive_url_version: int
    default_theme: Literal["light", "dark"]
    default_theme_version: int


class GeneralSettingsUpdateRequest(ApiModel):
    organization_name: str = Field(min_length=1, max_length=200)
    organization_name_version: int = Field(ge=1)
    archive_google_drive_url: str = Field(max_length=2_000)
    archive_google_drive_url_version: int = Field(ge=1)
    default_theme: Literal["light", "dark"]
    default_theme_version: int = Field(ge=1)

    @field_validator("organization_name")
    @classmethod
    def validate_organization_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Il nome dell'organizzazione è obbligatorio")
        return normalized


class ResponsibleUserResponse(ApiModel):
    id: int
    email: str
    display_name: str
    is_active: bool
    last_login_at: datetime | None
    version: int


class ResponsibleUserCreateRequest(ApiModel):
    email: str = Field(min_length=3, max_length=320)
    display_name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=12, max_length=256)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Il nome visualizzato è obbligatorio")
        return normalized


class ResponsibleUserUpdateRequest(ApiModel):
    is_active: bool
    version: int = Field(ge=1)
