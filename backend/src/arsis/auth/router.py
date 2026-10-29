from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from arsis.auth.dependencies import CurrentUser
from arsis.auth.schemas import AuthUser, LoginRequest, TokenResponse
from arsis.auth.service import (
    AuthenticationResult,
    authenticate,
    revoke_refresh_token,
    rotate_refresh_token,
)
from arsis.core.config import Settings, get_settings
from arsis.core.database import get_database_session
from arsis.core.errors import UnauthorizedError

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _set_refresh_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=token,
        max_age=settings.refresh_token_ttl,
        httponly=True,
        secure=settings.refresh_cookie_secure,
        samesite="lax",
        path="/api/v1/auth",
    )


def _clear_refresh_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        httponly=True,
        secure=settings.refresh_cookie_secure,
        samesite="lax",
        path="/api/v1/auth",
    )


def _token_response(result: AuthenticationResult, settings: Settings) -> TokenResponse:
    return TokenResponse(
        access_token=result.access_token,
        expires_in=settings.access_token_ttl,
        user=result.user,
    )


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    session: Annotated[Session, Depends(get_database_session)],
) -> TokenResponse:
    settings = get_settings()
    result = authenticate(
        session,
        email=payload.email,
        password=payload.password.get_secret_value(),
        settings=settings,
        client_info=request.headers.get("user-agent"),
        ip_address=_client_ip(request),
    )
    _set_refresh_cookie(response, result.refresh_token, settings)
    return _token_response(result, settings)


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    request: Request,
    response: Response,
    session: Annotated[Session, Depends(get_database_session)],
) -> TokenResponse:
    settings = get_settings()
    refresh_token = request.cookies.get(settings.refresh_cookie_name)
    if not refresh_token:
        raise UnauthorizedError(
            "Sessione non valida o scaduta", code="INVALID_REFRESH_SESSION"
        )
    result = rotate_refresh_token(
        session,
        refresh_token=refresh_token,
        settings=settings,
        client_info=request.headers.get("user-agent"),
        ip_address=_client_ip(request),
    )
    _set_refresh_cookie(response, result.refresh_token, settings)
    return _token_response(result, settings)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    session: Annotated[Session, Depends(get_database_session)],
) -> None:
    settings = get_settings()
    revoke_refresh_token(
        session,
        refresh_token=request.cookies.get(settings.refresh_cookie_name),
        ip_address=_client_ip(request),
    )
    _clear_refresh_cookie(response, settings)


@router.get("/me", response_model=AuthUser)
def me(current_user: CurrentUser) -> AuthUser:
    return AuthUser.model_validate(
        {
            "id": current_user.id,
            "email": current_user.email,
            "display_name": current_user.display_name,
            "last_login_at": current_user.last_login_at,
            "version": current_user.version,
        }
    )
