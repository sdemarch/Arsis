"""Public HTTP contracts for places."""

from decimal import Decimal

from pydantic import Field

from arsis.core.api_models import ApiModel


class PlaceCreateRequest(ApiModel):
    name: str = Field(min_length=1, max_length=200)
    address: str | None = Field(default=None, max_length=500)
    distance_km: int = Field(default=0, ge=0, le=100_000)
    highway_cost: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=12, decimal_places=2)
    notes: str | None = None


class PlaceUpdateRequest(ApiModel):
    version: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    address: str | None = Field(default=None, max_length=500)
    distance_km: int | None = Field(default=None, ge=0, le=100_000)
    highway_cost: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    notes: str | None = None


class PlaceResponse(ApiModel):
    id: int
    name: str
    address: str | None
    distance_km: int
    highway_cost: Decimal
    notes: str | None
    archived_at: str | None
    version: int
