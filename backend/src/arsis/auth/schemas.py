from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field, SecretStr, StringConstraints, field_validator

from arsis.core.api_models import ApiModel

Email = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=3, max_length=320),
]


def normalize_email(value: str) -> str:
    normalized = value.strip().lower()
    local, separator, domain = normalized.rpartition("@")
    if (
        normalized.count("@") != 1
        or not separator
        or not local
        or any(character.isspace() for character in normalized)
        or "." not in domain
        or domain.startswith(".")
        or domain.endswith(".")
    ):
        raise ValueError("Indirizzo email non valido")
    return normalized


class LoginRequest(ApiModel):
    email: Email
    password: SecretStr = Field(min_length=8, max_length=256)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class AuthUser(ApiModel):
    id: int
    email: str
    display_name: str
    role: Literal["responsible"] = "responsible"
    last_login_at: datetime | None = None
    version: int = Field(ge=1)


class TokenResponse(ApiModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(gt=0)
    user: AuthUser
