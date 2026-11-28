"""HTTP endpoints for the role catalogue."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from arsis.auth.dependencies import CurrentUser
from arsis.core.api_models import ERROR_RESPONSES
from arsis.core.database import get_database_session
from arsis.roles.schemas import RoleTypeCreateRequest, RoleTypeResponse, RoleTypeUpdateRequest
from arsis.roles.service import RoleTypesService

router = APIRouter(prefix="/api/v1/role-types", tags=["role-types"])
_service = RoleTypesService()


def _response(role: Any, active_people: int = 0) -> RoleTypeResponse:
    return RoleTypeResponse.model_validate(role).model_copy(update={"active_people": active_people})


@router.get("", response_model=list[RoleTypeResponse], responses=ERROR_RESPONSES)
def list_role_types(
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
    include_archived: Annotated[bool, Query()] = False,
) -> list[RoleTypeResponse]:
    # Small catalogue: returned whole, in display order.
    return [
        _response(role, holders)
        for role, holders in _service.list_role_types(session, include_archived=include_archived)
    ]


@router.get("/{role_type_id}", response_model=RoleTypeResponse, responses=ERROR_RESPONSES)
def get_role_type(
    role_type_id: int,
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> RoleTypeResponse:
    role, holders = _service.get_role_type(session, role_type_id)
    return _response(role, holders)


@router.post(
    "",
    response_model=RoleTypeResponse,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
)
def create_role_type(
    payload: RoleTypeCreateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> RoleTypeResponse:
    return _response(
        _service.create_role_type(session, **payload.model_dump(), actor_id=current_user.id)
    )


@router.patch("/{role_type_id}", response_model=RoleTypeResponse, responses=ERROR_RESPONSES)
def update_role_type(
    role_type_id: int,
    payload: RoleTypeUpdateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> RoleTypeResponse:
    _service.update_role_type(
        session,
        role_type_id=role_type_id,
        values=payload.model_dump(exclude={"version"}, exclude_unset=True),
        expected_version=payload.version,
        actor_id=current_user.id,
    )
    role, holders = _service.get_role_type(session, role_type_id)
    return _response(role, holders)


@router.delete("/{role_type_id}", response_model=RoleTypeResponse, responses=ERROR_RESPONSES)
def archive_role_type(
    role_type_id: int,
    version: Annotated[int, Query(ge=1)],
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> RoleTypeResponse:
    return _response(
        _service.archive_role_type(
            session, role_type_id=role_type_id, expected_version=version, actor_id=current_user.id
        )
    )
