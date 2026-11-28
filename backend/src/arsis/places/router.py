from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from arsis.auth.dependencies import CurrentUser
from arsis.core.api_models import ERROR_RESPONSES, Page, PaginationParams, build_page
from arsis.core.database import get_database_session
from arsis.generated.schemas import PlaceCreateDTO, PlaceUpdateDTO
from arsis.places.schemas import PlaceCreateRequest, PlaceResponse, PlaceUpdateRequest
from arsis.places.service import PlacesService

router = APIRouter(prefix="/api/v1/places", tags=["places"])
_service = PlacesService()


def _response(place: Any) -> PlaceResponse:
    return PlaceResponse.model_validate(place)


@router.get("", response_model=Page[PlaceResponse], responses=ERROR_RESPONSES)
def list_places(
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    include_archived: Annotated[bool, Query()] = False,
) -> Page[PlaceResponse]:
    places = list(_service.list_places(session, include_archived=include_archived))
    return build_page(
        [
            _response(item)
            for item in places[pagination.offset : pagination.offset + pagination.page_size]
        ],
        total_items=len(places),
        params=pagination,
    )


@router.get("/{place_id}", response_model=PlaceResponse, responses=ERROR_RESPONSES)
def get_place(
    place_id: int,
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> PlaceResponse:
    return _response(_service.get_place(session, place_id))


@router.post(
    "", response_model=PlaceResponse, status_code=status.HTTP_201_CREATED, responses=ERROR_RESPONSES
)
def create_place(
    payload: PlaceCreateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> PlaceResponse:
    return _response(
        _service.create_place(
            session, data=PlaceCreateDTO(**payload.model_dump()), actor_id=current_user.id
        )
    )


@router.patch("/{place_id}", response_model=PlaceResponse, responses=ERROR_RESPONSES)
def update_place(
    place_id: int,
    payload: PlaceUpdateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> PlaceResponse:
    return _response(
        _service.update_place(
            session,
            place_id=place_id,
            data=PlaceUpdateDTO(**payload.model_dump(exclude={"version"}, exclude_unset=True)),
            expected_version=payload.version,
            actor_id=current_user.id,
        )
    )


@router.delete("/{place_id}", response_model=PlaceResponse, responses=ERROR_RESPONSES)
def archive_place(
    place_id: int,
    version: Annotated[int, Query(ge=1)],
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> PlaceResponse:
    return _response(
        _service.archive_place(
            session, place_id=place_id, expected_version=version, actor_id=current_user.id
        )
    )
