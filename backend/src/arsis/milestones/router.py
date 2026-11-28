"""HTTP endpoints for milestones and their resets."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from arsis.auth.dependencies import CurrentUser
from arsis.core.api_models import ERROR_RESPONSES, Page, PaginationParams, build_page
from arsis.core.database import get_database_session, transaction
from arsis.generated.schemas import MilestoneCreateDTO, MilestoneUpdateDTO
from arsis.milestones.schemas import (
    AchievementStatus,
    MilestoneAchievementResponse,
    MilestoneBoardResponse,
    MilestoneCreateRequest,
    MilestoneResetRequest,
    MilestoneResponse,
    MilestoneUpdateRequest,
)
from arsis.milestones.service import BoardEntry, MilestonesService

router = APIRouter(prefix="/api/v1/milestones", tags=["milestones"])
_service = MilestonesService()


def _response(milestone: Any) -> MilestoneResponse:
    return MilestoneResponse.model_validate(milestone)


def _board(entry: BoardEntry) -> MilestoneBoardResponse:
    return MilestoneBoardResponse.model_validate(
        {**entry, "milestone": _response(entry["milestone"])}
    )


@router.get("", response_model=Page[MilestoneResponse], responses=ERROR_RESPONSES)
def list_milestones(
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    include_archived: Annotated[bool, Query()] = False,
) -> Page[MilestoneResponse]:
    milestones = list(_service.list_milestones(session, include_archived=include_archived))
    return build_page(
        [
            _response(item)
            for item in milestones[pagination.offset : pagination.offset + pagination.page_size]
        ],
        total_items=len(milestones),
        params=pagination,
    )


def _synced(session: Session, actor_id: int) -> None:
    """Self-heal the achievement log before reading (writes happen only on drift)."""
    with transaction(session):
        _service.sync_achievements(session, actor_id=actor_id)


# Declared before /{milestone_id} so the literal paths are not read as an id.
@router.get("/board", response_model=list[MilestoneBoardResponse], responses=ERROR_RESPONSES)
def get_board(
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> list[MilestoneBoardResponse]:
    _synced(session, current_user.id)
    return [_board(entry) for entry in _service.board(session)]


@router.get(
    "/achievements",
    response_model=list[MilestoneAchievementResponse],
    responses=ERROR_RESPONSES,
)
def list_achievements(
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
    status_filter: Annotated[AchievementStatus | None, Query(alias="status")] = None,
    milestone_id: Annotated[int | None, Query(ge=1)] = None,
    person_id: Annotated[int | None, Query(ge=1)] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 200,
) -> list[MilestoneAchievementResponse]:
    _synced(session, current_user.id)
    return [
        MilestoneAchievementResponse.model_validate(row)
        for row in _service.achievements(
            session,
            status=status_filter,
            milestone_id=milestone_id,
            person_id=person_id,
            limit=limit,
        )
    ]


@router.get("/{milestone_id}", response_model=MilestoneResponse, responses=ERROR_RESPONSES)
def get_milestone(
    milestone_id: int,
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> MilestoneResponse:
    return _response(_service.get_milestone(session, milestone_id))


@router.post(
    "",
    response_model=MilestoneResponse,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
)
def create_milestone(
    payload: MilestoneCreateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> MilestoneResponse:
    return _response(
        _service.create_milestone(
            session, data=MilestoneCreateDTO(**payload.model_dump()), actor_id=current_user.id
        )
    )


@router.patch("/{milestone_id}", response_model=MilestoneResponse, responses=ERROR_RESPONSES)
def update_milestone(
    milestone_id: int,
    payload: MilestoneUpdateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> MilestoneResponse:
    return _response(
        _service.update_milestone(
            session,
            milestone_id=milestone_id,
            data=MilestoneUpdateDTO(**payload.model_dump(exclude={"version"}, exclude_unset=True)),
            expected_version=payload.version,
            actor_id=current_user.id,
        )
    )


@router.delete("/{milestone_id}", response_model=MilestoneResponse, responses=ERROR_RESPONSES)
def archive_milestone(
    milestone_id: int,
    version: Annotated[int, Query(ge=1)],
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> MilestoneResponse:
    return _response(
        _service.archive_milestone(
            session, milestone_id=milestone_id, expected_version=version, actor_id=current_user.id
        )
    )


@router.post(
    "/{milestone_id}/resets", response_model=MilestoneBoardResponse, responses=ERROR_RESPONSES
)
def reset_milestone(
    milestone_id: int,
    payload: MilestoneResetRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> MilestoneBoardResponse:
    return _board(
        _service.reset(
            session,
            milestone_id=milestone_id,
            person_ids=payload.person_ids,
            actor_id=current_user.id,
        )
    )


@router.delete(
    "/{milestone_id}/resets/{reset_id}",
    response_model=MilestoneBoardResponse,
    responses=ERROR_RESPONSES,
)
def undo_reset(
    milestone_id: int,
    reset_id: int,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> MilestoneBoardResponse:
    return _board(
        _service.undo_reset(
            session, milestone_id=milestone_id, reset_id=reset_id, actor_id=current_user.id
        )
    )
