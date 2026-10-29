"""HTTP endpoints for activities."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from arsis.activities.schemas import ActivityCreateRequest, ActivityResponse, ActivityUpdateRequest
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

router = APIRouter(prefix="/api/v1/activities", tags=["activities"])
_service = ActivitiesService()
_SORT_FIELDS = {"title", "starts_at", "status", "created_at", "updated_at"}


def _response(activity: Any) -> ActivityResponse:
    return ActivityResponse.model_validate(activity)


@router.get("", response_model=Page[ActivityResponse], responses=ERROR_RESPONSES)
def list_activities(
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    q: Annotated[str | None, Query(max_length=200)] = None,
    sort: str | None = None,
    include_archived: bool = False,
) -> Page[ActivityResponse]:
    sort_spec = parse_sort(
        sort,
        allowed_fields=_SORT_FIELDS,
        default_field="starts_at",
        default_direction=SortDirection.DESC,
    )
    activities = list(
        _service.list_activities(session, search=q, include_archived=include_archived)
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
        [
            _response(activity)
            for activity in activities[pagination.offset : pagination.offset + pagination.page_size]
        ],
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
    return _response(
        _service.create_activity(
            session, data=ActivityCreateDTO(**payload.model_dump()), actor_id=current_user.id
        )
    )


@router.get("/{activity_id}", response_model=ActivityResponse, responses=ERROR_RESPONSES)
def get_activity(
    activity_id: int,
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> ActivityResponse:
    return _response(_service.get_activity(session, activity_id))


@router.patch("/{activity_id}", response_model=ActivityResponse, responses=ERROR_RESPONSES)
def update_activity(
    activity_id: int,
    payload: ActivityUpdateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> ActivityResponse:
    values = payload.model_dump(exclude={"version"}, exclude_unset=True)
    return _response(
        _service.update_activity(
            session,
            activity_id=activity_id,
            data=ActivityUpdateDTO(**values),
            expected_version=payload.version,
            actor_id=current_user.id,
        )
    )


@router.delete("/{activity_id}", response_model=ActivityResponse, responses=ERROR_RESPONSES)
def archive_activity(
    activity_id: int,
    version: Annotated[int, Query(ge=1)],
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> ActivityResponse:
    return _response(
        _service.archive_activity(
            session, activity_id=activity_id, expected_version=version, actor_id=current_user.id
        )
    )
