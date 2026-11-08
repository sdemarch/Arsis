from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from arsis.accounting.schemas import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
    MovementCreateRequest,
    MovementResponse,
    MovementUpdateRequest,
    OpeningBalancesRequest,
    OpeningBalancesResponse,
    SummaryResponse,
)
from arsis.accounting.service import AccountingService
from arsis.auth.dependencies import CurrentUser
from arsis.core.api_models import ERROR_RESPONSES, Page, PaginationParams, build_page
from arsis.core.database import get_database_session

router = APIRouter(prefix="/api/v1/accounting", tags=["accounting"])
_service = AccountingService()


def _category_response(value: Any) -> CategoryResponse:
    return CategoryResponse.model_validate(value)


def _movement_response(value: Any) -> MovementResponse:
    return MovementResponse.model_validate(value)


@router.get("/categories", response_model=list[CategoryResponse], responses=ERROR_RESPONSES)
def list_categories(
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
    include_archived: bool = False,
) -> list[CategoryResponse]:
    return [
        _category_response(item)
        for item in _service.list_categories(session, include_archived=include_archived)
    ]


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
)
def create_category(
    payload: CategoryCreateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> CategoryResponse:
    return _category_response(
        _service.create_category(session, values=payload.model_dump(), actor_id=current_user.id)
    )


@router.patch(
    "/categories/{category_id}", response_model=CategoryResponse, responses=ERROR_RESPONSES
)
def update_category(
    category_id: int,
    payload: CategoryUpdateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> CategoryResponse:
    values = payload.model_dump(exclude={"version"}, exclude_unset=True)
    return _category_response(
        _service.update_category(
            session,
            category_id=category_id,
            values=values,
            expected_version=payload.version,
            actor_id=current_user.id,
        )
    )


@router.delete(
    "/categories/{category_id}", response_model=CategoryResponse, responses=ERROR_RESPONSES
)
def archive_category(
    category_id: int,
    version: Annotated[int, Query(ge=1)],
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> CategoryResponse:
    return _category_response(
        _service.archive_category(
            session, category_id=category_id, expected_version=version, actor_id=current_user.id
        )
    )


@router.get("/movements", response_model=Page[MovementResponse], responses=ERROR_RESPONSES)
def list_movements(
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    fiscal_year: Annotated[int | None, Query(ge=2000, le=2100)] = None,
    month: Annotated[int | None, Query(ge=1, le=12)] = None,
    account: str | None = None,
    direction: str | None = None,
    category_id: Annotated[int | None, Query(ge=1)] = None,
    person_id: Annotated[int | None, Query(ge=1)] = None,
    course_id: Annotated[int | None, Query(ge=1)] = None,
    q: Annotated[str | None, Query(max_length=200)] = None,
    is_highlighted: bool | None = None,
) -> Page[MovementResponse]:
    movements = list(
        _service.list_movements(
            session,
            fiscal_year=fiscal_year,
            month=month if fiscal_year is not None else None,
            account=account,
            direction=direction,
            category_id=category_id,
            person_id=person_id,
            course_id=course_id,
            search=q,
            highlighted=is_highlighted,
        )
    )
    return build_page(
        [
            _movement_response(item)
            for item in movements[pagination.offset : pagination.offset + pagination.page_size]
        ],
        total_items=len(movements),
        params=pagination,
    )


@router.post(
    "/movements",
    response_model=MovementResponse,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
)
def create_movement(
    payload: MovementCreateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> MovementResponse:
    return _movement_response(
        _service.create_movement(session, values=payload.model_dump(), actor_id=current_user.id)
    )


@router.patch(
    "/movements/{movement_id}", response_model=MovementResponse, responses=ERROR_RESPONSES
)
def update_movement(
    movement_id: int,
    payload: MovementUpdateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> MovementResponse:
    values = payload.model_dump(exclude={"version"}, exclude_unset=True)
    return _movement_response(
        _service.update_movement(
            session,
            movement_id=movement_id,
            values=values,
            expected_version=payload.version,
            actor_id=current_user.id,
        )
    )


@router.delete(
    "/movements/{movement_id}", status_code=status.HTTP_204_NO_CONTENT, responses=ERROR_RESPONSES
)
def delete_movement(
    movement_id: int,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> None:
    _service.delete_movement(session, movement_id=movement_id, actor_id=current_user.id)


@router.get(
    "/opening-balances/{fiscal_year}",
    response_model=OpeningBalancesResponse,
    responses=ERROR_RESPONSES,
)
def get_opening_balances(
    fiscal_year: Annotated[int, Path(ge=2000, le=2100)],
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> OpeningBalancesResponse:
    return OpeningBalancesResponse(
        fiscal_year=fiscal_year, **_service.get_opening_balances(session, fiscal_year)
    )


@router.put(
    "/opening-balances/{fiscal_year}",
    response_model=OpeningBalancesResponse,
    responses=ERROR_RESPONSES,
)
def save_opening_balances(
    fiscal_year: Annotated[int, Path(ge=2000, le=2100)],
    payload: OpeningBalancesRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> OpeningBalancesResponse:
    return OpeningBalancesResponse(
        fiscal_year=fiscal_year,
        **_service.save_opening_balances(
            session,
            fiscal_year=fiscal_year,
            bank=payload.bank,
            cash=payload.cash,
            actor_id=current_user.id,
        ),
    )


@router.get("/summary/{fiscal_year}", response_model=SummaryResponse, responses=ERROR_RESPONSES)
def get_summary(
    fiscal_year: Annotated[int, Path(ge=2000, le=2100)],
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> SummaryResponse:
    return SummaryResponse.model_validate(_service.summarize(session, fiscal_year))
