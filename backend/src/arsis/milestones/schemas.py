"""Public HTTP contracts for milestones (RB-19)."""

from decimal import Decimal
from typing import Literal

from pydantic import Field

from arsis.core.api_models import ApiModel

MilestoneMetric = Literal[
    "rehearsal_count", "concert_count", "event_count", "attendance_count", "reimbursement_total"
]
COUNT_METRICS: frozenset[str] = frozenset(
    {"rehearsal_count", "concert_count", "event_count", "attendance_count"}
)


class MilestoneCreateRequest(ApiModel):
    name: str = Field(min_length=1, max_length=200)
    metric: MilestoneMetric
    threshold: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    notes: str | None = None


class MilestoneUpdateRequest(ApiModel):
    version: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    metric: MilestoneMetric | None = None
    threshold: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    notes: str | None = None


class MilestoneResponse(ApiModel):
    id: int
    name: str
    metric: MilestoneMetric
    threshold: Decimal
    notes: str | None
    archived_at: str | None
    version: int


class MilestoneProgressResponse(ApiModel):
    person_id: int
    person_name: str
    progress: Decimal
    remaining: Decimal
    times_reached: int
    last_reset_id: int | None
    last_reset_at: str | None


class MilestoneBoardResponse(ApiModel):
    milestone: MilestoneResponse
    reached: list[MilestoneProgressResponse]
    in_progress: list[MilestoneProgressResponse]


class MilestoneResetRequest(ApiModel):
    person_ids: list[int] = Field(min_length=1, max_length=500)
