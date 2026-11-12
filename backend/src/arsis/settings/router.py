from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from arsis.auth.dependencies import CurrentUser
from arsis.core.api_models import ERROR_RESPONSES
from arsis.core.database import get_database_session
from arsis.settings.schemas import (
    GeneralSettingsResponse,
    GeneralSettingsUpdateRequest,
    RefundRulesResponse,
    RefundRulesUpdateRequest,
    ResponsibleUserCreateRequest,
    ResponsibleUserResponse,
    ResponsibleUserUpdateRequest,
)
from arsis.settings.service import SettingsService

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])
_service = SettingsService()


@router.get(
    "/responsible-users",
    response_model=list[ResponsibleUserResponse],
    responses=ERROR_RESPONSES,
)
def list_responsible_users(
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> list[ResponsibleUserResponse]:
    return _service.list_responsible_users(session)


@router.post(
    "/responsible-users",
    response_model=ResponsibleUserResponse,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
)
def create_responsible_user(
    payload: ResponsibleUserCreateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> ResponsibleUserResponse:
    return _service.create_responsible_user(session, data=payload, actor_id=current_user.id)


@router.patch(
    "/responsible-users/{user_id}",
    response_model=ResponsibleUserResponse,
    responses=ERROR_RESPONSES,
)
def update_responsible_user(
    user_id: int,
    payload: ResponsibleUserUpdateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> ResponsibleUserResponse:
    return _service.update_responsible_user(
        session, user_id=user_id, data=payload, actor_id=current_user.id
    )


@router.get("/general", response_model=GeneralSettingsResponse, responses=ERROR_RESPONSES)
def get_general_settings(
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> GeneralSettingsResponse:
    return _service.get_general(session)


@router.put("/general", response_model=GeneralSettingsResponse, responses=ERROR_RESPONSES)
def update_general_settings(
    payload: GeneralSettingsUpdateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> GeneralSettingsResponse:
    return _service.update_general(session, data=payload, actor_id=current_user.id)


@router.get("/activity-refund-rules", response_model=RefundRulesResponse, responses=ERROR_RESPONSES)
def get_activity_refund_rules(
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> RefundRulesResponse:
    return _service.get_refund_rules(session)


@router.put("/activity-refund-rules", response_model=RefundRulesResponse, responses=ERROR_RESPONSES)
def update_activity_refund_rules(
    payload: RefundRulesUpdateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> RefundRulesResponse:
    return _service.update_refund_rules(session, data=payload, actor_id=current_user.id)
