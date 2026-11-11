"""HTTP endpoints for activities."""

from decimal import Decimal
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from arsis.activities.participants_service import ParticipantsService
from arsis.activities.schemas import (
    ActivityCreateRequest,
    ActivityResponse,
    ActivityUpdateRequest,
    ParticipantAddRequest,
    ParticipantAttendanceRequest,
    ParticipantResponse,
    ParticipationResponse,
    RefundSummaryRowResponse,
)
from arsis.activities.service import ActivitiesService
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
from arsis.generated.schemas import ActivityCreateDTO, ActivityUpdateDTO
from arsis.settings.service import SettingsService

router = APIRouter(prefix="/api/v1/activities", tags=["activities"])
_service = ActivitiesService()
_participants = ParticipantsService()
_settings = SettingsService()
_SORT_FIELDS = {"title", "starts_at", "status", "created_at", "updated_at"}


def _response(
    activity: Any,
    counts: tuple[int, int, int] = (0, 0, 0),
    rules: dict[str, Decimal] | None = None,
) -> ActivityResponse:
    participant_count, present_count, absent_count = counts
    return ActivityResponse.model_validate(activity).model_copy(
        update={
            "participant_count": participant_count,
            "present_count": present_count,
            "absent_count": absent_count,
            "reimbursement_total": Decimal(present_count) * (rules or {}).get(
                activity.type, Decimal("0.00")
            ),
        }
    )


def _with_counts(session: Session, activities: list[Any]) -> list[ActivityResponse]:
    counts = _participants.counts(session, activity_ids=[activity.id for activity in activities])
    refund_rules = _settings.get_refund_rules(session)
    rules = {
        "rehearsal": refund_rules.rehearsal,
        "concert": refund_rules.concert,
        "event": refund_rules.event,
    }
    return [
        _response(activity, counts.get(activity.id, (0, 0, 0)), rules) for activity in activities
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


# Declared before /{activity_id} so the literal path is not read as an id.
@router.get(
    "/participations", response_model=list[ParticipationResponse], responses=ERROR_RESPONSES
)
def list_participations(
    person_id: Annotated[int, Query(ge=1)],
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> list[ParticipationResponse]:
    refund_rules = _settings.get_refund_rules(session)
    rules = {
        "rehearsal": refund_rules.rehearsal,
        "concert": refund_rules.concert,
        "event": refund_rules.event,
    }
    return [
        ParticipationResponse.model_validate(row).model_copy(
            update={
                "reimbursement_amount": rules[row["type"]]
                if row["attendance"] == "present"
                else Decimal("0.00")
            }
        )
        for row in _participants.participations(session, person_id=person_id)
    ]


@router.get(
    "/refund-summary", response_model=list[RefundSummaryRowResponse], responses=ERROR_RESPONSES
)
def get_refund_summary(
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> list[RefundSummaryRowResponse]:
    refund_rules = _settings.get_refund_rules(session)
    return [
        RefundSummaryRowResponse.model_validate(row)
        for row in _participants.refund_summary(
            session,
            rules={
                "rehearsal": refund_rules.rehearsal,
                "concert": refund_rules.concert,
                "event": refund_rules.event,
            },
        )
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
    values = payload.model_dump(exclude={"version"}, exclude_unset=True)
    return _with_counts(
        session,
        [
        _service.update_activity(
            session,
            activity_id=activity_id,
            data=ActivityUpdateDTO(**values),
            expected_version=payload.version,
            actor_id=current_user.id,
        )
        ],
    )[0]


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


@router.post(
    "/{activity_id}/participants",
    response_model=ParticipantResponse,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
)
def add_participant(
    activity_id: int,
    payload: ParticipantAddRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> ParticipantResponse:
    return ParticipantResponse.model_validate(
        _participants.add_participant(
            session, activity_id=activity_id, person_id=payload.person_id, actor_id=current_user.id
        )
    )


@router.post(
    "/{activity_id}/participants/musicians",
    response_model=list[ParticipantResponse],
    responses=ERROR_RESPONSES,
)
def convoke_musicians(
    activity_id: int,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> list[ParticipantResponse]:
    """Add the musicians active on the activity date who are missing (not those removed)."""
    _participants.refresh_musicians(session, activity_id=activity_id, actor_id=current_user.id)
    return [
        ParticipantResponse.model_validate(row)
        for row in _participants.list_participants(session, activity_id=activity_id)
    ]


@router.delete(
    "/{activity_id}/participants/{person_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ERROR_RESPONSES,
)
def remove_participant(
    activity_id: int,
    person_id: int,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> None:
    _participants.remove_participant(
        session, activity_id=activity_id, person_id=person_id, actor_id=current_user.id
    )


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
        rows=[(row.person_id, row.attendance) for row in payload.rows],
        actor_id=current_user.id,
    )
    return [
        ParticipantResponse.model_validate(row)
        for row in _participants.list_participants(session, activity_id=activity_id)
    ]
