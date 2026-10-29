"""HTTP endpoints for the people registry."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from arsis.auth.dependencies import CurrentUser
from arsis.core.api_models import ERROR_RESPONSES, Page, PaginationParams, build_page, parse_sort
from arsis.core.database import get_database_session
from arsis.generated.schemas import (
    PersonCreateDTO,
    PersonRoleCreateDTO,
    PersonRoleUpdateDTO,
    PersonUpdateDTO,
)
from arsis.people.schemas import (
    PersonCreateRequest,
    PersonResponse,
    PersonRoleCreateRequest,
    PersonRoleResponse,
    PersonRoleUpdateRequest,
    PersonUpdateRequest,
)
from arsis.people.service import PeopleService

router = APIRouter(prefix="/api/v1/people", tags=["people"])
_service = PeopleService()
_PERSON_SORT_FIELDS = {"first_name", "last_name", "email", "created_at", "updated_at"}


def _person_response(person: Any) -> PersonResponse:
    return PersonResponse.model_validate(person)


def _role_response(role: Any) -> PersonRoleResponse:
    return PersonRoleResponse.model_validate(role)


@router.get("", response_model=Page[PersonResponse], responses=ERROR_RESPONSES)
def list_people(
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    q: Annotated[str | None, Query(max_length=200)] = None,
    sort: str | None = None,
    include_archived: bool = False,
) -> Page[PersonResponse]:
    sort_spec = parse_sort(
        sort, allowed_fields=_PERSON_SORT_FIELDS, default_field="last_name"
    )
    people = list(
        _service.list_people(
            session, search=q, include_archived=include_archived
        )
    )
    people.sort(
        key=lambda person: (
            getattr(person, sort_spec.field) is None,
            str(getattr(person, sort_spec.field) or "").casefold(),
            person.id,
        ),
        reverse=sort_spec.direction == "desc",
    )
    offset = pagination.offset
    return build_page(
        [_person_response(person) for person in people[offset : offset + pagination.page_size]],
        total_items=len(people),
        params=pagination,
    )


@router.post(
    "",
    response_model=PersonResponse,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
)
def create_person(
    payload: PersonCreateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> PersonResponse:
    person = _service.create_person(
        session,
        data=PersonCreateDTO(**payload.model_dump()),
        actor_id=current_user.id,
    )
    return _person_response(person)


@router.get("/{person_id}", response_model=PersonResponse, responses=ERROR_RESPONSES)
def get_person(
    person_id: int,
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> PersonResponse:
    return _person_response(_service.get_person(session, person_id))


@router.patch("/{person_id}", response_model=PersonResponse, responses=ERROR_RESPONSES)
def update_person(
    person_id: int,
    payload: PersonUpdateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> PersonResponse:
    values = payload.model_dump(exclude={"version"}, exclude_unset=True)
    person = _service.update_person(
        session,
        person_id=person_id,
        data=PersonUpdateDTO(**values),
        expected_version=payload.version,
        actor_id=current_user.id,
    )
    return _person_response(person)


@router.delete("/{person_id}", response_model=PersonResponse, responses=ERROR_RESPONSES)
def archive_person(
    person_id: int,
    version: Annotated[int, Query(ge=1)],
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> PersonResponse:
    return _person_response(
        _service.archive_person(
            session,
            person_id=person_id,
            expected_version=version,
            actor_id=current_user.id,
        )
    )


@router.get(
    "/{person_id}/roles",
    response_model=list[PersonRoleResponse],
    responses=ERROR_RESPONSES,
)
def list_roles(
    person_id: int,
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
    include_archived: bool = False,
) -> list[PersonRoleResponse]:
    return [
        _role_response(role)
        for role in _service.list_roles(
            session, person_id=person_id, include_archived=include_archived
        )
    ]


@router.post(
    "/{person_id}/roles",
    response_model=PersonRoleResponse,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
)
def create_role(
    person_id: int,
    payload: PersonRoleCreateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> PersonRoleResponse:
    role = _service.create_role(
        session,
        data=PersonRoleCreateDTO(person_id=person_id, **payload.model_dump()),
        actor_id=current_user.id,
    )
    return _role_response(role)


@router.patch("/roles/{role_id}", response_model=PersonRoleResponse, responses=ERROR_RESPONSES)
def update_role(
    role_id: int,
    payload: PersonRoleUpdateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> PersonRoleResponse:
    values = payload.model_dump(exclude={"version"}, exclude_unset=True)
    role = _service.update_role(
        session,
        role_id=role_id,
        data=PersonRoleUpdateDTO(**values),
        expected_version=payload.version,
        actor_id=current_user.id,
    )
    return _role_response(role)


@router.delete("/roles/{role_id}", response_model=PersonRoleResponse, responses=ERROR_RESPONSES)
def archive_role(
    role_id: int,
    version: Annotated[int, Query(ge=1)],
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> PersonRoleResponse:
    return _role_response(
        _service.archive_role(
            session,
            role_id=role_id,
            expected_version=version,
            actor_id=current_user.id,
        )
    )
