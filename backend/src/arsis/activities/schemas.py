"""Public HTTP contracts for activities."""

from decimal import Decimal
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
    place_id: int | None = Field(default=None, ge=1)
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
    place_id: int | None = Field(default=None, ge=1)
    status: ActivityStatus | None = None
    reference_person_id: int | None = Field(default=None, ge=1)
    notes: str | None = None
    recalculate_refunds: bool = Field(
        default=False,
        description="Conferma il ricalcolo dei rimborsi già registrati quando cambiano "
        "tipo o luogo dell'attività",
    )


class ActivityPlaceSummary(ApiModel):
    id: int
    name: str
    distance_km: int
    highway_cost: Decimal
    archived: bool


DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"
Frequency = Literal["weekly", "monthly"]


class RecurrenceRequest(ApiModel):
    frequency: Frequency
    interval: int = Field(default=1, ge=1, le=12)
    weekdays: list[int] | None = Field(
        default=None, description="Giorni ISO (1 = lunedì … 7 = domenica), solo settimanale."
    )
    ends_on: str = Field(pattern=DATE_PATTERN)


class SeriesPreviewRequest(ApiModel):
    starts_on: str = Field(pattern=DATE_PATTERN)
    recurrence: RecurrenceRequest


class SeriesPreviewResponse(ApiModel):
    dates: list[str]
    description: str


class ActivitySeriesCreateRequest(ApiModel):
    type: ActivityType
    title: str = Field(min_length=1, max_length=300)
    description: str | None = None
    location: str | None = None
    place_id: int | None = Field(default=None, ge=1)
    status: ActivityStatus | None = None
    reference_person_id: int | None = Field(default=None, ge=1)
    notes: str | None = None
    starts_on: str = Field(pattern=DATE_PATTERN)
    recurrence: RecurrenceRequest
    occurrences: list[str] = Field(
        min_length=1,
        max_length=200,
        description="Timestamp con fuso orario di ogni data della regola, nell'ordine "
        "restituito dall'anteprima: il browser fornisce lo scostamento corretto.",
    )


class ActivitySeriesSummary(ApiModel):
    id: int
    frequency: Frequency
    interval: int
    weekdays: list[int]
    starts_on: str
    ends_on: str
    description: str
    occurrence_count: int
    position: int = Field(description="Posizione di questa attività nella serie (da 1).")


class SeriesOccurrenceResponse(ApiModel):
    id: int
    starts_at: str
    status: ActivityStatus
    participant_count: int


class ActivitySeriesResponse(ApiModel):
    series: ActivitySeriesSummary
    occurrences: list[SeriesOccurrenceResponse]


class SeriesFollowingUpdateRequest(ApiModel):
    """Changes applied to an occurrence and all the following ones (dates excluded)."""

    type: ActivityType | None = None
    title: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = None
    location: str | None = None
    place_id: int | None = Field(default=None, ge=1)
    status: ActivityStatus | None = None
    reference_person_id: int | None = Field(default=None, ge=1)
    notes: str | None = None
    recalculate_refunds: bool = False


class SeriesBulkResponse(ApiModel):
    updated: int = 0
    archived: int = 0
    kept: int = Field(default=0, description="Attività lasciate perché hanno presenze registrate.")


class ActivityResponse(ApiModel):
    id: int
    type: ActivityType
    title: str
    description: str | None
    starts_at: str
    ends_at: str | None
    location: str | None
    place_id: int | None = None
    place: ActivityPlaceSummary | None = None
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
    series_id: int | None = None
    series: ActivitySeriesSummary | None = None
    participant_count: int = Field(
        default=0, description="Persone con presenza registrata (presenti + assenti)."
    )
    present_count: int = 0
    absent_count: int = 0
    reimbursement_flat: Decimal = Decimal("0.00")
    reimbursement_mileage: Decimal = Decimal("0.00")
    reimbursement_highway: Decimal = Decimal("0.00")
    reimbursement_total: Decimal = Decimal("0.00")
    driver_count: int = 0
    passenger_count: int = 0


AttendanceStatus = Literal["present", "absent"]


class ParticipantResponse(ApiModel):
    person_id: int
    person_name: str
    attendance: AttendanceStatus | None
    attendance_recorded_at: str | None
    is_driver: bool = False
    passenger_count: int | None = None
    refund_flat_amount: Decimal = Decimal("0.00")
    refund_distance_km: int | None = None
    refund_bonus_pct: int | None = None
    refund_mileage_amount: Decimal = Decimal("0.00")
    refund_highway_amount: Decimal = Decimal("0.00")
    refund_total: Decimal = Decimal("0.00")
    version: int


class ParticipantAttendanceWrite(ApiModel):
    person_id: int = Field(ge=1)
    attendance: AttendanceStatus | None = None
    is_driver: bool | None = Field(
        default=None, description="Assente: invariato. Solo per i presenti."
    )
    passenger_count: int | None = Field(
        default=None, ge=0, le=50, description="Passeggeri trasportati dall'autista."
    )

    @model_validator(mode="after")
    def validate_driver(self) -> ParticipantAttendanceWrite:
        if self.passenger_count is not None and self.is_driver is False:
            raise ValueError("I passeggeri si indicano solo per un autista")
        if self.is_driver and self.attendance != "present":
            raise ValueError("Solo un partecipante presente può essere autista")
        return self


class ParticipantAttendanceRequest(ApiModel):
    rows: list[ParticipantAttendanceWrite] = Field(min_length=1, max_length=500)


class ParticipationResponse(ApiModel):
    activity_id: int
    title: str
    type: ActivityType
    starts_at: str
    status: ActivityStatus
    attendance: AttendanceStatus | None
    is_driver: bool = False
    passenger_count: int | None = None
    distance_km: int | None = None
    reimbursement_flat: Decimal = Decimal("0.00")
    reimbursement_mileage: Decimal = Decimal("0.00")
    reimbursement_highway: Decimal = Decimal("0.00")
    reimbursement_amount: Decimal = Decimal("0.00")


class RefundSummaryRowResponse(ApiModel):
    person_id: int
    person_name: str
    rehearsal: Decimal = Decimal("0.00")
    concert: Decimal = Decimal("0.00")
    event: Decimal = Decimal("0.00")
    mileage: Decimal = Decimal("0.00")
    highway: Decimal = Decimal("0.00")
    distance_km: int = 0
    total: Decimal = Decimal("0.00")
