"""HTTP endpoints for activities."""

from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from arsis.activities.participants_service import ActivityTotals, ParticipantsService
from arsis.activities.recurrence import describe, occurrence_dates
from arsis.activities.schemas import (
    ActivityCreateRequest,
    ActivityPlaceSummary,
    ActivityResponse,
    ActivitySeriesCreateRequest,
    ActivitySeriesResponse,
    ActivitySeriesSummary,
    ActivityStatus,
    ActivityUpdateRequest,
    ParticipantAttendanceRequest,
    ParticipantResponse,
    ParticipationResponse,
    RefundSummaryRowResponse,
    SeriesBulkResponse,
    SeriesFollowingUpdateRequest,
    SeriesOccurrenceResponse,
    SeriesPreviewRequest,
    SeriesPreviewResponse,
)
from arsis.activities.service import ActivitiesService, series_summary
from arsis.auth.dependencies import CurrentUser
from arsis.core.api_models import (
    ERROR_RESPONSES,
    Page,
    PaginationParams,
    SortDirection,
    build_page,
    parse_sort,
)
from arsis.core.database import get_database_session
from arsis.core.errors import ImportValidationError
from arsis.generated.models import Place
from arsis.generated.schemas import ActivityCreateDTO, ActivityUpdateDTO
from arsis.places.repository import PlacesRepository

router = APIRouter(prefix="/api/v1/activities", tags=["activities"])
_service = ActivitiesService()
_participants = ParticipantsService()
_places = PlacesRepository()
_SORT_FIELDS = {"title", "starts_at", "status", "created_at", "updated_at"}


def _response(
    activity: Any,
    counts: tuple[int, int, int] = (0, 0, 0),
    totals: ActivityTotals | None = None,
    place: Place | None = None,
    series: dict[str, Any] | None = None,
) -> ActivityResponse:
    participant_count, present_count, absent_count = counts
    update: dict[str, Any] = {
        "series": None if series is None else ActivitySeriesSummary.model_validate(series),
        "participant_count": participant_count,
        "present_count": present_count,
        "absent_count": absent_count,
        "place": None
        if place is None
        else ActivityPlaceSummary(
            id=place.id,
            name=place.name,
            distance_km=place.distance_km,
            highway_cost=place.highway_cost,
            archived=place.archived_at is not None,
        ),
    }
    if totals is not None:
        breakdown = totals["breakdown"]
        update |= {
            "reimbursement_flat": breakdown.flat,
            "reimbursement_mileage": breakdown.mileage,
            "reimbursement_highway": breakdown.highway,
            "reimbursement_total": breakdown.total,
            "driver_count": totals["driver_count"],
            "passenger_count": totals["passenger_count"],
        }
    return ActivityResponse.model_validate(activity).model_copy(update=update)


def _with_counts(session: Session, activities: list[Any]) -> list[ActivityResponse]:
    ids = [activity.id for activity in activities]
    counts = _participants.counts(session, activity_ids=ids)
    totals = _participants.totals(session, activity_ids=ids)
    places: dict[int, Place] = {}
    for place_id in {activity.place_id for activity in activities if activity.place_id}:
        place = _places.get_place(session, place_id, active_only=False)
        if place is not None:
            places[place_id] = place
    series = _service.series_summaries(session, activities)
    return [
        _response(
            activity,
            counts.get(activity.id, (0, 0, 0)),
            totals.get(activity.id),
            places.get(activity.place_id) if activity.place_id else None,
            series.get(activity.id),
        )
        for activity in activities
    ]


@router.get("", response_model=Page[ActivityResponse], responses=ERROR_RESPONSES)
def list_activities(
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    q: Annotated[str | None, Query(max_length=200)] = None,
    sort: str | None = None,
    include_archived: bool = False,
    starts_from: Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}-\d{2}$")] = None,
    starts_to: Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}-\d{2}$")] = None,
) -> Page[ActivityResponse]:
    sort_spec = parse_sort(
        sort,
        allowed_fields=_SORT_FIELDS,
        default_field="starts_at",
        default_direction=SortDirection.DESC,
    )
    activities = list(
        _service.list_activities(
            session,
            search=q,
            include_archived=include_archived,
            starts_from=starts_from,
            starts_to=starts_to,
        )
    )
    activities.sort(
        key=lambda activity: (
            getattr(activity, sort_spec.field) is None,
            str(getattr(activity, sort_spec.field) or "").casefold(),
            activity.id,
        ),
        reverse=sort_spec.direction == "desc",
    )
    return build_page(
        _with_counts(
            session, activities[pagination.offset : pagination.offset + pagination.page_size]
        ),
        total_items=len(activities),
        params=pagination,
    )


@router.post(
    "",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
)
def create_activity(
    payload: ActivityCreateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> ActivityResponse:
    activity = _service.create_activity(
        session, data=ActivityCreateDTO(**payload.model_dump()), actor_id=current_user.id
    )
    return _with_counts(session, [activity])[0]


@router.post(
    "/series/preview", response_model=SeriesPreviewResponse, responses=ERROR_RESPONSES
)
def preview_series(
    payload: SeriesPreviewRequest,
    _current_user: CurrentUser,
) -> SeriesPreviewResponse:
    rule = _service.preview_series(
        starts_on=payload.starts_on, recurrence=payload.recurrence.model_dump()
    )
    try:
        dates = [day.isoformat() for day in occurrence_dates(rule)]
    except ValueError as exc:
        raise ImportValidationError(str(exc)) from exc
    return SeriesPreviewResponse(dates=dates, description=describe(rule))


@router.post(
    "/series",
    response_model=list[ActivityResponse],
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
)
def create_series(
    payload: ActivitySeriesCreateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> list[ActivityResponse]:
    values = payload.model_dump(exclude={"starts_on", "recurrence", "occurrences"})
    try:
        _series, created = _service.create_series(
            session,
            values=values,
            starts_on=payload.starts_on,
            recurrence=payload.recurrence.model_dump(),
            occurrences=payload.occurrences,
            actor_id=current_user.id,
        )
    except ValueError as exc:
        raise ImportValidationError(str(exc)) from exc
    return _with_counts(session, created)


@router.get(
    "/series/{series_id}", response_model=ActivitySeriesResponse, responses=ERROR_RESPONSES
)
def get_series(
    series_id: int,
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> ActivitySeriesResponse:
    series = _service.get_series(session, series_id)
    occurrences = list(_service.series_occurrences(session, series_id))
    counts = _participants.counts(session, activity_ids=[item.id for item in occurrences])
    return ActivitySeriesResponse(
        series=ActivitySeriesSummary.model_validate(series_summary(series, len(occurrences))),
        occurrences=[
            SeriesOccurrenceResponse(
                id=item.id,
                starts_at=item.starts_at,
                status=cast(ActivityStatus, item.status),
                participant_count=counts.get(item.id, (0, 0, 0))[0],
            )
            for item in occurrences
        ],
    )


# Declared before /{activity_id} so the literal path is not read as an id.
@router.get(
    "/participations", response_model=list[ParticipationResponse], responses=ERROR_RESPONSES
)
def list_participations(
    person_id: Annotated[int, Query(ge=1)],
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> list[ParticipationResponse]:
    return [
        ParticipationResponse.model_validate(row)
        for row in _participants.participations(session, person_id=person_id)
    ]


@router.get(
    "/refund-summary", response_model=list[RefundSummaryRowResponse], responses=ERROR_RESPONSES
)
def get_refund_summary(
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> list[RefundSummaryRowResponse]:
    return [
        RefundSummaryRowResponse.model_validate(row)
        for row in _participants.refund_summary(session)
    ]


@router.get("/{activity_id}", response_model=ActivityResponse, responses=ERROR_RESPONSES)
def get_activity(
    activity_id: int,
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> ActivityResponse:
    return _with_counts(session, [_service.get_activity(session, activity_id)])[0]


@router.patch("/{activity_id}", response_model=ActivityResponse, responses=ERROR_RESPONSES)
def update_activity(
    activity_id: int,
    payload: ActivityUpdateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> ActivityResponse:
    values = payload.model_dump(exclude={"version", "recalculate_refunds"}, exclude_unset=True)
    activity = _service.update_activity(
        session,
        activity_id=activity_id,
        data=ActivityUpdateDTO(**values),
        expected_version=payload.version,
        actor_id=current_user.id,
        recalculate_refunds=payload.recalculate_refunds,
    )
    return _with_counts(session, [activity])[0]


@router.patch(
    "/{activity_id}/following", response_model=SeriesBulkResponse, responses=ERROR_RESPONSES
)
def update_following(
    activity_id: int,
    payload: SeriesFollowingUpdateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> SeriesBulkResponse:
    """Apply the same changes to this occurrence and the following ones of its series."""
    values = payload.model_dump(exclude={"recalculate_refunds"}, exclude_unset=True)
    updated = _service.update_following(
        session,
        activity_id=activity_id,
        values=values,
        actor_id=current_user.id,
        recalculate_refunds=payload.recalculate_refunds,
    )
    return SeriesBulkResponse(updated=updated)


@router.post(
    "/{activity_id}/end-series", response_model=SeriesBulkResponse, responses=ERROR_RESPONSES
)
def end_series(
    activity_id: int,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> SeriesBulkResponse:
    """End the series after this occurrence; those with recorded attendance are kept."""
    archived, kept = _service.end_series_after(
        session, activity_id=activity_id, actor_id=current_user.id
    )
    return SeriesBulkResponse(archived=archived, kept=kept)


@router.delete("/{activity_id}", response_model=ActivityResponse, responses=ERROR_RESPONSES)
def archive_activity(
    activity_id: int,
    version: Annotated[int, Query(ge=1)],
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> ActivityResponse:
    return _with_counts(
        session,
        [
            _service.archive_activity(
                session, activity_id=activity_id, expected_version=version, actor_id=current_user.id
            )
        ],
    )[0]


@router.get(
    "/{activity_id}/participants",
    response_model=list[ParticipantResponse],
    responses=ERROR_RESPONSES,
)
def list_participants(
    activity_id: int,
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> list[ParticipantResponse]:
    return [
        ParticipantResponse.model_validate(row)
        for row in _participants.list_participants(session, activity_id=activity_id)
    ]


@router.put(
    "/{activity_id}/attendances",
    response_model=list[ParticipantResponse],
    responses=ERROR_RESPONSES,
)
def save_attendances(
    activity_id: int,
    payload: ParticipantAttendanceRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> list[ParticipantResponse]:
    _participants.save_attendance(
        session,
        activity_id=activity_id,
        rows=[
            (row.person_id, row.attendance, row.is_driver, row.passenger_count)
            for row in payload.rows
        ],
        actor_id=current_user.id,
    )
    return [
        ParticipantResponse.model_validate(row)
        for row in _participants.list_participants(session, activity_id=activity_id)
    ]
