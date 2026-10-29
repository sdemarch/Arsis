from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from arsis.audit.service import record_audit_event
from arsis.auth.schemas import AuthUser, normalize_email
from arsis.core.config import Settings
from arsis.core.database import transaction
from arsis.core.errors import ConflictError, UnauthorizedError
from arsis.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from arsis.core.time import to_iso8601, utc_now
from arsis.generated.models import RefreshSession, User


@dataclass(frozen=True, slots=True)
class AuthenticationResult:
    access_token: str
    refresh_token: str
    user: AuthUser


def _to_auth_user(user: User) -> AuthUser:
    return AuthUser.model_validate(
        {
            "id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "last_login_at": user.last_login_at,
            "version": user.version,
        }
    )


def _new_session(
    user: User,
    *,
    now: datetime,
    settings: Settings,
    client_info: str | None,
) -> tuple[RefreshSession, str]:
    refresh_token = create_refresh_token()
    refresh_session = RefreshSession(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=to_iso8601(now + timedelta(seconds=settings.refresh_token_ttl)),
        client_info=client_info[:500] if client_info else None,
    )
    return refresh_session, refresh_token


def _authentication_result(
    user: User,
    refresh_token: str,
    *,
    settings: Settings,
    now: datetime,
) -> AuthenticationResult:
    return AuthenticationResult(
        access_token=create_access_token(
            user.id,
            secret_key=settings.app_secret_key,
            ttl_seconds=settings.access_token_ttl,
            now=now,
        ),
        refresh_token=refresh_token,
        user=_to_auth_user(user),
    )


def authenticate(
    session: Session,
    *,
    email: str,
    password: str,
    settings: Settings,
    client_info: str | None = None,
    ip_address: str | None = None,
) -> AuthenticationResult:
    normalized_email = normalize_email(email)
    now = utc_now()
    with transaction(session):
        user = session.scalar(
            select(User).where(func.lower(User.email) == normalized_email)
        )
        valid, updated_hash = verify_password(password, user.password_hash if user else None)
        if user is None or not valid or not user.is_active or user.archived_at is not None:
            raise UnauthorizedError()

        if updated_hash:
            user.password_hash = updated_hash
        user.last_login_at = to_iso8601(now)
        user.updated_at = to_iso8601(now)
        user.version += 1
        refresh_session, refresh_token = _new_session(
            user, now=now, settings=settings, client_info=client_info
        )
        session.add(refresh_session)
        record_audit_event(
            session,
            action="auth.login",
            entity_type="user",
            entity_id=user.id,
            user_id=user.id,
            ip_address=ip_address,
        )
        session.flush()
        return _authentication_result(user, refresh_token, settings=settings, now=now)


def rotate_refresh_token(
    session: Session,
    *,
    refresh_token: str,
    settings: Settings,
    client_info: str | None = None,
    ip_address: str | None = None,
) -> AuthenticationResult:
    now = utc_now()
    token_hash = hash_refresh_token(refresh_token)
    with transaction(session):
        refresh_session = session.scalar(
            select(RefreshSession).where(RefreshSession.token_hash == token_hash)
        )
        if (
            refresh_session is None
            or refresh_session.revoked_at is not None
            or datetime.fromisoformat(refresh_session.expires_at.replace("Z", "+00:00")) <= now
        ):
            raise UnauthorizedError(
                "Sessione non valida o scaduta", code="INVALID_REFRESH_SESSION"
            )

        user = session.get(User, refresh_session.user_id)
        if user is None or not user.is_active or user.archived_at is not None:
            raise UnauthorizedError(
                "Sessione non valida o scaduta", code="INVALID_REFRESH_SESSION"
            )

        refresh_session.revoked_at = to_iso8601(now)
        replacement, replacement_token = _new_session(
            user, now=now, settings=settings, client_info=client_info
        )
        session.add(replacement)
        session.flush()
        record_audit_event(
            session,
            action="auth.refresh",
            entity_type="refresh_session",
            entity_id=replacement.id,
            user_id=user.id,
            details={"replaced_session_id": refresh_session.id},
            ip_address=ip_address,
        )
        session.flush()
        return _authentication_result(user, replacement_token, settings=settings, now=now)


def revoke_refresh_token(
    session: Session,
    *,
    refresh_token: str | None,
    ip_address: str | None = None,
) -> None:
    if not refresh_token:
        return
    now = utc_now()
    with transaction(session):
        refresh_session = session.scalar(
            select(RefreshSession).where(
                RefreshSession.token_hash == hash_refresh_token(refresh_token)
            )
        )
        if refresh_session is None or refresh_session.revoked_at is not None:
            return
        refresh_session.revoked_at = to_iso8601(now)
        record_audit_event(
            session,
            action="auth.logout",
            entity_type="refresh_session",
            entity_id=refresh_session.id,
            user_id=refresh_session.user_id,
            ip_address=ip_address,
        )


def bootstrap_first_responsible(
    session: Session,
    *,
    email: str,
    display_name: str,
    password: str,
) -> AuthUser:
    if len(password) < 12:
        raise ValueError("La password deve contenere almeno 12 caratteri")
    normalized_email = normalize_email(email)
    normalized_name = display_name.strip()
    if not normalized_name:
        raise ValueError("Il nome visualizzato è obbligatorio")

    now = utc_now()
    with transaction(session):
        if session.scalar(select(func.count()).select_from(User)):
            raise ConflictError(
                "Il primo responsabile è già stato configurato",
                code="BOOTSTRAP_ALREADY_COMPLETED",
            )
        user = User(
            email=normalized_email,
            password_hash=hash_password(password),
            display_name=normalized_name,
            is_active=True,
            created_at=to_iso8601(now),
            updated_at=to_iso8601(now),
            version=1,
        )
        session.add(user)
        session.flush()
        record_audit_event(
            session,
            action="auth.bootstrap",
            entity_type="user",
            entity_id=user.id,
            user_id=user.id,
        )
        return _to_auth_user(user)
