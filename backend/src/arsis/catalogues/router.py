from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from arsis.auth.dependencies import CurrentUser
from arsis.catalogues.schemas import (
    InstrumentCreateRequest,
    InstrumentResponse,
    InstrumentUpdateRequest,
    SectionCreateRequest,
    SectionResponse,
    SectionUpdateRequest,
)
from arsis.catalogues.service import CataloguesService
from arsis.core.api_models import ERROR_RESPONSES, Page, PaginationParams, build_page
from arsis.core.database import get_database_session
from arsis.generated.schemas import (
    InstrumentCreateDTO,
    InstrumentUpdateDTO,
    SectionCreateDTO,
    SectionUpdateDTO,
)

sections_router = APIRouter(prefix="/api/v1/sections", tags=["catalogues"])
instruments_router = APIRouter(prefix="/api/v1/instruments", tags=["catalogues"])
_service = CataloguesService()


def _section_response(section: Any) -> SectionResponse:
    return SectionResponse.model_validate(section)


def _instrument_response(instrument: Any) -> InstrumentResponse:
    return InstrumentResponse.model_validate(instrument)


@sections_router.get("", response_model=Page[SectionResponse], responses=ERROR_RESPONSES)
def list_sections(
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
) -> Page[SectionResponse]:
    sections = list(_service.list_sections(session))
    return build_page(
        [
            _section_response(item)
            for item in sections[pagination.offset : pagination.offset + pagination.page_size]
        ],
        total_items=len(sections),
        params=pagination,
    )


@sections_router.post(
    "",
    response_model=SectionResponse,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
)
def create_section(
    payload: SectionCreateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> SectionResponse:
    return _section_response(
        _service.create_section(
            session, data=SectionCreateDTO(**payload.model_dump()), actor_id=current_user.id
        )
    )


@sections_router.patch("/{section_id}", response_model=SectionResponse, responses=ERROR_RESPONSES)
def update_section(
    section_id: int,
    payload: SectionUpdateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> SectionResponse:
    return _section_response(
        _service.update_section(
            session,
            section_id=section_id,
            data=SectionUpdateDTO(**payload.model_dump(exclude={"version"}, exclude_unset=True)),
            expected_version=payload.version,
            actor_id=current_user.id,
        )
    )


@sections_router.delete("/{section_id}", response_model=SectionResponse, responses=ERROR_RESPONSES)
def archive_section(
    section_id: int,
    version: Annotated[int, Query(ge=1)],
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> SectionResponse:
    return _section_response(
        _service.archive_section(
            session, section_id=section_id, expected_version=version, actor_id=current_user.id
        )
    )


@instruments_router.get("", response_model=Page[InstrumentResponse], responses=ERROR_RESPONSES)
def list_instruments(
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
) -> Page[InstrumentResponse]:
    instruments = list(_service.list_instruments(session))
    return build_page(
        [
            _instrument_response(item)
            for item in instruments[pagination.offset : pagination.offset + pagination.page_size]
        ],
        total_items=len(instruments),
        params=pagination,
    )


@instruments_router.post(
    "",
    response_model=InstrumentResponse,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
)
def create_instrument(
    payload: InstrumentCreateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> InstrumentResponse:
    return _instrument_response(
        _service.create_instrument(
            session, data=InstrumentCreateDTO(**payload.model_dump()), actor_id=current_user.id
        )
    )


@instruments_router.patch(
    "/{instrument_id}", response_model=InstrumentResponse, responses=ERROR_RESPONSES
)
def update_instrument(
    instrument_id: int,
    payload: InstrumentUpdateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> InstrumentResponse:
    return _instrument_response(
        _service.update_instrument(
            session,
            instrument_id=instrument_id,
            data=InstrumentUpdateDTO(**payload.model_dump(exclude={"version"}, exclude_unset=True)),
            expected_version=payload.version,
            actor_id=current_user.id,
        )
    )


@instruments_router.delete(
    "/{instrument_id}", response_model=InstrumentResponse, responses=ERROR_RESPONSES
)
def archive_instrument(
    instrument_id: int,
    version: Annotated[int, Query(ge=1)],
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> InstrumentResponse:
    return _instrument_response(
        _service.archive_instrument(
            session, instrument_id=instrument_id, expected_version=version, actor_id=current_user.id
        )
    )
