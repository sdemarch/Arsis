"""Public HTTP contracts for activities."""

from typing import Literal

from pydantic import Field, model_validator

from arsis.core.api_models import ApiModel

ActivityType = Literal["rehearsal", "concert", "event"]
ActivityStatus = Literal["planned", "confirmed", "cancelled", "completed"]


class ActivityCreateRequest(ApiModel):
    type: ActivityType
    title: str = Field(min_length=1, max_length=300)
    description: str | None = None
    starts_at: str = Field(min_length=16, max_length=40)
    ends_at: str | None = Field(default=None, min_length=16, max_length=40)
    location: str | None = None
    status: ActivityStatus | None = None
    reference_person_id: int | None = Field(default=None, ge=1)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> ActivityCreateRequest:
        if self.ends_at is not None and self.ends_at <= self.starts_at:
            raise ValueError("La fine dell'attività deve seguire l'inizio")
        return self


class ActivityUpdateRequest(ApiModel):
    version: int = Field(ge=1)
    type: ActivityType | None = None
    title: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = None
    starts_at: str | None = Field(default=None, min_length=16, max_length=40)
    ends_at: str | None = Field(default=None, min_length=16, max_length=40)
    location: str | None = None
    status: ActivityStatus | None = None
    reference_person_id: int | None = Field(default=None, ge=1)
    notes: str | None = None


class ActivityResponse(ApiModel):
    id: int
    type: ActivityType
    title: str
    description: str | None
    starts_at: str
    ends_at: str | None
    location: str | None
    status: ActivityStatus
    reference_person_id: int | None
    notes: str | None
    created_at: str
    created_by: int | None
    updated_at: str
    updated_by: int | None
    archived_at: str | None
    archived_by: int | None
    version: int
