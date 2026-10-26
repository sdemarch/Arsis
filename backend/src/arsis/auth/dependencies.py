from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from arsis.core.config import get_settings
from arsis.core.database import get_database_session
from arsis.core.errors import UnauthorizedError
from arsis.core.security import InvalidAccessTokenError, decode_access_token
from arsis.generated.models import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[Session, Depends(get_database_session)],
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Autenticazione richiesta", code="AUTHENTICATION_REQUIRED")
    try:
        user_id = decode_access_token(
            credentials.credentials,
            secret_key=get_settings().app_secret_key,
        )
    except InvalidAccessTokenError as exception:
        raise UnauthorizedError(
            "Access token non valido o scaduto", code="INVALID_ACCESS_TOKEN"
        ) from exception

    user = session.get(User, user_id)
    if user is None or not user.is_active or user.archived_at is not None:
        raise UnauthorizedError(
            "Access token non valido o scaduto", code="INVALID_ACCESS_TOKEN"
        )
    session.expunge(user)
    session.rollback()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
